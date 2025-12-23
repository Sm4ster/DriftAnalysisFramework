import json
import argparse
import subprocess
import uuid
import os
import numpy as np
from pathlib import Path

# limit number of queue files to keep filesystem overhead manageable
WARN_LIMIT = 1_000
HARD_LIMIT = 5_000

TMUX_SESSION = "remote_workers"

# Command to run remotely – change this to your actual task
REMOTE_COMMAND = (
    "/science/franksyj/DriftAnalysisFramework/py.sh "
    "/science/franksyj/DriftAnalysisFramework/tools/drift_analysis/drift_analysis.py "
    "{run_dir} "
    "--worker {workers} "
)

parser = argparse.ArgumentParser(description="This script does a parallel start for the empirical drift analysis")
parser.add_argument("algorithm_config_file", help="Algorithm configuration name (without .json).")
parser.add_argument("potential_function_file", help="Potential functions configuration name (without .json).")
parser.add_argument("run_config_file", help="Run parameters configuration name (without .json).")
parser.add_argument("--output_dir", default="data", help="Output directory.")
parser.add_argument("--compute_resources", default="machines.json", help="JSON file listing machines to use.")
args = parser.parse_args()


def add_tmux_window(session_name: str, window_name: str) -> None:
    subprocess.run(["tmux", "new-window", "-t", session_name, "-n", window_name], check=True)


def run_tmux_command(session_name: str, window_name: str, command: str) -> None:
    # send the command to the tmux window and press Enter
    subprocess.run(["tmux", "send-keys", "-t", f"{session_name}:{window_name}", command, "C-m"], check=True)


def get_unique_session_name(base_name: str) -> str:
    # ensure the session name does not collide with an existing tmux session
    session_name = base_name
    counter = 1
    while True:
        result = subprocess.run(
            ["tmux", "has-session", "-t", session_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if result.returncode != 0:
            return session_name
        session_name = f"{base_name}_{counter}"
        counter += 1


def build_job_ranges(num_jobs: int, batch_size: int = 1) -> list[tuple[int, int]]:
    """
    Returns a list of (start, end) tuples with half-open intervals [start, end).
    """
    if batch_size <= 0:
        raise ValueError("batch_size must be >= 1")

    return [(start, min(start + batch_size, num_jobs)) for start in range(0, num_jobs, batch_size)]


def main() -> None:
    # --- run id + directory layout ------------------------------------------------

    # unique identifier for this run
    run_id = uuid.uuid4().hex

    # directory layout for this run
    run_dir = Path(args.output_dir) / run_id
    queue_dir = run_dir / "queue"  # job files live here: *.job / *.processing / *.done / ...
    raw_dir = run_dir / "raw"  # intermediate result shards live here, bundled at the end

    run_dir.mkdir(parents=True, exist_ok=True)
    queue_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)

    # --- read config files --------------------------------------------------------

    config_base = Path("configurations")

    # run parameters
    run_parameters = json.load(
        (config_base / "run_parameters" / f"{args.run_config_file}.json").open(encoding="utf-8")
    )

    # algorithm config
    algorithm = json.load(
        (config_base / "algorithms" / f"{args.algorithm_config_file}.json").open(encoding="utf-8")
    )

    # potential functions config
    potential_functions = json.load(
        (config_base / "potential_functions" / f"{args.potential_function_file}.json").open(encoding="utf-8")
    )

    # --- persist a unified config snapshot ---------------------------------------

    # single source of truth for this run (workers can read just this file)
    run_config = {
        "run_id": run_id,
        "output_dir": str(run_dir),
        "queue_dir": str(queue_dir),
        "raw_dir": str(raw_dir),
        "run_parameters": run_parameters,
        "algorithm": algorithm,
        "potential_functions": potential_functions,
    }

    with (run_dir / "config.json").open("w", encoding="utf-8") as f:
        json.dump(run_config, f, indent=2)

    # --- create queue files -------------------------------------------------------

    num_jobs = run_parameters["alpha"][2] * run_parameters["kappa"][2] * run_parameters["sigma"][2]
    batch_size = run_parameters.get("batch_size", 1024)

    # avoid creating too many files (filesystem overhead)
    num_files = (num_jobs + batch_size - 1) // batch_size
    if num_files > HARD_LIMIT:
        raise RuntimeError(
            f"Refusing to create {num_files} job files (hard limit={HARD_LIMIT}). "
            f"Increase batch_size (currently {batch_size})."
        )

    if num_files > WARN_LIMIT:
        print(f"[queue] warning: creating {num_files} job files (warn limit={WARN_LIMIT})")

    print(f"[queue] checks passed — creating {num_files} job files")

    for start, end in build_job_ranges(num_jobs, batch_size):
        job_path = queue_dir / f"{start}_{end}.job"

        try:
            # atomic create of an empty file (idempotent if producer is restarted)
            fd = os.open(job_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
            os.close(fd)
        except FileExistsError:
            pass

    # --- create raw data files ---------------------------------------------------

    grid_shape = (run_parameters["alpha"][2], run_parameters["kappa"][2], run_parameters["sigma"][2],
                  len(potential_functions))

    np.memmap(raw_dir / "drifts.dat", dtype=np.float64, mode="w+", shape=grid_shape)[:] = np.nan
    np.memmap(raw_dir / "standard_deviations.dat", dtype=np.float64, mode="w+", shape=grid_shape)[:] = np.nan
    np.memmap(raw_dir / "precisions.dat", dtype=np.float64, mode="w+", shape=grid_shape)[:] = np.nan
    np.memmap(raw_dir / "potential_after.dat", dtype=np.float64, mode="w+", shape=grid_shape)[:] = np.nan

    # --- start remote workers via tmux -------------------------------------------

    session_name = get_unique_session_name(run_id)
    subprocess.run(["tmux", "new-session", "-d", "-s", session_name], check=True)

    machine_list = json.load(Path(args.compute_resources).open(encoding="utf-8"))

    for entry in machine_list:
        hostname = entry["hostname"]
        workers = entry["workers"]

        # create a tmux window for each machine
        print(f"Creating tmux window in '{session_name}' for {hostname}")
        add_tmux_window(session_name, hostname)

        # ssh into machine
        print(f"Logging into {hostname}...")
        run_tmux_command(session_name, hostname, f"ssh {hostname}")

        # start the worker command
        remote_cmd = REMOTE_COMMAND.format(run_dir=run_dir, workers=workers)
        print(f"Starting run on {hostname}:\n{remote_cmd}")

        run_tmux_command(session_name, hostname, "cd /science/franksyj/DriftAnalysisFramework")
        run_tmux_command(session_name, hostname, remote_cmd)

    # remove the first window of the session (created by tmux by default)
    subprocess.run(["tmux", "kill-window", "-t", f"{session_name}:1"], check=True)
    subprocess.run(["tmux", "move-window", "-r", "-t", session_name], check=True)

    print("✅ All tmux sessions started.")


if __name__ == "__main__":
    main()
