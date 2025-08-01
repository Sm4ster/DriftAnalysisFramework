from DriftAnalysisFramework.Optimization import CMA_ES, OnePlusOne_CMA_ES
from DriftAnalysisFramework.Fitness import Sphere
import numpy as np

alg = CMA_ES(Sphere(), {
    "c_sigma": 1,
    "c_cov": 1,
})

alpha = np.array([0])
kappa = np.array([1])
sigma = np.array([1])

alg.iterate(alpha, kappa, sigma, num=1)
