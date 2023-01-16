import numpy as np
import matplotlib.pyplot as plt

def f(sigma22, x):
    48.0 * (0.0045 - 0.00037 * sigma22) * (13.0 * x + 1.1) + 0.34

results = np.load("sigma_data_pi_old.npy")

function_evals = np.empty([results.shape[0], 1])

for idx in range(results.shape[0]):
    function_evals[idx] = f(results[idx][0])

