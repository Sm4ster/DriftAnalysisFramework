import numpy as np


def gaussian_filter(x, steepness, width, position):
    abs_x = np.abs((1 / width) * (x - position))
    return np.where(abs_x < 1, 0, 1 - np.exp(-steepness * (np.square(np.log(abs_x)))))


def g(x):
    return 0.5 * (1 - np.cos(np.pi * x))


def spline_filter(x, a, b, c, d):
    # Define conditions
    condition1 = (x < a) | (x > d)
    condition2 = (b < x) & (x < c)
    condition3 = (a < x) & (x < b)
    condition4 = (c < x) & (x < d)

    # Compute the results for each condition
    result1 = 1
    result2 = 0
    result3 = 1 - g((x - a) / (b - a))
    result4 = g((x - c) / (d - c))

    # Apply the conditions using np.select for better readability
    conditions = [condition1, condition2, condition3, condition4]
    choices = [result1, result2, result3, result4]
    result = np.select(conditions, choices)

    return result
