import numpy as np
import numexpr as ne
from collections import ChainMap
from DriftAnalysisFramework.OptimizationAlgorithms import CMA_ES
from DriftAnalysisFramework.TargetFunctions import Sphere
from DriftAnalysisFramework.Transformations import CMA_ES as TR

# potential function
potential_function = "alpha * kappa + 5.456"

# config
alpha_samples = 2
kappa_samples = 2
sigma_samples = 2
batch_size = 3

# create states
alpha_sequence = np.linspace(0, np.pi / 4, num=alpha_samples)
kappa_sequence = np.geomspace(1 / 10, 10, num=kappa_samples)
sigma_sequence = np.geomspace(1 / 10, 10, num=sigma_samples)

states = np.vstack(np.meshgrid(alpha_sequence, kappa_sequence, sigma_sequence)).reshape(3, -1).T

# initialize the target function and optimization algorithm
alg = CMA_ES(Sphere(), {
    "d": 2,
    "p_target": 0.1818,
    "c_p": 0.8333,
    "c_cov": 0.2,
    "dim": 2
})

for i in range(states.shape[0]):
    # evaluate the before potential
    alpha, kappa, sigma = states[i][0], states[i][1], states[i][2]
    m, C, _ = TR.transform_to_parameters(alpha, kappa, sigma)
    potential_before = ne.evaluate(potential_function)

    print(m, C, alpha, kappa, sigma, potential_before, "\n")

    # make step
    normal_form, raw_params, raw_params_before, _ = alg.iterate(alpha, kappa, sigma, num=batch_size)

    # make sure that sigma does not get overwritten and
    # the raw sigma is available with underscore
    raw_params["sigma_"] = raw_params["sigma"]

    # evaluate the after potential
    potential_after = ne.evaluate(potential_function, dict(ChainMap(normal_form, raw_params)))

    print(normal_form, raw_params, raw_params_before, potential_after, "\n\n")

    # calculate the drift
