#
# This program checks if the indexing of the cube made from the raw_drifts
# is correct, meaning that the indexes of the edges of the cube are the indexes
# of the parameter sequences (alpha, kappa, sigma; in this order!).
#

import numpy as np

drift_data = np.load('../data/real_run_3.npz')

alpha_sequence = drift_data['alpha']
kappa_sequence = drift_data['kappa']
sigma_sequence = drift_data['sigma']

# To reproduce:
# states = np.vstack(np.meshgrid(alpha_sequence, kappa_sequence, sigma_sequence, indexing='ij')).reshape(3, -1).T
states = drift_data['states']
drifts_raw = drift_data['drifts']

# This is the correct reshaping function that puts the data into a cube with the indexing sequences along the edges
drifts = drifts_raw.reshape(len(alpha_sequence), len(kappa_sequence), len(sigma_sequence))


def test(state, drift):
    alpha_idx = np.where(alpha_sequence == state[0])
    kappa_idx = np.where(kappa_sequence == state[1])
    sigma_idx = np.where(sigma_sequence == state[2])

    return drifts[alpha_idx, kappa_idx, sigma_idx] == drift


true = 0
for i in range(states.shape[0]):
    if test(states[i], drifts_raw[i]):
        true += 1

print(str(true) + "/" + str(states.shape[0]))
