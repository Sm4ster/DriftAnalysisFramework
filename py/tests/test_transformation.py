import numpy as np
from DriftAnalysisFramework.Transformation import CMA_ES as TR
from alive_progress import alive_bar


def transform_to_parameters_unvectorized(alpha, kappa, sigma):
    # create m from alpha
    m = np.array([np.cos(alpha), np.sin(alpha)])

    # create C from kappa
    C = np.zeros((2, 2), dtype=float)
    C[0, 0] = kappa
    C[1, 1] = (1 / kappa)

    return m, C, sigma


def transform_to_normal_unvectorized(m, C, sigma):
    # get the the transformation matrix
    a, A = np.linalg.eigh(C)

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

    if C_normal[0][0] < 1:
        C_normal = axis_swap @ C_normal @ axis_swap.T
        m_normal = axis_swap @ m_normal

    return np.arccos(m_normal[0]), C_normal[0, 0], sigma_normal, {"scaling_factor": scaling_factor,
                                                                  "distance_factor": distance_factor}


# create states
alpha_sequence = np.linspace(0, np.pi/2, num=10)
kappa_sequence = np.geomspace(1, 10, num=20)
sigma_sequence = np.geomspace(1 / 10, 10, num=20)

# Transform the individual states to an array we can evaluate vectorized
states = np.vstack(np.meshgrid(alpha_sequence, kappa_sequence, sigma_sequence, indexing='ij')).reshape(3, -1).T
alpha, kappa, sigma = states[:, 0], states[:, 1], states[:, 2]

# Test the transformation to parameters
m_v, C_v, sigma_raw_v = TR.transform_to_parameters(alpha, kappa, sigma)
assert (
        states.shape[0] == alpha.shape[0] == kappa.shape[0] == sigma.shape[0] ==
        m_v.shape[0] == C_v.shape[0] == sigma_raw_v.shape[0]
)

with alive_bar(states.shape[0], force_tty=True, title="ToParameters") as bar:
    for i in range(states.shape[0]):
        m_uv, C_uv, sigma_raw_uv = transform_to_parameters_unvectorized(alpha[i], kappa[i], sigma[i])

        tolerance = 1e-10
        if not np.isclose(m_uv, m_v[i], atol=tolerance).all():
            raise Exception("m:", m_uv, m_v[i])
        if not np.isclose(C_uv, C_v[i], atol=tolerance).all():
            raise Exception("C:", C_uv, C_v[i])
        if not np.isclose(sigma_raw_uv, sigma_raw_v[i], atol=tolerance):
            raise Exception("sigma:", sigma_raw_uv, sigma_raw_v[i])

        bar()

# Test transformation to normal form
alpha_v, kappa_v, sigma_v, _ = TR.transform_to_normal(m_v, C_v, sigma_raw_v)
assert (
        states.shape[0] == alpha_v.shape[0] == kappa_v.shape[0] == sigma_v.shape[0] ==
        m_v.shape[0] == C_v.shape[0] == sigma_raw_v.shape[0]
)

with alive_bar(states.shape[0], force_tty=True, title="ToNormal") as bar:
    for i in range(states.shape[0]):
        alpha_uv, kappa_uv, sigma_uv, _ = transform_to_normal_unvectorized(m_v[i], C_v[i], sigma_raw_v[i], normal_form=1)

        tolerance = 1e-10
        if not (
                np.isclose(alpha_uv, alpha[i], atol=tolerance).all() and
                np.isclose(alpha_v[i], alpha[i], atol=tolerance).all()
        ):
            raise Exception("alpha:", alpha_uv, alpha_v[i], alpha[i])
        if not (
                np.isclose(kappa_uv, kappa[i], atol=tolerance).all() and
                np.isclose(kappa_v[i], kappa[i], atol=tolerance).all()
        ):
            raise Exception("kappa:", kappa_uv, kappa_v[i], kappa[i])
        if not (
                np.isclose(sigma_uv, sigma[i], atol=tolerance) and
                np.isclose(sigma_v[i], sigma[i], atol=tolerance)
        ):
            raise Exception("sigma:", sigma_uv, sigma_v[i], sigma[i])
        bar()

print("All tests passed")

# print("truth: ", alpha[i], kappa[i], sigma[i])
# print("inputs", m_v[i], C_v[i], sigma_raw_v[i])
# print("unvectorized: ", alpha_uv, kappa_uv, sigma_uv),
# print("vectorized: ", alpha_v[i], kappa_v[i], sigma_v[i]),
