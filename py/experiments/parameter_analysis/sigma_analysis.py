from datetime import datetime
import numpy as np
import multiprocessing
import json
import argparse

from DriftAnalysisFramework.Optimization import CMA_ES, OnePlusOne_CMA_ES
from DriftAnalysisFramework.Transformation import CMA_ES as TR
from DriftAnalysisFramework.Fitness import Sphere

from alive_progress import alive_bar

# Globals
debug = False

# alpha_sequence = np.linspace(0, np.pi / 2, num=1)
alpha_sequence = np.linspace(0, np.pi / 2, num=64)

# kappa_sequence = np.geomspace(1, 2000, num=1)
kappa_sequence = np.geomspace(1, 2000, num=2048)

progress_size = 1000

def experiment(alpha_chunk, kappa_chunk, queue, idx):
    chunk_size_ = idx[1] - idx[0]
    assert alpha_chunk.shape[0] == kappa_chunk.shape[0] == chunk_size_

    local_log_sigma_store = np.zeros([chunk_size_])
    local_success_store = np.zeros([chunk_size_])

    sigma = 1
    m, C, sigma = TR.transform_to_parameters(alpha_chunk, kappa_chunk, sigma)
    for i in range(groove_iteration):
        new_m, new_C, new_sigma, success = alg.step(m, C, sigma)
        _, _, sigma, factors = TR.transform_to_normal(new_m, new_C, new_sigma)
        sigma /= factors["distance_factor"]

        # report progress to the queue
        if i > 0 and i % progress_size == 0:
            if queue is not None: queue.put({"message": "progress"})

    for i in range(measured_samples):
        new_m, new_C, new_sigma, success = alg.step(m, C, sigma)
        _, _, sigma, factors = TR.transform_to_normal(new_m, new_C, new_sigma)
        sigma /= factors["distance_factor"]

        local_log_sigma_store += np.log(sigma)
        local_success_store += success[:, 0]

        # report progress to the queue
        if i > 0 and i % progress_size == 0:
            if queue is not None: queue.put({"message": "progress"})

    queue.put({
        "message": "done",
        "idx": idx,
        "kappa_data": local_log_sigma_store,
        "success_data": local_success_store
    })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='This script computes stable kappa values for CMA.')
    parser.add_argument('output', type=str, help='Output file name', default='stable_sigma.json')
    parser.add_argument('--algorithm', type=str, help='[1+1-CMA-ES, CMA-ES]', default="1+1-CMA-ES")
    parser.add_argument('--constants', type=str,
                        help='JSON string specifing the algorithm and the respective parameters of the algorithm')
    parser.add_argument('--workers', type=int, help='Number of workers running the simulation', default=12)
    parser.add_argument('--groove_iterations', type=int, help='Number of groove iterations before data gets recorded', default=5000)
    parser.add_argument('--measured_samples', type=int, help='Number of iterations that are measured and averaged', default=1000000)
    args = parser.parse_args()

    workers = args.workers

    groove_iteration = args.groove_iterations
    measured_samples = args.measured_samples

    chunk_size = int(np.ceil(alpha_sequence.shape[0] * kappa_sequence.shape[0] / workers))

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

    # stable sigma experiment
    print("Stable Sigma Experiment")

    # get start time
    start_time = datetime.now()

    # Initialize the target function and optimization algorithm
    if args.algorithm == "1+1-CMA-ES":
        alg = OnePlusOne_CMA_ES(Sphere(), constants)
    elif args.algorithm == "CMA-ES":
        alg = CMA_ES(Sphere(), constants)
    else:
        alg = None
        print("Error: No valid algorithm specified")
        exit()

    # combine all alphas and kappas
    alpha, kappa = np.repeat(alpha_sequence, kappa_sequence.shape[0]), np.tile(kappa_sequence, alpha_sequence.shape[0])
    assert alpha.shape[0] == kappa.shape[0]

    # Initialize data structures to hold results
    log_sigma_store = np.zeros([alpha_sequence.shape[0] * kappa_sequence.shape[0]])
    success_store = np.zeros([alpha_sequence.shape[0] * kappa_sequence.shape[0]])

    if debug:
        for p_idx in range(workers):
            l_idx = p_idx * chunk_size
            h_idx = (p_idx + 1) * chunk_size if p_idx + 1 < workers else alpha.shape[0]
            experiment(alpha[l_idx:h_idx], kappa[l_idx:h_idx], None, (l_idx, h_idx))

    else:
        # Create a multiprocessing Queue for progress updates
        progress_queue = multiprocessing.Queue()

        # List to keep track of processes
        processes = []

        # Creating and starting worker processes
        for p_idx in range(workers):
            l_idx = p_idx * chunk_size
            h_idx = (p_idx + 1) * chunk_size if p_idx + 1 < workers else alpha.shape[0]
            p = multiprocessing.Process(target=experiment,
                                        args=(alpha[l_idx:h_idx], kappa[l_idx:h_idx], progress_queue, (l_idx, h_idx)))
            processes.append(p)
            p.start()

        total_progress = (((measured_samples + groove_iteration) // progress_size) - 1) * workers
        with alive_bar(total_progress, force_tty=True, title="Collecting") as bar:
            completed_workers = 0
            while completed_workers < len(processes):
                update = progress_queue.get()  # Block until update is received
                if update["message"] == 'done':
                    completed_workers += 1
                    l_idx = update["idx"][0]
                    h_idx = update["idx"][1]
                    log_sigma_store[l_idx:h_idx] = update["kappa_data"]
                    success_store[l_idx:h_idx] = update["success_data"]
                else:
                    bar()

        # Ensure all processes have finished
        for p in processes:
            p.join()

    # get the end time after te run has finished
    end_time = datetime.now()

    # store the data in an efficient form to allow for interpolation later
    stable_sigma_data = np.exp(log_sigma_store / measured_samples).reshape(alpha_sequence.shape[0],
                                                                           kappa_sequence.shape[0])
    success_data = success_store.reshape(alpha_sequence.shape[0], kappa_sequence.shape[0])

    sigma_data = {
        'run_started': start_time.strftime("%d.%m.%Y %H:%M:%S"),
        'run_finished': end_time.strftime("%d.%m.%Y %H:%M:%S"),
        'iterations': int(measured_samples),
        'groove_iterations': int(groove_iteration),
        'sequences': [
            {'name': 'alpha', 'sequence': alpha_sequence.tolist()},
            {'name': 'kappa', 'sequence': kappa_sequence.tolist()}
        ],
        'values': stable_sigma_data.tolist(),
        'success': success_data.tolist()
    }

    with open(f'./{args.output}', 'w') as f:
        json.dump(sigma_data, f)
