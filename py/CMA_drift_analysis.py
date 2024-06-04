import numpy as np
import json
import argparse
from datetime import datetime
from alive_progress import alive_bar
from concurrent.futures import ProcessPoolExecutor

from DriftAnalysisFramework.Optimization import CMA_ES
from DriftAnalysisFramework.Fitness import Sphere
from DriftAnalysisFramework.Interpolation import get_data_value
from DriftAnalysisFramework.Analysis import DriftAnalysis, eval_drift

parallel_execution = True
workers = 12

# potential function
potential_function = [
    ['\log(|m|)', "log(norm(m))"],
    ['|\log(\kappa/\kappa_s)|', "abs(log(kappa/stable_kappa(alpha,sigma)))"],
    ['|\log(\sigma/\sigma_s)|', "abs(log(sigma/stable_sigma(alpha,kappa)))"],
    ['|\log(\kappa^2/\kappa_s)|', "abs(log(kappa**2/stable_kappa(alpha,sigma)))"]
]

# config
sub_batch_size = 50000

# Initialize the target function and optimization algorithm
alg = CMA_ES(Sphere(), {
    "d": 2,
    "p_target": 0.1818,
    "c_p": 0.8333,
    "c_cov": 0.2,
    "dim": 2
})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='This script does drift simulation for CMA')
    parser.add_argument('--parameter_file', type=str, help='Parameter file name', default='parameters.json')
    parser.add_argument('--kappa_input', type=str, help='Stable kappa data file name', default='stable_kappa.json')
    parser.add_argument('--sigma_input', type=str, help='Stable sigma data file name', default='stable_sigma.json')
    parser.add_argument('--output', type=str, help='Output file name', default='drift_run.json')
    args = parser.parse_args()

    # get start time
    start_time = datetime.now()

    # config
    parameters = json.load(open(f'./{args.parameter_file}'))

    # create states
    alpha_sequence = np.linspace(parameters["alpha"][0], parameters["alpha"][1], num=parameters["alpha"][2])
    kappa_sequence = np.logspace(parameters["kappa"][0], parameters["kappa"][1], num=parameters["kappa"][2])
    sigma_sequence = np.logspace(parameters["sigma"][0], parameters["sigma"][1], num=parameters["sigma"][2])

    # Initialize the Drift Analysis class
    da = DriftAnalysis(alg)
    da.batch_size = parameters["batch_size"]
    da.sub_batch_size = sub_batch_size

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
    da.function_dict.update({
        "stable_kappa": lambda alpha_, sigma_: get_data_value(alpha_, sigma_, kappa_data['alpha'], kappa_data['sigma'],
                                                              kappa_data['stable_kappa']),
        "stable_sigma": lambda alpha_, kappa_: get_data_value(alpha_, kappa_, sigma_data['alpha'], sigma_data['kappa'],
                                                              sigma_data['stable_sigma'])
    })

    # Evaluate the before potential to set up the class
    da.eval_potential([e[1] for e in potential_function], alpha_sequence, kappa_sequence, sigma_sequence)

    # Initialize data structures to hold results
    drifts = np.zeros([len(alpha_sequence), len(kappa_sequence), len(sigma_sequence), len(da.potential_expr)])
    standard_deviations = np.zeros([len(alpha_sequence), len(kappa_sequence), len(sigma_sequence), len(da.potential_expr)])
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
        'potential_function': potential_function,
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

    with open(f'./data/{args.output}', 'w') as f:
        json.dump(data, f)