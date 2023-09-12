import numpy as np

drift_data = np.load('./data/real_run_1.npz')

alpha_sequence = drift_data['alpha']
kappa_sequence = drift_data['kappa']
sigma_sequence = drift_data['sigma']

states = drift_data['states']
drifts_raw = drift_data['drifts']

states = np.vstack(np.meshgrid(alpha_sequence, kappa_sequence, sigma_sequence)).reshape(3, -1).T
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

