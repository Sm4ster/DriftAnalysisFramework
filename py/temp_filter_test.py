import numpy as np
import matplotlib.pyplot as plt

# Define the filter function
filter_func = lambda x, steepness, width, position: np.where(np.abs((1/width)*(x-position)) < 1, 0 ,1 - np.exp(-steepness * (np.square(np.log(np.abs((1/width)*(x-position)))))))
# filter_func = lambda x: np.where(x < 1, 0 ,1 - np.exp(-1 * (np.square(np.log(x)))))

# Sample data arrays
x = np.linspace(1, 1000, 100)  # avoid zero to prevent log issues
y = filter_func(x ,0, 0, 540)

print(x,y)

# Create a line plot with a logarithmic x-axis
plt.figure(figsize=(8, 6))
plt.plot(x, y, marker='o')
# plt.xscale('log')
plt.title('Line Plot with Logarithmic X-axis')
plt.xlabel('X-axis (Log Scale)')
plt.ylabel('Y-axis')
plt.grid(True)
plt.show()