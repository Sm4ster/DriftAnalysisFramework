import numpy as np
import json
from alive_progress import alive_bar
import cma

drift_data_raw = json.load(open('./data/big_test_run.json'))
drift_data = np.array(drift_data_raw["drifts"])

weight_status = np.array([True, True, True, True], dtype=bool)
batch_size = 1


class Fitness:
    def __init__(self, data):
        self.drift_data = data

    def combined_drift(self, weights):
        combined_drift = np.zeros([self.drift_data.shape[0], self.drift_data.shape[1], self.drift_data.shape[2]])

        weight_idx = 0
        for idx in range(len(weight_status)):
            if weight_status[idx]:
                combined_drift += self.drift_data[:, :, :, weight_idx] * weights[0, weight_idx]
                weight_idx += 1

        return combined_drift

    def eval(self, weights, keepdims=False):
        drift = self.combined_drift(weights)


        fitness = 10 * drift.max() + (drift.max() - drift.min()) + 100 * np.power(1 - weights[0, 0], 2)
        return np.array([fitness])

    def smallest_drift(self, weights):
        drift = self.combined_drift(weights)
        return drift.max()

    def smallest_log_m_drift(self, weight):
        return drift_data[:, :, :, 0].max() * weight


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

        x = m + np.einsum('ij,ilj->il', z, sigma[:, np.newaxis, np.newaxis] * np.linalg.cholesky(C))
        # print(x, m, np.einsum('ij,ilj->il', z, sigma[:, np.newaxis, np.newaxis] * np.linalg.cholesky(C)))

        # evaluate samples
        fm = self.target.eval(m, keepdims=True)
        fx = self.target.eval(x, keepdims=True)
        success = (fx <= fm).astype(np.float64)
        # print(fx)
        # calculate new m, new sigma and new C
        # print(sigma, success,  sigma * np.exp((1 / self.d) * ((success - self.p_target) / (1 - self.p_target))))
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
dim = np.sum(weight_status)
print(type(dim))

m, C, sigma = np.ones([1, dim]), np.repeat(np.eye(dim)[np.newaxis, :, :], 1, axis=0), np.ones([1]) * 10

with alive_bar(10000, force_tty=True, title="Optimizing") as bar:
    for i in range(10000):
        m, C, sigma = alg.step(m, C, sigma)
        if i % 1000 == 0:
            print(m, C, sigma)
            print("Final weights vector: ", m)
            print("Fitness value: ", f.eval(m))
            print("Smallest drift: ", f.smallest_drift(m))
            print("Smallest log_m drift (weighted):", f.smallest_log_m_drift(1), "(", f.smallest_log_m_drift(m[0, 0]),
                  ")")
        bar()

# m = np.array([[ 5.17538277e-01,  1.52261307e+02, -2.77779864e+02,  1.40517244e+03]])
# [[ 1.80408898e+00 -5.41665879e+02  2.26951635e+03  8.53872821e+02]] [0.42390573] -0.42659210729724883
# [[    2.99399693  1311.6470841   2304.67866042 -1222.35048192]] [0.69903951] -0.004458200615063571 -0.0014890464872300772
