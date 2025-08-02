import numpy as np
import matplotlib.pyplot as plt

steepness = 0.01
width = 2
position = 0
# Define the filter function
filter_func = lambda x, steepness, width, position: np.where(np.abs((1 / width) * (x)) < 1, 0, 1 - np.exp(
   -steepness * (np.square(np.log(np.abs((1 / width) * (x)))))))

# g = lambda x: 0.5 * (1 - np.cos(np.pi * x))
#
#
# def filter_func(x, a, b, c, d):
#     # Define conditions
#     condition1 = (x < a) | (x > d)
#     condition2 = (b < x) & (x < c)
#     condition3 = (a < x) & (x < b)
#     condition4 = (c < x) & (x < d)
#
#     # Compute the results for each condition
#     result1 = 1
#     result2 = 0
#     result3 = 1 - g((x - a) / (b - a))
#     result4 = g((x - c) / (d - c))
#
#     print(x)
#     print(condition1)
#
#     # Apply the conditions using np.select for better readability
#     conditions = [condition1, condition2, condition3, condition4]
#     choices = [result1, result2, result3, result4]
#     result = np.select(conditions, choices)
#
#     return result


# Sample data arrays
x = np.linspace(-5, 5, 100)  # avoid zero to prevent log issues
# y = 1 - filter_func(x, 1.5707963267948966/4, 1.5707963267948966/2, 5, 10)
y = filter_func(x, steepness, width, position)

print(x, y)

# Create a line plot with a logarithmic x-axis
plt.figure(figsize=(8, 6))
plt.plot(x, y, marker='o')
# plt.xscale('log')
plt.title(f'Filter steepness={steepness},width={width},position={position}')
plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.grid(True)
plt.show()
