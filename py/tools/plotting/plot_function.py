import numpy as np
import matplotlib.pyplot as plt


# def f0(sigmavar):
#     params = [ 2.17139551e-05, -9.68610759e+00,  1.19851080e+01,  8.05184732e-02, 2.39198346e+02]
#     return (params[0] * ((params[1] * sigmavar + params[2]) * params[3]) ** params[4])
#
#
# def f1(sigmavar):
#     params = [1.71794092, 0.16084129, 1.94203689, 0.80126126, 2.12725817]
#     return (params[0] * ((params[1] * sigmavar + params[2]) * params[3]) ** params[4])
#
#
# def f2(sigmavar):
#     # params =  [ 4.37650584, -2.5126537,  -2.05925185, -0.2529315,  -1.50053785]
#     params = [ 4.06810283, -2.70812722, -2.12072882, -0.3988214,  -1.17725648]
#     return (params[0] * ((params[1] * sigmavar + params[2]) * params[3]) ** params[4])


def f0(sigma22, a=25, b=1.5, c=1.8, d=2.5, e=1.01):
    return (a * ((b * sigma22 + c) * d) ** e)


def f1(sigma22, a=0.98, b=0.35, c=0.51, d=1.0, e=1):
    return (a * ((b * sigma22 + c) * d) ** e)
    # return a - b * np.log(c * sigma22 + d) ** e


def f2(sigma22, a=25, b=1.5, c=1.8, d=2.5, e=1.01):
    return (a * ((b * sigma22 + c) * d) ** e)


def f(sigma_var):
    input = [0.11266539, 9.86245131, 1.13466994, 0.82103122, 0.89260681, 0.93995208,
             1.06595626, 0.90815017, 0.89893571, 1.16504169, 1.16402273, 1.07920067,
             0.77917671, 0.82706872, 0.94281873, 0.8320501, 0.19830234, 1.06818142,
             0.95651097, 0.91144903, 1.13920617]

    if sigma_var < input[0]:
        return f0(sigma_var, *input[2:7])
    elif sigma_var < input[1]:
        return f1(sigma_var, *input[7:12])
    else:
        return f2(sigma_var, *input[12:17])


plt.figure(dpi=600)
# 0.00057 - 0.002*log(1.5e-6*sigma22 - 0.099)
results = np.load("../../data/sigma_data_pi_2023_01_21.npy")
distance_sequence = np.geomspace(1, 100, 10)
curve_idxs = [0]
distance_idxs = [0]
plot_functions = True
plot_helping_lines = False

# x axis array, we take the 0th one, since it is as good as any
x_axis_idx = 1
x_axis = results[0][0][:, x_axis_idx]

# Plot the ground truth lines
for distance_idx in distance_idxs:
    for curve_idx in curve_idxs:
        plt.loglog(x_axis, results[curve_idx][distance_idx][:, 0], label='truth', linestyle='-', lw=0.2)

# Plot functions
if plot_functions:
    function_evals0 = np.empty([x_axis.shape[0], 1])
    # function_evals1 = np.empty([x_axis.shape[0], 1])
    # function_evals2 = np.empty([x_axis.shape[0], 1])

    for idx, x in enumerate(x_axis):
        function_evals0[idx] = f(x)
        # function_evals1[idx] = f1(x)
        # function_evals2[idx] = f2(x)

    plt.loglog(x_axis, function_evals0, linestyle='--', label='f0', lw=0.5)
    # plt.loglog(x_axis, function_evals1, linestyle=':', label='f1', lw=0.5)
    # plt.loglog(x_axis, function_evals2, linestyle='-', label='f2', lw=0.5)

# plot helping lines
if plot_helping_lines:
    plt.vlines(x=0.005, ymin=10 ** (-6), ymax=10, color='g', linestyle='--')
    plt.vlines(x=50, ymin=10 ** (-6), ymax=10, color='g', linestyle='--')

plt.legend()
plt.show()
