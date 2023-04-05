from DriftAnalysisFramework.OptimizationAlgorithms import CMA_ES
from DriftAnalysisFramework.TargetFunctions import Sphere
import numpy as np
# from performance.performance import perf
import time

# Globals
alpha_samples = 500
sigma_samples = 5000

max_sigma = 2
alpha_sequence = np.linspace(5, 7, num=alpha_samples)
sigma_sequence = np.linspace(1, 2, num=sigma_samples)
alg_iterations = 100000
cutoff = 20000

dimension = 2

states = np.array([np.repeat(alpha_sequence, sigma_samples), np.tile(sigma_sequence, alpha_samples),
                   alpha_samples * sigma_samples * [4]])

d = 2
p_target = 0.1818
c_p = 0.8333
c_cov = 0.2
dim = 2


def transform_to_normal_unvectorized(m, C, sigma):
    # get the the transformation matrix
    A = np.linalg.eigh(C)[1]

    # rotate the coordinate system such that the eigenvalues of
    # the covariance matrix are parallel to the coordinate axis
    C_rot = A.T @ C @ A
    m_rot = A.T @ m

    # calculate the scaling factor which brings the covariance matrix to det = 1
    scaling_factor = 1 / (np.sqrt(np.linalg.det(C_rot)))

    m_normal = np.dot(m_rot, scaling_factor)
    C_normal = np.dot(C_rot, scaling_factor)

    print("\nSingle C_normal\n", C_normal)
    # print("\nSingle m_normal\n", m_normal)

    # The distance factor sets norm(m) = 1. To keep the proportion between the distance
    # of the center to the optimum and the spread of the distribution we adjust sigma.
    distance_factor = 1 / np.linalg.norm(m_normal)

    m_normal = m_normal * distance_factor
    sigma_normal = sigma * distance_factor

    # We transform m to (cos, sin)
    x_flip = np.array([[-1, 0], [0, 1]])
    y_flip = np.array([[1, 0], [0, -1]])
    axis_swap = np.array([[0, 1], [1, 0]])

    if m_normal[0] < 0:
        C_normal = x_flip @ C_normal @ x_flip.T
        m_normal = x_flip @ m_normal

    if m_normal[1] < 0:
        C_normal = y_flip @ C_normal @ y_flip.T
        m_normal = y_flip @ m_normal

    if m_normal[0] < np.cos(np.pi / 4):
        C_normal = axis_swap @ C_normal @ axis_swap.T
        m_normal = axis_swap @ m_normal

    return m_normal, C_normal, sigma_normal, scaling_factor, distance_factor


def transform_to_normal_vectorized(m, C, sigma):
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
    C_normal = np.einsum('i,ijk->ijk', scaling_factor, C_rot) # np.dot(C_rot, scaling_factor, axis=1)

    print("\nAll C_normal\n", C_normal)
    # print("\nAll m_normal\n", m_normal)
    # print("\nAll scaling_factors\n", scaling_factor)

    # The distance factor sets norm(m) = 1. To keep the proportion between the distance
    # of the center to the optimum and the spread of the distribution we adjust sigma.
    distance_factor = 1 / np.linalg.norm(m_normal)

    m_normal = m_normal * distance_factor
    sigma_normal = sigma * distance_factor

    # We transform m to (cos, sin)
    x_flip = np.array([[-1, 0], [0, 1]])
    y_flip = np.array([[1, 0], [0, -1]])
    axis_swap = np.array([[0, 1], [1, 0]])

    if m_normal[0] < 0:
        C_normal = x_flip @ C_normal @ x_flip.T
        m_normal = x_flip @ m_normal

    if m_normal[1] < 0:
        C_normal = y_flip @ C_normal @ y_flip.T
        m_normal = y_flip @ m_normal

    if m_normal[0] < np.cos(np.pi / 4):
        C_normal = axis_swap @ C_normal @ axis_swap.T
        m_normal = axis_swap @ m_normal

    return m_normal, C_normal, sigma_normal, scaling_factor, distance_factor


