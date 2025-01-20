import numpy as np
import os

# Change the working directory
os.chdir("/home/franksyj/DriftAnalysisFramework/py/")

# List of parameter sets for each execution
factor_1_sequence = np.geomspace(1 / 16, 2, num=6)
factor_2_sequence = np.geomspace(1 / 16, 16, num=9)
param_factors = np.array(np.meshgrid(factor_1_sequence, factor_2_sequence)).T.reshape(-1, 2)

np.savetxt("configurations/parameter_exploration/exploration_grid.txt", param_factors, delimiter=",")