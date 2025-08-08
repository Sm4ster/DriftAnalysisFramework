from DriftAnalysisFramework.Optimization import CMA_ES
from DriftAnalysisFramework.Fitness import Sphere
from DriftAnalysisFramework.Transformation import CMA_ES as CMA_TR
import numpy as np

alg = CMA_ES(
    Sphere(),
    CMA_TR("determinant"),
    {
        "c_mu": 0.1
    }
)

# create states
alpha_sequence = np.linspace(0, 1.5707963267948966, 2)
kappa_sequence = np.geomspace(1, 100, 2)
sigma_sequence = np.geomspace(0.1, 10, 2)

states = np.vstack(np.meshgrid(
    alpha_sequence,
    kappa_sequence,
    sigma_sequence,
    indexing='ij')).reshape(3, -1).T

alpha, kappa, sigma = states[:, 0], states[:, 1], states[:, 2]
alg.iterate(alpha, kappa, sigma)
