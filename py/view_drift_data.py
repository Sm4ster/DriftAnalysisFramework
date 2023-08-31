import numpy as np
from mayavi import mlab

drift_data = np.load('./data/real_run_1.npz')

alpha_sequence = drift_data['alpha']
kappa_sequence = drift_data['kappa']
sigma_sequence = drift_data['sigma']

states = drift_data['states']
drifts_raw = drift_data['drifts']

print(drifts_raw.shape)

drifts = drifts_raw.reshape(len(alpha_sequence), len(kappa_sequence), len(sigma_sequence))
print(drifts.shape)

src = mlab.pipeline.scalar_field(drifts)
mlab.pipeline.iso_surface(src, contours=[drifts.min(), drifts.max()], opacity=0.1)
mlab.pipeline.image_plane_widget(src,
                            plane_orientation='z_axes',
                            slice_index=20,
                        )
mlab.show()