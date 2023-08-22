import numpy as np
from concurrent.futures import ThreadPoolExecutor
from DriftAnalysisFramework.Optimization import CMA_ES
from DriftAnalysisFramework.Transformation import CMA_ES as TR
from DriftAnalysisFramework.Fitness import Sphere

from alive_progress import alive_bar

number_cores = 8

# Globals
groove_iteration = 500
measured_samples = 500

alpha_sequence = np.linspace(0, np.pi / 4, num=64)
kappa_sequence = np.geomspace(1 / 20, 20, num=256)
sigma_sequence = np.geomspace(1 / 20, 20, num=256)

alg = CMA_ES(Sphere(), {
    "d": 2,
    "p_target": 0.1818,
    "c_p": 0.8333,
    "c_cov": 0.2,
    "dim": 2
})

def chunk_data(data, num_chunks):
    """Splits a numpy array into approximately equal chunks."""
    chunk_size = len(data) // num_chunks
    chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
    return chunks


# stable kappa experiment
print("Stable Kappa Experiment")

alpha, kappa, sigma = np.repeat(alpha_sequence, sigma_sequence.shape[0]), 1, np.tile(sigma_sequence, alpha_sequence.shape[0])
m, C, sigma = TR.transform_to_parameters(alpha, kappa, sigma)

with alive_bar(groove_iteration, force_tty=True, title="Grooving", bar="notes", title_length=10) as bar:
    for i in range(groove_iteration):
        C = alg.step(m, C, sigma)[1]
        bar()

def process_chunk(chunk_idx):
    m_chunk = m_chunks[chunk_idx]
    C_chunk = C_chunks[chunk_idx]
    sigma_chunk = sigma_chunks[chunk_idx]

    print(m_chunk.shape[0], C_chunk.shape[0], sigma_chunk.shape[0])

    kappa_sum_store = np.empty([m_chunk.shape[0]])

    for i in range(measured_samples):
        C_val = alg.step(m_chunk, C_chunk, sigma_chunk)[1]
        kappa_val = TR.transform_to_normal(m_chunk, C_val, sigma_chunk)[1]
        kappa_sum_store += kappa_val
        bar()

    return kappa_sum_store / measured_samples

# Splitting m, C, sigma into chunks
m_chunks = chunk_data(m, number_cores)
C_chunks = chunk_data(C, number_cores)
sigma_chunks = chunk_data(sigma, number_cores)

print(C_chunks[0].shape)

# Multithreading the processing of chunks again
with alive_bar(measured_samples * number_cores, force_tty=True, title="Collecting") as bar:
    with ThreadPoolExecutor(max_workers=number_cores) as executor:
        results = list(executor.map(process_chunk, range(number_cores)))

# Aggregate the results
kappa_averages = np.hstack(results)

# Store the data in an efficient form
stable_kappa_data = kappa_averages.reshape(alpha_sequence.shape[0], sigma_sequence.shape[0])

# with alive_bar(measured_samples, force_tty=True, title="Collecting") as bar:
#     for i in range(measured_samples):
#         C = alg.step(m, C, sigma)[1]
#         kappa = TR.transform_to_normal(m, C, sigma)[1]
#         kappa_store[i] = kappa
#         bar()












# stable_kappa_data = np.mean(kappa_store, axis=0).reshape(alpha_sequence.shape[0], sigma_sequence.shape[0])

# stable sigma experiment
print("Stable Sigma Experiment")

# prepare algorithm inputs
alpha, kappa, sigma = np.repeat(alpha_sequence, kappa_sequence.shape[0]), np.tile(kappa_sequence, alpha_sequence.shape[0]), 1
m, C, sigma = TR.transform_to_parameters(alpha, kappa, sigma)

with alive_bar(groove_iteration, force_tty=True, title="Grooving", bar="notes", title_length=10) as bar:
    for i in range(groove_iteration):
        sigma = alg.step(m, C, sigma)[2]
        bar()

sigma_store = np.empty([alpha_sequence.shape[0] * kappa_sequence.shape[0]])
with alive_bar(measured_samples, force_tty=True, title="Collecting") as bar:
    for i in range(measured_samples):
        sigma = alg.step(m, C, sigma)[2]
        sigma_store += sigma
        bar()

# store the data in an efficient form to allow for interpolation later
stable_sigma_data = (sigma_store/measured_samples).reshape(alpha_sequence.shape[0], kappa_sequence.shape[0])

# Run data
filename = "./data/stable_parameters.txt"

# Write the array of strings into the file
with open(filename, 'w') as f:
    f.write('./data/stable_parameters.npz\n')
    f.write(str(measured_samples) + '\n')
    f.write(str(groove_iteration) + '\n')

# Save variables into a file
np.savez('./data/stable_parameters.npz', alpha=alpha_sequence, kappa=kappa_sequence, sigma=sigma_sequence,
         stable_kappa=stable_kappa_data, stable_sigma=stable_sigma_data)


