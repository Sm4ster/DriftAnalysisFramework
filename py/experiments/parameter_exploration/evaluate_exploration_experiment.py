import numpy as np
import argparse
import subprocess
import json
import sys

parser = argparse.ArgumentParser(description='This script computes stable kappa values for CMA.')
parser.add_argument('input_dir', type=str, help='Input directory name')
parser.add_argument('--output', type=str, help='Output file name', default='4_drift_results.json')
parser.add_argument('--exploration_grid', type=str, help='Exploration grid file name', default='1_grid.txt')
parser.add_argument('--terms', type=str, help='Comma separated terms', default='1,2')
parser.add_argument('--iterations', type=str, help='iterations to find the best value', default='3')
args = parser.parse_args()

output_file = args.output
param_sets = np.loadtxt("data/" + args.input_dir + "/" + args.exploration_grid, delimiter=",")

with open("data/" + args.input_dir + "/" + output_file, 'w') as file:
    json.dump([], file, indent=4)  # Writing with indentation for readability

for param_set in param_sets:
    dataset_name = "./data/" + args.input_dir + "/3_drift/" + str(param_set[0]) + "_" + str(param_set[1])

    command = [
        sys.executable, 'experiments/drift_analysis/drift_optimization.py',
        "--data_file", dataset_name,
        "--output_file", "data/" + args.input_dir + "/" + output_file,
        "--iterations", args.iterations,
        "--terms", args.terms,
        "--data", json.dumps({"factors": [param_set[0], param_set[1]]})
    ]

    print(command)

    # Execute the command and wait for it to finish
    try:
        # Command to run the other script
        result = subprocess.run(command)
        print(f"Execution with parameters {param_set} completed successfully.")
        print("Standard Output:", result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred with parameters {param_set}.")
        print("Standard Error:", e.stderr)
        # Optionally, handle the error (e.g., log it, break the loop, etc.)
        break  # Stop the loop if an error occurs
