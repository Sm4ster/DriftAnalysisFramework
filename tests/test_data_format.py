#
# This program checks if the indexing of the cube made from the raw_drifts
# is correct, meaning that the indexes of the edges of the cube are the indexes
# of the parameter sequences (alpha, kappa, sigma; in this order!).
#

import numpy as np


def test_data_format(drifts_raw, states, drifts_cube, alpha_sequence, kappa_sequence, sigma_sequence):

    for state_idx, state in enumerate(states):
        alpha_idx = np.where(alpha_sequence == state[0])
        kappa_idx = np.where(kappa_sequence == state[1])
        sigma_idx = np.where(sigma_sequence == state[2])

        # Check if the length is correct, if not the format is completely broken
        if len(drifts_raw[state_idx]) != len(np.squeeze(drifts_cube[alpha_idx, kappa_idx, sigma_idx])):
            return False

        for drift_idx in range(len(drifts_raw[state_idx])):
            if drifts_cube[alpha_idx, kappa_idx, sigma_idx, drift_idx] != drifts_raw[state_idx][drift_idx]:
                return False

    return True
