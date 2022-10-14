import numpy as np


class Sphere:
    dim = None
    optimum = None
    viable_dims = lambda self, dim: True

    def __init__(self, dim):
        # init the input
        if not self.viable_dims(dim):
            raise Exception("Dimensionality is not valid")
        else:
            self.dim = dim

        # set optimum as class variable
        self.optimum = np.zeros(dim)

    def eval(self, x):
        return abs(np.linalg.norm(x))


class convex_quadratic:
    dim = 2
    optimum = None
    norm_matrix = None

    def __init__(self, dim, target):
        # init the input
        self.dim = dim
        self.norm_matrix = np.array(
            [
                [target["A"], 1 / 2 * target["B"]],
                [1 / 2 * target["B"], target["C"]]
            ])

        # set optimum as class variable
        self.optimum = np.zeros(dim)

    def eval(self, x):
        return x @ self.norm_matrix @ x

