#!/bin/bash

# Set the PYTHONPATH to include the directories you need
export PYTHONPATH="${PYTHONPATH}:/home/franksyj/DriftAnalysisFramework/py"

# Run the Python script with any arguments passed to this shell script
/home/franksyj/DriftAnalysisFramework/py/venv/bin/python "$@"