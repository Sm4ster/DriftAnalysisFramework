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


def find_closest_values_vectorized(arr, target):
    # Find closest values higher than and lower than the given values
    diff = np.abs(arr - target[:, np.newaxis])
    sorted_indices = np.argsort(diff, axis=1)

    # Get the index of the closest value lower than or equal to the given value
    lower_indices = np.argmax(arr[sorted_indices] <= target[:, np.newaxis], axis=1)

    # Get the index of the closest value higher than or equal to the given value
    higher_indices = np.argmin(arr[sorted_indices] >= target[:, np.newaxis], axis=1)
    return np.array[[lower_indices, higher_indices]]


def interpolate_vectorized(x, y, values, target):
    print(x, target, values)
    x_1, x_2, x = x[0], x[1], target[0]
    y_1, y_2, y = y[0], y[1], target[1]

    return (1 / ((x_2 - x_1) * (y_2 - y_1)) * (
            values[0] * (x_2 - x) * (y_2 - y) + values[1] * (x - x_1) * (y_2 - y) + values[2] * (x_2 - x) * (
            y - y_1) + values[3] * (x - x_1) * (y - y_1)))


results = np.load("../../data/sigma_data_56000_samples.npy")

state = 0.0001291549665014884

