import numpy as np
import matplotlib.pyplot as plt

def f0(sigma22):
    return 5.4
def f1(sigma22):
    return 0.98 - 0.35 * np.log(np.log(0.51 * sigma22 + 1.0) ** 2)
def f2(sigma22):
    return (25 / (((sigma22 +1.8)*2.5) ** 1.01))

#
#0.00057 - 0.002*log(1.5e-6*sigma22 - 0.099)

results = np.load("sigma_data_pi_old.npy")


# function_evals0 = np.empty([results.shape[0], 1])
function_evals1 = np.empty([results.shape[0], 1])
function_evals2 = np.empty([results.shape[0], 1])

for idx in range(results.shape[0]):
    # print(function_evals)
    # function_evals[idx] = 1
    # function_evals0[idx] = f0(results[idx][0])
    function_evals1[idx] = f1(results[idx][0])
    function_evals2[idx] = f2(results[idx][0])

# Plot the first line
# plt.loglog(results[:, 0], function_evals0, color='red', linestyle='--', label='f0')
plt.loglog(results[:, 0], function_evals1, color='red', linestyle=':', label='f1')
plt.loglog(results[:, 0], function_evals2, color='red', linestyle='--', label='f2')

# Plot the second line
plt.loglog(results[:, 0], results[:, 1], color='blue', linestyle='-', label='ground truth')

plt.hlines(y=5.5, xmin=10 ** (-6), xmax=10, color='g', linestyle='--')
plt.vlines(x=0.005, ymin=10 ** (-6), ymax=10, color='g', linestyle='--')

plt.vlines(x=50, ymin=10 ** (-6), ymax=10, color='g', linestyle='--')

# Add a legend
plt.legend()

# Show the plot
plt.show()
