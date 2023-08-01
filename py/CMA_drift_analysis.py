import numpy as np
from alive_progress import alive_bar
from concurrent.futures import ThreadPoolExecutor

from DriftAnalysisFramework.Optimization import CMA_ES
from DriftAnalysisFramework.Fitness import Sphere
from DriftAnalysisFramework.Interpolation import get_data_value
from DriftAnalysisFramework.Analysis import DriftAnalysis

# potential function
potential_function = "stable_kappa(alpha, sigma)"

# config
alpha_samples = 2
kappa_samples = 2
sigma_samples = 2
batch_size = 10

# create states
alpha_sequence = np.linspace(0, np.pi / 3, num=alpha_samples)
kappa_sequence = np.geomspace(1 / 10, 10, num=kappa_samples)
sigma_sequence = np.geomspace(1 / 10, 10, num=sigma_samples)

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
data = np.load('./data/stable_parameters.npz')

alpha_data = data['alpha']
kappa_data = data['kappa']
sigma_data = data['sigma']
stable_kappa = data['stable_kappa']
stable_sigma = data['stable_sigma']

# Update the function dict of the potential evaluation
da.function_dict.update({
    "stable_kappa": lambda alpha_, sigma_: get_data_value(alpha_, sigma_, alpha_data, sigma_data, stable_kappa),
    "stable_sigma": lambda alpha_, kappa_: get_data_value(alpha_, kappa_, alpha_data, kappa_data, stable_sigma)
})

# Transform the individual states to an array we can evaluate vectorized
states = np.vstack(np.meshgrid(alpha_sequence, kappa_sequence, sigma_sequence)).reshape(3, -1).T

# Evaluate the before potential to set up the class
da.eval_potential(potential_function, states)

# with alive_bar(states.shape[0], force_tty=True, title="Evaluating") as bar:
    # with ThreadPoolExecutor(max_workers=7) as executor:
    #     futures = [executor.submit(da.eval_drift, i) for i in range(states.shape[0])]
    #     for future in futures:
    #         future.add_done_callback(lambda _: bar())

# # Save results into a file
# np.savez('./data/drifts.npz', alpha=alpha_sequence, kappa=kappa_sequence, sigma=sigma_sequence,
#          states=da.states, drifts=da.drifts)
#
# print(da.errors)
# for i in range(da.states.shape[0]):
#     print(da.states[i], da.drifts[i])
