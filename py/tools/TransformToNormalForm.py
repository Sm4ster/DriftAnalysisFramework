import numpy as np
from worker_module import analyze_step_size
from DriftAnalysisFramework.OptimizationAlgorithms import CMA_ES
from DriftAnalysisFramework.TargetFunctions import Sphere

alpha = 359 * np.pi / 180
distance = 5

# set arbitrary C and m
C = np.array([[1 / 8, -5 / (8 * np.sqrt(3))], [-5 / (8 * np.sqrt(3)), 11 / 8]])
m = [distance * np.sin(alpha), distance * np.cos(alpha)]
sigma = .5

target = Sphere(2)
algorithm = CMA_ES(
    target,
    {
        "d": 2,
        "p_target": 0.1818,
        "c_cov": 0.2,
        "c_p": 0.8333,
        "alpha": 2
    }
)

# get the the transformation matrix
A = np.linalg.eig(C)[1]

# rotate the coordinate system such that
C_rot = A.T @ C @ A
m_rot = A.T @ m

# calculate the scaling factor which brings the covariance matrix to det = 1
scaling_factor = 1 / (np.sqrt(np.linalg.det(C_rot)))

m_normal = np.dot(m_rot, scaling_factor)
C_normal = np.dot(C_rot, scaling_factor)

# The distance factor is actually not part the of the transformation but is just
# used to bring m to the normal form. In the real transformation this would be
# done by also changing sigma (which is the scaling for the covariance matrix)
# In this case sigma is meaningless which is why we do not even bother. However,
# the distance is important for the stable sigma. The proportion of m and C
# is significant while both need to be det(c) = norm(m) = 1. As the stable sigma
# and the norm(m) scale linear with each other we just change m to be of unit
# length and add the distance scaling to the final stable sigma.
distance_factor = 1 / np.linalg.norm(m_normal)

m_normal = m_normal * distance_factor
sigma_normal = sigma * distance_factor

print(np.linalg.det(C_normal))

x_flip = np.array([[-1, 0], [0, 1]])
y_flip = np.array([[1, 0], [0, -1]])
axis_swap = np.array([[0, 1], [1, 0]])

if m_normal[0] < 0:
    C_normal = x_flip @ C_normal @ x_flip.T
    m_normal = x_flip @ m_normal

if m_normal[1] < 0:
    C_normal = y_flip @ C_normal @ y_flip.T
    m_normal = y_flip @ m_normal

if m_normal[0] < np.pi / 4 and m_normal[1] > np.pi / 4:
    C_normal = axis_swap @ C_normal @ axis_swap.T
    m_normal = axis_swap @ m_normal

print(m_normal)

algorithm.set_location(m_normal)
sigma_star_1 = analyze_step_size({"sigma": sigma_normal, "cov_m": C_normal}, algorithm,
                                 {"alg_iterations": 100000, "cutoff": 20000})

algorithm.set_location(m)
sigma_star_2 = analyze_step_size({"sigma": sigma, "cov_m": C}, algorithm,
                                 {"alg_iterations": 100000, "cutoff": 20000})

print((sigma_star_1[0] / np.sqrt(scaling_factor)) / distance_factor, sigma_star_2[0])
print(sigma_star_1[0] / (np.sqrt(scaling_factor) * distance_factor), sigma_star_2[0])
