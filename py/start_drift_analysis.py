import numpy as np
import numexpr as ne
from DriftAnalysisFramework.OptimizationAlgorithms import CMA_ES
from DriftAnalysisFramework.TargetFunctions import Sphere

# potential function
potential_function = "alpha * kappa"

# config
alpha_samples = 5
kappa_samples = 5
sigma_samples = 5
batch_size = 10

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

# evaluate the before potential
alpha, kappa, sigma = states[0][0], states[0][1], states[0][2]


# make step
alpha, kappa, sigma = alg.iterate(alpha, kappa, sigma, num=batch_size)

# evaluate the after potential
potential_after = ne.evaluate(potential_function)

print(alpha, kappa, alpha * kappa, potential_after)

# calculate the drift
