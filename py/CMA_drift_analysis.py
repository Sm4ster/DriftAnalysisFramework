import numpy as np
from alive_progress import alive_bar
from concurrent.futures import ThreadPoolExecutor

from DriftAnalysisFramework.Optimization import CMA_ES
from DriftAnalysisFramework.Fitness import Sphere
from DriftAnalysisFramework.Interpolation import get_data_value
from DriftAnalysisFramework.Analysis import DriftAnalysis

filename = "./data/drifts"

# potential function
potential_function = "stable_kappa(alpha, sigma)"

# config
batch_size = 100000

# create states
alpha_sequence = np.linspace(0, np.pi / 4, num=64)
kappa_sequence = np.geomspace(1 / 10, 10, num=256)
sigma_sequence = np.geomspace(1 / 10, 10, num=256)

# Initialize the target function and optimization algorithm
alg = CMA_ES(Sphere(), {
    "d": 2,
    "p_target": 0.1818,
    "c_p": 0.8333,
    "c_cov": 0.2,
    "dim": 2
})

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
states = np.vstack(np.meshgrid(alpha_sequence, kappa_sequence, sigma_sequence)).reshape(3, -1).T

# Evaluate the before potential to set up the class
da.eval_potential(potential_function, states)

with alive_bar(states.shape[0], force_tty=True, title="Evaluating") as bar:
    with ThreadPoolExecutor(max_workers=7) as executor:
        futures = [executor.submit(da.eval_drift, i) for i in range(states.shape[0])]
        for future in futures:
            future.add_done_callback(lambda _: bar())

# Save results into a file
np.savez(filename + '.npz', alpha=alpha_sequence, kappa=kappa_sequence, sigma=sigma_sequence,
         states=da.states, drifts=da.drifts)


da.errors.add_error("Test this error manager")
da.errors.add_error("Test this error manager again")

# Write the array of strings into the file
with open(filename + '.txt', 'w') as f:
    f.write(filename + '.npz\n')
    f.write(potential_function + '\n')
    f.write(str(batch_size) + '\n')
    f.write(str(alpha_sequence.shape[0]) + ' ' + str(alpha_sequence.min()) + ' ' + str(alpha_sequence.max()) + '\n')
    f.write(str(kappa_sequence.shape[0]) + ' ' + str(kappa_sequence.min()) + ' ' + str(kappa_sequence.max()) + '\n')
    f.write(str(sigma_sequence.shape[0]) + ' ' + str(sigma_sequence.min()) + ' ' + str(sigma_sequence.max()) + '\n')

    for error in da.errors.error_array:
        f.write(error + '\n')
