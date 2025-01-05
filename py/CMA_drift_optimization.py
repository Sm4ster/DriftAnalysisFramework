import numpy as np
import json
import cma
import argparse

def int_list(s):
    try:
        return [int(item) for item in s.split(',')]
    except ValueError:
        raise argparse.ArgumentTypeError("List must be comma-separated integers.")

parser = argparse.ArgumentParser(description='This script does drift simulation for CMA')
parser.add_argument('--data_file', help='The data file name.')
parser.add_argument('--terms', type=int_list, help='index of the terms to optimize. index 0 is always included and serves as a norm. usually this is the log(m) term')
args = parser.parse_args()

# input parameters
terms = args.terms
drift_data_raw = json.load(open(f'./{args.data_file}'))


# prepare data to work with
drift_data = np.array(drift_data_raw["drift"]) + np.array(drift_data_raw["precision"])


def c_drift(weights):
    cdrift = np.array(drift_data[:, :, :, 0])

    for idx, term_idx in enumerate(terms):
        cdrift += drift_data[:, :, :, term_idx] * weights[idx]

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

# TODO add values to a file

print("Best weights vector: ", best_solution)
print("Fitness value: ", best_fitness)
print("Smallest drift: ", c_drift(best_solution).max())
print("log_m drift:", drift_data[:, :, :, 0].max())
print("--------------------------------")
print("Smallest drift: ", c_drift(np.array([1.7, 3.14])).max())
print("Smallest drift: ", c_drift(np.array([2.5, 5])).max())
print("log_m drift:", drift_data[:, :, :, 0].max())