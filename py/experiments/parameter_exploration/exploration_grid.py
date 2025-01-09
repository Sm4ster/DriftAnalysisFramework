import numpy as np

# List of parameter sets for each execution
factor_1_sequence = np.geomspace(1 / 16, 2, num=6)
factor_2_sequence = np.geomspace(1 / 16, 2, num=6)
param_factors = np.array(np.meshgrid(factor_1_sequence, factor_2_sequence)).T.reshape(-1, 2)

np.savetxt("factor_grid.txt", param_factors, delimiter=",")