import numpy as np
import argparse
import subprocess
import json
import sys

parser = argparse.ArgumentParser(description='This script computes stable kappa values for CMA.')
parser.add_argument('--output', type=str, help='Output file name', default='stable_sigma.json')
parser.add_argument('--Comma_CMA_c_sigma', type=float, help='c_sigma parameter of CMA-ES', default=0.2)
parser.add_argument('--Comma_CMA_c_cov', type=float, help='c_cov parameter of CMA-ES', default=0.09182736455463728)
parser.add_argument('--Elitist_CMA_c_cov', type=float, help='c_cov parameter of CMA-ES', default=0.3)
parser.add_argument('--Elitist_CMA_d', type=float, help='dampening parameter of CMA-ES', default=2)
args = parser.parse_args()

output_file = args.output
param_sets = np.loadtxt(args.input, delimiter=",")

with open(output_file, 'w') as file:
    json.dump([], file, indent=4)  # Writing with indentation for readability

for param_set in param_sets:
    dataset_name = "./data/" + str(param_set[0]) + "_" + str(param_set[1]) + "_" + "parameter_experiment.json"

    command = [
        sys.executable, 'drift_optimization.py',
        "--data_file", dataset_name,
        "--output_file", output_file,
        "--iterations", "5",
        "--terms", "1,3",
        "--data", json.dumps({"factors": {"c_cov": param_set[0], "d": param_set[1]}})
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
