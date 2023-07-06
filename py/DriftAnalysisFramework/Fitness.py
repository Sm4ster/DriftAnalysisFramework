import numpy as np


class Sphere:
    def eval(self, x, keepdims=False):
        if type(x) == list:
            x = np.array(list)
        if x.ndim == 1:
            return np.linalg.norm(x)
        if x.ndim == 2:
            return np.linalg.norm(x, axis=1, keepdims=keepdims)
        else:
            raise Exception("Input dimensionality is wrong")


class ConvexQuadratic:
    norm_matrix = None

    def __init__(self, target):
        # init the input
        self.norm_matrix = np.array(
            [
                [target["A"], 1 / 2 * target["B"]],
                [1 / 2 * target["B"], target["C"]]
            ])

    def eval(self, x):
        if type(x) == list:
            x = np.array(list)
        if x.ndim == 1:
            return x @ self.norm_matrix @ x
        if x.ndim == 2:
            return np.sum((x @ self.norm_matrix) * x, axis=1, keepdims=True)
        else:
            raise Exception("Input dimensionality is wrong")

