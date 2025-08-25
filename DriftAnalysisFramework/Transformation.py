import numpy as np


class CMA_ES:
    def __init__(self, normalization="determinant", sigma_scaling=None):
        self.normalization = normalization
        self.sigma_scaling = sigma_scaling

    def transform_to_parameters(self, alpha, kappa, sigma, num=1):
        # Determine which parameters are arrays and their lengths
        is_array = [isinstance(param, np.ndarray) for param in [alpha, kappa, sigma]]
        array_lengths = [len(param) if is_array[i] else None for i, param in enumerate([alpha, kappa, sigma])]

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
        alpha, kappa, sigma = [np.tile(param, array_length)[:array_length] if not is_array[i] else param
                               for i, param in enumerate([alpha, kappa, sigma])]

        # create m from alpha
        m = np.array([np.cos(alpha), np.sin(alpha)]).T

        # create C from kappa
        C = np.zeros((array_length, 2, 2), dtype=float)

        if self.normalization == "determinant":
            C[:, 0, 0] = kappa
            C[:, 1, 1] = (1 / kappa)

        if self.normalization == "trace": # 2D case
            C[:, 0, 0] = 2 * kappa / (kappa + 1)
            C[:, 1, 1] = 2 / (kappa + 1)

        if self.sigma_scaling == "log1sigma_lower_zdl":
            sigma = sigma * ((1 - 2 * alpha / np.pi) + (2 * alpha / np.pi) * 2 / np.sqrt(kappa + 4))

        return m, C, sigma

    def transform_to_normal(self, m, C, sigma):
        # get the transformation matrix
        eigval, A = np.linalg.eigh(C)

        # rotate the coordinate system such that the eigenvalues of
        # the covariance matrix are parallel to the coordinate axis
        A_T = np.transpose(A, [0, 2, 1])

        C_rot = np.matmul(np.matmul(A_T, C), A)
        m_rot = np.einsum('...ij,...j->...i', A_T, m)

        # make values close to zero equal zero
        C_rot[np.abs(C_rot) < 1e-15] = 0

        # calculate the scaling factor
        scaling_factor = np.ones(C_rot.shape[0])
        if self.normalization == "determinant":
            scaling_factor = np.sqrt(C_rot[:, 0, 0] * C_rot[:, 1, 1])
        if self.normalization == "trace":
            scaling_factor = np.einsum('...ii', C_rot) / 2 # 2D case

        C_normal = np.einsum('i,ijk->ijk', 1 / scaling_factor, C_rot)
        sigma_scaled = sigma * np.sqrt(scaling_factor)

        # The distance factor sets norm(m) = 1. To keep the proportion between the distance
        # of the center to the optimum and the spread of the distribution, we adjust sigma.
        distance_factor = 1 / np.linalg.norm(m_rot, axis=1)

        m_normal = np.einsum('i,ij->ij', distance_factor, m_rot)
        sigma_normal = sigma_scaled * distance_factor

        # conditional x-axis flip
        flip = (m_normal[:, 0] < 0).astype(np.float64)
        m_normal[:, 0] = (np.array([1]) - flip) * m_normal[:, 0] + flip * np.array([-1]) * m_normal[:, 0]

        # conditional y-axis flip
        flip = (m_normal[:, 1] <= 0).astype(np.float64)
        m_normal[:, 1] = (np.array([1]) - flip) * m_normal[:, 1] + flip * np.array([-1]) * m_normal[:, 1]

        # conditional axis swap
        if self.normalization == "determinant":
            swap = (C_normal[:, 0, 0] < 1).astype(np.float64)
        if self.normalization == "trace":
            swap = (C_normal[:, 0, 0] < C_normal[:, 1, 1]).astype(np.float64)


        # axis swap of C_normal (with condition)
        C_normal[:, 0, 0], C_normal[:, 1, 1] = C_normal[:, 1, 1] * swap + C_normal[:, 0, 0] * (
                np.array([1]) - swap), C_normal[:, 0, 0] * swap + C_normal[:, 1, 1] * (np.array([1]) - swap)

        # axis swap of m_normal (with condition)
        m_normal[:, 0], m_normal[:, 1] = m_normal[:, 1] * swap + m_normal[:, 0] * (
                np.array([1]) - swap), m_normal[:, 0] * swap + m_normal[:, 1] * (np.array([1]) - swap)

        if self.normalization == "determinant":
            kappa = C_normal[:, 0, 0]
        if self.normalization == "trace":
            kappa = C_normal[:, 0, 0] / C_normal[:, 1, 1]

        alpha = np.arccos(m_normal[:, 0])

        if self.sigma_scaling == "log1sigma_lower_zdl":
            sigma_normal = sigma_normal / ((1 - 2 * alpha / np.pi) + (2 * alpha / np.pi) * 2 / np.sqrt(kappa + 4))

        return alpha, kappa, sigma_normal, {
            "scaling_factor": scaling_factor,"distance_factor": distance_factor, "C_rot": C_rot, "m_rot": m_rot}
