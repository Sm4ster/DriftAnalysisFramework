import subprocess
import argparse
import shutil
import json
import sys
import os

# Change the working directory
os.chdir("/home/franksyj/DriftAnalysisFramework/")

parser = argparse.ArgumentParser(description='This script does drift simulation for CMA')
parser.add_argument('potential_function_file', help='The input file containing all potential functions for the run.')
parser.add_argument('parameter_file', help='The input file containing all options and parameters for the run.')
parser.add_argument('output_dir', help='The output directory name.')
parser.add_argument('--indexes', type=str, help='Start and stop indexes of the input file', default='all')
parser.add_argument('--workers', type=str, help='Number of workers running the simulation', default=12)
args = parser.parse_args()

# Build the output directory with subdirectories
data_path = args.output_dir
if not os.path.exists(data_path):
    os.makedirs(data_path)

if args.indexes != "all":
    part_results_path = data_path + "/parts/"
    if not os.path.exists(part_results_path):
        os.makedirs(part_results_path)


# shutil.copy("configurations/" + args.parameter_file, data_path + "/0_configuration.json")

config = json.load(open(f'./configurations/run_parameters/{args.parameter_file}'))
potential_functions = json.load(open(f'./configurations/potential_functions/{args.potential_function_file}'))

# Parameters to pass
options = [
    args.output_dir,
    '--algorithm', potential_functions["algorithm"],
    '--potential_functions', json.dumps(potential_functions["potential_functions"]),
    '--workers', str(args.workers),
    '--indexes', args.indexes
]

if "stable_sigma_file" in config:
    options.extend(['--sigma_input', str(config["stable_sigma_file"])])

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

command = [sys.executable, 'tools/drift_analysis/drift_analysis.py'] + options

print(command)

# Execute the command
subprocess.run(command)

