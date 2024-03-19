import numpy as np
import json

from DriftAnalysisFramework.Optimization import CMA_ES
from DriftAnalysisFramework.Transformation import CMA_ES as TR
from DriftAnalysisFramework.Fitness import Sphere

from alive_progress import alive_bar

# Globals
groove_iteration = 50000
measured_samples = 1000000

alpha_sequence = np.linspace(0, np.pi / 2, num=64)
kappa_sequence = np.geomspace(1, 20, num=256)

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

log_sigma_store = np.zeros([alpha_sequence.shape[0] * kappa_sequence.shape[0]])
success_store = np.zeros([alpha_sequence.shape[0] * kappa_sequence.shape[0]])
with alive_bar(measured_samples, force_tty=True, title="Collecting") as bar:
    for i in range(measured_samples):
        _, _, sigma, success = alg.step(m, C, sigma)
        log_sigma_store += np.log(sigma)
        success_store += success[:, 0]
        bar()

# store the data in an efficient form to allow for interpolation later
stable_sigma_data = np.exp(log_sigma_store / measured_samples).reshape(alpha_sequence.shape[0], kappa_sequence.shape[0])


sigma_data = {
    'iterations': int(measured_samples),
    'groove_iterations': int(groove_iteration),
    'sequences': [
        {'name': 'alpha', 'sequence': alpha_sequence.tolist()},
        {'name': 'kappa', 'sequence': kappa_sequence.tolist()}
    ],
    'values': stable_sigma_data.tolist(),
    'success': success_store.tolist()
}

with open('/home/franksyj/DriftAnalysisFramework/py/data/stable_sigma_new.json', 'w') as f:
    json.dump(sigma_data, f)