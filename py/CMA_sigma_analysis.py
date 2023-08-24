import numpy as np

from DriftAnalysisFramework.Optimization import CMA_ES
from DriftAnalysisFramework.Transformation import CMA_ES as TR
from DriftAnalysisFramework.Fitness import Sphere

from alive_progress import alive_bar

# Globals
groove_iteration = 5000
measured_samples = 1000000

alpha_sequence = np.linspace(0, np.pi / 4, num=64)
kappa_sequence = np.geomspace(1 / 20, 20, num=256)

alg = CMA_ES(Sphere(), {
    "d": 2,
    "p_target": 0.1818,
    "c_p": 0.8333,
    "c_cov": 0.2,
    "dim": 2
})

# stable sigma experiment
print("Stable Sigma Experiment")

# prepare algorithm inputs
alpha, kappa, sigma = np.repeat(alpha_sequence, kappa_sequence.shape[0]), np.tile(kappa_sequence,
                                                                                  alpha_sequence.shape[0]), 1
m, C, sigma = TR.transform_to_parameters(alpha, kappa, sigma)

with alive_bar(groove_iteration, force_tty=True, title="Grooving", bar="notes", title_length=10) as bar:
    for i in range(groove_iteration):
        sigma = alg.step(m, C, sigma)[2]
        bar()

sigma_store = np.empty([alpha_sequence.shape[0] * kappa_sequence.shape[0]])
with alive_bar(measured_samples, force_tty=True, title="Collecting") as bar:
    for i in range(measured_samples):
        sigma = alg.step(m, C, sigma)[2]
        sigma_store += sigma
        bar()

# store the data in an efficient form to allow for interpolation later
stable_sigma_data = (sigma_store / measured_samples).reshape(alpha_sequence.shape[0], kappa_sequence.shape[0])

# Run data
filename = "./data/stable_sigma.txt"

# Write the array of strings into the file
with open(filename, 'w') as f:
    f.write('./data/stable_sigma.npz\n')
    f.write(str(measured_samples) + '\n')
    f.write(str(groove_iteration) + '\n')


# Save variables into a file
np.savez('./data/stable_sigma.npz',
         alpha=alpha_sequence, kappa=kappa_sequence,
         stable_sigma=stable_sigma_data
         )
