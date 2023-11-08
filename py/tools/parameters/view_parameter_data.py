import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Qt5Agg')


# Initialize stable_sigma and stable_kappa
kappa_data = np.load('../../data/stable_kappa.npz')
sigma_data = np.load('../../data/stable_sigma.npz')

alpha_sequence_kappa = kappa_data['alpha']
alpha_sequence_sigma = sigma_data['alpha']

kappa_sequence = sigma_data['kappa']
sigma_sequence = kappa_data['sigma']

stable_kappa_data = kappa_data['stable_kappa']
stable_sigma_data = sigma_data['stable_sigma']


# plotting
fig, (ax1, ax2) = plt.subplots(2)
fig.suptitle('CMA Parameter Analysis')
# fig.text(0.50, 0.95, f'Groove iterations - {groove_iteration}, measured samples - {measured_samples}',
#          horizontalalignment='center', wrap=True, fontsize='small')

# Plot the results
for alpha_index in range(alpha_sequence_kappa.shape[0]):
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