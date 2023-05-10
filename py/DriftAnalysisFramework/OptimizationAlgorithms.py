import numpy as np


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
        # dimension
        self.dim = 2

        # constants
        self.d = constants["d"]  # 1 + self.dim / 2
        self.p_target = constants["p_target"]  # 2 / 11
        self.c_cov = constants["c_cov"]  # 2 / (np.power(self.dim, 2) + 6)

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

    def step_unvectorized(self, state):
        m_t, sigma_t, cov_m = self.m, state["sigma"], state["cov_m"]

        # step 1: draw random sample
        z = self.rng.multivariate_normal(np.zeros(self.dim), cov_m)
        x_t = m_t + sigma_t * z

        # step 2: update parameters
        if self.f(x_t) <= self.f(m_t):
            # a) Let x <- y
            m_t = x_t
            # b) update the success probability
            p_succ = 1  # (1 - self.c_p) * p_succ + self.c_p
            # c) omitted
            # d) update the covariance matrix as in equation (1) without search paths
            cov_m = (1 - self.c_cov_plus) * cov_m + self.c_cov_plus * np.outer(z, z)

        # Otherwise update the success probability
        else:
            p_succ = 0  # (1 - self.c_p) * p_succ

        # step 3: update the global step size
        sigma_t = sigma_t * np.exp((1 / self.d) * ((p_succ - self.p_target) / (1 - self.p_target)))

        return {"m": m_t, "sigma": sigma_t, "cov_m": cov_m, "p_succ": p_succ}

    def step(self, m, C, sigma, z=None):
        if z is None:
            # create standard normal samples and transform them
            z = np.random.standard_normal(m.shape)

        # this is equivalent to Az in the normal form, as the matrix C is diagonal,
        # therefore matrix A (with AA = C) is [[sqrt(C_00), 0][0, sqrt(C_11)]]
        sigma_A = np.array([sigma * np.sqrt(C[:, 0, 0]), sigma * np.sqrt(C[:, 1, 1])]).T
        x = m + z * sigma_A

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

    def iterate(self, alpha, kappa, sigma, num=1000, transform_normal=True):
        # Sanitize parameters #
        # Determine which parameters are arrays and their lengths
        is_array = [isinstance(param, np.ndarray) for param in [alpha, sigma, kappa]]
        array_lengths = [len(param) if is_array[i] else None for i, param in enumerate([alpha, sigma, kappa])]

        if is_array.count(True) > 0:
            # If there are multiple arrays, make sure they have the same length
            unique_lengths = set(list(filter(lambda x: x is not None, array_lengths)))
            if len(unique_lengths) > 1:
                raise ValueError("All array parameters must have the same length.")

            # Set length of parameters to expand to
            array_index = is_array.index(True)
            array_length = array_lengths[array_index]

        else:
            # Expand all numeric parameters to the same length given by num
            array_length = num

        # Expand all numeric parameters to its length
        alpha, sigma, kappa = [np.tile(param, array_length)[:array_length] if not is_array[i] else param for i, param in
                               enumerate([alpha, sigma, kappa])]

        # Start the computations #
        # create m from alpha
        m = np.array([np.cos(alpha), np.sin(alpha)]).T

        # create C from kappa
        C = np.zeros((array_length, 2, 2), dtype=float)
        # C = np.full((num, 2, 2), 0.5, dtype=float)
        C[:, 0, 0] = kappa
        C[:, 1, 1] = (1 / kappa)

        # create the random samples
        z = np.array([np.random.standard_normal(array_length), np.random.standard_normal(array_length)]).T

        # vectorized step
        states = self.step(m, C, sigma, z)

        # vectorized transformation
        if transform_normal:
            m_normal, C_normal, sigma_normal, scaling_factor, distance_factor = self.transform_to_normal(states[0],
                                                                                                         states[1],
                                                                                                         states[2])
        else:
            m_normal, C_normal, sigma_normal, scaling_factor, distance_factor = states[0], states[1], states[2], 1, 1

        return np.arccos(m_normal[:, 0]), C_normal[:, 0, 0], sigma_normal, \
               m_normal, C_normal, scaling_factor, \
               distance_factor, states

    def transform_to_normal(self, m, C, sigma, normal_form=0):
        # get the the transformation matrix
        A = np.linalg.eigh(C)[1]

        # rotate the coordinate system such that the eigenvalues of
        # the covariance matrix are parallel to the coordinate axis
        A_T = np.transpose(A, [0, 2, 1])

        C_rot = np.matmul(np.matmul(A_T, C), A)
        m_rot = np.einsum('...ij,...j->...i', A_T, m)

        # calculate the scaling factor which brings the covariance matrix to det = 1
        scaling_factor = 1 / (np.sqrt(np.linalg.det(C_rot)))

        m_normal = np.einsum('i,ij->ij', scaling_factor, m_rot)
        C_normal = np.einsum('i,ijk->ijk', scaling_factor, C_rot)

        # make values close to zero equal zero
        C_normal[np.abs(C_normal) < 1e-15] = 0

        # The distance factor sets norm(m) = 1. To keep the proportion between the distance
        # of the center to the optimum and the spread of the distribution we adjust sigma.
        distance_factor = 1 / np.linalg.norm(m_normal, axis=1)

        m_normal = np.einsum('i,ij->ij', distance_factor, m_normal)
        sigma_normal = sigma * distance_factor

        # conditional x-axis flip
        flip = (m_normal[:, 0] < 0).astype(np.float64)
        m_normal[:, 0] = (np.array([1]) - flip) * m_normal[:, 0] + flip * np.array([-1]) * m_normal[:, 0]

        # conditional y-axis flip
        flip = (m_normal[:, 1] <= 0).astype(np.float64)
        m_normal[:, 1] = (np.array([1]) - flip) * m_normal[:, 1] + flip * np.array([-1]) * m_normal[:, 1]

        # conditional axis swap
        if normal_form == 0:
            swap = (m_normal[:, 0] <= np.cos(np.pi / 4)).astype(np.float64)
        if normal_form == 1:
            swap = (C_normal[:, 1, 1] < 1).astype(np.float64)

        # axis swap of C_normal (with condition)
        C_normal[:, 0, 0], C_normal[:, 1, 1] = C_normal[:, 1, 1] * swap + C_normal[:, 0, 0] * (
                np.array([1]) - swap), C_normal[:, 0, 0] * swap + C_normal[:, 1, 1] * (np.array([1]) - swap)

        # axis swap of m_normal (with condition)
        m_normal[:, 0], m_normal[:, 1] = m_normal[:, 1] * swap + m_normal[:, 0] * (
                np.array([1]) - swap), m_normal[:, 0] * swap + m_normal[:, 1] * (np.array([1]) - swap)

        return m_normal, C_normal, sigma_normal, scaling_factor, distance_factor
