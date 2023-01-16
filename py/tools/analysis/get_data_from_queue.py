import matplotlib.pyplot as plt
import numpy as np
from tools.database.JobQueue import JobQueue

q = JobQueue("step_size_analysis")

arc_iterations = 100
sigma_iterations = 1000

results = np.empty([arc_iterations, sigma_iterations, 6])

for job in q.get_finished_jobs():
    result = job.result
    if isinstance(job.meta["position_idx"], int):
        results[job.meta["position_idx"]][job.meta["sigma_idx"]] = result[0], job.meta["sigma_var"], job.meta["angle"], \
                                                                   job.meta["dir_cond_number"], job.meta["location"][0], \
                                                                   job.meta["location"][1]
    else:
        print(job.id)
        q.remove(job.id)

np.save("sigma_data_pi", results)
print("saved data")

# Plotting, evaluating results
plt.figure(dpi=600)
plt.title("Middle value of converged Stepsize")
plt.xlabel("sigma_var")
plt.ylabel("sigma*")
for i in range(arc_iterations):
    plt.loglog(results[i, :, 1], results[i, :, 0], lw=0.2)
plt.show()