def step_vectorized(m, C, sigma, z=None):
    if z is None:
        # create standard normal samples and transform them
        z = np.random.standard_normal(m.shape)

    # this is equivalent to Az in the normal form, as the matrix C is diagonal,
    # therefore matrix A (with AA = C) is [[sqrt(C_00), 0][0, sqrt(C_11)]]
    sigma_A = np.array([sigma * np.sqrt(C[:, 0, 0]), sigma * np.sqrt(C[:, 1, 1])]).T
    x = m + z * sigma_A

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

    return new_m, new_C, new_sigma


def step_unvectorized(m, C, sigma, z=None):
    m_t, sigma_t, cov_m = m, sigma, C

    if z is None:
        # step 1: draw random sample
        z = np.random.multivariate_normal(np.zeros(dim), cov_m)

    # A = np.linalg.cholesky(C) in the general case
    A = np.sqrt(C)
    x_t = m_t + sigma_t * A @ z

    # step 2: update parameters
    if np.linalg.norm(x_t) <= 1:  # np.linalg.norm(m_t) in the general case
        # a) Let x <- y
        m_t = x_t
        # b) update the success probability
        p_succ = 1  # (1 - self.c_p) * p_succ + self.c_p
        # c) omitted
        # d) update the covariance matrix as in equation (1) without search paths
        cov_m = (1 - c_cov) * cov_m + c_cov * np.outer(z, z)

    # Otherwise update the success probability
    else:
        p_succ = 0  # (1 - self.c_p) * p_succ

    # step 3: update the global step size
    sigma_t = sigma_t * np.exp((1 / d) * ((p_succ - p_target) / (1 - p_target)))

    return m_t, cov_m, sigma_t


def iterate_normal(alpha, sigma, kappa, num=1000):
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
    start_time = time.perf_counter()
    states_vectorized = step_vectorized(m, C, sigma, z)
    end_time = time.perf_counter()
    execution_time_vec = end_time - start_time
    # print(f"The execution time of the vectorized iteration is: {execution_time_vec}")

    # unvectorized step
    start_time = time.perf_counter()
    states_unvectorized = (np.empty([z.shape[0], 2]), np.empty([z.shape[0], 2, 2]), np.empty([z.shape[0]]))
    for i in range(z.shape[0]):
        states_unvectorized[0][i], states_unvectorized[1][i], states_unvectorized[2][i] = step_unvectorized(m[i], C[i],
                                                                                                            sigma[i],
                                                                                                            z[i])
    end_time = time.perf_counter()
    execution_time_unvec = end_time - start_time
    # print(f"The execution time of the unvectorized iteration is: {execution_time_unvec}")

    # print(f"Performance gain: {execution_time_unvec / execution_time_vec}")

    print(states_vectorized, "\n", states_unvectorized, "\n",
          np.array_equal(states_vectorized[0], states_unvectorized[0]),
          np.array_equal(states_vectorized[1], states_unvectorized[1]),
          np.array_equal(states_vectorized[2], states_unvectorized[2])
          )

    # unvectorized transformation
    start_time = time.perf_counter()
    normal_states_unvectorized = [np.empty([z.shape[0], 2]), np.empty([z.shape[0], 2, 2]), np.empty([z.shape[0]])]
    for i in range(z.shape[0]):
        normal_states_unvectorized[0][i], normal_states_unvectorized[1][i], normal_states_unvectorized[2][
            i] = transform_to_normal_unvectorized(states_unvectorized[0][i], states_unvectorized[1][i],
                                                  states_unvectorized[2][i])[:3]
    end_time = time.perf_counter()
    execution_time_unvec = end_time - start_time
    print(f"The execution time of the unvectorized transformation is: {execution_time_unvec}")

    # vectorized transformation
    start_time = time.perf_counter()
    normal_states_vectorized = transform_to_normal_vectorized(states_vectorized[0], states_vectorized[1],
                                                              states_vectorized[2])[:3]
    end_time = time.perf_counter()
    execution_time_vec = end_time - start_time
    print(f"The execution time of the unvectorized transformation is: {execution_time_vec}")

    # extract alpha and kappa from new_m and new_C
    # return np.arccos(new_m.T[0]), new_sigma, new_C[:,0,0]


num = 5
iterate_normal(np.linspace(1, 3, num=num), np.linspace(0.3, 0.5, num=num), np.linspace(1, 5, num=num))
