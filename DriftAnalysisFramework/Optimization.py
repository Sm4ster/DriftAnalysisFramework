import numpy as np
from DriftAnalysisFramework.Transformation import CMA_ES as CMA_TR


class OnePlusOne_ES:
    m = None

    def __init__(self, target, transformation, constants):
        self.dim = 2

        self.transformation = transformation

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

    def __init__(self, target, transformation, constants, selection_scheme='normal'):
        # make target function available
        self.target = target

        self.transformation = transformation

        # constants
        self.lamda = constants["lamda"]
        self.mu = constants["mu"]

        self.c_mu = constants["c_mu"]

        weights = []

        if selection_scheme == "uniform":
            # Uniform weights for top μ, zero for rest
            weights = np.zeros(self.lamda)
            weights[:self.mu] = 1.0 / self.mu
            self.weights = np.array(weights)

        if selection_scheme == "default":
            for i in range(self.mu):
                weights.append(np.log(self.mu + 1 / 2) - np.log(i + 1))

            for i in range(self.lamda - self.mu):
                weights.append(0)

            self.weights = np.array(weights)
            self.weights = self.weights / np.sum(self.weights)

        # calc mu_eff
        self.mu_eff = 1 / np.sum(self.weights ** 2)
        # print(self.weights)
        # print("mu_eff:", 1 / np.sum(self.weights ** 2))

    def step(self, m, C, sigma, z=None):
        if z is None:
            # create standard normal samples and transform them
            z = np.random.randn(m.shape[0], self.lamda, 2)

        # Expand and calculate
        m_expanded = np.repeat(m[:, np.newaxis, :], self.lamda, axis=1)

        # Since this is the normal form the matrix A (with AA = C) is [[sqrt(C_00), 0][0, sqrt(C_11)]]
        # for higher dimensions possibly use (untested): sigma * np.sqrt(np.diagonal(C, axis1=1, axis2=2))
        A = np.array([np.sqrt(C[:, 0, 0]), np.sqrt(C[:, 1, 1])]).T
        A_expanded = np.repeat(A[:, np.newaxis, :], self.lamda, axis=1)

        # y = Az
        y = A_expanded * z

        # x = m + sigma Az
        x = m_expanded + (sigma.reshape(sigma.shape[0], 1, 1) * y)

        # Compute f(x)
        norms = self.target.eval(x)

        # Get ranking indices based on the norms for each subarray in the middle axis
        indices = np.argsort(norms, axis=-1)
        ranks = np.argsort(indices, axis=-1)

        # Apply the weights to the indices
        weights = np.take(self.weights, ranks)

        ## Parameter updates
        # m = \sum w_i * x_i (or m + \sigma * \sum w_i+y_i)
        new_m = np.einsum("ij,ijk->ik", weights, x)

        # \sigma = \sigma * \exp(
        #   \frac{\sqrt{\mu_{\text{eff}}} * \|\sum^{\mu}_{i=1} w_i z_i\|} {\sqrt{\pi/2}}- 1
        # )
        norm_z_w_sum = np.linalg.norm(np.einsum("ij,ijk->ik", weights, z), axis=1)
        new_sigma = sigma * np.exp((((np.sqrt(self.mu_eff) * norm_z_w_sum) / np.sqrt(np.pi / 2)) - 1))

        # C = (1-c_cov) * C + c_cov \sum w_i * Az_i * (Az_i)^T
        y_outer_product = np.einsum('...i,...j->...ij', y, y)
        y_outer_product_w = np.einsum("ij,ijkl->ikl", weights, y_outer_product)

        new_C = (1 - self.c_mu) * C + self.c_mu * y_outer_product_w

        return new_m, new_C, new_sigma, {}

    def iterate(self, alpha, kappa, sigma, num=1):
        # Sanitize, transform and expand the parameters
        m, C, sigma = self.transformation.transform_to_parameters(alpha, kappa, sigma, num)

        # create the random samples
        z = np.random.randn(m.shape[0], self.lamda, 2)

        # set target
        self.target.set(alpha, kappa, sigma)

        # vectorized step
        m, C, sigma, info = self.step(m, C, sigma, z)

        # vectorized transformation
        alpha, kappa, sigma_normal, transformation_parameters = self.transformation.transform_to_normal(m, C, sigma)

        # prepare data for the return statement
        raw_state = {"m": m, "C": C, "sigma": sigma}
        normal_form = {"alpha": alpha, "kappa": kappa, "sigma": sigma_normal}
        misc_parameters = {}

        return normal_form, raw_state, transformation_parameters, misc_parameters


class OnePlusOne_CMA_ES:
    m = None

    def __init__(self, target, transformation, constants):
        # make the target function available
        self.target = target

        self.transformation = transformation

        # constants
        self.d = constants["d"]  # 1 + self.dim / 2
        self.p_target = constants["p_target"]  # 2 / 11
        self.c_cov = constants["c_cov"]  # 2 / (np.power(self.dim, 2) + 6)

    def step(self, m, C, sigma, z=None):
        if z is None:
            # create standard normal samples and transform them
            z = np.array([np.random.standard_normal(m.shape[0]), np.random.standard_normal(m.shape[0])]).T

        # this is equivalent to Az in the normal form, as the matrix C is diagonal,
        # therefore the matrix A (with AA = C) is [[sqrt(C_00), 0][0, sqrt(C_11)]]
        # for higher dimensions possibly use (untested): sigma * np.sqrt(np.diagonal(C, axis1=1, axis2=2))
        sigma_A = np.array([sigma * np.sqrt(C[:, 0, 0]), sigma * np.sqrt(C[:, 1, 1])]).T
        x = m + z * sigma_A

        # evaluate samples
        fx = self.target.eval(x)
        success = (fx <= 1).astype(np.float64)  # This works because on the sphere in the normal form f(m)=1

        # calculate new m, new sigma and new C
        new_m = np.where(success[:, None], x, m)
        new_sigma = sigma * np.exp((1 / self.d) * ((success - self.p_target) / (1 - self.p_target))).reshape(
            sigma.shape[0])
        unsuccessful = ((1 - success.reshape(success.shape[0])[:, np.newaxis, np.newaxis]) * C)
        s = np.array([z[:, 0] * np.sqrt(C[:, 0, 0]), z[:, 1] * np.sqrt(C[:, 1, 1])]).T
        successful = (success.reshape(success.shape[0])[:, np.newaxis, np.newaxis]) * (
                np.array((1 - self.c_cov)) * C + np.array(self.c_cov) * np.einsum("ij,ik->ijk", s, s))
        new_C = successful + unsuccessful

        return new_m, new_C, new_sigma, {"success": success}

    def iterate(self, alpha, kappa, sigma, num=1):
        # Sanitize, transform and expand the parameters
        m, C, sigma = self.transformation.transform_to_parameters(alpha, kappa, sigma, num)

        # create the random samples
        z = np.array([np.random.standard_normal(m.shape[0]), np.random.standard_normal(m.shape[0])]).T

        # vectorized step

        m, C, sigma, info = self.step(m, C, sigma, z)
        # vectorized transformation
        alpha, kappa, sigma_normal, transformation_parameters = self.transformation.transform_to_normal(m, C, sigma)

        # prepare data for the return statement
        raw_state = {"m": m, "C": C, "sigma": sigma}
        normal_form = {"alpha": alpha, "kappa": kappa, "sigma": sigma_normal}
        misc_parameters = {"success": info["success"]}

        return normal_form, raw_state, transformation_parameters, misc_parameters
