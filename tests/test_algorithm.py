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


# implementation of the unvectorized algorithm for comparison
def CMA_ES_uv(alpha, kappa, sigma):
    pass

# create states
alpha_sequence = np.linspace(0, 1.5707963267948966, 128)
kappa_sequence = np.geomspace(1, 100, 128)
sigma_sequence = np.geomspace(0.1, 10, 128)

states = np.vstack(np.meshgrid(
    alpha_sequence,
    kappa_sequence,
    sigma_sequence,
    indexing='ij')).reshape(3, -1).T

alpha, kappa, sigma = states[:, 0], states[:, 1], states[:, 2]
alg.iterate(alpha, kappa, sigma)

