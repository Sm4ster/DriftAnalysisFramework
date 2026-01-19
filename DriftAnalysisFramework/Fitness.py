import numpy as np


class Sphere:
    def set(self, alpha, kappa, sigma):
        pass

    def eval(self, x):
        return np.square(np.linalg.norm(x, axis=-1))


class LinearizedSphere2D:
    """
    "Linearized sphere" in 2D:
      f(x,y) = scale * (n · (x-c))^2
      n = (cos(theta), sin(theta))
    Flat in der orthogonalen Richtung.
    """

    def __init__(self, center=(0.0, 0.0), scale=1.0):
        self.set_theta(0)
        self.center = np.asarray(center, dtype=float)
        if self.center.shape != (2,):
            raise ValueError("center must be a 2-tuple / shape (2,).")
        self.scale = float(scale)

    def set(self, alpha, kappa, sigma):
        self.set_theta(alpha)

    def set_theta(self, theta):
        self.theta = float(theta)
        self.n = np.array([np.cos(self.theta), np.sin(self.theta)], dtype=float)  # shape (2,)

    def eval(self, x):
        c = self.center
        n = self.n
        s = self.scale

        # (N,2) · (2,) -> (N,)
        u = (x - c) @ n
        out = s * (u * u)
        return out


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

