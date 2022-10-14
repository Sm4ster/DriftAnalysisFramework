import numpy as np


class OnePlusOne_ES:
    m = None

    def __init__(self, target, constants):
        self.dim = target.dim

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

    def iterate(self, state):
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
        # dimension
        self.dim = target.dim

        # constants
        self.d = 1 + self.dim / 2
        self.p_target = 2 / 11
        self.c_cov_plus = 2 / (np.power(self.dim, 2) + 6)
        self.c_p = 1 / 12

        # make target function available
        self.target = target
        self.f = self.target.eval

        # init rng
        self.rng = np.random.default_rng()

    def set_location(self, location):
        if isinstance(location, list):
            location = np.asarray(location)
        self.m = location

    def get_location(self):
        return self.m

    def iterate(self, state):
        m_t, sigma_t, cov_m, p_succ = self.m, state["sigma"], state["cov_m"], state["p_succ"]

        # step 1: draw random sample
        z = self.rng.multivariate_normal(np.zeros(self.dim), cov_m)
        x_t = m_t + sigma_t * z

        # step 2: update parameters
        if self.f(x_t) <= self.f(m_t):
            # a) Let x <- y
            m_t = x_t
            # b) update the success probability
            p_succ = (1 - self.c_p) * p_succ + self.c_p
            # c) omitted
            # d) update the covariance matrix as in equation (1) without search paths
            cov_m = (1 - self.c_cov_plus) * cov_m + self.c_cov_plus * np.outer(z, z)

        # Otherwise update the success probability
        else:
            p_succ = (1 - self.c_p) * p_succ

        # step 3: update the global step size
        sigma_t = sigma_t * np.exp((1 / self.d) * ((p_succ - self.p_target) / (1 - self.p_target)))

        return {"m": m_t, "sigma": sigma_t, "cov_m": cov_m, "p_succ": p_succ}
