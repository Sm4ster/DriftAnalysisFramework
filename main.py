import json
import argparse
import subprocess
import uuid


parser = argparse.ArgumentParser(description='This script does a parallel start for the empirical drift analysis')
parser.add_argument('potential_function_file', help='The input file containing all potential functions for the run.')
parser.add_argument('parameter_file', help='The input file containing all options and parameters for the run.')
parser.add_argument('--output_dir', default='data', help='The output directory name.')
parser.add_argument('--compute_resources', default='machines.json', help='A JSON file with all machines used to compute the simulation run.')
parser.add_argument('--session_name', default='empirical_drift_analysis', help='The name for the tmux session.')
args = parser.parse_args()



# Name of the main tmux session
TMUX_SESSION = "remote_workers"

# Command to run remotely – change this to your actual task
REMOTE_COMMAND = ("/home/franksyj/DriftAnalysisFramework/py.sh "
                  "/home/franksyj/DriftAnalysisFramework/tools/drift_analysis/start_experiment.py "
                  "{potential_function_file} "
                  "{parameter_file} "
                  "{output_dir} "
                  "--run_id {run_id} "
                  "--server_id {server_id} "
                  "--max_servers {max_servers} "
                  "--worker {workers} "
                  "--indexes {start_idx}_{stop_idx} ")

def add_tmux_window(session_name, window_name):
    subprocess.run([
        "tmux", "new-window",  "-t", session_name, "-n", window_name
    ], check=True)

def run_tmux_command(session_name, window_name, command):
     # Send the command to the new window and press Enter
    subprocess.run([
        "tmux", "send-keys", "-t", f"{session_name}:{window_name}", command, "C-m"
    ], check=True)

def get_unique_session_name(base_name):
    session_name = base_name
    counter = 1
    while True:
        result = subprocess.run(["tmux", "has-session", "-t", session_name],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        if result.returncode != 0:
            # Session does not exist
            return session_name
        # Session exists, try a new name
        session_name = f"{base_name}_{counter}"
        counter += 1

def distribute_jobs_by_cores(num_jobs, cores_per_machine):
    total_cores = sum(cores_per_machine)
    job_shares = [core / total_cores * num_jobs for core in cores_per_machine]

    # Round down each share and track the fractional remainders
    job_counts = [int(share) for share in job_shares]
    remainders = [share - count for share, count in zip(job_shares, job_counts)]

    # Distribute leftover jobs to machines with largest remainders
    leftover_jobs = num_jobs - sum(job_counts)
    for _ in range(leftover_jobs):
        idx = remainders.index(max(remainders))
        job_counts[idx] += 1
        remainders[idx] = 0  # prevent giving another extra to the same machine

    # Convert to start/end ranges
    result = []
    current = 0
    for count in job_counts:
        result.append((current, current + count))
        current += count

    return result

def main():
    machine_list = json.load(open(f'./{args.compute_resources}'))
    core_list = []
    for idx, entry in enumerate(machine_list):
        core_list.append(entry["workers"])

    config = json.load(open(f'./configurations/run_parameters/{args.parameter_file}.json'))
    num_jobs = config['alpha'][2] * config['kappa'][2] * config['sigma'][2]

    index_list = distribute_jobs_by_cores(num_jobs, core_list)

    run_id = uuid.uuid4().hex

    # create tmux session
    session_name = get_unique_session_name(args.session_name)
    subprocess.run(["tmux", "new-session", "-d", "-s", session_name], check=True)

    for idx, entry in enumerate(machine_list):
        hostname = entry["hostname"]
        workers = entry["workers"]

        ssh_cmd = f"ssh {hostname}"

        # add commands in new windows
        print(f"Creating tmux window in '{session_name}'")
        add_tmux_window(session_name, hostname)

        # starting command in those sessions
        print(f"Logging into {hostname}...")
        run_tmux_command(session_name, hostname, ssh_cmd)

        # run the command to start the run
        remote_cmd = REMOTE_COMMAND.format(
            potential_function_file=args.potential_function_file,
            parameter_file=args.parameter_file,
            output_dir=args.output_dir,
            run_id=run_id,
            server_id=idx,
            max_servers=len(machine_list),
            workers=workers,
            start_idx=index_list[idx][0],
            stop_idx=index_list[idx][1]
        )
        print(f"Starting run... \n {remote_cmd}")
        run_tmux_command(session_name, hostname, "cd /home/franksyj/DriftAnalysisFramework")
        run_tmux_command(session_name, hostname, remote_cmd)

    # remove the first window of the session, as it is not used
    subprocess.run(["tmux", "kill-window", "-t", f"{session_name}:1"], check=True)
    subprocess.run(["tmux", "move-window", "-r", "-t", session_name], check=True)

    print("✅ All tmux sessions started.")

if __name__ == "__main__":
    main()