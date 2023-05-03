from DriftAnalysisFramework.OptimizationAlgorithms import CMA_ES
from DriftAnalysisFramework.TargetFunctions import Sphere
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from alive_progress import alive_bar

matplotlib.use('Qt5Agg')


# Globals
groove_iteration = 10000
measured_samples = 10000

alpha_samples = 1
kappa_samples = 500
sigma_samples = 500

alpha_sequence = np.linspace(0, np.pi / 4, num=alpha_samples)
kappa_sequence = np.geomspace(1 / 10000, 100000, num=kappa_samples)
sigma_sequence = np.linspace(1 / 5, 5, num=sigma_samples)
print(alpha_sequence)
alg = CMA_ES(Sphere(2), {
    "d": 2,
    "p_target": 0.1818,
    "c_p": 0.8333,
    "c_cov": 0.2,
    "dim": 2
})

# stable alpha experiment
# print("Starting the alpha experiment...")
#
# alpha, kappa, sigma = 1, np.repeat(kappa_sequence, sigma_samples), np.tile(sigma_sequence, kappa_samples)
# alpha_store = np.empty([measured_samples, kappa_samples * sigma_samples])
#
# with alive_bar(groove_iteration, force_tty=True, title="Grooving", bar="notes", title_length=10) as bar:
#     for i in range(groove_iteration):
#         alpha = alg.iterate_normal(alpha, kappa, sigma)[0]
#         bar()
#
# with alive_bar(measured_samples, force_tty=True, title="Collecting") as bar:
#     for i in range(measured_samples):
#         alpha = alg.iterate_normal(alpha, kappa, sigma)[0]
#         print(alg.iterate_normal(alpha, kappa, sigma)[0])
#         alpha_store[i] = alpha
#         bar()
#
# print(alpha_store)

# # stable kappa experiment
# alpha, kappa, sigma = np.repeat(alpha_sequence, sigma_samples), 1, np.tile(sigma_sequence, alpha_samples)
# kappa_store = np.array([measured_samples, alpha_samples * sigma_samples])
#
# for i in range(groove_iteration):
#     print(i)
#     kappa = alg.iterate_normal(alpha, kappa, sigma)[1]
#
# print("cutoff")
# for i in range(measured_samples):
#     print(i)
#     kappa = alg.iterate_normal(alpha, kappa, sigma)[1]
#     kappa_store[i] = kappa

# stable sigma experiment
alpha, kappa, sigma = np.repeat(alpha_sequence, kappa_samples), np.tile(kappa_sequence, alpha_samples), 1
sigma_store = np.empty([measured_samples, alpha_samples * kappa_samples])

with alive_bar(groove_iteration, force_tty=True, title="Grooving", bar="notes", title_length=10) as bar:
    for i in range(groove_iteration):
        sigma = alg.iterate(alpha, kappa, sigma, transform_normal=False)[2]
        bar()


with alive_bar(measured_samples, force_tty=True, title="Collecting") as bar:
    for i in range(measured_samples):
        sigma = alg.iterate(alpha, kappa, sigma, transform_normal=False)[2]
        sigma_store[i] = sigma
        bar()

plt.loglog(kappa_sequence, np.mean(sigma_store, axis=0))
plt.show()
