import subprocess
import argparse
import json

parser = argparse.ArgumentParser(description='This script does drift simulation for CMA')
parser.add_argument('parameter_file', help='The input file containing all options and parameters for the run.')
parser.add_argument('--output_file', help='The output file name.')
args = parser.parse_args()

data = json.load(open(f'./{args.parameter_file}'))

defaults = {
    "output_file": "drift_run.json",
    "batch_size": 50000,
    "sub_batch_size": 25000,
    "alpha": [0, 1.5707963267948966, 24],
    "kappa": [1, 100, 256],
    "sigma": [0.01, 10, 368],
    "CMA_d": 2,
    "CMA_c_cov": 0.2,
    "kappa_input": "stable_kappa.json",
    "sigma_input": "stable_sigma_with_transformation.json",
    "potential_functions": ["\\log(|m|)", "log(norm(m))"],
}

# Parameters to pass
options = [
    '--output_file',
    args.output_file if args.output_file else data["output_file"] if "output_file" in data else defaults["output_file"],
    '--sigma_input',
    str(data["sigma_input"]) if "sigma_input" in data else str(defaults["sigma_input"]),
    '--kappa_input',
    str(data["kappa_input"]) if "kappa_input" in data else str(defaults["kappa_input"]),
    '--potential_functions',
    json.dumps(data["potential_functions"]) if "potential_functions" in data else defaults["potential_functions"],
    '--batch_size',
    str(data["batch_size"]) if "batch_size" in data else str(defaults["batch_size"]),
    '--sub_batch_size',
    str(data["sub_batch_size"]) if "sub_batch_size" in data else str(defaults["sub_batch_size"]),
    '--alpha_start',
    str(data["alpha"][0]) if "alpha" in data else str(defaults["alpha"][0]),
    '--alpha_end',
    str(data["alpha"][1]) if "alpha" in data else str(defaults["alpha"][1]),
    '--alpha_samples',
    str(data["alpha"][2]) if "alpha" in data else str(defaults["alpha"][2]),
    '--kappa_start',
    str(data["kappa"][0]) if "kappa" in data else str(defaults["kappa"][0]),
    '--kappa_end',
    str(data["kappa"][1]) if "kappa" in data else str(defaults["kappa"][1]),
    '--kappa_samples',
    str(data["kappa"][2]) if "kappa" in data else str(defaults["kappa"][2]),
    '--sigma_start',
    str(data["sigma"][0]) if "sigma" in data else str(defaults["sigma"][0]),
    '--sigma_end',
    str(data["sigma"][1]) if "sigma" in data else str(defaults["sigma"][1]),
    '--sigma_samples',
    str(data["sigma"][2]) if "sigma" in data else str(defaults["sigma"][2]),
    '--CMA_c_cov',
    str(data["CMA_c_cov"]) if "CMA_c_cov" in data else str(defaults["CMA_c_cov"]),
    '--CMA_d',
    str(data["CMA_d"]) if "CMA_d" in data else str(defaults["CMA_d"]),

]

# Command to run the other script
command = ['/home/franksyj/DriftAnalysisFramework/py/venv/bin/python', 'drift_analysis.py'] + options

# Execute the command
subprocess.run(command)

print("ended")
