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


def transform_state_to_normal_form(m, C, sigma):
    # get the the transformation matrix
    A = np.linalg.eig(C)[1]

    # rotate the coordinate system such that the eigenvalues of
    # the covariance matrix are parallel to the coordinate axis
    C_rot = A.T @ C @ A
    m_rot = A.T @ m

    # calculate the scaling factor which brings the covariance matrix to det = 1
    scaling_factor = 1 / (np.sqrt(np.linalg.det(C_rot)))

    m_normal = np.dot(m_rot, scaling_factor)
    C_normal = np.dot(C_rot, scaling_factor)

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

    # this is equivalent to Az in the normal form, as the matrix C is diagonal, therefore matrix A (with AA = C) is [[sqrt(C_00), 0][0, sqrt(C_11)]]
    A_sigma = np.array([sigma * np.sqrt(C[:, 0, 0]), sigma * np.sqrt(C[:, 1, 1])]).T
    x = m + z * A_sigma

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
    x_t = m_t + sigma_t * z

    # step 2: update parameters
    if np.linalg.norm(x_t) <= np.linalg.norm(m_t):
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


def iterate_normal(alpha, sigma, kappa, num=10):
    # expand inputs if necessary
    if isinstance(alpha, (int, float)): alpha = np.tile(alpha, num)
    if isinstance(sigma, (int, float)): sigma = np.tile(sigma, num)
    if isinstance(kappa, (int, float)): kappa = np.tile(kappa, num)

    # check if all elements have equal length
    shapes = [alpha.shape[0], sigma.shape[0], kappa.shape[0]]
    if not all(element == shapes[0] for element in shapes):
        raise Exception("")

    # create m from alpha
    m = np.array([np.cos(alpha), np.sin(alpha)]).T

    # create C from kappa
    C = np.empty((num, 2, 2), dtype=float)
    C[:, 0, 0] = kappa
    C[:, 1, 1] = (1 / kappa)

    # create the random samples
    z = np.array([np.random.standard_normal(num), np.random.standard_normal(num)]).T

    # get vectorized steps
    start_time = time.perf_counter()
    step_vectorized(m, C, sigma, z)
    end_time = time.perf_counter()
    execution_time_vec = end_time - start_time
    print(f"The execution time of the vectorized code is: {execution_time_vec}")

    # get unvectorized steps
    start_time = time.perf_counter()
    unvectorized_after_states = []
    for i in range(z.shape[0]):
        unvectorized_after_states.append(step_unvectorized(m[i], C[i], sigma[i], z[i]))
    end_time = time.perf_counter()
    execution_time_unvec = end_time - start_time
    print(f"The execution time of the unvectorized code is: {execution_time_unvec}")

    print(f"Performance gain: {execution_time_unvec / execution_time_vec}")

    # TODO vectorize the transformation to normal form
    print(unvectorized_after_states[0])
    normal_form = transform_state_to_normal_form(*unvectorized_after_states[0])
    print(normal_form)
    normal_form_2 = transform_state_to_normal_form(*normal_form[0:3])
    print(normal_form_2)
    # extract alpha and kappa from new_m and new_C
    # return np.arccos(new_m.T[0]), new_sigma, new_C[:,0,0]


iterate_normal(np.linspace(1, 3, num=100000), np.linspace(3, 5, num=100000), np.linspace(5, 7, num=100000), num=100000)
