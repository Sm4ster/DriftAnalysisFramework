import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from scipy.stats import multivariate_normal, norm

alpha = np.pi / 8
kappa = 1
sigma = 1 / 2

# Define the number of points in each dimension
num_points_x = 300
num_points_y = 300

# TODO Sum um the densities in the success region and calculate the success rate
# TODO Clean up the code and vectorize it

# Generate grid points
uniform_points_x = np.linspace(0, 1, num_points_x + 2)[1:-1]
uniform_points_y = np.linspace(0, 1, num_points_y + 2)[1:-1]

print(uniform_points_x)

# Use the inverse CDF (percent-point function) of the normal distribution
# to map uniform points to a normal distribution for both dimensions
normal_points_x = norm.ppf(uniform_points_x, loc=np.cos(alpha), scale=np.sqrt(kappa))
normal_points_y = norm.ppf(uniform_points_y, loc=np.sin(alpha), scale=np.sqrt(1 / kappa))

print(normal_points_x)

# Scale the points to spread them across a larger area
scaling_factor = 1
scaled_points_x = normal_points_x  # * 2/(np.abs(normal_points_x[0]) + np.abs(normal_points_x[-1]))
scaled_points_y = normal_points_y  # * 2/(np.abs(normal_points_y[0]) + np.abs(normal_points_y[-1]))

print(scaled_points_x)

# Create the 2D grid
X, Y = np.meshgrid(scaled_points_x, scaled_points_y)

print(X, Y)
xx = X.flatten()
yy = Y.flatten()

print(len(xx), len(yy))

# Filter points to keep only those within the circle
circle_mask = np.sqrt(xx ** 2 + yy ** 2) <= 1
print(circle_mask.sum())
xx_within_circle = xx[circle_mask]
yy_within_circle = yy[circle_mask]

# Create a multivariate normal distribution object
rv = multivariate_normal(np.array([np.cos(alpha), np.sin(alpha)]), np.array([[kappa, 0], [0, 1 / kappa]]))

# Evaluate the density function
pos = np.dstack((xx_within_circle, yy_within_circle))
print("pos:", pos)
z_values = rv.pdf(pos)

# Define colors and range for the custom color scale
start_color = 'blue'
end_color = 'red'
custom_cmap = LinearSegmentedColormap.from_list('custom_cmap', [start_color, end_color])

print(z_values)
# Normalize the density values to the range [0, 1]
z_min, z_max = z_values.min(), z_values.max()
normalized_values = (z_values - z_min) / (z_max - z_min)

# Get colors for the normalized density values
colors = custom_cmap(normalized_values)

fig, ax = plt.subplots(figsize=(10, 10), dpi=500)
for i in range(xx_within_circle.shape[0]):
    ax.plot(xx_within_circle[i], yy_within_circle[i], 'o', color=colors[i], markersize=2)

# Plot the outline of the circle
circle = plt.Circle((0, 0), 1, color='r', fill=False, linestyle='--')
ax.add_artist(circle)

# Setting equal aspect ratio
ax.set_aspect('equal', 'box')
# Display the plot
plt.xlim(-1.1, 1)
plt.ylim(-1.1, 1)
plt.grid(True)
# plt.title('Meshgrid in Polar Coordinates')
plt.xlabel('x')
plt.ylabel('y')
plt.show()
