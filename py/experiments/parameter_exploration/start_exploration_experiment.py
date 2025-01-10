import subprocess
import argparse
import json
import numpy as np
import sys
import os

# Change the working directory
os.chdir("/home/franksyj/DriftAnalysisFramework/py/")

parser = argparse.ArgumentParser(description='This script does drift simulation for CMA')
parser.add_argument('parameter_file', help='The input file containing all options and parameters for the run.')
parser.add_argument('output_dir', help='The output directory name.')
parser.add_argument('--exploration_grid', type=str, help='Filename of the exploration input')
parser.add_argument('--workers', type=str, help='Number of workers running the simulation', default=12)
parser.add_argument('--indexes', type=str, help='Start and stop indexes of the input file', default='all')
parser.add_argument('--stable_sigma_file', type=str, help='Skips parameter analysis and uses the provided file')
args = parser.parse_args()

# Ensure the directory exists
os.makedirs(os.path.dirname("configurations/" + args.output_dir), exist_ok=True)
# Get the current working directory
current_directory = os.getcwd()
print("Current working directory:", current_directory)

# Load parameter file for the drift run
print("configurations/" + args.parameter_file)
config = json.load(open("configurations/" + args.parameter_file))

# Load the parameter weights from the file if provided
param_sets = np.loadtxt("configurations/" + args.exploration_grid, delimiter=",") if args.exploration_grid else np.array([1, 1])

print(param_sets)

# Loop over the parameter sets and call the script
for param_set in param_sets:
    constants = []

    if config["algorithm"] == "1+1-CMA-ES":
        constants = {
            "c_cov": param_set[0] * config["c_cov"],
            "d": param_set[1] * config["d"]
        }
    if config["algorithm"] == "CMA-ES":
        constants = {
            "c_cov": param_set[0] * config["c_cov"],
            "c_sigma": param_set[1] * config["c_sigma"]
        }
    else:
        alg = None
        print("Error: No valid algorithm specified")
        exit()

    # Initialize the target function and optimization algorithm
    command_pre = [
        sys.executable, 'experiments/parameter_analysis/sigma_analysis.py',
        "stable_sigma_" + str(param_set[0]) + "_" + str(param_set[1]),
        '--algorithm', config["algorithm"],
        '--constants', json.dumps(constants),
        '--workers', str(args.workers)
    ]

    # Parameters to pass
    options = [
        args.output_dir + "drift_" + str(param_set[0]) + "_" + str(param_set[1]),
        '--algorithm', config["algorithm"],
        '--potential_functions', json.dumps(config["potential_functions"]),
        '--constants', json.dumps(constants),
        '--workers', str(args.workers)
    ]

    if args.stable_sigma_file:
        options.extend(['--sigma_input', args.stable_sigma_file])
    else:
        options.extend(['--sigma_input', "stable_sigma_" + str(param_set[0]) + "_" + str(param_set[1])])

    if "batch_size" in config:
        options.extend(['--batch_size', str(config["batch_size"])])

    if "sub_batch_size" in config:
        options.extend(['--sub_batch_size', str(config["sub_batch_size"])])

    if "alpha" in config:
        options.extend(['--alpha_start', str(config["alpha"][0])])

    if "kappa" in config:
        options.extend(['--kappa_start', str(config["kappa"][0])])

    if "sigma" in config:
        options.extend(['--sigma_start', str(config["sigma"][0])])

    if "alpha" in config:
        options.extend(['--alpha_end', str(config["alpha"][1])])

    if "kappa" in config:
        options.extend(['--kappa_end', str(config["kappa"][1])])

    if "sigma" in config:
        options.extend(['--sigma_end', str(config["sigma"][1])])

    if "alpha" in config:
        options.extend(['--alpha_samples', str(config["alpha"][2])])

    if "kappa" in config:
        options.extend(['--kappa_samples', str(config["kappa"][2])])

    if "sigma" in config:
        options.extend(['--sigma_samples', str(config["sigma"][2])])


    command_main = [sys.executable, 'experiments/drift_analysis/drift_analysis.py'] + options

    # Execute the command and wait for it to finish
    try:
        # Command to run the other script
        if not args.stable_sigma_file:
            result = subprocess.run(command_pre)
            print(f"Execution of parameter analysis with parameters {param_set} completed successfully.")
            print("Standard Output:", result.stdout)

        result = subprocess.run(command_main)
        print(f"Execution of drift analysis with parameters {param_set} completed successfully.")
        print("Standard Output:", result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred with parameters {param_set}.")
        print("Standard Error:", e.stderr)
        # Optionally, handle the error (e.g., log it, break the loop, etc.)
        break  # Stop the loop if an error occurs

print("Run ended successfully")
