from DriftAnalysisFramework.OptimizationAlgorithms import CMA_ES
from DriftAnalysisFramework.TargetFunctions import Sphere
import numpy as np
import matplotlib.pyplot as plt
from worker_module import analyze_step_size
import time
from tools.database.JobQueue import JobQueue

# Globals
sigma_iterations = 1000
alg_iterations = 100000
cutoff = 10000

dimension = 2

q = JobQueue("step_size_analysis")

# Experiments
results = np.empty([sigma_iterations, 2])

target = Sphere(dimension)
algorithm = CMA_ES(
    target,
    {
        "d": 2,
        "p_target": 0.1818,
        "c_cov_plus": 0.2,
        "c_p": 0.8333
    }
)
algorithm.set_location([1, 0])
jobs = []
for sigma_idx, sigma_22 in enumerate(np.linspace(1, 10, num=sigma_iterations)):
    state = {
        "sigma": 3,
        "cov_m": np.array([[1, 1], [1, sigma_22]]),
        "p_succ": 1
    }

    q.enqueue(analyze_step_size, state, algorithm, {"alg_iterations": alg_iterations, "cutoff": cutoff},
              meta={"sigma_idx": sigma_idx, "sigma_22": sigma_22, "state": state})

while not q.finished():
    time.sleep(1)
    print("Checked the queue, still working... " + str(q.open()))

for job in q.jobs:
    result = job.result
    results[job.meta["sigma_idx"]] = job.meta["sigma_22"], result[0]

# Plotting, evaluating results
plt.title("Middle value of converged Stepsize")
plt.xlabel("sigma_22")
plt.ylabel("sigma*")
plt.plot(results[:, 0], results[:, 1])
plt.show()

np.save("sigma_data", results)

print("saved data")

