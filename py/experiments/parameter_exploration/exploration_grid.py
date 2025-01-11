import numpy as np
import os

# Change the working directory
os.chdir("/home/franksyj/DriftAnalysisFramework/py/")

# List of parameter sets for each execution
factor_1_sequence = np.geomspace(1 / 16, 4, num=7)
factor_2_sequence = np.geomspace(1 / 16, 4, num=7)
param_factors = np.array(np.meshgrid(factor_1_sequence, factor_2_sequence)).T.reshape(-1, 2)

np.savetxt("configurations/parameter_exploration/factor_grid.txt", param_factors, delimiter=",")