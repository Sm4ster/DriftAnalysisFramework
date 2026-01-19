import subprocess
import argparse
import json
import numpy as np
import shutil
import sys
import os

# Change the working directory
os.chdir("/science/franksyj/DriftAnalysisFramework/py/")

parser = argparse.ArgumentParser(description='This script does drift simulation for CMA')
parser.add_argument('parameter_file', help='The input file containing all options and parameters for the run.')
parser.add_argument('output_dir', help='The output directory name.')
parser.add_argument('--exploration_grid', type=str, help='Filename of the exploration input')
parser.add_argument('--workers', type=str, help='Number of workers running the simulation', default=12)
parser.add_argument('--indexes', type=str, help='Start and stop indexes of the input file', default='all')
parser.add_argument('--stable_sigma_file', type=str, help='Skips parameter analysis and uses the provided file')
args = parser.parse_args()

# Build the output directory with subdirectories
data_path = "data/" + args.output_dir
if not os.path.exists(data_path):
    os.makedirs(data_path)

stable_sigma_path = data_path + "/2_stable_sigma/"
if not os.path.exists(stable_sigma_path):
    os.makedirs(stable_sigma_path)

drift_path = data_path + "/3_drift/"
if not os.path.exists(drift_path):
    os.makedirs(drift_path)

if args.exploration_grid: shutil.copy("configurations/" + args.exploration_grid, data_path + "/1_grid.txt")
shutil.copy("configurations/" + args.parameter_file, data_path + "/0_configuration.json")

# Load parameter file for the drift run
config = json.load(open("configurations/" + args.parameter_file))

# Load the parameter weights from the file if provided
param_sets = np.loadtxt("configurations/" + args.exploration_grid,
                        delimiter=",") if args.exploration_grid else np.array([[1.0, 1.0]])

if param_sets.ndim == 1:
    param_sets = np.expand_dims(param_sets, axis=0)

# slice param sets
start_idx = 0
if args.indexes != "all":
    start_idx = int(args.indexes.split(",")[0])
    param_sets = param_sets[start_idx:int(args.indexes.split(",")[1])]

# Loop over the parameter sets and call the script
for idx, param_set in enumerate(param_sets):
    constants = []

    if config["algorithm"] == "1+1-CMA-ES":
        constants = {
            "c_cov": param_set[0] * config["c_cov"],
            "d": param_set[1] * config["d"]
        }
    elif config["algorithm"] == "CMA-ES":
        constants = {
            "c_cov": param_set[0] * config["c_cov"],
            "c_sigma": param_set[1] * config["c_sigma"]
        }
    else:
        alg = None
        print("Error: No valid algorithm specified! Algorithm found: " + config["algorithm"])
        print()
        exit()

    # Initialize the target function and optimization algorithm
    filename = str(param_set[0]) + "_" + str(param_set[1])
    command_pre = [
        sys.executable, 'tools/parameter_analysis/sigma_analysis.py',
        stable_sigma_path + filename,
        '--algorithm', config["algorithm"],
        '--constants', json.dumps(constants),
        '--workers', str(args.workers)
    ]

    if "groove_iterations" in config:
        command_pre.extend(['--groove_iterations', str(config["groove_iterations"])])

    if "measured_samples" in config:
        command_pre.extend(['--measured_samples', str(config["measured_samples"])])

    # Parameters to pass
    options = [
        drift_path + filename,
        '--algorithm', config["algorithm"],
        '--potential_functions', json.dumps(config["potential_functions"]),
        '--constants', json.dumps(constants),
        '--workers', str(args.workers)
    ]

    if args.stable_sigma_file:
        options.extend(['--sigma_input', args.stable_sigma_file])
    else:
        options.extend(['--sigma_input', stable_sigma_path + filename])

    if "batch_size" in config:
        options.extend(['--batch_size', str(config["batch_size"])])

    if "batch_size" in config:
        options.extend(['--batch_size', str(config["batch_size"])])

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

    command_main = [sys.executable, 'tools/drift_analysis/drift_analysis.py'] + options

    # Execute the command and wait for it to finish
    try:
        # Command to run the other script
        print("\n\n************** Iteration " + str(idx) + " (index "+ str(start_idx+idx) + ") **************")
        if not args.stable_sigma_file:
            print(f"Starting stable sigma experiment ({param_set}):")
            if os.path.isfile(stable_sigma_path + filename):
                print("\n... file already exists ... skipping")
            else:
                print("\n" + " ".join(map(str, command_pre)) + "\n")
                result = subprocess.run(command_pre)
                print(f"...completed successfully.")

        if os.path.isfile(drift_path + filename):
            print("\n... file already exists ... skipping")
        else:
            print(f"\nStarting drift analysis experiment ({param_set}):")
            print("\n" + " ".join(map(str, command_main)) + "\n")
            result = subprocess.run(command_main)
            print(f"Execution of drift analysis with parameters  completed successfully.")

    except subprocess.CalledProcessError as e:
        print(f"An error occurred with parameters {param_set}.")
        print("Standard Error:", e.stderr)
        # Optionally, handle the error (e.g., log it, break the loop, etc.)
        break  # Stop the loop if an error occurs

print("Run ended successfully")
