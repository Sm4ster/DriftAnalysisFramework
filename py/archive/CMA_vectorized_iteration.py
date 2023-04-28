import numpy as np

d = 2
p_target = 0.1818
c_p = 0.8333
c_cov = 0.2
dim = 2


def iterate_classically(alpha, sigma, kappa, m, C):
    # step 1: draw random sample
    Az = np.random.multivariate_normal(np.zeros(2), C)
    x = m + sigma * Az

    # step 2: update parameters
    if np.linalg.norm(x) <= np.linalg.norm(m):
        # a) Let x <- y
        m = x
        # b) update the success probability
        p_succ = 1  # (1 - self.c_p) * p_succ + self.c_p
        # c) omitted
        # d) update the covariance matrix as in equation (1) without search paths
        C = (1 - c_cov) * C + c_cov * np.outer(Az, Az)

    # Otherwise update the success probability
    else:
        p_succ = 0  # (1 - self.c_p) * p_succ

    # step 3: update the global step size
    sigma = sigma * np.exp((1 / d) * ((p_succ - p_target) / (1 - p_target)))

    return m, sigma, C


def iterate_batch(alpha, sigma, kappa, m, C):
    # create m and C from alpha and kappa
    m = np.array([np.cos(alpha), np.sin(alpha)]).T

    C = np.empty((len(kappa), 2, 2), dtype=float)
    C[:, 0, 0] = sigma * kappa
    C[:, 1, 1] = sigma * (1 / kappa)

    # create standard normal samples and transform them
    z = np.random.standard_normal(m.shape)
    Az = np.vstack([np.sqrt(kappa), np.sqrt(1 / kappa)]).T
    x = m + sigma * Az

    # evaluate samples
    fx = np.linalg.norm(x, axis=1, keepdims=True)
    success = (fx <= 1).astype(np.float64)

    # calculate new m, new sigma and new C
    new_m = success * x + (1 - success) * m
    new_sigma = sigma * np.exp((1 / d) * ((success - p_target) / (1 - p_target))).reshape(sigma.shape[0])
    unsuccessful = ((1 - success.reshape(success.shape[0])[:, np.newaxis, np.newaxis]) * C)
    successful = (success.reshape(success.shape[0])[:, np.newaxis, np.newaxis]) * (
            np.array((1 - c_cov)) * C + np.array(c_cov) * np.einsum("ij,ik->ijk", z, z))
    new_C = successful + unsuccessful

    return new_m, new_sigma, new_C


kappa = 2
C = np.array([[kappa, 0], [0, 1 / kappa]])

print(np.tile(C, (100000, 1, 1)))

Az_classic = np.random.multivariate_normal(np.zeros(2), C, size=100000)

Az_vectorized = np.vstack(np.tile(C, (100000, 1, 1))).T

print(Az_classic, Az_vectorized)
