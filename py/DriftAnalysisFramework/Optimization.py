import numpy as np
from DriftAnalysisFramework.Transformation import CMA_ES as CMA_TR


class OnePlusOne_ES:
    m = None

    def __init__(self, target, constants):
        self.dim = 2

        # make target function available
        self.target = target
        self.f = self.target.eval

        # init identity
        self.identity = np.identity(self.dim)

        # init rng
        self.rng = np.random.default_rng()

        # constants
        self.alpha = constants["alpha"]

    def set_location(self, location):
        if isinstance(location, list):
            location = np.asarray(location)
        self.m = location

    def get_location(self):
        return self.m

    def step(self, state):
        m_t, sigma_t = self.m, state["sigma"]

        # sample x_t ~ m_t + sigma_t N(0,I)
        x_t = self.rng.multivariate_normal(m_t, sigma_t * self.identity)

        if self.f(x_t) <= self.f(m_t):
            m_t = x_t
            sigma_t = sigma_t * self.alpha
        else:
            sigma_t = sigma_t * np.power(self.alpha, -(1 / 4))

        return {"m": m_t, "sigma": sigma_t}

    # def shuffle_state(self):
    #
    # def shuffle_location(self):


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
            z = np.array([np.random.standard_normal(m.shape[0]), np.random.standard_normal(m.shape[0])]).T

        # this is equivalent to Az in the normal form, as the matrix C is diagonal,
        # therefore matrix A (with AA = C) is [[sqrt(C_00), 0][0, sqrt(C_11)]]
        # for higher dimensions possibly use (untested): sigma * np.sqrt(np.diagonal(C, axis1=1, axis2=2))
        sigma_A = np.array([sigma * np.sqrt(C[:, 0, 0]), sigma * np.sqrt(C[:, 1, 1])]).T
        x = m + z * sigma_A

        # evaluate samples
        fx = self.target.eval(x, keepdims=True)
        success = (fx <= 1).astype(np.float64)  # This works because on the sphere in the normal form f(m)=1

        # calculate new m, new sigma and new C
        new_m = success * x + (1 - success) * m
        new_sigma = sigma * np.exp((1 / self.d) * ((success - self.p_target) / (1 - self.p_target))).reshape(
            sigma.shape[0])
        unsuccessful = ((1 - success.reshape(success.shape[0])[:, np.newaxis, np.newaxis]) * C)
        successful = (success.reshape(success.shape[0])[:, np.newaxis, np.newaxis]) * (
                np.array((1 - self.c_cov)) * C + np.array(self.c_cov) * np.einsum("ij,ik->ijk", z, z))
        new_C = successful + unsuccessful

        return new_m, new_C, new_sigma, success

    def iterate(self, alpha, kappa, sigma, num=1):
        # Sanitize, transform and expand the parameters
        m, C, sigma = CMA_TR.transform_to_parameters(alpha, kappa, sigma, num)
        raw_state_before = {"m": m, "C": C, "sigma": sigma}

        # create the random samples
        z = np.array([np.random.standard_normal(m.shape[0]), np.random.standard_normal(m.shape[0])]).T

        # vectorized step
        m, C, sigma, success = self.step(m, C, sigma, z)

        # vectorized transformation
        alpha, kappa, sigma_normal, transformation_parameters = CMA_TR.transform_to_normal(m, C, sigma)

        # prepare data for return statement
        raw_state = {"m": m, "C": C, "sigma": sigma}
        normal_form = {"alpha": alpha, "kappa": kappa, "sigma": sigma_normal}

        return normal_form, raw_state, success, raw_state_before, transformation_parameters
