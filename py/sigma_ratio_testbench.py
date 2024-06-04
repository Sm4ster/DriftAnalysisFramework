import numpy as np
from DriftAnalysisFramework.Transformation import CMA_ES as CMA_TR
from DriftAnalysisFramework.Optimization import CMA_ES
from DriftAnalysisFramework.Fitness import Sphere

# Initialize the target function and optimization algorithm
alg = CMA_ES(Sphere(), {
    "d": 2,
    "p_target": 0.1818,
    "c_p": 0.8333,
    "c_cov": 0.2,
    "dim": 2
})


size = 10

m = np.array([np.array([0,1]) for _ in range(size)])
sigma = np.repeat(1, size)
C = np.array([np.eye(2) for _ in range(size)])
r = np.geomspace(0.1, 10, size)


sigma = (1/r) * sigma
C = np.square(r[:, np.newaxis, np.newaxis]) * C

z = np.random.standard_normal(2) / 2
z =  np.array([z for _ in range(size)])


alpha_before, kappa_before, sigma_before, _ = CMA_TR.transform_to_normal(m, C, sigma)

m, C, sigma, success = alg.step(m, C, sigma, z)
print(m)

alpha_after, kappa_after, sigma_after, _ = CMA_TR.transform_to_normal(m, C, sigma)

print(alpha_after)
print(kappa_after)
print(sigma_after)