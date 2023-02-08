import numpy as np
import scipy

results = np.load("../../data/sigma_data_56000_samples.npy")

# find all angles

#interpolate for a single angle


for idx in range(results.shape[0]-1):
    input_1 = results[idx]
    input_2 = results[idx+1]

print(results)
