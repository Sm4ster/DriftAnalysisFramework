import numpy as np


def find_closest_values(arr, target):
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


def interpolate(x, y, values, target):
    print(x, target, values)
    x_1, x_2, x = x[0], x[1], target[0]
    y_1, y_2, y = y[0], y[1], target[1]

    return (1 / ((x_2 - x_1) * (y_2 - y_1)) * (
            values[0] * (x_2 - x) * (y_2 - y) + values[1] * (x - x_1) * (y_2 - y) + values[2] * (x_2 - x) * (
            y - y_1) + values[3] * (x - x_1) * (y - y_1)))


state = {'sigma': 0.0001291549665014884, 'sigma_var': 10000.4842503189421, 'm': [.783981633974483, 0.]}
results = np.load("../../data/sigma_data_56000_samples.npy")


