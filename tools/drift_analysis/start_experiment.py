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
parser.add_argument('--run_id', type=str, help='The run_id to distinguish runs', default="default")
parser.add_argument('--server_id', type=int, help='Identifier of this server and process', default=0)
parser.add_argument('--max_servers', type=int, help='Total number of servers', default=1)
parser.add_argument('--indexes', type=str, help='Start and stop indexes of the input file', default='all')
parser.add_argument('--workers', type=str, help='Number of workers running the simulation', default=12)
args = parser.parse_args()

# Build the output directory with subdirectories
data_path = args.output_dir
if not os.path.exists(data_path):
    os.makedirs(data_path)

if args.indexes != "all":
    part_results_path = data_path + "/parts/" + args.run_id
    if not os.path.exists(part_results_path):
        os.makedirs(part_results_path)


config = json.load(open(f'./configurations/run_parameters/{args.parameter_file}.json'))
potential_functions = json.load(open(f'./configurations/potential_functions/{args.potential_function_file}.json'))

# Parameters to pass
options = [
    args.output_dir,
    '--run_id', args.run_id,
    '--server_id', str(args.server_id),
    '--max_servers', str(args.max_servers),
    '--algorithm', potential_functions["algorithm"],
    '--normal_form', potential_functions["normal_form"],
    '--potential_functions', json.dumps(potential_functions["potential_functions"]),
    '--workers', str(args.workers),
    '--indexes', args.indexes
]

if "sample_size" in config:
    options.extend(['--sample_size', str(config["sample_size"])])

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

command = [sys.executable, 'tools/drift_analysis/drift_analysis.py'] + options

# Execute the command
subprocess.run(command)

