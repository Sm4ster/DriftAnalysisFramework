import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from scipy.stats import multivariate_normal, norm

# Define the number of points in each dimension
num_points_x = 200
num_points_y = 200

# TODO Introduce alpha, kappa, sigma to choose the correct grid for every configuration
# TODO Sum um the densities in the success region and calculate the success rate
# TODO Clean up the code and vectorize it

# Generate grid points
r = np.sqrt(np.random.uniform(0, 1, num_points_x))
phi = np.random.uniform(0, 2 * np.pi, num_points_x)

uniform_points_x = np.linspace(0, 1, num_points_x)[1:-1]
uniform_points_y = np.linspace(0, 1, num_points_y)[1:-1]

# Use the inverse CDF (percent-point function) of the normal distribution
# to map uniform points to a normal distribution for both dimensions
kappa = 2
normal_points_x = norm.ppf(uniform_points_x, loc=1, scale=np.sqrt(kappa))
normal_points_y = norm.ppf(uniform_points_y, loc=0, scale=1 / np.sqrt(kappa))

# Scale the points to spread them across a larger area
scaling_factor = 2
scaled_points_x = normal_points_x
scaled_points_y = normal_points_y

# Create the 2D grid
X, Y = np.meshgrid(scaled_points_x, scaled_points_y)
xx = X.flatten()
yy = Y.flatten()

# Filter points to keep only those within the circle
circle_mask = (xx ** 2 + yy ** 2) <= 1
print(circle_mask.sum())
xx_within_circle = xx[circle_mask]
yy_within_circle = yy[circle_mask]

# Define the mean vector and covariance matrix
mean = [1, 0]
covariance = [[2, 0.], [0.5, 1]]

# # Convert polar coordinates to Cartesian coordinates
# xx = r * np.cos(phi)
# yy = r * np.sin(phi)

# Create a multivariate normal distribution object
rv = multivariate_normal(mean, covariance)

# Evaluate the density function
pos = np.dstack((xx_within_circle, yy_within_circle))
z_values = rv.pdf(pos)

# Define colors and range for the custom color scale
start_color = 'blue'
end_color = 'red'
custom_cmap = LinearSegmentedColormap.from_list('custom_cmap', [start_color, end_color])

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
