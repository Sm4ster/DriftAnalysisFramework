from DriftAnalysisFramework.OptimizationAlgorithms import CMA_ES
from DriftAnalysisFramework.TargetFunctions import Sphere
import numpy as np
import matplotlib.pyplot as plt

# Globals
sigma_iterations = 200
alg_iterations = 10000
cutoff = 500

dimension = 2

# Experiments
results = np.empty([sigma_iterations,4])

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
algorithm.set_location([1, 0])

for sigma_idx, sigma_22 in enumerate(np.linspace(1, 0.0001, num=sigma_iterations)):

    state = {
        "sigma": 3,
        "cov_m": np.array([[1, 1], [1, sigma_22]]),
        "p_succ": 1
    }

    sigma_array = np.empty([alg_iterations, 1])

    for idx in range(alg_iterations):
        next_state = algorithm.iterate(state)
        sigma_array[idx] = next_state["sigma"]
        state["sigma"] = next_state["sigma"]
        state["p_succ"] = next_state["p_succ"]

    # remove the first few iterations just to be sure to catch no starting bias
    sigma_array = np.split(sigma_array, [cutoff, alg_iterations])[1]

    results[sigma_idx] = sigma_22, sigma_array.mean(), sigma_array.var(), sigma_array.max() - sigma_array.min()

# Plotting, evaluating results
plt.title("Middle value of converged Stepsize")
plt.xlabel("sigma_22")
plt.ylabel("sigma*")
plt.plot(results[:,0],results[:,1])
plt.show()

