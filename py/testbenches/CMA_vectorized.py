import numpy as np

w = [0.1,1,10, 0,0]

m = [5,6,7,8]
sigma = [4,3,2,1]
C =  np.array([[[1,0],[0,1]],  np.array([[2,0],[0,2]]), np.array([[3,0],[0,3]]), np.array([[4,0],[0,4]])])

sigma_A = np.array([sigma * np.sqrt(C[:, 0, 0]), sigma * np.sqrt(C[:, 1, 1])]).T

# Define the 3D array
data = np.array([[[4,3], [5,1], [2,6], [2,.6], [.2,6]],
                 [[12,3], [5,3], [2,8], [2,.6], [.2,6]],
                 [[3,3], [1,1], [2,2], [2,.6], [.2,6]]])

# Compute the norms of each vector in the middle axis
norms = np.linalg.norm(data, axis=2)

# Get sorting indices based on the norms for each subarray in the middle axis
indices = np.argsort(norms, axis=1)

# Apply the weights to the indices
weights = np.take(w, indices)

# Multiply each of the samples with the assigned weight
weighted_samples = np.einsum("ij,ijk->ijk", weights, data)

print("Original Data:\n", data)
print("incides:\n", indices)
# print("norms:\n", norms)
# print("weights:\n", weights)
print("weighted samples:\n", weighted_samples)