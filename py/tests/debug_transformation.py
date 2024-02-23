import numpy as np
from DriftAnalysisFramework.Transformation import CMA_ES as TR


def transform_to_normal_unvectorized(m, C, sigma, normal_form=0):
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

    # make values close to zero equal zero
    C_normal[np.abs(C_normal) < 1e-15] = 0

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
        m_normal = x_flip @ m_normal

    if m_normal[1] < 0:
        m_normal = y_flip @ m_normal

    if (normal_form == 0 and m_normal[0] < np.cos(np.pi / 4)) or (normal_form == 1 and C_normal[1][1] < 1):
        C_normal = axis_swap @ C_normal @ axis_swap.T
        m_normal = axis_swap @ m_normal

    print(C_normal)
    return np.arccos(m_normal[0]), C_normal[0, 0], sigma_normal, {"scaling_factor": scaling_factor,
                                                                  "distance_factor": distance_factor}


m, C, sigma_raw = np.array([[0.70710678, 0.70710678]]), np.array([[[0.1, 0.], [0., 10.]]]), np.array([0.1])
alpha_uv, kappa_uv, sigma_uv, _ = transform_to_normal_unvectorized(m[0], C[0], sigma_raw[0], normal_form=1)
alpha_v, kappa_v, sigma_v, _ = TR.transform_to_normal(m, C, sigma_raw, normal_form=1)

print(alpha_uv, kappa_uv, sigma_uv, alpha_v, kappa_v, sigma_v)
