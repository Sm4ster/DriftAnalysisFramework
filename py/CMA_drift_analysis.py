import numpy as np
import json
import argparse
from datetime import datetime
from alive_progress import alive_bar
from concurrent.futures import ProcessPoolExecutor

from DriftAnalysisFramework.Optimization import OnePlusOne_CMA_ES, CMA_ES
from DriftAnalysisFramework.Fitness import Sphere
from DriftAnalysisFramework.Interpolation import get_data_value
from DriftAnalysisFramework.Analysis import DriftAnalysis, eval_drift
from DriftAnalysisFramework.Filter import gaussian_filter, spline_filter

parallel_execution = True
workers = 63

helper_functions = {
    "stable_kappa": lambda alpha_, sigma_: get_data_value(alpha_, sigma_, kappa_data['alpha'], kappa_data['sigma'],
                                                          kappa_data['stable_kappa']),
    "stable_sigma": lambda alpha_, kappa_: get_data_value(alpha_, kappa_, sigma_data['alpha'], sigma_data['kappa'],
                                                          sigma_data['stable_sigma']),
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

    parser.add_argument('--potential_functions', type=str, help='JSON String of potential functions', default='')
    parser.add_argument('--batch_size', type=int, help='Number of samples to test', default=50000)
    parser.add_argument('--sub_batch_size', type=int, help='Number of samples to test in on iteration', default=25000)

    parser.add_argument('--algorithm', type=str, help='[1+1-CMA-ES, CMA-ES]', default="1+1-CMA-ES")
    parser.add_argument('--CMA_c_cov', type=float, help='c_cov parameter of CMA-ES', default=0.2)
    parser.add_argument('--CMA_d', type=float, help='dampening parameter of CMA-ES', default=2)

    parser.add_argument('--alpha_start', type=float, help='Stable kappa data file name', default=0)
    parser.add_argument('--alpha_end', type=float, help='Stable kappa data file name', default=1.5707963267948966)
    parser.add_argument('--alpha_samples', type=int, help='Stable kappa data file name', default=24)

    parser.add_argument('--kappa_start', type=float, help='Stable kappa data file name', default=1)
    parser.add_argument('--kappa_end', type=float, help='Stable kappa data file name', default=100)
    parser.add_argument('--kappa_samples', type=int, help='Stable kappa data file name', default=128)

    parser.add_argument('--sigma_start', type=float, help='Stable kappa data file name', default=0.1)
    parser.add_argument('--sigma_end', type=float, help='Stable kappa data file name', default=10)
    parser.add_argument('--sigma_samples', type=int, help='Stable kappa data file name', default=256)

    parser.add_argument('--kappa_input', type=str, help='Stable kappa data file name', default='stable_kappa.json')
    parser.add_argument('--sigma_input', type=str, help='Stable sigma data file name', default='stable_sigma.json')
    parser.add_argument('--output_file', type=str, help='Output file name', default='drift_run.json')

    args = parser.parse_args()

    # potential_functions
    potential_functions = json.loads(args.potential_functions)

    # get start time
    start_time = datetime.now()

    # Initialize the target function and optimization algorithm
    if args.algorithm == "1+1-CMA-ES":
        alg = OnePlusOne_CMA_ES(Sphere(), {
            "d": args.CMA_d,
            "p_target": 0.1818,
            "c_cov": args.CMA_c_cov,
            "dim": 2
        })
    if args.algorithm == "CMA-ES":
        alg = CMA_ES(Sphere(), {
            "d": args.CMA_d,
            "p_target": 0.1818,
            "c_cov": args.CMA_c_cov,
            "dim": 2
        })
    else:
        alg = None
        print("Error: No valid algorithm specified")
        exit()

    # create states
    alpha_sequence = np.linspace(args.alpha_start, args.alpha_end, num=args.alpha_samples)
    kappa_sequence = np.geomspace(args.kappa_start, args.kappa_end, num=args.kappa_samples)
    sigma_sequence = np.geomspace(args.sigma_start, args.sigma_end, num=args.sigma_samples)

    # Initialize the Drift Analysis class
    da = DriftAnalysis(alg)
    da.batch_size = args.batch_size
    da.sub_batch_size = args.sub_batch_size

    # Initialize stable_sigma and stable_kappa
    kappa_data_raw = json.load(open(f'./data/{args.kappa_input}'))
    sigma_data_raw = json.load(open(f'./data/{args.sigma_input}'))

    kappa_data = {
        "alpha": np.array(
            next((sequence["sequence"] for sequence in kappa_data_raw["sequences"] if sequence["name"] == "alpha"),
                 None)),
        "sigma": np.array(
            next((sequence["sequence"] for sequence in kappa_data_raw["sequences"] if sequence["name"] == "sigma"),
                 None)),
        "stable_kappa": np.array(kappa_data_raw["values"])
    }

    sigma_data = {
        "alpha": np.array(
            next((sequence["sequence"] for sequence in sigma_data_raw["sequences"] if sequence["name"] == "alpha"),
                 None)),
        "kappa": np.array(
            next((sequence["sequence"] for sequence in sigma_data_raw["sequences"] if sequence["name"] == "kappa"),
                 None)),
        "stable_sigma": np.array(sigma_data_raw["values"])
    }

    # Check if sample sequence and precalculated are compatible
    if alpha_sequence.min() < kappa_data['alpha'].min() or alpha_sequence.max() > kappa_data['alpha'].max():
        print("Warning: alpha_sequence_k is out of bounds for the stable_parameter data")
    if alpha_sequence.min() < sigma_data['alpha'].min() or alpha_sequence.max() > sigma_data['alpha'].max():
        print("Warning: alpha_sequence_s is out of bounds for the stable_parameter data")
    if kappa_sequence.min() < sigma_data['kappa'].min() or kappa_sequence.max() > sigma_data['kappa'].max():
        print("Warning: alpha_sequence is out of bounds for the stable_parameter data")
    if sigma_sequence.min() < kappa_data['sigma'].min() or sigma_sequence.max() > kappa_data['sigma'].max():
        print("Warning: alpha_sequence is out of bounds for the stable_parameter data")

    # Update the function dict of the potential evaluation
    da.function_dict.update(helper_functions)

    # Evaluate the before potential to set up the class
    da.eval_potential([e[1] for e in potential_functions], alpha_sequence, kappa_sequence, sigma_sequence)

    # Initialize data structures to hold results
    drifts = np.zeros([len(alpha_sequence), len(kappa_sequence), len(sigma_sequence), len(da.potential_expr)])
    standard_deviations = np.zeros(
        [len(alpha_sequence), len(kappa_sequence), len(sigma_sequence), len(da.potential_expr)])
    precisions = np.zeros([len(alpha_sequence), len(kappa_sequence), len(sigma_sequence), len(da.potential_expr)])
    successes = np.zeros([len(alpha_sequence), len(kappa_sequence), len(sigma_sequence)])
    success_mean = np.zeros([len(alpha_sequence), len(kappa_sequence), len(sigma_sequence), 3])
    success_std = np.zeros([len(alpha_sequence), len(kappa_sequence), len(sigma_sequence), 3])
    no_success_mean = np.zeros([len(alpha_sequence), len(kappa_sequence), len(sigma_sequence), 3])
    no_success_std = np.zeros([len(alpha_sequence), len(kappa_sequence), len(sigma_sequence), 3])

    # For debugging the critical function and performance comparisons
    if parallel_execution:
        with alive_bar(da.states.shape[0], force_tty=True, title="Evaluating") as bar:
            def callback(future_):
                mean, std, precision, successes_, follow_up_success, follow_up_no_success, idx = future_.result()

                drifts[idx[0], idx[1], idx[2]] = mean
                standard_deviations[idx[0], idx[1], idx[2]] = std
                precisions[idx[0], idx[1], idx[2]] = precision
                successes[idx[0], idx[1], idx[2]] = successes_
                success_mean[idx[0], idx[1], idx[2]] = follow_up_success.mean
                success_std[idx[0], idx[1], idx[2]] = follow_up_success.std
                no_success_mean[idx[0], idx[1], idx[2]] = follow_up_no_success.mean
                no_success_std[idx[0], idx[1], idx[2]] = follow_up_no_success.std
                bar()


            with ProcessPoolExecutor(max_workers=workers) as executor:
                for i in range(da.states.shape[0]):
                    future = executor.submit(eval_drift, *da.get_eval_args(i))
                    future.add_done_callback(callback)
    else:
        with alive_bar(da.states.shape[0], force_tty=True, title="Evaluating") as bar:
            for i in range(da.states.shape[0]):
                mean, std, precision, successes_, follow_up_success, follow_up_no_success, idx = \
                    eval_drift(*da.get_eval_args(i))

                drifts[idx[0], idx[1], idx[2]] = mean
                standard_deviations[idx[0], idx[1], idx[2]] = std
                precisions[idx[0], idx[1], idx[2]] = precision
                successes[idx[0], idx[1], idx[2]] = successes_
                success_mean[idx[0], idx[1], idx[2]] = follow_up_success.mean
                success_std[idx[0], idx[1], idx[2]] = follow_up_success.std
                no_success_mean[idx[0], idx[1], idx[2]] = follow_up_no_success.mean
                no_success_std[idx[0], idx[1], idx[2]] = follow_up_no_success.std

                bar()

    # get the end time after te run has finished
    end_time = datetime.now()

    # Save data to file
    data = {
        'run_started': start_time.strftime("%d.%m.%Y %H:%M:%S"),
        'run_finished': end_time.strftime("%d.%m.%Y %H:%M:%S"),
        'batch_size': da.batch_size,
        'potential_function': potential_functions,
        'sequences': [
            {'name': 'alpha', 'sequence': alpha_sequence.tolist()},
            {'name': 'kappa', 'sequence': kappa_sequence.tolist()},
            {'name': 'sigma', 'sequence': sigma_sequence.tolist()}
        ],
        'drift': drifts.tolist(),
        'standard_deviation': standard_deviations.tolist(),
        'success': successes.tolist(),
        'precision': precisions.tolist(),
        'success_mean': success_mean.tolist(),
        'success_std': success_std.tolist(),
        'no_success_mean': no_success_mean.tolist(),
        'no_success_std': no_success_std.tolist(),
        'stable_kappa': kappa_data_raw,
        'stable_sigma': sigma_data_raw
    }

    with open(f'./data/{args.output_file}', 'w') as f:
        json.dump(data, f)
