import matplotlib.pyplot as plt
import numpy as np
from tools.database.JobQueue import JobQueue

q = JobQueue("step_size_analysis")

distance_sequence = np.geomspace(1, 100, 10)
angle_sequence = np.linspace(0, (np.pi / 4), 10)

sigma_iterations = 800

results = np.empty([distance_sequence.shape[0], angle_sequence.shape[0], sigma_iterations, 6])

for job in q.get_jobs(q.get_finished_jobs().get_job_ids()):
    result = job.result
    print(job)
    results[job.meta["angle_idx"]][job.meta["distance_idx"]][job.meta["sigma_idx"]] = result[0], job.meta[
        "sigma_var"], \
                                                                                      job.meta["angle"], \
                                                                                      job.meta["dir_cond_number"], \
                                                                                      job.meta["location"][0], \
                                                                                      job.meta["location"][1]

np.save("sigma_data_pi", results)
print("saved data")

# # Plotting, evaluating results
# plt.figure(dpi=600)
# plt.title("Middle value of converged Stepsize")
# plt.xlabel("sigma_var")
# plt.ylabel("sigma*")
# for i in range(arc_iterations):
#     plt.loglog(results[i, :, 1], results[i, :, 0], lw=0.2)
# plt.show()
