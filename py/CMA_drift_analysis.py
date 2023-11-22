import numpy as np
import json
from datetime import datetime
from alive_progress import alive_bar
from concurrent.futures import ProcessPoolExecutor, as_completed

from DriftAnalysisFramework.Optimization import CMA_ES
from DriftAnalysisFramework.Fitness import Sphere
from DriftAnalysisFramework.Interpolation import get_data_value
from DriftAnalysisFramework.Analysis import DriftAnalysis, eval_drift
from tests.test_data_format import test_data_format

parallel_execution = True

filename = "real_run_3"

# potential function
potential_function = ["norm(m)",
                      "where(log(kappa/stable_kappa(alpha, sigma)) > log(stable_kappa(alpha, sigma) / kappa), log(kappa/stable_kappa(alpha, sigma)), log(stable_kappa(alpha, sigma) / kappa))",
                      "where(log(sigma/stable_sigma(alpha, kappa)) > log(stable_sigma(alpha, kappa) / sigma), log(sigma/stable_sigma(alpha, kappa)), log(stable_sigma(alpha, kappa) / sigma))",
                      "(4*alpha)/3.14"]

# config
batch_size = 10000

# create states
alpha_sequence = np.linspace(0, np.pi / 4, num=3)
kappa_sequence = np.geomspace(1 / 10, 10, num=12)
sigma_sequence = np.geomspace(1 / 10, 10, num=12)

# Initialize the target function and optimization algorithm
alg = CMA_ES(Sphere(), {
    "d": 2,
    "p_target": 0.1818,
    "c_p": 0.8333,
    "c_cov": 0.2,
    "dim": 2
})


def main():
    # get start time
    start_time = datetime.now()

    # Initialize the Drift Analysis class
    da = DriftAnalysis(alg)
    da.batch_size = batch_size

    # Initialize stable_sigma and stable_kappa
    kappa_data = np.load('./data/stable_kappa.npz')
    sigma_data = np.load('./data/stable_sigma.npz')

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

    # Transform the individual states to an array we can evaluate vectorized
    states = np.vstack(np.meshgrid(alpha_sequence, kappa_sequence, sigma_sequence, indexing='ij')).reshape(3, -1).T

    # Evaluate the before potential to set up the class
    da.eval_potential(potential_function, states)

    # Initialize data structure to hold results
    drifts_raw = np.zeros([states.shape[0], len(da.potential_expr)])

    # For debugging the critical function and performance comparisons
    if parallel_execution:
        with alive_bar(states.shape[0], force_tty=True, title="Evaluating") as bar:
            def callback(future_):
                result = future_.result()
                drifts_raw[result[1]] = result[0]
                bar()

            with ProcessPoolExecutor(max_workers=8) as executor:
                for i in range(states.shape[0]):
                    future = executor.submit(eval_drift, *da.get_eval_args(i), i)
                    future.add_done_callback(callback)
    else:
        with alive_bar(states.shape[0], force_tty=True, title="Evaluating") as bar:
            for i in range(states.shape[0]):
                result = eval_drift(*da.get_eval_args(i), i)
                drifts_raw[result[1]] = result[0]
                bar()

    # get the end time after te run has finished
    end_time = datetime.now()

    # Transform data into a cube and check that the transformation was correct
    drifts = drifts_raw.reshape(
        len(alpha_sequence),
        len(kappa_sequence),
        len(sigma_sequence),
        len(da.potential_expr)
    )

    # Check if transformation worked properly
    if not test_data_format(drifts_raw, states, drifts, alpha_sequence, kappa_sequence, sigma_sequence):
        raise Exception("Transformation format check did not pass.")

    # Save data to file
    data = {
        'run_started': start_time.strftime("%d.%m.%Y %H:%M:%S"),
        'run_finished': end_time.strftime("%d.%m.%Y %H:%M:%S"),
        'potential_function': potential_function,
        'sequences': [
            {'name': 'alpha', 'sequence': alpha_sequence.tolist()},
            {'name': 'kappa', 'sequence': kappa_sequence.tolist()},
            {'name': 'sigma', 'sequence': sigma_sequence.tolist()}
        ],
        'drifts': drifts.tolist(),
    }

    with open(f'./data/{filename}.json', 'w') as f:
        json.dump(data, f)


if __name__ == '__main__':
    main()
