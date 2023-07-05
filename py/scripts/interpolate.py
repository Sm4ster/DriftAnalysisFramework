import numpy as np

def find_closest_values(given_array, target_values):
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


def interpolate(x, y, x1, y1, x2, y2, q11, q12, q21, q22):
    result = np.zeros_like(x)

    # print("x", x)
    # print("y", y)
    # print("x1", x1)
    # print("x2", x2)
    # print("y1", y1)
    # print("y2", y2)
    # print("q11", q11)
    # print("q12", q12)
    # print("q21", q21)
    # print("q22", q22)

    # Perform bilinear interpolation for non-identical points
    non_identical_mask = (x1 != x2) & (y1 != y2)

    if np.any(non_identical_mask):
        x2_x1_diff = x2[non_identical_mask] - x1[non_identical_mask]
        y2_y1_diff = y2[non_identical_mask] - y1[non_identical_mask]

        x2_x_diff = x2[non_identical_mask] - x[non_identical_mask]
        y2_y_diff = y2[non_identical_mask] - y[non_identical_mask]

        x_x1_diff = x[non_identical_mask] - x1[non_identical_mask]
        y_y1_diff = y[non_identical_mask] - y1[non_identical_mask]

        result[non_identical_mask] = (1 / (x2_x1_diff * y2_y1_diff)) * (
                (q11[non_identical_mask] * x2_x_diff * y2_y_diff) +
                (q21[non_identical_mask] * x_x1_diff * y2_y_diff) +
                (q12[non_identical_mask] * x2_x_diff * y_y1_diff) +
                (q22[non_identical_mask] * x_x1_diff * y_y1_diff))

    # Handle identical points and interpolate the other pair
    x_mask = (x1 == x2) & (y1 != y2)
    y_mask = (x1 != x2) & (y1 == y2)

    # Interpolate along y-axis where x-coordinates are identical
    t_y = (y[x_mask] - y1[x_mask]) / (y2[x_mask] - y1[x_mask])
    result[x_mask] = (1 - t_y) * q11[x_mask] + t_y * q12[x_mask]

    # Interpolate along x-axis where y-coordinates are identical
    t_x = (x[y_mask] - x1[y_mask]) / (x2[y_mask] - x1[y_mask])
    result[y_mask] = (1 - t_x) * q11[y_mask] + t_x * q21[y_mask]

    # Handle points where both pairs are identical
    identical_mask = (x1 == x2) & (y1 == y2)
    result[identical_mask] = q11[identical_mask]

    return result


# Load variables from the file
data = np.load('../data/stable_parameters.npz')

# Access the variables
alpha = data['alpha']
kappa = data['kappa']
sigma = data['sigma']
stable_kappa = data['stable_kappa']
stable_sigma = data['stable_sigma']

alpha_samples = 9
kappa_samples = 9
sigma_samples = 9

alpha_sequence = np.linspace(0, np.pi / 4, num=alpha_samples)
kappa_sequence = np.geomspace(1 / 1000, 1000, num=kappa_samples)
sigma_sequence = np.geomspace(1 / 1000, 1000, num=sigma_samples)

# find the closest values for each sequence
l_alpha_val, h_alpha_val, l_alpha_idx, h_alpha_idx = find_closest_values(alpha_sequence, alpha)
l_kappa_val, h_kappa_val, l_kappa_idx, h_kappa_idx = find_closest_values(kappa_sequence, kappa)
l_sigma_val, h_sigma_val, l_sigma_idx, h_sigma_idx = find_closest_values(sigma_sequence, sigma)

# get the interpolated stable kappa out of the bilinear interpolation
result = interpolate(
    alpha_sequence, sigma_sequence, l_alpha_val, l_sigma_val, h_alpha_val, h_sigma_val,
    stable_kappa[l_alpha_idx, l_sigma_idx], stable_kappa[h_alpha_idx, l_sigma_idx],
    stable_kappa[l_alpha_idx, h_sigma_idx], stable_kappa[h_alpha_idx, h_sigma_idx]
)

print(result)

# print(kappa_sequence, kappa)
# print(sigma_sequence, sigma)
