import numpy as np

'''
This test script simulates a one-step iteration of the CMA-ES algorithm. It does so in a vectorized manner with the
assumption that C is in the normal form. 
'''
# TODO make these realistic
c_m = 1
c_sigma = 1
c_cov = 1

m = np.array([[5, 4], [6, 2], [3, 7], [8, 0]])
sigma = np.array([4, 3, 2, 1.1])
C = np.array([
    [[1, 0], [0, 2]],
    [[2.1, 0], [0, 2]],
    [[3, 0], [0, 3]],
    [[4, 0], [0, 4]]
])

w = np.array([0.1, 1, 5, 0, 0])
A = np.array([np.sqrt(C[:, 0, 0]), np.sqrt(C[:, 1, 1])]).T

# randomness for a mu = 5
z = np.array([
    [[4, 3], [5, 1], [2, 6], [2, .6], [.2, 6]],
    [[12, 3], [5, 3], [2, 8], [5, .6], [.2, 6]],
    [[3, 3], [1, 1], [2, 2], [2, .6], [.2, 6]],
    [[6, 9], [3, 1], [2, 6], [1, .6], [.6, 2]]
])

print("sigma_A:\n", A)

# Reshape the matrix to be able to broadcast across the data slices
A_expanded = np.repeat(A[:, np.newaxis, :], 5, axis=1)
print("A_expanded:\n", A_expanded)

sigma_A_expanded = A_expanded * sigma.reshape(4, 1, 1)
print("sigma_A_expanded:\n", sigma_A_expanded)

y = A_expanded * z
print("y_expanded:\n", y)


m_expanded = np.repeat(m[:, np.newaxis, :], 5, axis=1)
print("m_expanded:\n", m_expanded)

x = m_expanded + (sigma_A_expanded * z)
print("x:\n", x)

# Compute the norms of each vector in the middle axis
norms = np.linalg.norm(x, axis=2)

# Get sorting indices based on the norms for each subarray in the middle axis
indices = np.argsort(norms, axis=1)

# Apply the weights to the indices
weights = np.take(w, indices)

# Multiply each of the samples with the assigned weight
z_w = np.einsum("ij,ijk->ijk", weights, z)
z_w_sum = np.einsum("ij,ijk->ik", weights, z)

print("z_w:\n", z_w)
print("z_w_sum:\n", z_w_sum)

# Multiply each of the samples with the assigned weight
y_w = np.einsum("ij,ijk->ijk", weights, y)
y_w_sum = np.einsum("ij,ijk->ik", weights, y)

print("y_w:\n", y_w)
print("y_w_sum:\n", y_w_sum)

# Multiply each of the samples with the assigned weight
x_w = np.einsum("ij,ijk->ijk", weights, x)
x_w_sum = np.einsum("ij,ijk->ik", weights, x)

print("x_w:\n", x_w)
print("x_w_sum:\n", x_w_sum)

# Make outer product of the y's
y_w_outer_product = np.einsum('...i,...j->...ij', y_w, y_w)
y_w_outer_product_sum = np.einsum('pni,pnj->pij', y_w, y_w)
print("y_w:\n", y_w)
print("y_w_outer_product:\n", y_w_outer_product)
print("y_w_outer_product_sum:\n", y_w_outer_product_sum)

# Updates of the thing TODO this isnt final yet (talk to Tobias)
m = m + c_m * y_w_sum
sigma = sigma * np.exp(c_sigma * np.linalg.norm(z_w_sum)) #TODO why is this so strangely normalized in the tutorial paper?
C = (1-c_cov) * C + c_cov * y_w_outer_product_sum

# print("new m:\n", m)
# print("new sigma:\n", sigma)
# print("new C:\n", C)


