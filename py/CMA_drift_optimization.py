import numpy as np
import json

drift_data_raw = json.load(open('./data/big_test_run.json'))
drift_data = np.array(drift_data_raw["drifts"])


class Fitness:
    def __init__(self, data):
        self.drift_data = data

    def combined_drift(self, weights):
        combined_drift = np.zeros([self.drift_data.shape[0], self.drift_data.shape[1], self.drift_data.shape[2]])

        for idx in range(len(weights)):
            combined_drift += self.drift_data[:, :, :, idx] * weights[0, idx]

        return combined_drift

    def eval(self, weights, keepdims=False):
        drift = self.combined_drift(weights)
        return np.array([drift.max() - drift.min()])

    def min_drift(self, weights):
        drift = self.combined_drift(weights)
        return drift.min()


class CMA_ES:
    m = None

    def __init__(self, target, constants):
        # make target function available
        self.target = target

        # constants
        self.d = constants["d"]  # 1 + self.dim / 2
        self.p_target = constants["p_target"]  # 2 / 11
        self.c_cov = constants["c_cov"]  # 2 / (np.power(self.dim, 2) + 6)

    def step(self, m, C, sigma, z=None):
        if z is None:
            # create standard normal samples and transform them
            z = np.random.standard_normal(m.shape)

        # this is equivalent to Az in the normal form, as the matrix C is diagonal,
        # therefore matrix A (with AA = C) is [[sqrt(C_00), 0][0, sqrt(C_11)]]
        x = m + np.matmul(z, sigma[:, np.newaxis, np.newaxis] * np.linalg.cholesky(C))[0]

        # evaluate samples
        fx = self.target.eval(x, keepdims=True)
        success = (fx <= 1).astype(np.float64)

        # calculate new m, new sigma and new C
        new_m = success * x + (1 - success) * m
        new_sigma = sigma * np.exp((1 / self.d) * ((success - self.p_target) / (1 - self.p_target))).reshape(
            sigma.shape[0])
        unsuccessful = ((1 - success.reshape(success.shape[0])[:, np.newaxis, np.newaxis]) * C)
        successful = (success.reshape(success.shape[0])[:, np.newaxis, np.newaxis]) * (
                np.array((1 - self.c_cov)) * C + np.array(self.c_cov) * np.einsum("ij,ik->ijk", z, z))
        new_C = successful + unsuccessful

        return new_m, new_C, new_sigma


f = Fitness(drift_data)
alg = CMA_ES(f, {
    "d": 2,
    "p_target": 0.1818,
    "c_p": 0.8333,
    "c_cov": 0.2,
    "dim": 2
})

m, C, sigma = np.ones(drift_data.shape[3])[np.newaxis, :], np.identity(drift_data.shape[3])[np.newaxis, :], np.array([1])

for i in range(10000):
    m, C, sigma = alg.step(m, C, sigma)


print(m, f.eval(m), f.min_drift(m))
# m = np.array([[ 5.17538277e-01,  1.52261307e+02, -2.77779864e+02,  1.40517244e+03]])
# [[ 1.80408898e+00 -5.41665879e+02  2.26951635e+03  8.53872821e+02]] [0.42390573] -0.42659210729724883