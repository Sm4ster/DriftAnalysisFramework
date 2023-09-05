import numpy as np
from mayavi import mlab

drift_data = np.load('./data/real_run_1.npz')

alpha_sequence = drift_data['alpha']
kappa_sequence = drift_data['kappa']
sigma_sequence = drift_data['sigma']

states = drift_data['states']
drifts_raw = drift_data['drifts']

print(kappa_sequence.max())

drifts = drifts_raw.reshape(len(alpha_sequence), len(kappa_sequence), len(sigma_sequence))
print(drifts.shape)


x, y, z = np.meshgrid(alpha_sequence, kappa_sequence, sigma_sequence, indexing='ij')

print(x,y,z)
src = mlab.pipeline.scalar_field(x, y, z, drifts)
surface = mlab.pipeline.iso_surface(src)
plane_widget = mlab.pipeline.image_plane_widget(src,
                                                plane_orientation='x_axes',
                                                slice_index=20,
                                                )


# Display axes
axes = mlab.axes(xlabel="alpha", ylabel="kappa", zlabel="sigma")

# Create a custom colormap centered at 0
colormap = np.zeros((256, 4))
colors = [(0, 1, 0), (0, 0.5, 1), (0.5, 0.5, 0.5), (1, 1, 0), (1, 0, 0)]  # green, blue, gray, yellow, red
n = len(colors)
s = 256 // (n - 1)
for i, c in enumerate(colors):
    if i < n - 1:
        r_vals = np.linspace(colors[i][0], colors[i+1][0], s)
        g_vals = np.linspace(colors[i][1], colors[i+1][1], s)
        b_vals = np.linspace(colors[i][2], colors[i+1][2], s)
        colormap[i*s:(i+1)*s, :3] = np.column_stack([r_vals, g_vals, b_vals])
    else:
        colormap[i*s:, :3] = colors[i]

# Scale the colormap values to the range [0, 255]
colormap[:, :3] *= 255
colormap[:, 3] = 255

# Set the color LUT range to ensure 0 is centered
vmin, vmax = drifts.min(), drifts.max()
max_abs = max(abs(vmin), abs(vmax))
surface.module_manager.scalar_lut_manager.data_range = [-max_abs, max_abs]
plane_widget.module_manager.scalar_lut_manager.data_range = [-max_abs, max_abs]

# Apply the custom colormap to both the isosurface and the image plane widget
surface.module_manager.scalar_lut_manager.lut.number_of_colors = 256
surface.module_manager.scalar_lut_manager.lut.table = colormap
plane_widget.module_manager.scalar_lut_manager.lut.number_of_colors = 256
plane_widget.module_manager.scalar_lut_manager.lut.table = colormap


mlab.show()
