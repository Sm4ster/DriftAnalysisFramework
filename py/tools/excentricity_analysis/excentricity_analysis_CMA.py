from DriftAnalysisFramework.OptimizationAlgorithms import CMA_ES
from DriftAnalysisFramework.TargetFunctions import Sphere
import numpy as np
# from performance.performance import perf
import time

# Globals
alpha_samples = 50
sigma_samples = 500

max_sigma = 2
alpha_sequence = np.linspace(5, 7, num=alpha_samples)
sigma_sequence = np.linspace(1, 2, num=sigma_samples)
alg_iterations = 100000
cutoff = 20000

target = Sphere(2)
constants = {
    "d": 2,
    "p_target": 0.1818,
    "c_p": 0.8333,
    "c_cov": 0.2,
    "dim": 2
}

alg = CMA_ES(target, constants)

alpha, kappa, sigma = np.repeat(alpha_sequence, sigma_samples), np.tile(sigma_sequence, alpha_samples), 4
kappa_store = np.array([alg_iterations, cutoff])

for i in range(cutoff):
    print(i)
    kappa = alg.iterate_normal(alpha, kappa, sigma)[1]

print("cutoff")
for i in range(alg_iterations - cutoff):
    print(i)
    kappa = alg.iterate_normal(alpha, kappa_store, sigma)[1]
    kappa_store[i] = kappa

