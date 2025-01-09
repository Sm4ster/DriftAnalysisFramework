import subprocess

parser.add_argument('parameter_file', help='The input file containing all options and parameters for the run.')

# Parameters to pass
options = ['--verbose', '-o', 'output.txt']
params = ['param1', 'param2']

# Command to run the other script
command = ['python', 'other_script.py'] + params

# Loop over the parameter sets and call the script
for params in param_sets:
    # Construct the command
    command = ['python', 'drift_analysis.py'] + options + params

    # Execute the command and wait for it to finish
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print(f"Execution with parameters {params} completed successfully.")
        print("Standard Output:", result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred with parameters {params}.")
        print("Standard Error:", e.stderr)
        # Optionally, handle the error (e.g., log it, break the loop, etc.)
        break  # Stop the loop if an error occurs
