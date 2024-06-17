import numpy as np


def gaussian_filter(x, steepness, width, position):
    abs_x = np.abs((1 / width) * (x - position))
    return np.where(abs_x < 1, 0, 1 - np.exp(-steepness * (np.square(np.log(abs_x)))))
