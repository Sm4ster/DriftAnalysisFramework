from DriftAnalysisFramework.OptimizationAlgorithms import CMA_ES
from DriftAnalysisFramework.TargetFunctions import Sphere
import numpy as np
import matplotlib.pyplot as plt
from worker_module import analyze_step_size
import time
from tools.database.JobQueue import JobQueue

# Globals
curves = 4
sigma_iterations = 2000
alg_iterations = 200000
cutoff = 50000

dimension = 2

q = JobQueue("step_size_analysis")

# Experiments
results = np.empty([curves+1, sigma_iterations, 5])

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

for i in range(curves + 1):
    angle = np.pi / 2 * i / curves
    algorithm.set_location([np.cos(angle), np.sin(angle)])
    jobs = []
    for sigma_idx, sigma_22 in enumerate(np.geomspace(0.00001, 100000, num=sigma_iterations)):
        state = {
            "sigma": 3,
            "cov_m": np.array([[1, 0], [0, sigma_22]]),
            "p_succ": 1
        }

        q.enqueue(analyze_step_size, state, algorithm, {"alg_iterations": alg_iterations, "cutoff": cutoff},
                  meta={"position_idx": i, "angle": angle, "location": [np.cos(angle), np.sin(angle)], "sigma_idx": sigma_idx, "sigma_22": sigma_22, "state": state},
                  result_ttl=86400)

print("finished queueing")

while not q.finished():
    time.sleep(1)
    print("Checked the queue, still working... " + str(q.open()))


print("starting so save data...")
for job in q.jobs:
    result = job.result
    results[job.meta["position_idx"]][job.meta["sigma_idx"]] = job.meta["location"][0], job.meta["location"][1], job.meta["angle"], job.meta["sigma_22"], result[0]

np.save("sigma_data_pi", results)

print("saved data")

# Plotting, evaluating results
plt.title("Middle value of converged Stepsize")
plt.xlabel("sigma_22")
plt.ylabel("sigma*")
for i in range(curves+1):
    plt.loglog(results[i, :, 4], results[i, :, 5], lw=0.2)
plt.show()
