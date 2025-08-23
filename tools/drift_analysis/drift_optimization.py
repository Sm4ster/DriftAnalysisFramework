import numpy as np
import multiprocessing as mp
from cma.optimization_tools import EvalParallel2
import json
import cma
import argparse


def int_list(s):
    try:
        return [int(item) for item in s.split(',')]
    except ValueError:
        raise argparse.ArgumentTypeError("List must be comma-separated integers.")


def str_list(s):
    try:
        return [str(item) for item in s.split(',')]
    except ValueError:
        raise argparse.ArgumentTypeError("List must be comma-separated strings.")


parser = argparse.ArgumentParser(description='This script does drift simulation for CMA')
parser.add_argument('data', type=str_list, help='The data file names.')
parser.add_argument('--combinations', type=bool, default=False, help='Whether to check all combinations of terms')
parser.add_argument('--output_file', help='The output file name.')
parser.add_argument('--base_terms', type=int, default=2, help='File names of the data that should be used as base terms')
parser.add_argument('--min_terms', type=int, default=2, help='Minimum number of terms per combination (inclusive)')
parser.add_argument('--max_terms', type=int, default=None, help='Maximum number of terms per combination (inclusive)')
parser.add_argument('--iterations', type=int, default=3, help='number of optimization iterations to perform')

args = parser.parse_args()

iterations = args.iterations

# Load drift data
drift_data = []
for file in args.data:
    raw_data = json.load(open(f'./data/{file}'))
    drift_data.append(raw_data["drift"] + raw_data["precision"])

term_count = len(drift_data)
drift_data = np.array(drift_data)

if args.combinations:
    term_combinations = [list(range(1,term_count))]
    pass
    # excluded = set(args.exclude_terms + [base_term])
    # available_terms = [i for i in range(term_count) if i not in excluded]
    # max_l = args.max_terms if args.max_terms is not None else len(available_terms)
    # term_combinations = [
    #     list(c) for l in range(args.min_terms, max_l + 1)
    #     for c in itertools.combinations(available_terms, l)
    # ]

else:
    term_combinations = [list(range(1,term_count))]


# Load or initialize output

output_data = []

# Reference base drift for output
base_drift = drift_data[0].max()

print(f"Starting optimization for {len(term_combinations)} term combination(s)...")

# Iterate over term combinations only
for combo_idx, terms in enumerate(term_combinations, 1):
    print(f"[{combo_idx}/{len(term_combinations)}] Optimizing for terms = {terms}/{len(terms)}")


    def c_drift(weights):
        combined = drift_data[0]
        for idx, term_idx in enumerate(terms):
            combined += drift_data[term_idx] * weights[idx]
        return combined


    def fitness(weights):
        return c_drift(weights).max()


    best_solutions = []
    best_fitnesses = []

    for run in range(iterations):
        print(f"  CMA run {run + 1}/{iterations} ...", end="", flush=True)

        n = len(terms)

        # Initial guess for the solution
        x0 = np.ones([n])

        # Standard deviation for the initial search distribution
        sigma0 = 10

        # Create an optimizer object
        es = cma.CMAEvolutionStrategy(x0, sigma0, {
            'verbose': -9,
            'bounds': [0, 10],
            'popsize': 8 * (4 + int(3 * np.log(n))),
            'CMA_mirrors': 1,
        })

        # Parallel über alle Kerne:
        with EvalParallel2(fitness, mp.cpu_count()) as eval_all:
            while not es.stop():
                X = es.ask()
                fvals = eval_all(X)  # wird parallel ausgewertet
                es.tell(X, fvals)

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

if args.output_file:
    with open(f'./data/{args.output_file}', 'w') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
else:
    print("Best drift: ", output_data[0]["smallest_drift"])
    print("Base drift: ", output_data[0]["base_drift"])
    for vi, val in enumerate(output_data[0]["weights_vector"]):
        print(f"v_{vi + 1}: ", val)

