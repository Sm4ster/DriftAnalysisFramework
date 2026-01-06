import numpy as np
import json
import socket, os
import threading
import argparse
import subprocess
from datetime import datetime
from pathlib import Path
from alive_progress import alive_bar
from concurrent.futures import ProcessPoolExecutor
import signal
import sys
import hashlib
import random
import math


def handle_sigint(signum, frame):
    print("SIGINT received. Cleaning up...")
    # Kill all python processes from my user
    subprocess.run(["pkill", "-u", os.getlogin(), "-f", "python"])
    sys.exit(0)


signal.signal(signal.SIGINT, handle_sigint)

from DriftAnalysisFramework.Optimization import OnePlusOne_CMA_ES, CMA_ES
from DriftAnalysisFramework.Info import OnePlusOne_CMA_ES as OnePlusOne_CMA_ES_Info, CMA_ES as CMA_ES_Info
from DriftAnalysisFramework.Transformation import CMA_ES as CMA_TR
from DriftAnalysisFramework.Fitness import Sphere
from DriftAnalysisFramework.Analysis import DriftAnalysis, eval_drift
from DriftAnalysisFramework.Filter import gaussian_filter, spline_filter

parallel_execution = True

helper_functions = {
    "f": lambda x: gaussian_filter(x, 0.2, 0.01, 1) * x,
    "filter_alpha": lambda x, alpha: 1 - spline_filter(alpha, 1.5707963267948966 / 4, 1.5707963267948966 / 2, 5,
                                                       10) * x,
    "s_filter_1": lambda x, kappa: gaussian_filter(x, 0.5, 0.3 * (np.log(kappa) + 1), 0) * x,
    "s_filter_2": lambda x, kappa: gaussian_filter(x, 0.1, 0.1 * (np.log(kappa) + 1), 0) * x,
    "s_filter_3": lambda x, kappa: gaussian_filter(x, 0.01, 0.1 * (np.log(kappa) + 1), 0) * x,

    "target_kappa": lambda alpha, sigma: np.where(((np.cos(alpha) + 0.00000001) / sigma) ** 2 < 1, 1,
                                                  ((np.cos(alpha) + 0.00000001) / sigma) ** 2)
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='This script does drift simulation for CMA')
    parser.add_argument('run_dir', type=str, help='Path to which the files are written', default='data')
    parser.add_argument('--workers', type=int, help='Number of workers running the simulation', default=12)

    args = parser.parse_args()

    with (Path(args.run_dir) / "config.json").open(encoding="utf-8") as f:
        config = json.load(f)

    # make chunk dir available
    chunk_dir = Path(config["chunk_dir"])

    # get start time
    start_time = datetime.now()

    # number of workers
    workers = args.workers

    # algorithm config
    algo_cfg = config.get("algorithm", {})

    # constants
    algo_defaults = {
        "CMA-ES": {
            "c_mu": 0.1  # 0.09182736455463728
        },
        "1+1-CMA-ES": {
            "d": 2,
            "p_target": 0.1818,
            "c_cov": 0.3,
        }
    }

    experiment_defaults = {
        "normal_form": "trace",
        "sigma_scaling": "none",
        "selection_scheme": "default",
    }

    algo_name = algo_cfg.get("algorithm")

    # only these are valid algorithm names
    if algo_name not in ("CMA-ES", "1+1-CMA-ES"):
        raise ValueError(f"Unknown algorithm '{algo_name}'. Known: ['CMA-ES', '1+1-CMA-ES']")

    # merge default constants with optional overrides
    algorithm_params = algo_cfg.get("constants") or {}
    constants = {**algo_defaults[algo_name], **algorithm_params}

    # experiment-level defaults
    normal_form = algo_cfg.get("normal_form", experiment_defaults["normal_form"])
    sigma_scaling = algo_cfg.get("sigma_scaling", experiment_defaults["sigma_scaling"])
    selection_scheme = algo_cfg.get("selection_scheme", experiment_defaults["selection_scheme"])

    # Initialize the target function and optimization algorithm
    if algo_name == "1+1-CMA-ES":
        alg = OnePlusOne_CMA_ES(
            Sphere(),
            CMA_TR(normal_form),
            {
                "d": constants["d"],
                "p_target": constants["p_target"],
                "c_cov": constants["c_cov"],
            },
        )
        info = OnePlusOne_CMA_ES_Info()

    elif algo_name == "CMA-ES":
        alg = CMA_ES(
            Sphere(),
            CMA_TR(normal_form, sigma_scaling),
            {"c_mu": constants["c_mu"]},
            selection_scheme,
        )
        info = CMA_ES_Info()
    else:
        raise ValueError(f"No valid algorithm specified: {algo_name}")

    # create states
    run_params = config["run_parameters"]
    alpha_sequence = np.arccos(np.linspace(run_params["alpha"][0], run_params["alpha"][1], num=run_params["alpha"][2]))[
        ::-1]
    kappa_sequence = np.geomspace(run_params["kappa"][0], run_params["kappa"][1], num=run_params["kappa"][2])
    sigma_sequence = np.geomspace(run_params["sigma"][0], run_params["sigma"][1], num=run_params["sigma"][2])

    filenames = []
    filtered_potential_functions = []
    run_configs = []
    for idx, potential_function in enumerate(config["potential_functions"]):
        # create a unique string for this potential function and run
        current_run_config = {
            'algorithm': algo_name,
            'constants': constants,
            'normal_form': normal_form,
            'potential_function': potential_function,
            'samples_size': run_params["sample_size"],
            'grid': [
                {'name': 'alpha', 'start': run_params["alpha"][0], 'end': run_params["alpha"][1],
                 'samples': run_params["alpha"][2]},
                {'name': 'kappa', 'start': run_params["kappa"][0], 'end': run_params["kappa"][1],
                 'samples': run_params["kappa"][2]},
                {'name': 'sigma', 'start': run_params["sigma"][0], 'end': run_params["sigma"][1],
                 'samples': run_params["sigma"][2]},
            ],
        },

        unique_string = json.dumps(current_run_config, sort_keys=True)
        unique_filename = hashlib.sha256(unique_string.encode()).hexdigest()[:10]

        if not os.path.exists(f"{config["output_dir"]}/{unique_filename}.json"):
            run_configs.append(current_run_config)
            filenames.append(unique_filename)
            filtered_potential_functions.append(potential_function)
        else:
            print(f"[SKIP] Already exists: {unique_filename}.json")

    potential_functions = filtered_potential_functions

    if len(potential_functions) == 0:
        print("[INFO] All potential functions already computed. Nothing to do.")
        print(f"[INFO] To re-run, delete or move files in ./{config["output_dir"]}/")
        sys.exit(0)

    # Initialize the Drift Analysis class
    da = DriftAnalysis(alg, info)
    da.batch_size = min(run_params["sample_size"], run_params["sub_batch_size"])

    # Number of Batches (rounded up)
    num_batches = math.ceil(run_params["sample_size"] / da.batch_size)

    # final sample size, which is a multiple of the subbatchsize
    da.sample_size = da.batch_size * num_batches

    # Update the function dict of the potential evaluation
    da.function_dict.update(helper_functions)

    # Evaluate the before potential to set up the class
    da.eval_potential([e["code"] for e in potential_functions], alpha_sequence, kappa_sequence, sigma_sequence)


    def claim_job(queue_dir: Path):
        jobs = list(queue_dir.glob("*.job"))
        if not jobs:
            return None

        random.shuffle(jobs)

        for job in jobs:
            processing = job.with_suffix(".processing")
            try:
                os.rename(job, processing)  # atomic
                return processing
            except FileExistsError:
                continue

        return None


    while True:
        job = claim_job(Path(config["queue_dir"]))

        if job is None:
            # no jobs left right now
            break  # or time.sleep(...) and continue, see below

        start_idx, stop_idx = map(int, job.stem.split("_"))
        batch_size = stop_idx - start_idx
        total = da.states.shape[0]
        print(f"[job] {start_idx:>6}–{stop_idx:<6} | batch {batch_size:>4} / total {total}")

        # Initialize data structures to hold results
        true_idxs = np.empty((batch_size, 3), dtype=np.int32)
        drifts = np.empty((batch_size, len(da.potential_expr)), dtype=np.float64)
        standard_deviations = np.empty((batch_size, len(da.potential_expr)), dtype=np.float64)
        precisions = np.empty((batch_size, len(da.potential_expr)), dtype=np.float64)
        potential_after = np.empty((batch_size, len(da.potential_expr)), dtype=np.float64)

        info_data = {}
        for key, field_info in da.info.fields.items():
            info_data[key] = np.empty((batch_size, *field_info["shape"]), dtype=np.float64)

            if field_info["type"] == "mean":
                info_data[key + "_std"] = np.empty((batch_size, *field_info["shape"]), dtype=np.float64)

        bar_lock = threading.Lock()
        with alive_bar(stop_idx - start_idx, force_tty=True, title="Evaluating") as bar:
            def callback(future_):
                mean, std, precision, potential, info, idx, i = future_.result()

                local_idx = i - start_idx
                true_idxs[local_idx] = (idx[0], idx[1], idx[2])
                drifts[local_idx] = mean
                standard_deviations[local_idx] = std
                precisions[local_idx] = precision
                potential_after[local_idx] = potential

                for key, field_info in da.info.fields.items():
                    info_data[key][local_idx] = info[key]

                    if field_info["type"] == "mean":
                        info_data[key + "_std"][local_idx] = info[key + "_std"]

                with bar_lock:
                    bar()


            with ProcessPoolExecutor(max_workers=workers) as executor:
                for i in range(start_idx, stop_idx):
                    future = executor.submit(eval_drift, *da.get_eval_args(i))
                    future.add_done_callback(callback)

                executor.shutdown(wait=True)

        # Save data to files
        chunk_results = {
            "idxs": true_idxs,
            "drifts": drifts,
            "potential_after": potential_after,
            "standard_deviations": standard_deviations,
            "precisions": precisions,
        }

        for key, field_info in da.info.fields.items():
            chunk_results[key] = info_data[key]

            if field_info["type"] == "mean":
                chunk_results[key + "_std"] = info_data[key + "_std"]

        chunk_final = chunk_dir / f"job_{start_idx}_{stop_idx}.npz"
        chunk_tmp = chunk_dir / f"job_{start_idx}_{stop_idx}.npz.tmp"

        with open(chunk_tmp, "wb") as f:
            np.savez_compressed(f, **chunk_results)
        os.replace(chunk_tmp, chunk_final)

        # mark job as done (atomic rename)
        os.rename(job, job.with_suffix(".done"))

    print("No more jobs... Done!")


    def is_last_worker(queue_dir: Path) -> bool:
        """Return True, wenn keine Jobs und keine laufenden Jobs mehr existieren."""
        jobs = list(queue_dir.glob("*.job"))
        processing = list(queue_dir.glob("*.processing"))
        return len(jobs) == 0 and len(processing) == 0


    def sanitize_for_json(x):
        def _san(v):
            if isinstance(v, float):
                return v if math.isfinite(v) else None
            if isinstance(v, dict):
                for k, vv in v.items():
                    v[k] = _san(vv)
                return v
            if isinstance(v, list):
                for i, vv in enumerate(v):
                    v[i] = _san(vv)
                return v
            if isinstance(v, tuple):
                return tuple(_san(e) for e in v)
            return v

        return _san(x)


    if is_last_worker(Path(config["queue_dir"])):
        print("Last worker, merging files...")

        chunks = sorted(chunk_dir.glob("job_*.npz"))

        grid_shape = (len(alpha_sequence), len(kappa_sequence), len(sigma_sequence), len(da.potential_expr))
        full_drifts = np.empty(grid_shape)
        full_potential_after = np.empty(grid_shape)
        full_precisions = np.empty(grid_shape)
        full_standard_deviations = np.empty(grid_shape)

        full_info_data = {}
        for key, field_info in da.info.fields.items():
            full_info_data[key] = np.empty(
                (len(alpha_sequence), len(kappa_sequence), len(sigma_sequence), *field_info["shape"]), dtype=np.float64)

            if field_info["type"] == "mean":
                full_info_data[key + "_std"] = np.empty(
                    (len(alpha_sequence), len(kappa_sequence), len(sigma_sequence), *field_info["shape"]),
                    dtype=np.float64)

        for c in chunks:
            d = np.load(c, allow_pickle=False)

            for t in range(d["idxs"].shape[0]):
                alpha_idx = d["idxs"][t, 0]
                kappa_idx = d["idxs"][t, 1]
                sigma_idx = d["idxs"][t, 2]

                full_drifts[alpha_idx, kappa_idx, sigma_idx, :] = d["drifts"][t, :]
                full_potential_after[alpha_idx, kappa_idx, sigma_idx, :] = d["potential_after"][t, :]
                full_precisions[alpha_idx, kappa_idx, sigma_idx, :] = d["precisions"][t, :]
                full_standard_deviations[alpha_idx, kappa_idx, sigma_idx, :] = d["standard_deviations"][t, :]

                for key, field_info in da.info.fields.items():
                    full_info_data[key][alpha_idx, kappa_idx, sigma_idx, :] = d[key][t, :]
                    if field_info["type"] == "mean":
                        full_info_data[key + "_std"][alpha_idx, kappa_idx, sigma_idx, :] = d[key + "_std"][t, :]

        # get the end time after the run has finished
        end_time = datetime.now()

        for idx, potential_function in enumerate(potential_functions):
            arrays = {
                "drift": full_drifts[:, :, :, idx].astype(np.float32),
                "potential_after": full_potential_after[:, :, :, idx].astype(np.float32),
                "precision": full_precisions[:, :, :, idx].astype(np.float32),
                "standard_deviation": full_standard_deviations[:, :, :, idx].astype(np.float32),
                "grid_alpha": alpha_sequence,
                "grid_kappa": kappa_sequence,
                "grid_sigma": sigma_sequence
            }

            for key, field_info in da.info.fields.items():
                arrays[f"info_{key}"] = np.asarray(full_info_data[key])  # dtype beibehalten oder casten

                if field_info["type"] == "mean":
                    arrays[f"info_{key}_std"] = np.asarray(full_info_data[key + "_std"])

            meta = {
                "run_config": run_configs[idx],
                "run_finished": end_time.strftime("%d.%m.%Y %H:%M:%S"),
                "info_keys": list(info_data.keys()),
            }

            # save file
            output_dir = Path(config["output_dir"])
            output_dir.mkdir(parents=True, exist_ok=True)

            out_path = output_dir / f"{filenames[idx]}.npz"

            meta_u8 = np.frombuffer(
                json.dumps(meta, ensure_ascii=False).encode("utf-8"),
                dtype=np.uint8
            )
            arrays["meta_json"] = meta_u8

            np.savez_compressed(out_path, **arrays)
