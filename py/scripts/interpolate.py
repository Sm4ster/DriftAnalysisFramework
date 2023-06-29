import numpy as np


def find_closest_values_unvectorized(arr, target):
    # Find the index of the first value in the array greater than target
    idx = np.searchsorted(arr, target)

    # Check if the exact value is in the array
    if target in arr:
        values = [target, arr[idx - 1 if idx > 0 else idx + 1]]
        values.sort()
        return values
    else:
        # Get the closest value greater than target
        greater = arr[idx] if idx < len(arr) else None

        # Get the closest value smaller than target
        smaller = arr[idx - 1] if idx > 0 else None
    return [smaller, greater]


def interpolate_unvectorized(x, y, values, target):
    print(x, target, values)
    x_1, x_2, x = x[0], x[1], target[0]
    y_1, y_2, y = y[0], y[1], target[1]

    return (1 / ((x_2 - x_1) * (y_2 - y_1)) * (
            values[0] * (x_2 - x) * (y_2 - y) + values[1] * (x - x_1) * (y_2 - y) + values[2] * (x_2 - x) * (
            y - y_1) + values[3] * (x - x_1) * (y - y_1)))


def find_closest_values_vectorized(given_array, target_values):
    # Find closest values higher than and lower than the given values
    h_mask = target_values[:, np.newaxis] >= given_array
    l_mask = target_values[:, np.newaxis] <= given_array

    h_filtered_values = np.where(h_mask, target_values[:, np.newaxis], np.inf)
    l_filtered_values = np.where(l_mask, target_values[:, np.newaxis], -np.inf)

    h_closest_indices = np.argmin(h_filtered_values, axis=0)
    l_closest_indices = np.argmax(l_filtered_values, axis=0)

    return np.array([l_closest_indices, h_closest_indices])


def interpolate_vectorized(x, y, values, target):
    print(x, target, values)
    x_1, x_2, x = x[0], x[1], target[0]
    y_1, y_2, y = y[0], y[1], target[1]

    return (1 / ((x_2 - x_1) * (y_2 - y_1)) * (
            values[0] * (x_2 - x) * (y_2 - y) + values[1] * (x - x_1) * (y_2 - y) + values[2] * (x_2 - x) * (
            y - y_1) + values[3] * (x - x_1) * (y - y_1)))


# Load variables from the file
data = np.load('../data/stable_parameters.npz')

# Access the variables
alpha = data['alpha']
kappa = data['kappa']
sigma = data['sigma']
stable_kappa = data['stable_kappa']
stable_sigma = data['stable_sigma']

alpha_samples = 9
kappa_samples = 24
sigma_samples = 24

alpha_sequence = np.linspace(0, np.pi / 4, num=alpha_samples)
kappa_sequence = np.geomspace(1 / 1000, 1000, num=kappa_samples)
sigma_sequence = np.geomspace(1 / 1000, 10000, num=sigma_samples)

print(find_closest_values_vectorized(alpha_sequence, alpha))
# print(kappa_sequence, kappa)
# print(sigma_sequence, sigma)
