from DriftAnalysisFramework.Optimization import CMA_ES
from DriftAnalysisFramework.Fitness import Sphere
from DriftAnalysisFramework.Transformation import CMA_ES as CMA_TR
from alive_progress import alive_bar
import numpy as np

transformation = CMA_TR("trace")

alg = CMA_ES(
    Sphere(),
    transformation,
    {
        "c_mu": 0.1
    }
)

# get parameters from algorithm
lamda = alg.lamda
mu = alg.mu
c_mu = alg.c_mu
weights = alg.weights
mu_eff = alg.mu_eff


# implementation of the unvectorized algorithm for comparison
def CMA_ES_uv(m, C, sigma, z):
    A = np.array([[np.sqrt(C[0, 0]), 0], [0, np.sqrt(C[1, 1])]])

    y = np.zeros([lamda, 2])
    x = np.zeros([lamda, 2])
    for i in range(lamda):
        # y = Az
        y[i] = A @ z[i]

        # x = m + sigma Az
        x[i] = m + sigma * y[i]

    x_sorted = x[np.argsort(np.linalg.norm(x, axis=1))]
    y_sorted = y[np.argsort(np.linalg.norm(x, axis=1))]
    z_sorted = z[np.argsort(np.linalg.norm(x, axis=1))]

    new_m = 0
    for i in range(mu):
        new_m += weights[i] * x_sorted[i]

    z_w_sum = 0
    for i in range(mu):
        z_w_sum += weights[i] * z_sorted[i]
    new_sigma = sigma * np.exp(
        0.5 *
        (
                (np.sqrt(mu_eff) * np.linalg.norm(z_w_sum) / np.sqrt(2 * np.pi)) - 1
        )
    )

    # C = (1-c_cov) * C + c_cov \sum w_i * Az_i * (Az_i)^T
    y_outer_product_w = np.zeros([2, 2])
    for i in range(mu):
        y_outer_product_w += weights[i] * np.outer(y_sorted[i], y_sorted[i])
    new_C = (1 - c_mu) * C + c_mu * y_outer_product_w

    return new_m, new_C, new_sigma


# create states
alpha_sequence = np.linspace(0, 1.5707963267948966, 16)
kappa_sequence = np.geomspace(1, 10000, 16)
sigma_sequence = np.geomspace(0.001, 1000, 16)

states = np.vstack(np.meshgrid(
    alpha_sequence,
    kappa_sequence,
    sigma_sequence,
    indexing='ij')).reshape(3, -1).T

alpha, kappa, sigma = states[:, 0], states[:, 1], states[:, 2]

# transform to normal form
m, C, sigma = transformation.transform_to_parameters(alpha, kappa, sigma)

# Create randomness for a step
z = np.random.randn(m.shape[0], lamda, 2)
# z = np.array([[[0.1, 0.1],[0.1,-0.1],[-0.25,-0.15],[0.15,-0.05],[-0.1,-0.025],[-0.15,0.15]]])


# Make an algorithm step
m_v, C_v, sigma_v, _ = alg.step(m, C, sigma, z)

with alive_bar(states.shape[0], force_tty=True, title="ToParameters") as bar:
    for i in range(states.shape[0]):
        m_uv, C_uv, sigma_uv = CMA_ES_uv(m[i], C[i], sigma[i], z[i])

        tolerance = 1e-10
        if not np.isclose(m_uv, m_v[i], atol=tolerance).all():
            raise Exception("m:", m_uv, m_v[i], np.linalg.norm(m_uv), np.linalg.norm(m_v))
        if not np.isclose(C_uv, C_v[i], atol=tolerance).all():
            raise Exception("C:", C_uv, C_v[i])
        if not np.isclose(sigma_uv, sigma_v[i], atol=tolerance):
            raise Exception("sigma:", sigma_uv, sigma_v[i])

        bar()

print("All tests passed")
