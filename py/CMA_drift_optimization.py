import numpy as np
import json
import cma

drift_data_raw = json.load(open('./data/big_test_run.json'))
drift_data = np.array(drift_data_raw["drifts"])

def c_drift(weights):
    cdrift = np.zeros([drift_data.shape[0], drift_data.shape[1], drift_data.shape[2]])

    for idx in range(drift_data.shape[3]):
        cdrift += drift_data[:, :, :, idx] * weights[idx]

    return cdrift

def fitness(weights):
    cdrift = c_drift(weights)
    return cdrift.max() + 10 * np.power(1 - weights[0], 2)


def log_m_drift(weight):
    return drift_data[:, :, :, 0].max() * weight


# Initial guess for the solution
x0 = np.ones([drift_data.shape[3]]) * 0.5

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
print("log_m drift (weighted):", log_m_drift(1), "(", log_m_drift(best_solution[0]), ")")
