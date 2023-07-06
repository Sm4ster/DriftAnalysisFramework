from DriftAnalysisFramework.Optimization import OnePlusOne_ES
from DriftAnalysisFramework.Fitness import Sphere
import numpy as np

# Globals
alg_iterations = 100000
cutoff = 20000
dimension = 2


# Experiments
target = Sphere(dimension)
algorithm = OnePlusOne_ES(
    target,
    {
        "alpha": 2
    })

location = [1, 0]
algorithm.set_location(location)

sigma_array = np.empty([alg_iterations, 1])

state = {
    "sigma": 3,
}
for idx in range(alg_iterations):
    next_state = algorithm.iterate(state)
    sigma_array[idx] = next_state["sigma"]
    state["sigma"] = next_state["sigma"]

# remove the first few iterations just to be sure to catch no starting bias
sigma_array = np.split(sigma_array, [cutoff, alg_iterations])[1]

print(sigma_array.mean())
