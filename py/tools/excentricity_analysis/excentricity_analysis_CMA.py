from DriftAnalysisFramework.OptimizationAlgorithms import CMA_ES
from DriftAnalysisFramework.TargetFunctions import Sphere
import numpy as np
import timeit

# Globals
alpha_samples = 500
sigma_samples = 500

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


def transform_state_to_normal_form(self, m, C, sigma):
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



def iterate(alpha, sigma, kappa):
    # create m and C from alpha and kappa
    m = np.array([np.cos(alpha), np.sin(alpha)]).T

    C = np.empty((len(kappa), 2, 2), dtype=float)
    C[:, 0, 0] = sigma * kappa
    C[:, 1, 1] = sigma * (1 / kappa)


    # create standard normal samples and transform them
    z = np.random.standard_normal(m.shape)
    x = m + z * np.vstack([sigma * np.sqrt(kappa), sigma * np.sqrt(1 / kappa)]).T

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

    # TODO vectorize the transformation to normal form

    # extract alpha and kappa from new_m and new_C
    return np.arccos(new_m.T[0]), new_sigma, new_C[:,0,0]


results = np.zeros(states.shape[1], dtype='float64')
for iteration in range(alg_iterations):
    states[2] = iterate(states[0], states[1], states[2])[2]
    print(iteration)
    if iteration % 1 == 0: print(iteration)
    if iteration > cutoff:
        results += states[2]

results = results / (alg_iterations - cutoff)
