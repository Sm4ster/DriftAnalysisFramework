import numpy as np
import json
import cma
import argparse
import os


def int_list(s):
    try:
        return [int(item) for item in s.split(',')]
    except ValueError:
        raise argparse.ArgumentTypeError("List must be comma-separated integers.")


parser = argparse.ArgumentParser(description='This script does drift simulation for CMA')
parser.add_argument('--output_file', help='The output file name.')
parser.add_argument('--data_file', help='The data file name.')
parser.add_argument('--data', help='pass data to be written into the result file')
parser.add_argument('--terms', type=int_list,
                    help='index of the terms to optimize. index 0 is always included and serves as a norm. usually this is the log(m) term')
parser.add_argument('--base_term', type=int, help='index to serve as a norm. usually this is the log(m) term')
parser.add_argument('--iterations', type=int, help='number of optimization iterations to perform')

args = parser.parse_args()

# input parameters
terms = args.terms
drift_data_raw = json.load(open(f'./{args.data_file}'))
output_data = json.load(open(f'./{args.output_file}'))

# result vector
results = {
    **json.loads(args.data),
    "weights_vector": [],
    "smallest_drift": [],
    "base_drift": []
}

# prepare data to work with
drift_data = np.array(drift_data_raw["drift"]) + np.array(drift_data_raw["precision"])

best_solutions = []
smallest_drifts = []
largest_drifts = []


def c_drift(weights):
    cdrift = np.array(drift_data[:, :, :, args.base_term])

    for idx, term_idx in enumerate(terms):
        cdrift += drift_data[:, :, :, term_idx] * weights[idx]

    return cdrift


def fitness(weights):
    cdrift = c_drift(weights)

    return cdrift.max()


for i in range(args.iterations):
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

    best_solutions.append(best_solution)
    smallest_drifts.append(c_drift(best_solution).max())
    largest_drifts.append(c_drift(best_solution).min())

idx = np.argmin(smallest_drifts)
for v_idx in range(len(best_solutions[idx].tolist())):
    results["v_" + str(v_idx + 1)] = best_solutions[idx][v_idx]
results["weights_vector"] = best_solutions[idx].tolist()
results["smallest_drift"] = smallest_drifts[idx]
results["largest_drift"] = largest_drifts[idx]
results["base_drift"] = drift_data[:, :, :, args.base_term].max()

output_data.append(results)
with open(f'./{args.output_file}', 'w') as f:
    json.dump(output_data, f)
