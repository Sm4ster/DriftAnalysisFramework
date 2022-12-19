from DriftAnalysisFramework.OptimizationAlgorithms import CMA_ES
from DriftAnalysisFramework.TargetFunctions import Sphere
import numpy as np
import matplotlib.pyplot as plt

# Globals
iterations = 1000
dimension = 2

# Experiments
target = Sphere(dimension)
algorithm = CMA_ES(
    target,
    {
        "d": 2,
        "p_target": 0.1818,
        "c_cov_plus": 0.2,
        "c_p": 0.8333
    }
)
algorithm.set_location([0, 1])

sigma_22 = 10
state = {
    "sigma": 100,
    "cov_m": np.array([[1, 1], [1, sigma_22]]),
    "p_succ": 1
}

sigma_array = np.empty([iterations, 1])

for idx in range(iterations):
    next_state = algorithm.iterate(state)
    sigma_array[idx] = next_state["sigma"]
    state["sigma"] = next_state["sigma"]
    state["p_succ"] = next_state["p_succ"]

# Plotting, evaluating results
print(sigma_array.mean())

plt.plot(sigma_array)
plt.show()

