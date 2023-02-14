##
## This program finds a close-to-optimal potential function for the
## (1+1)-ES (without CMA) of the form
##   $\log(\|m\|) + q(\log(\bar \sigma))$
## where q is a piecewise linear and continuous function, i.e., a
## function formed by linear interpolation between a finite set of
## support points. The coefficients are obtained from an LP.
##
## The quantity $\bar \sigma = \sigma / \|m\|$ is the normalized step size.
## We use its logarithm as a state variable.
##


import sys
import numpy as np
import matplotlib.pyplot as plt
from mip import *


# Definition of a grid of states. Since states are themselves logarithmic,
# a linearly spaced grid is appropriate.
grid_min = -7
grid_max = 3
grid_res = 10
grid_size = grid_res * (grid_max - grid_min) + 1
grid = np.linspace(grid_min, grid_max, grid_size)

# number of offspring per state
samples_per_point = 10000


# perform a single (vectorized) step on the given states with the (1+1)-ES;
# return successor states and log-progress
def step(state, dim=10):
    n = state.shape[0]
    sigma = np.exp(state)
    m = np.zeros((n, dim))
    m[:, 0] = 1
    x = m + sigma * np.random.randn(n, dim)
    fx = np.linalg.norm(x, axis=1, keepdims=True)
    success = (fx <= 1).astype(np.float64)
    new_m = success * x + (1 - success) * m
    new_sigma = sigma * np.exp((5 * success - 1) / dim)
    progress = np.linalg.norm(new_m, axis=1, keepdims=True)
    normalized = new_sigma / progress
    return np.log(normalized), -np.log(progress)


# transform state into grid coordinates
def state_to_grid(state):
    return grid_res * (state - grid_min)

# transform grid into state coordinates
def grid_to_state(g):
    return g / grid_res + grid_min

# compute interpolation/extrapolation weights for a set of states
def state_to_weights(state, average=False):
    n = state.shape[0]
    w = np.zeros((n, grid_size))
    g = state_to_grid(state).flatten()
    i = np.floor(g).astype(np.int32)
    below = np.flatnonzero(i < 0)
    inside = np.flatnonzero((i >= 0) & (i+1 < grid_size))
    above = np.flatnonzero(i+1 >= grid_size)
    w[below, 0] = 1 - g[below]
    w[below, 1] = g[below]
    w[inside, i[inside]] = 1 - g[inside] + i[inside]
    w[inside, i[inside]+1] = g[inside] - i[inside]
    w[above, grid_size-2] = grid_size - 1 - g[above]
    w[above, grid_size-1] = 2 + g[above] - grid_size
    if average:
        w = np.mean(w, axis=0)
        assert(np.sum(w) > 0.9999 and np.sum(w) < 1.0001)
    return w


# compute weights for each grid point
sys.stdout.write("computing weight matrix")
sys.stdout.flush()
weights = np.zeros((grid_size, grid_size))
log_progress = np.zeros(grid_size)
for g in range(grid_size):
    s = grid_to_state(g)
    before = s * np.ones((samples_per_point, 1))
    after, log_prog = step(before)
    sys.stdout.write(".")
    sys.stdout.flush()
    log_progress[g] = np.mean(log_prog)
    weights[g] = state_to_weights(after, average=True)
sys.stdout.write("done.\n")

# plot the progress measures by $\log(\|m\|)$
plt.title("log-progress")
plt.plot(grid, log_progress)
plt.show()

# plot the weight matrix, which is nothing but a discretized version of
# the algorithm dynamics restricted to the normalized state
plt.title("weight matrix")
plt.imshow(weights, interpolation="nearest")
plt.show()

# find the piecewise linear potential function
"""
LP formulation:
Let p[i] denote the log-progress, q[i] the potential of the normalized state, and w[i,j] the weights.
goal:
    maximize drift
subject to:
    drift \leq p[i] - q[i] - sum_j(w[i,j] \cdot q[j])
    q[i] \geq 0
"""
sys.stdout.write("solving LP ...")
sys.stdout.flush()
model = Model()
model.verbose = 0
q = [model.add_var(var_type=CONTINUOUS, lb=0) for g in range(grid_size)]
d = model.add_var(name='drift', var_type=CONTINUOUS, lb=-100, ub=100)
model.objective = maximize(d)
for g in range(grid_size):
    model += d <= log_progress[g] + q[g] - xsum(weights[g, j] * q[j] for j in range(grid_size))
model.max_gap = 0
sys.stdout.write(" done.\n")
status = model.optimize(max_seconds = 3600)
if status != OptimizationStatus.OPTIMAL:
    print("LP optimization failed with status", status)
    sys.exit(1)
print("minimal drift:", model.var_by_name("drift").x)

# plot the penalty term
penalty = np.array([x.x for x in q])
if penalty[0] == 0:
    # fix boundary (extrapolation) defect
    penalty[0] = 2 * penalty[1] - penalty[2]
print("q:", np.array(penalty))
plt.title("step size penalty q")
plt.plot(grid, penalty)
plt.show()

# plot the drift
drift = log_progress + penalty - weights @ penalty
print("drift:", drift)
plt.title("drift over states")
plt.plot(grid, drift)
plt.ylim([0, 0.05])
plt.show()