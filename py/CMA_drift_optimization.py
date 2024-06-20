import numpy as np
import json
import cma

drift_data_raw = json.load(open('./data/SPECIAL_RUN_14.json'))
drift_data = np.array(drift_data_raw["drift"])  # + np.array(drift_data_raw["precision"])
terms = [1, 3]

def c_drift(weights):
    cdrift = np.array(drift_data[:, :, :, 0])

    for idx, term_idx in enumerate(terms):
        cdrift += drift_data[:, :, :, term_idx] * np.exp(weights[idx])

    return cdrift


def fitness(weights):
    cdrift = c_drift(weights)
    return cdrift.max()


# Initial guess for the solution
x0 = np.ones([len(terms)]) * -0.5

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

print("Best weights vector: ", np.exp(best_solution))
print("Fitness value: ", best_fitness)
print("Smallest drift: ", c_drift(best_solution).max())
print("log_m drift:", drift_data[:, :, :, 0].max())
