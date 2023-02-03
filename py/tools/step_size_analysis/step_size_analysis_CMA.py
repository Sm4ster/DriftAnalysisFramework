from DriftAnalysisFramework.OptimizationAlgorithms import CMA_ES
from DriftAnalysisFramework.TargetFunctions import Sphere
import numpy as np
import matplotlib.pyplot as plt
from worker_module import analyze_step_size
import time
from DriftAnalysisFramework.JobQueue import JobQueue

# Globals
angle_sequence = np.linspace(0, (np.pi / 4), 7)
sigma_iterations = 80
alg_iterations = 100000
cutoff = 20000

dimension = 2
max_excentricity = 100000

q = JobQueue("step_size_analysis")

# Experiments
results = np.empty([angle_sequence.shape[0] * sigma_iterations, 4])

target = Sphere(dimension)
algorithm = CMA_ES(
    target,
    {
        "d": 2,
        "p_target": 0.1818,
        "c_cov": 0.2,
        "c_p": 0.8333,
        "alpha": 2
    }
)


for angle_idx, angle in enumerate(angle_sequence):
    print("Queued jobs " + str(
        sigma_iterations * angle_idx) + "/" + str(
        sigma_iterations * angle_sequence.shape[0]))

    location = [np.cos(angle), np.sin(angle)]
    algorithm.set_location(location)

    sigma_sequence = np.concatenate(
        (1 / (np.flip(np.geomspace(1, max_excentricity, num=int(sigma_iterations / 2)))),
         np.geomspace(1, max_excentricity, num=int(sigma_iterations / 2))))
    for sigma_idx, sigma_var in enumerate(sigma_sequence):
        state = {
            "sigma": 3,
            "cov_m": np.array([[1 / sigma_var, 0], [0, sigma_var]]),
        }
        q.enqueue(analyze_step_size, args=[state, algorithm, {"alg_iterations": alg_iterations, "cutoff": cutoff}],
                  meta={"job_idx": sigma_iterations * angle_idx + sigma_idx, "location": location,
                        "sigma_var": sigma_var},
                  result_ttl=86400)
    q.start()
print("finished queueing")

while not q.is_finished():
    time.sleep(10)
    print("Checked the queue, still working... " + str(len(q.get_finished_jobs())) + "/" + str(len(q.jobs_ids)))

print("Receiving data...")
for job in q.get_finished_jobs():
    print("checking jobs...")
    result = job.result
    print(result)
    results[job.meta["job_idx"]] = result[0], job.meta["sigma_var"], job.meta["location"][0], job.meta["location"][1]

np.save("sigma_data_test_run", results)
print("saved data")

q.empty()

