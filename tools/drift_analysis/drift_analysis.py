import numpy as np
import json
import os
import argparse
import subprocess
from datetime import datetime
from alive_progress import alive_bar
from concurrent.futures import ProcessPoolExecutor
import signal
import sys
import hashlib


def handle_sigint(signum, frame):
    print("SIGINT received. Cleaning up...")
    # Kill all python processes from my user
    subprocess.run(["pkill", "-u", os.getlogin(), "-f", "python"])
    sys.exit(0)


signal.signal(signal.SIGINT, handle_sigint)

from DriftAnalysisFramework.Optimization import OnePlusOne_CMA_ES, CMA_ES
from DriftAnalysisFramework.Info import OnePlusOne_CMA_ES as OnePlusOne_CMA_ES_Info, CMA_ES as CMA_ES_Info
from DriftAnalysisFramework.Fitness import Sphere
from DriftAnalysisFramework.Interpolation import get_data_value
from DriftAnalysisFramework.Analysis import DriftAnalysis, eval_drift
from DriftAnalysisFramework.Filter import gaussian_filter, spline_filter

parallel_execution = True

helper_functions = {
    # "stable_kappa": lambda alpha_, sigma_: get_data_value(alpha_, sigma_, kappa_data['alpha'], kappa_data['sigma'],
    #                                                       kappa_data['stable_kappa']),
    # "stable_sigma": lambda alpha_, kappa_: get_data_value(alpha_, kappa_, sigma_data['alpha'], sigma_data['kappa'],
    #                                                       sigma_data['stable_sigma']),
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
    parser.add_argument('output_path', type=str, help='Path to which the files are written', default='data')

    parser.add_argument('--potential_functions', type=str, help='JSON String of potential functions')
    parser.add_argument('--batch_size', type=int, help='Number of samples to test', default=50000)
    parser.add_argument('--sub_batch_size', type=int, help='Number of samples to test in on iteration', default=25000)

    parser.add_argument('--algorithm', type=str, help='[1+1-CMA-ES, CMA-ES]', default="1+1-CMA-ES")
    parser.add_argument('--constants', type=str, help='The constants for the run')
    parser.add_argument('--workers', type=int, help='Number of workers running the simulation', default=12)
    parser.add_argument('--indexes', type=str, help='Start and stop indexes for distributed execution', default='all')

    parser.add_argument('--alpha_start', type=float, help='Stable kappa data file name', default=0)
    parser.add_argument('--alpha_end', type=float, help='Stable kappa data file name', default=1.5707963267948966)
    parser.add_argument('--alpha_samples', type=int, help='Stable kappa data file name', default=24)

    parser.add_argument('--kappa_start', type=float, help='Stable kappa data file name', default=1)
    parser.add_argument('--kappa_end', type=float, help='Stable kappa data file name', default=100)
    parser.add_argument('--kappa_samples', type=int, help='Stable kappa data file name', default=128)

    parser.add_argument('--sigma_start', type=float, help='Stable kappa data file name', default=0.1)
    parser.add_argument('--sigma_end', type=float, help='Stable kappa data file name', default=10)
    parser.add_argument('--sigma_samples', type=int, help='Stable kappa data file name', default=256)

    # parser.add_argument('--sigma_input', type=str, help='Stable sigma data file name', default='stable_sigma.json')

    args = parser.parse_args()

    # get start time
    start_time = datetime.now()

    # number of workers
    workers = args.workers

    # potential_expressions
    potential_functions = json.loads(args.potential_functions)

    # constants
    defaults = {
        "CMA-ES": {
            "c_sigma": 0.2,
            "c_cov": 0.09182736455463728
        },
        "1+1-CMA-ES": {
            "d": 2,
            "p_target": 0.1818,
            "c_cov": 0.3,
        }
    }
    config_params = json.loads(args.constants) if args.constants else {}
    constants = {**defaults[args.algorithm], **config_params}

    # Initialize the target function and optimization algorithm
    if args.algorithm == "1+1-CMA-ES":
        alg = OnePlusOne_CMA_ES(Sphere(), {
            "d": constants["d"],
            "p_target": constants["p_target"],
            "c_cov": constants["c_cov"],
        })
        info = OnePlusOne_CMA_ES_Info()
    elif args.algorithm == "CMA-ES":
        alg = CMA_ES(Sphere(), {
            "c_sigma": constants["c_sigma"],
            "c_cov": constants["c_cov"],
        })
        info = CMA_ES_Info()
    else:
        alg = None
        print("Error: No valid algorithm specified")
        exit()

    # create states
    alpha_sequence = np.linspace(args.alpha_start, args.alpha_end, num=args.alpha_samples)
    kappa_sequence = np.geomspace(args.kappa_start, args.kappa_end, num=args.kappa_samples)
    sigma_sequence = np.geomspace(args.sigma_start, args.sigma_end, num=args.sigma_samples)

    # Initialize the Drift Analysis class
    da = DriftAnalysis(alg, info)
    da.batch_size = args.batch_size
    da.sub_batch_size = args.sub_batch_size

    # Initialize stable_sigma
    # sigma_data_raw = json.load(open(f'./{args.sigma_input}'))
    # sigma_data = {
    #     "alpha": np.array(
    #         next((sequence["sequence"] for sequence in sigma_data_raw["sequences"] if sequence["name"] == "alpha"),
    #              None)),
    #     "kappa": np.array(
    #         next((sequence["sequence"] for sequence in sigma_data_raw["sequences"] if sequence["name"] == "kappa"),
    #              None)),
    #     "stable_sigma": np.array(sigma_data_raw["values"])
    # }

    # Check if the sample sequence and precalculated are compatible
    # if alpha_sequence.min() < sigma_data['alpha'].min() or alpha_sequence.max() > sigma_data['alpha'].max():
    #     print("Warning: alpha_sequence_s is out of bounds for the stable_parameter data")
    # if kappa_sequence.min() < sigma_data['kappa'].min() or kappa_sequence.max() > sigma_data['kappa'].max():
    #     print("Warning: alpha_sequence is out of bounds for the stable_parameter data")

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

    start_idx = 0
    stop_idx = da.states.shape[0]

    if args.indexes != "all":
        start_idx = int(args.indexes.split("_")[0])
        stop_idx = int(args.indexes.split("_")[1])

    print(f"Indexes (start-stop): {start_idx}-{stop_idx}")
    print(f"Number of grid points (batch/total): {stop_idx - start_idx}/{da.states.shape[0]}")

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

    # Save data to a files
    for idx, potential_function in enumerate(potential_functions):
        # create a unique string for this potential function and run
        unique = {
            "algorithm": args.algorithm,
            "potential_expression": potential_function["code"].replace(" ", ""),
            'batch_size': da.batch_size,
            'sequences': [
                {'name': 'alpha', 'sequence': alpha_sequence.tolist()},
                {'name': 'kappa', 'sequence': kappa_sequence.tolist()},
                {'name': 'sigma', 'sequence': sigma_sequence.tolist()}
            ]
        }

        unique_string = json.dumps(unique, sort_keys=True)
        filename = hashlib.sha256(unique_string.encode()).hexdigest()[:10]

        data = {
            'algorithm': args.algorithm,
            'potential_function': potential_function,
            'drift': drifts[:, :, :, idx].tolist(),
            'potential_after': potential_after[:, :, :, idx].tolist(),
            'precision': precisions[:, :, :, idx].tolist(),
            'standard_deviation': standard_deviations[:, :, :, idx].tolist(),
            "info": {
                'batch_size': da.batch_size,
                'run_started': start_time.strftime("%d.%m.%Y %H:%M:%S"),
                'run_finished': end_time.strftime("%d.%m.%Y %H:%M:%S"),
                'sequences': [
                    {'name': 'alpha', 'sequence': alpha_sequence.tolist()},
                    {'name': 'kappa', 'sequence': kappa_sequence.tolist()},
                    {'name': 'sigma', 'sequence': sigma_sequence.tolist()}
                ],
            },
        }

        for key, field_info in da.info.fields.items():
            data["info"][key] = info_data[key].tolist()

            if field_info["type"] == "mean":
                data["info"][key + "_std"] = info_data[key + "_std"].tolist()

        if args.indexes != "all":
            filename = f'./{args.output_path}/parts/{filename}_{start_idx}-{stop_idx}.part'
        else:
            filename = f'./{args.output_path}/{filename}.json'

        with open(filename, 'w') as f:
            json.dump(data, f)
