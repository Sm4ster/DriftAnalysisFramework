import numpy as np
import json
import os
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
import glob
import socket


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
        "selection_scheme": "normal",
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
    alpha_sequence = np.arccos(np.linspace(run_params["alpha"][0], run_params["alpha"][1], num=run_params["alpha"][2]))
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
    da.batch_size = min(run_params["batch_size"], run_params["sub_batch_size"])

    # Number of Batches (rounded up)
    num_batches = math.ceil(run_params["sample_size"] / da.batch_size)

    # final sample size, which is a multiple of the subbatchsize
    da.sample_size = da.batch_size * num_batches

    # Update the function dict of the potential evaluation
    da.function_dict.update(helper_functions)

    # Evaluate the before potential to set up the class
    da.eval_potential([e["code"] for e in potential_functions], alpha_sequence, kappa_sequence, sigma_sequence)

    # Initialize data structures to hold results
    drifts = np.full([len(alpha_sequence), len(kappa_sequence), len(sigma_sequence), len(da.potential_expr)], np.nan)
    potential_after = np.full([len(alpha_sequence), len(kappa_sequence), len(sigma_sequence), len(da.potential_expr)],
                              np.nan)
    standard_deviations = np.full(
        [len(alpha_sequence), len(kappa_sequence), len(sigma_sequence), len(da.potential_expr)], np.nan)
    precisions = np.full([len(alpha_sequence), len(kappa_sequence), len(sigma_sequence), len(da.potential_expr)],
                         np.nan)

    info_data = {}
    for key, field_info in da.info.fields.items():
        info_data[key] = np.full(
            [len(alpha_sequence), len(kappa_sequence), len(sigma_sequence), *field_info["shape"]], np.nan)

        if field_info["type"] == "mean":
            info_data[key + "_std"] = np.full(
                [len(alpha_sequence), len(kappa_sequence), len(sigma_sequence), *field_info["shape"]], np.nan)


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

        # For debugging the critical function and performance comparisons
        if parallel_execution:
            with alive_bar(stop_idx - start_idx, force_tty=True, title="Evaluating") as bar:
                def callback(future_):
                    mean, std, precision, potential, info, idx = future_.result()

                    drifts[idx[0], idx[1], idx[2]] = mean
                    standard_deviations[idx[0], idx[1], idx[2]] = std
                    precisions[idx[0], idx[1], idx[2]] = precision
                    potential_after[idx[0], idx[1], idx[2]] = potential

                    for key, field_info in da.info.fields.items():
                        info_data[key][idx[0], idx[1], idx[2]] = info[key]

                        if field_info["type"] == "mean":
                            info_data[key + "_std"][idx[0], idx[1], idx[2]] = info[key + "_std"]

                    bar()


                with ProcessPoolExecutor(max_workers=workers) as executor:
                    for i in range(start_idx, stop_idx):
                        future = executor.submit(eval_drift, *da.get_eval_args(i))
                        future.add_done_callback(callback)

                    executor.shutdown(wait=True)


        else:
            with alive_bar(da.states.shape[0], force_tty=True, title="Evaluating") as bar:
                for i in range(da.states.shape[0]):
                    mean, std, precision, potential, info, idx = eval_drift(*da.get_eval_args(i))

                    drifts[idx[0], idx[1], idx[2]] = mean
                    standard_deviations[idx[0], idx[1], idx[2]] = std
                    precisions[idx[0], idx[1], idx[2]] = precision
                    potential_after[idx[0], idx[1], idx[2]] = potential

                    for key, field_info in da.info.fields.items():
                        info_data[key][idx[0], idx[1], idx[2]] = info[key]

                        if field_info["type"] == "mean":
                            info_data[key + "_std"][idx[0], idx[1], idx[2]] = info[key + "_std"]

                    bar()

        # get the end time after the run has finished
        end_time = datetime.now()

        # Save data to files
        for idx, potential_function in enumerate(potential_functions):
            data = {
                'run_config': run_configs[idx],
                "meta": {
                    'run_started': start_time.strftime("%d.%m.%Y %H:%M:%S"),
                    'run_finished': end_time.strftime("%d.%m.%Y %H:%M:%S"),
                    'batch_size': da.batch_size
                },
                "info": {},
                'drift': drifts[:, :, :, idx].tolist(),
                'potential_after': potential_after[:, :, :, idx].tolist(),
                'precision': precisions[:, :, :, idx].tolist(),
                'standard_deviation': standard_deviations[:, :, :, idx].tolist(),
                'grid': [
                    {'name': 'alpha', 'sequence': alpha_sequence.tolist()},
                    {'name': 'kappa', 'sequence': kappa_sequence.tolist()},
                    {'name': 'sigma', 'sequence': sigma_sequence.tolist()}
                ]
            }

            for key, field_info in da.info.fields.items():
                data["info"][key] = info_data[key].tolist()

                if field_info["type"] == "mean":
                    data["info"][key + "_std"] = info_data[key + "_std"].tolist()

            # save file with partial results
            filename = f'./{config["output_dir"]}/parts/{filenames[idx]}_{start_idx}-{stop_idx}.part'
            with open(filename, 'w') as f:
                json.dump(data, f)

        # mark job as done (atomic rename)
        os.rename(job, job.with_suffix(".done"))

    print("No more jobs... Done!")

    # remaining = glob.glob(os.path.join(lock_dir, "*.lock"))
    # if not remaining:
    #     # Combine data to files
    #     print("[INFO] Last worker done – calling combine_results.py")
    #     for idx, potential_function in enumerate(potential_functions):
    #         subprocess.run([
    #             sys.executable,
    #             "tools/drift_analysis/combine_results.py",
    #             args.output_path,
    #             args.run_id,
    #             filenames[idx]
    #         ])
    #
    #     # remove lock directory
    #     try:
    #         os.rmdir(lock_dir)
    #     except OSError:
    #         pass
    #
    #     # remove parent lock directory
    #     locks_parent = os.path.dirname(lock_dir)
    #     try:
    #         os.rmdir(locks_parent)
    #     except OSError:
    #         pass
