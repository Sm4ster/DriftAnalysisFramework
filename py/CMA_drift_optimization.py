import numpy as np
import json
import cma

drift_data_raw = json.load(open('./data/full_run_dense_grid.json'))
drift_data = np.array(drift_data_raw["drift"]) + np.array(drift_data_raw["precision"])

def c_drift(weights):
    cdrift = np.array(drift_data[:, :, :, 0])

    for idx in range(1, drift_data.shape[3]):
        cdrift += drift_data[:, :, :, idx] * weights[idx-1]

    return cdrift


def fitness(weights):
    cdrift = c_drift(weights)
    return cdrift.max()

# Initial guess for the solution
x0 = np.ones([drift_data.shape[3]-1]) * 0.5

# Standard deviation for the initial search distribution
sigma0 = 10  # Example standard deviation

# The dimension of the problem
dimension = len(x0)

# Create an optimizer object
es = cma.CMAEvolutionStrategy(x0, sigma0)

# Run the optimization
es.optimize(fitness)

# Best solution found
best_solution = es.result.xbest

# Fitness value of the best solution
best_fitness = es.result.fbest


print("Best weights vector: ", best_solution)
print("Fitness value: ", best_fitness)
print("Smallest drift: ", c_drift(best_solution).max())
print("log_m drift:", drift_data[:, :, :, 0].max())
