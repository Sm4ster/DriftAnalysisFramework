import numpy as np

from DriftAnalysisFramework.Optimization import CMA_ES
from DriftAnalysisFramework.Transformation import CMA_ES as TR
from DriftAnalysisFramework.Fitness import Sphere

from alive_progress import alive_bar

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('Qt5Agg')

# Globals
groove_iteration = 5000
measured_samples = 10000

alpha_sequence = np.linspace(0, np.pi / 4, num=10)
kappa_sequence = np.geomspace(1 / 1000, 1000, num=25)
sigma_sequence = np.geomspace(1 / 1000, 10000, num=25)

alg = CMA_ES(Sphere(), {
    "d": 2,
    "p_target": 0.1818,
    "c_p": 0.8333,
    "c_cov": 0.2,
    "dim": 2
})

# plotting
fig, (ax1, ax2) = plt.subplots(2)
fig.suptitle('CMA Parameter Analysis')
fig.text(0.50, 0.95, f'Groove iterations - {groove_iteration}, measured samples - {measured_samples}',
         horizontalalignment='center', wrap=True, fontsize='small')

# stable kappa experiment
print("Stable Kappa Experiment")

alpha, kappa, sigma = np.repeat(alpha_sequence, sigma_sequence.shape[0]), 1, np.tile(sigma_sequence, alpha_sequence.shape[0])
m, C, sigma = TR.transform_to_parameters(alpha, kappa, sigma)

with alive_bar(groove_iteration, force_tty=True, title="Grooving", bar="notes", title_length=10) as bar:
    for i in range(groove_iteration):
        C = alg.step(m, C, sigma)[1]
        bar()

kappa_store = np.empty([measured_samples, alpha_sequence.shape[0] * sigma_sequence.shape[0]])
with alive_bar(measured_samples, force_tty=True, title="Collecting") as bar:
    for i in range(measured_samples):
        C = alg.step(m, C, sigma)[1]
        kappa = TR.transform_to_normal(m, C, sigma)[1]
        kappa_store[i] = kappa
        bar()

# store the data in an efficient form to allow for interpolation later
stable_kappa_data = np.mean(kappa_store, axis=0).reshape(alpha_sequence.shape[0], sigma_sequence.shape[0])

# stable sigma experiment
print("Stable Sigma Experiment")

# prepare algorithm inputs
alpha, kappa, sigma = np.repeat(alpha_sequence, kappa_sequence.shape[0]), np.tile(kappa_sequence, alpha_sequence.shape[0]), 1
m, C, sigma = TR.transform_to_parameters(alpha, kappa, sigma)

with alive_bar(groove_iteration, force_tty=True, title="Grooving", bar="notes", title_length=10) as bar:
    for i in range(groove_iteration):
        sigma = alg.step(m, C, sigma)[2]
        bar()

sigma_store = np.empty([measured_samples, alpha_sequence.shape[0] * kappa_sequence.shape[0]])
with alive_bar(measured_samples, force_tty=True, title="Collecting") as bar:
    for i in range(measured_samples):
        sigma = alg.step(m, C, sigma)[2]
        sigma_store[i] = sigma
        bar()

# store the data in an efficient form to allow for interpolation later
stable_sigma_data = np.mean(sigma_store, axis=0).reshape(alpha_sequence.shape[0], kappa_sequence.shape[0])

# Save variables into a file
np.savez('./data/stable_parameters.npz', alpha=alpha_sequence, kappa=kappa_sequence, sigma=sigma_sequence,
         stable_kappa=stable_kappa_data, stable_sigma=stable_sigma_data)

# Plot the results
for alpha_index in range(alpha_sequence.shape[0]):
    ax1.loglog(sigma_sequence, stable_kappa_data[alpha_index])
    ax2.loglog(kappa_sequence, stable_sigma_data[alpha_index])

ax1.set_title('Stable Kappa Experiment', fontsize='small', loc='left')
ax1.set_xlabel(r'$\sigma$')
ax1.set_ylabel(r'$\kappa^*$')

ax2.set_title('Stable Sigma Experiment', fontsize='small', loc='left')
ax2.set_xlabel(r'$\kappa$')
ax2.set_ylabel(r'$\sigma^*$')

plt.subplots_adjust(bottom=0.1, hspace=0.4)
plt.show()