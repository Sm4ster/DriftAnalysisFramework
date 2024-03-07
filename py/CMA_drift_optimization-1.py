import numpy as np
import json
import cma
from scipy.stats import multivariate_normal

drift_data_raw = json.load(open('./data/big_test_run.json'))
drift_data = np.array(drift_data_raw["drifts"])


def invert_gaussian_weight(grid_values, param_vector):
    """
    Apply weights (probability densities) to each value in a 3D grid.

    Parameters:
    - grid_values: A 3D numpy array of values in the grid.
    - param_vector: A 3D numpy array of the following shape:
                [mean, covariance, scaling]

    Returns:
    - weighted_values: A 3D numpy array where each value in grid_values has been
                       weighted by the corresponding probability density.
    """

    # Step 1: Define the mean and covariance of the 3D normal distribution
    mean = param_vector[0:3]
    covariance = np.eye(3) * param_vector[3:6]

    # Step 2: Create a 3D grid

    x_size, y_size, z_size = np.ceil(grid_values.shape[0] / 2), np.ceil(grid_values.shape[1] / 2), np.ceil(
        grid_values.shape[2] / 2)
    x, y, z = np.mgrid[
              -x_size:x_size:1,
              -y_size:y_size:1,
              -z_size:z_size:1
              ]
    pos = np.dstack((x, y, z))

    # check if matrix is positive semidefinite
    if not np.all(np.linalg.eigvals(x) > 0):
        return grid_values

    # Step 3: Evaluate the PDF over the grid
    rv = multivariate_normal(mean, covariance)
    probability_densities = rv.pdf(pos)

    weighted_values = grid_values * (1 - (probability_densities * param_vector[6]))
    return weighted_values


def c_drift(weights):
    cdrift = np.zeros([drift_data.shape[0], drift_data.shape[1], drift_data.shape[2]])

    cdrift += drift_data[:, :, :, 0] * weights[0]
    cdrift += drift_data[:, :, :, 1] * weights[1]
    # cdrift += drift_data[:, :, :, 2] * weights[2]
    cdrift += invert_gaussian_weight(drift_data[:, :, :, 2], weights[4:17]) * weights[2]
    cdrift += drift_data[:, :, :, 3] * weights[3]

    return cdrift


def fitness(weights):
    cdrift = c_drift(weights)
    return cdrift.max() + 10 * np.power(1 - weights[0], 2)


def log_m_drift(weight):
    return drift_data[:, :, :, 0].max() * weight


# Initial guess for the solution
# x0 = np.ones([drift_data.shape[3]]) * 0.5
x0 = np.ones([10]) * 0.5

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
