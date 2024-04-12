from datetime import datetime
import numpy as np
import multiprocessing
import json

from DriftAnalysisFramework.Optimization import CMA_ES
from DriftAnalysisFramework.Transformation import CMA_ES as TR
from DriftAnalysisFramework.Fitness import Sphere

from alive_progress import alive_bar

# Globals
workers = 63
groove_iteration = 50000
measured_samples = 10000000

alpha_sequence = np.linspace(0, np.pi / 2, num=64)
sigma_sequence = np.geomspace(1 / 2000, 2, num=4096)

progress_size = 1000
chunk_size = int(np.ceil(alpha_sequence.shape[0] * sigma_sequence.shape[0] / workers))


def experiment(alpha_chunk, sigma_chunk, queue, idx):
    chunk_size_ = idx[1] - idx[0]
    assert alpha_chunk.shape[0] == sigma_chunk.shape[0] == chunk_size_

    local_kappa_store = np.zeros([chunk_size_])
    local_success_store = np.zeros([chunk_size_])

    kappa = 1
    for i in range(groove_iteration):
        m, C, sigma = TR.transform_to_parameters(alpha_chunk, kappa, sigma_chunk)
        new_m, C, new_sigma, success = alg.step(m, C, sigma)
        kappa = TR.transform_to_normal(new_m, C, new_sigma)[1]

        # report progress to the queue
        if i > 0 and i % progress_size == 0:
            queue.put({"message": "progress"})

    for i in range(measured_samples):
        m, C, sigma = TR.transform_to_parameters(alpha_chunk, kappa, sigma_chunk)
        new_m, C, new_sigma, success = alg.step(m, C, sigma)
        kappa = TR.transform_to_normal(new_m, C, new_sigma)[1]

        local_kappa_store += kappa
        local_success_store += success[:, 0]

        # report progress to the queue
        if i % progress_size == 0:
            queue.put({"message": "progress"})

    queue.put({
        "message": "done",
        "idx": idx,
        "kappa_data": local_kappa_store,
        "success_data": local_success_store
    })


if __name__ == "__main__":
    # stable kappa experiment
    print("Stable Kappa Experiment")

    # get start time
    start_time = datetime.now()

    # Initialize the algorithm
    alg = CMA_ES(Sphere(), {
        "d": 2,
        "p_target": 0.1818,
        "c_p": 0.8333,
        "c_cov": 0.2,
        "dim": 2
    })

    # combine all alphas and sigmas
    alpha, sigma = np.repeat(alpha_sequence, sigma_sequence.shape[0]), np.tile(sigma_sequence, alpha_sequence.shape[0])
    assert alpha.shape[0] == sigma.shape[0]

    # Initialize data structures to hold results
    kappa_store = np.zeros([alpha_sequence.shape[0] * sigma_sequence.shape[0]])
    success_store = np.zeros([alpha_sequence.shape[0] * sigma_sequence.shape[0]])

    # Create a multiprocessing Queue for progress updates
    progress_queue = multiprocessing.Queue()

    # List to keep track of processes
    processes = []

    # Creating and starting worker processes
    for p_idx in range(workers):
        l_idx = p_idx * chunk_size
        h_idx = (p_idx + 1) * chunk_size if p_idx + 1 < workers else alpha.shape[0]
        p = multiprocessing.Process(target=experiment,
                                    args=(alpha[l_idx:h_idx], sigma[l_idx:h_idx], progress_queue, (l_idx, h_idx)))
        processes.append(p)
        p.start()

    with alive_bar((((measured_samples + groove_iteration) // progress_size) - 1) * workers, force_tty=True, title="Processing") as bar:
        completed_workers = 0
        while completed_workers < len(processes):
            update = progress_queue.get()  # Block until update is received
            if update["message"] == 'done':
                print("A worker has completed")
                completed_workers += 1
                l_idx = update["idx"][0]
                h_idx = update["idx"][1]
                kappa_store[l_idx:h_idx] = update["kappa_data"]
                success_store[l_idx:h_idx] = update["success_data"]
            else:
                bar()

    # Ensure all processes have finished
    for p in processes:
        p.join()

    # get the end time after te run has finished
    end_time = datetime.now()

    # store the data in an efficient form to allow for interpolation later
    stable_kappa_data = (kappa_store / measured_samples).reshape(alpha_sequence.shape[0], sigma_sequence.shape[0])
    success_data = success_store.reshape(alpha_sequence.shape[0], sigma_sequence.shape[0])

    kappa_data = {
        'run_started': start_time.strftime("%d.%m.%Y %H:%M:%S"),
        'run_finished': end_time.strftime("%d.%m.%Y %H:%M:%S"),
        'iterations': int(measured_samples),
        'groove_iterations': int(groove_iteration),
        'sequences': [
            {'name': 'alpha', 'sequence': alpha_sequence.tolist()},
            {'name': 'sigma', 'sequence': sigma_sequence.tolist()},
        ],
        'values': stable_kappa_data.tolist(),
        'success': success_data.tolist()
    }

    with open('data/stable_kappa_small.json', 'w') as f:
        json.dump(kappa_data, f)
