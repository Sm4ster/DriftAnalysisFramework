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

    h_closest_values = np.min(h_filtered_values, axis=0)
    l_closest_values = np.max(l_filtered_values, axis=0)

    h_closest_indices = np.argmin(h_filtered_values, axis=0)
    l_closest_indices = np.argmax(l_filtered_values, axis=0)

    return l_closest_values, h_closest_values, l_closest_indices, h_closest_indices


def interpolate_vectorized(x, y, x1, y1, x2, y2, q_values):
    identical_points = (x1 == x2) & (y1 == y2)
    print(x2, x1, y2, y1, identical_points)

    # Perform bilinear interpolation for non-identical points
    non_identical_indices = ~identical_points
    result = np.zeros_like(x)
    if np.any(non_identical_indices):
        q11 = q_values[0][non_identical_indices]
        q12 = q_values[1][non_identical_indices]
        q21 = q_values[2][non_identical_indices]
        q22 = q_values[3][non_identical_indices]

        x_diff = x[non_identical_indices] - x1[non_identical_indices]
        y_diff = y[non_identical_indices] - y1[non_identical_indices]

        print(y2[non_identical_indices] - y[non_identical_indices])
        result[non_identical_indices] = (q11 * (x2[non_identical_indices] - x[non_identical_indices]) * (
                    y2[non_identical_indices] - y[non_identical_indices]) + q21 * (
                                                     x[non_identical_indices] - x1[non_identical_indices]) * (
                                                     y2[non_identical_indices] - y[non_identical_indices]) + q12 * (
                                                     x2[non_identical_indices] - x[non_identical_indices]) * (
                                                     y[non_identical_indices] - y1[non_identical_indices]) + q22 * (
                                                     x[non_identical_indices] - x1[non_identical_indices]) * (
                                                     y[non_identical_indices] - y1[non_identical_indices])) / (
                                                    (x2[non_identical_indices] - x1[non_identical_indices]) * (
                                                        y2[non_identical_indices] - y1[non_identical_indices]))
    print(result)
    # Handle identical points and interpolate the other pair
    identical_indices = identical_points.nonzero()[0]
    print(identical_indices)
    x_mask = (x1[identical_indices] == x2[identical_indices])
    y_mask = ~x_mask

    print(x_mask, y_mask)

    # Interpolate along y-axis where x-coordinates are identical
    t_y = (y[identical_indices] - y1[identical_indices]) / (y2[identical_indices] - y1[identical_indices])
    result[identical_indices] += x_mask * ((1 - t_y) * q_values[0][identical_indices] + t_y * q_values[1][identical_indices])

    # Interpolate along x-axis where y-coordinates are identical
    t_x = (x[identical_indices] - x1[identical_indices]) / (x2[identical_indices] - x1[identical_indices])
    result[identical_indices] += y_mask * ((1 - t_x) * q_values[0][identical_indices] + t_x * q_values[2][identical_indices])


    return result

    # return (1 / ((x2 - x1) * (y2 - y1)) * (
    #         q_values[0] * (x2 - x) * (y2 - y) + q_values[1] * (x - x1) * (y2 - y) + q_values[2] * (x2 - x) * (
    #         y - y1) + q_values[3] * (x - x1) * (y - y1)))


# Load variables from the file
data = np.load('../data/stable_parameters.npz')

# Access the variables
alpha = data['alpha']
kappa = data['kappa']
sigma = data['sigma']
stable_kappa = data['stable_kappa']
stable_sigma = data['stable_sigma']

print(stable_kappa.shape)

alpha_samples = 9
kappa_samples = 9
sigma_samples = 9

alpha_sequence = np.linspace(0, np.pi / 4, num=alpha_samples)
kappa_sequence = np.geomspace(1 / 1000, 1000, num=kappa_samples)
sigma_sequence = np.geomspace(1 / 1000, 10000, num=sigma_samples)

# find the closest values for each sequence
l_alpha_val, h_alpha_val, l_alpha_idx, h_alpha_idx = find_closest_values_vectorized(alpha_sequence, alpha)
l_kappa_val, h_kappa_val, l_kappa_idx, h_kappa_idx = find_closest_values_vectorized(kappa_sequence, kappa)
l_sigma_val, h_sigma_val, l_sigma_idx, h_sigma_idx = find_closest_values_vectorized(sigma_sequence, sigma)

# get the edge values out of the table for kappa
q_values = np.array([stable_kappa[l_alpha_idx, l_sigma_idx], stable_kappa[h_alpha_idx, l_sigma_idx],
                     stable_kappa[l_alpha_idx, h_sigma_idx], stable_kappa[h_alpha_idx, h_sigma_idx]])

# get the interpolated stable kappa out of the bilinear interpolation
result = interpolate_vectorized(alpha_sequence, sigma_sequence, l_alpha_val, l_sigma_val, h_alpha_val, h_sigma_val,
                                q_values)

print(result)

# print(kappa_sequence, kappa)
# print(sigma_sequence, sigma)
