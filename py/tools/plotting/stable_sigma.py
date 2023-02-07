import numpy as np
import matplotlib.pyplot as plt


results = np.load("../../data/sigma_data_56000_samples.npy")
angles = []
for result in results:
    angles.append(np.arccos(result[2]))

print(set(angles))

# plt.figure(dpi=600)
#
# plt.legend()
# plt.show()