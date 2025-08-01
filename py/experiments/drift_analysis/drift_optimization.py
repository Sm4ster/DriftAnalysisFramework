import numpy as np
import json
import cma
import argparse
import os
import itertools

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
parser.add_argument('--base_term', type=int, default=0,
                    help='index to serve as a norm. usually this is the log(m) term')
parser.add_argument('--min_terms', type=int, default=2, help='Minimum number of terms per combination (inclusive)')
parser.add_argument('--max_terms', type=int, default=None, help='Maximum number of terms per combination (inclusive)')
parser.add_argument('--exclude_terms', type=int_list, default=[],
                    help='Optional: comma-separated list of term indices to exclude (in addition to the base term).')
parser.add_argument('--iterations', type=int, help='number of optimization iterations to perform')

args = parser.parse_args()

base_term = args.base_term
iterations = args.iterations

if args.data is None:
    data = {}
else:
    data = json.loads(args.data)

# Load drift data
drift_data_raw = json.load(open(f'./data/{args.data_file}'))
drift_data = np.array(drift_data_raw["drift"]) + np.array(drift_data_raw["precision"])

term_count = drift_data.shape[3]

if args.terms is None:
    excluded = set(args.exclude_terms + [base_term])
    available_terms = [i for i in range(term_count) if i not in excluded]
    max_l = args.max_terms if args.max_terms is not None else len(available_terms)
    term_combinations = [
        list(c) for l in range(args.min_terms, max_l + 1)
        for c in itertools.combinations(available_terms, l)
    ]
else:
    term_combinations = [args.terms]

# Load or initialize output
if os.path.exists(args.output_file):
    output_data = json.load(open(args.output_file))
else:
    output_data = []

# Reference base drift for output
base_drift = drift_data[:, :, :, base_term].max()

print(f"Starting optimization for {len(term_combinations)} term combinations...")

# Iterate over term combinations only
for combo_idx, terms in enumerate(term_combinations, 1):
    print(f"[{combo_idx}/{len(term_combinations)}] Optimizing for terms = {terms}")


    def c_drift(weights):
        combined = drift_data[:, :, :, base_term]
        for idx, term_idx in enumerate(terms):
            combined += drift_data[:, :, :, term_idx] * weights[idx]
        return combined


    def fitness(weights):
        return c_drift(weights).max()


    best_solutions = []
    best_fitnesses = []

    for run in range(iterations):
        print(f"  CMA run {run + 1}/{iterations} ...", end="", flush=True)

        # Initial guess for the solution
        x0 = np.ones([len(terms)]) * -0.5

        # Standard deviation for the initial search distribution
        sigma0 = 10  # Example standard deviation

        # Create an optimizer object
        es = cma.CMAEvolutionStrategy(x0, sigma0, {'verbose': -9})

        # Run the optimization
        es.optimize(fitness)

        # Best solution found
        best_solutions.append(es.result.xbest)

        # Fitness value of the best solution
        best_fitnesses.append(es.result.fbest)

        print(" done.")

    idx_best = int(np.argmin(best_fitnesses))
    best_solution = best_solutions[idx_best]
    best_fitness = best_fitnesses[idx_best]

    # result vector
    result = {
        **data,
        "terms_used": terms,
        "weights_vector": best_solution.tolist(),
        "smallest_drift": float(best_fitness),
        "base_drift": float(base_drift)
    }
    for vi, val in enumerate(best_solution.tolist()):
        result[f"v_{vi + 1}"] = val
    output_data.append(result)

# Sort all results by "smallest_drift" (ascending = most negative drift on top)
output_data.sort(key=lambda entry: entry["smallest_drift"])

with open(f'./data/{args.output_file}', 'w') as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)
