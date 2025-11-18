#!/bin/bash

# Set the PYTHONPATH to include the directories you need
export PYTHONPATH="${PYTHONPATH}:/science/franksyj/DriftAnalysisFramework"

# Run the Python script with any arguments passed to this shell script
nice -n 1 /science/franksyj/.conda/envs/DriftAnalysisFramework/bin/python "$@"

# ./py.sh /science/franksyj/DriftAnalysisFramework/py/tools/parameter_exploration/start_exploration_experiment.py parameter_exploration/1+1_CMA-ES.json parameter_exploration_4 --workers=20 --exploration_grid parameter_exploration/factor_grid.txt --indexes 33,36