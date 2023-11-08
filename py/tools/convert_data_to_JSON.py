import numpy as np
import json

drift_data = np.load('../data/real_run_3.npz')

alpha_sequence = drift_data['alpha']
kappa_sequence = drift_data['kappa']
sigma_sequence = drift_data['sigma']

states = drift_data['states']
drifts_raw = drift_data['drifts']

drifts = drifts_raw.reshape(len(alpha_sequence), len(kappa_sequence), len(sigma_sequence))

file1 = open('../data/real_run_3.txt', 'r')
lines = file1.readlines()

print(lines[1])

# Closing files
file1.close()

data = {
    'potential_function': lines[1],
    'sequences': [
        {'name': 'alpha', 'sequence': alpha_sequence.tolist()},
        {'name': 'kappa', 'sequence': kappa_sequence.tolist()},
        {'name': 'sigma', 'sequence': sigma_sequence.tolist()}
    ],
    'drifts': drifts.tolist(),
}

with open('data.json', 'w') as f:
    json.dump(data, f)
