import numpy as np
import matplotlib.pyplot as plt


def f0(sigmavar):
    return 0.0055 - 0.063 / (-0.00038 * sigmavar - 0.1)  # 0.0078 + 0.071/(0.00041*sigmavar + 0.11)


def f1(sigma22):
    return (25 / (((sigma22 + 10) * 2) ** 1.5))


def f2(sigma22):
    return (25 / (((sigma22 + 5) * 1) ** 1.5))


plt.figure(dpi=600)
# 0.00057 - 0.002*log(1.5e-6*sigma22 - 0.099)
results = np.load("sigma_data_pi_2023_01_16.npy")

curve_idxs = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9,19,29,39,49,59,69,79,89,99]
plot_functions = False
plot_helping_lines = False

# x axis array, we take the 0th one, since it is as good as any
x_axis_idx = 1
x_axis = results[0][:, x_axis_idx]

# Plot the ground truth lines
for curve_idx in curve_idxs:
    plt.loglog(x_axis, results[curve_idx][:, 0], linestyle='-', lw=0.2)

# Plot functions
if plot_functions:
    function_evals0 = np.empty([x_axis.shape[0], 1])
    function_evals1 = np.empty([x_axis.shape[0], 1])
    function_evals2 = np.empty([x_axis.shape[0], 1])

    for idx, x in enumerate(x_axis):
        function_evals0[idx] = f0(x)
        function_evals1[idx] = f1(x)
        function_evals2[idx] = f2(x)

    # plt.loglog(x_axis, function_evals0, linestyle='--', label='f0', lw=0.5)
    plt.loglog(x_axis, function_evals1, linestyle=':', label='f1', lw=0.5)
    plt.loglog(x_axis, function_evals2, linestyle='-', label='f2', lw=0.5)

# plot helping lines
if plot_helping_lines:
    plt.vlines(x=0.005, ymin=10 ** (-6), ymax=10, color='g', linestyle='--')
    plt.vlines(x=50, ymin=10 ** (-6), ymax=10, color='g', linestyle='--')

plt.legend()
plt.show()
