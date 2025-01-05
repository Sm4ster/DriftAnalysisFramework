import numpy as np
import subprocess

# List of parameter sets for each execution
c_cov_sequence = np.geomspace(1 / 16, 2, num=6)
d_sequence = np.geomspace(1 / 16, 2, num=6)
param_sets = np.array(np.meshgrid(c_cov_sequence, d_sequence)).T.reshape(-1, 2)

for param_set in param_sets:
    dataset_name = "./data/" + str(param_set[0]) + "_" + str(param_set[1]) + "_" + "parameter_experiment.json"

    command = [
        '/home/franksyj/DriftAnalysisFramework/py/venv/bin/python', 'CMA_drift_optimization.py',
        "--data_file", dataset_name,
        "--terms", "1,3"
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
