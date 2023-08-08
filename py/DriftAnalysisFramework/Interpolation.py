import numpy as np


def closest_values(needle_values, haystack_array):
    overflow_mask = needle_values > haystack_array.max() + haystack_array.max() * 0.001
    underflow_mask = needle_values < haystack_array.min() - haystack_array.min() * 0.001

    if overflow_mask.any():
        print(f"Warning: {np.sum(overflow_mask)} needle value(s) are larger than any value in the haystack array.")
        for i in range(overflow_mask.shape[0]):
            if overflow_mask[i]:
                print(i, haystack_array.max(), needle_values[i])

    if underflow_mask.any():
        print(f"Warning: {np.sum(underflow_mask)} needle value(s) are smaller than any value in the haystack array.")

    # Find closest values higher than and lower than the given values
    h_mask = haystack_array[:, np.newaxis] >= needle_values
    l_mask = haystack_array[:, np.newaxis] <= needle_values

    # Setting the values to max and min is a bit unclean, because we do not notice when values are out of bounds.
    # However settings these to inf and -inf makes slight rounding errors fail the whole thing.
    h_filtered_values = np.where(h_mask, haystack_array[:, np.newaxis], haystack_array.max())
    l_filtered_values = np.where(l_mask, haystack_array[:, np.newaxis], haystack_array.min())

    h_closest_values = np.min(h_filtered_values, axis=0)
    l_closest_values = np.max(l_filtered_values, axis=0)

    h_closest_indices = np.argmin(h_filtered_values, axis=0)
    l_closest_indices = np.argmax(l_filtered_values, axis=0)

    return l_closest_values, h_closest_values, l_closest_indices, h_closest_indices


def interpolate(x, y, x1, y1, x2, y2, q11, q12, q21, q22):
    result = np.zeros_like(x)

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
    x_mask = np.array((x1 == x2) & (y1 != y2))
    y_mask = np.array((x1 != x2) & (y1 == y2))

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


def get_data_value(x, y, x_data, y_data, f_data):
    # print("get_data_value_x", x, x_data, closest_values(x, x_data))
    # print("get_data_value_y", y, y_data, closest_values(y, y_data))

    # find the closest values for each sequence
    l_x_val, h_x_val, l_x_idx, h_x_idx = closest_values(x, x_data)
    l_y_val, h_y_val, l_y_idx, h_y_idx = closest_values(y, y_data)

    return interpolate(
        x, y, l_x_val, l_y_val, h_x_val, h_y_val,
        f_data[l_x_idx, l_y_idx], f_data[l_x_idx, h_y_idx],
        f_data[h_x_idx, l_y_idx], f_data[h_x_idx, h_y_idx]
    )
