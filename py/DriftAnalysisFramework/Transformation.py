import numpy as np


class CMA_ES:
    @staticmethod
    def transform_to_parameters(alpha, kappa, sigma, num=1):
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
        C[:, 0, 0] = kappa
        C[:, 1, 1] = (1 / kappa)

        return m, C, sigma

    @staticmethod
    def transform_to_normal(m, C, sigma, normal_form=1):
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
            swap = (C_normal[:, 0, 0] < 1).astype(np.float64)

        # axis swap of C_normal (with condition)
        C_normal[:, 0, 0], C_normal[:, 1, 1] = C_normal[:, 1, 1] * swap + C_normal[:, 0, 0] * (
                np.array([1]) - swap), C_normal[:, 0, 0] * swap + C_normal[:, 1, 1] * (np.array([1]) - swap)

        # axis swap of m_normal (with condition)
        m_normal[:, 0], m_normal[:, 1] = m_normal[:, 1] * swap + m_normal[:, 0] * (
                np.array([1]) - swap), m_normal[:, 0] * swap + m_normal[:, 1] * (np.array([1]) - swap)

        return np.arccos(m_normal[:, 0]), C_normal[:, 0, 0], sigma_normal, {"scaling_factor": scaling_factor,
                                                                            "distance_factor": distance_factor}
