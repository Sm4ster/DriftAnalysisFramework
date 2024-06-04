from datetime import datetime
import numpy as np
import json

from DriftAnalysisFramework.Optimization import CMA_ES
from DriftAnalysisFramework.Transformation import CMA_ES as TR
from DriftAnalysisFramework.Fitness import Sphere

from alive_progress import alive_bar

# Globals
groove_iteration = 50000
measured_samples = 5000000

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

# get start time
start_time = datetime.now()

# prepare algorithm inputs
alpha, kappa, sigma = np.repeat(alpha_sequence, kappa_sequence.shape[0]), np.tile(kappa_sequence,
                                                                                  alpha_sequence.shape[0]), 1
m, C, sigma = TR.transform_to_parameters(alpha, kappa, sigma)

with alive_bar(groove_iteration, force_tty=True, title="Grooving", bar="notes", title_length=10) as bar:
    for i in range(groove_iteration):
        new_m, new_C, new_sigma, success = alg.step(m, C, sigma)
        _, _, sigma, factors = TR.transform_to_normal(new_m, new_C, new_sigma)
        sigma /= factors["distance_factor"]
        bar()

log_sigma_store = np.zeros([alpha_sequence.shape[0] * kappa_sequence.shape[0]])
success_store = np.zeros([alpha_sequence.shape[0] * kappa_sequence.shape[0]])
with alive_bar(measured_samples, force_tty=True, title="Collecting") as bar:
    for i in range(measured_samples):
        new_m, new_C, new_sigma, success = alg.step(m, C, sigma)
        _, _, sigma, factors = TR.transform_to_normal(new_m, new_C, new_sigma)
        # sigma /= factors["distance_factor"]
        log_sigma_store += np.log(sigma)
        success_store += success[:, 0]
        bar()

# store the data in an efficient form to allow for interpolation later
stable_sigma_data = np.exp(log_sigma_store / measured_samples).reshape(alpha_sequence.shape[0], kappa_sequence.shape[0])

# get the end time after te run has finished
end_time = datetime.now()

sigma_data = {
    'run_started': start_time.strftime("%d.%m.%Y %H:%M:%S"),
    'run_finished': end_time.strftime("%d.%m.%Y %H:%M:%S"),
    'iterations': int(measured_samples),
    'groove_iterations': int(groove_iteration),
    'sequences': [
        {'name': 'alpha', 'sequence': alpha_sequence.tolist()},
        {'name': 'kappa', 'sequence': kappa_sequence.tolist()}
    ],
    'values': stable_sigma_data.tolist(),
    'success': success_data.tolist()
}

with open('./data/stable_sigma_without_transformation.json', 'w') as f:
    json.dump(sigma_data, f)