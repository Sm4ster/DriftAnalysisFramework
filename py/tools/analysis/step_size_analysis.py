from DriftAnalysisFramework.OptimizationAlgorithms import CMA_ES
from DriftAnalysisFramework.TargetFunctions import Sphere
import numpy as np
import matplotlib.pyplot as plt
from worker_module import analyze_step_size
import time
from tools.database.JobQueue import JobQueue
import copy

# Globals
sigma_iterations = 1000
arc_iterations = 25
alg_iterations = 100000
cutoff = 20000

dimension = 2
max_excentricity = 100000

q = JobQueue("step_size_analysis")

# Experiments
results = np.empty([arc_iterations, sigma_iterations, 6])

target = Sphere(dimension)
algorithm = CMA_ES(
    target,
    {
        "d": 2,
        "p_target": 0.1818,
        "c_cov": 0.2,
        "c_p": 0.8333
    }
)

angle_sequence = np.linspace(0, (np.pi / 25), arc_iterations)
for angle_idx, angle in enumerate(angle_sequence):
    location = [np.cos(angle), np.sin(angle)]
    algorithm.set_location(location)

    sigma_sequence = np.concatenate((1 / (np.flip(np.geomspace(1, max_excentricity, num=int(sigma_iterations / 2)))),
                                     np.geomspace(1, max_excentricity, num=int(sigma_iterations / 2))))
    for sigma_idx, sigma_var in enumerate(sigma_sequence):
        state = {
            "sigma": 3,
            "cov_m": np.array([[1 / sigma_var, 0], [0, sigma_var]]),
            "p_succ": 1
        }

        q.enqueue(analyze_step_size, args=[state, algorithm, {"alg_iterations": alg_iterations, "cutoff": cutoff}],
                  meta={"position_idx": angle_idx, "angle": angle, "location": location, "sigma_idx": sigma_idx,
                        "sigma_var": sigma_var, "dir_cond_number": np.power(sigma_var, 2)},
                  result_ttl=86400)

        if (sigma_idx % 10 == 0): print("Queued jobs " + str(sigma_iterations * angle_idx + sigma_idx) + "/" + str(
            sigma_iterations * arc_iterations))

        q.start()
print("finished queueing")



while not q.is_finished():
    time.sleep(10)
    print("Checked the queue, still working... " + str(q.get_finished().count) + "/" + str(len(q.jobs_ids)))

print("Receiving data...")
for job in q.get_finished_jobs():
    print("checking jobs...")
    result = job.result
    print(result)
    results[job.meta["position_idx"]][job.meta["sigma_idx"]] = result[0], job.meta["sigma_var"], job.meta["angle"], \
                                                               job.meta["dir_cond_number"], job.meta["location"][0], \
                                                               job.meta["location"][1]

np.save("sigma_data_pi", results)
print("saved data")

q.empty()

# Plotting, evaluating results
plt.figure(dpi=600)
plt.title("Middle value of converged Stepsize")
plt.xlabel("sigma_var")
plt.ylabel("sigma*")
for i in range(arc_iterations):
    plt.loglog(results[i, :, 1], results[i, :, 0], lw=0.2)
plt.show()
