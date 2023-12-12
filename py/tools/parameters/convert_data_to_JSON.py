import numpy as np
import json

# Initialize stable_sigma and stable_kappa
kappa_data = np.load('../../data/stable_kappa.npz')
sigma_data = np.load('../../data/stable_sigma.npz')

kappa_file = open('../../data/stable_kappa.txt', 'r')
sigma_file = open('../../data/stable_sigma.txt', 'r')

alpha_sequence_kappa = kappa_data['alpha']
alpha_sequence_sigma = sigma_data['alpha']

kappa_sequence = sigma_data['kappa']
sigma_sequence = kappa_data['sigma']

stable_kappa_data = kappa_data['stable_kappa']
stable_sigma_data = sigma_data['stable_sigma']


kappa_lines = kappa_file.readlines()
sigma_lines = sigma_file.readlines()

kappa_file.close()
sigma_file.close()

kappa_data = {
    'iterations': int(kappa_lines[1].strip("\n")),
    'groove_iterations': int(kappa_lines[2].strip("\n")),
    'sequences': [
        {'name': 'alpha', 'sequence': alpha_sequence_kappa.tolist()},
        {'name': 'sigma', 'sequence': sigma_sequence.tolist()},
    ],
    'values': stable_kappa_data.tolist(),
}

sigma_data = {
    'iterations': int(sigma_lines[1].strip("\n")),
    'groove_iterations': int(sigma_lines[2].strip("\n")),
    'sequences': [
        {'name': 'alpha', 'sequence': alpha_sequence_sigma.tolist()},
        {'name': 'kappa', 'sequence': kappa_sequence.tolist()}
    ],
    'values': stable_sigma_data.tolist(),
}

with open('../../data/stable_kappa.json', 'w') as f:
    json.dump(kappa_data, f)

with open('../../data/stable_sigma.json', 'w') as f:
    json.dump(sigma_data, f)