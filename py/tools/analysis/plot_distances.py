import numpy as np
import matplotlib.pyplot as plt


results = np.load("sigma_data_pi_old.npy")

plt.figure(dpi=300)
plt.loglog(results[0, :, 3], results[0, :, 4], lw=0.2, label="curve 1")
plt.loglog(results[1, :, 3], results[1, :, 4], lw=0.2,  label="curve 2")
# plt.loglog(results[2, :, 3], results[2, :, 4], lw=0.2,  label="curve 3")
# plt.loglog(results[3, :, 3], results[3, :, 4], lw=0.2,  label="curve 4")
# plt.loglog(results[4, :, 3], results[4, :, 4], lw=0.2,  label="curve 5")


plt.loglog(results[0, :, 3], np.abs(results[0, :, 4] - results[3, :, 4]), lw=0.2,  label="resulting curve")

plt.legend()
plt.show()
