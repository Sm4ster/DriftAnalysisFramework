from DriftAnalysisFramework import AnalysisTools as AT, JobQueue as JQ
import numpy as np
from worker_module import potential_analysis
import time

d = 2
alpha = 2
#
A = 1 / d
#
r_dash = 1 - np.exp(- np.log(alpha) / (d * np.log(alpha) - 1))
SP_r_dash = AT.SuccessProbability("probability", d, r=r_dash)
#
# q = JQ.JobQueue("lu_search")
#


# lu_list = AT.get_ul_tuple(d, alpha)
# print(len(lu_list))
# for lu in lu_list:
#     l = lu[0][0]
l = 0.75
    # u = lu[0][1]
u = 4.0
#     p_l = lu[1][0]
#     p_u = lu[1][1]
#
p_dash = SP_r_dash.get_min(l, u)
v = p_dash / (2 * d * np.log(alpha))
print(v)
#
# SP = AT.SuccessProbability("probability", d, r=(1 - np.exp(-(A / (1 - v)))), init=False)
#
#     q.enqueue(
#         potential_analysis,
#         args=[SP, alpha, A, v, l, u, p_l, p_u],
#         meta={"u": u, "l": l},
#         result_ttl=86400
#     )
#
# q.start()
#
# while not q.is_finished():
#     time.sleep(5)
#
# jobs = q.get_finished_jobs()
# results = []
# for job in jobs:
#     results.append([job.result, job.meta])
#     # print(job.result, job.meta)
#
# only_values = [item[0] for item in results]
# print(only_values)
# max_value = max(only_values)
# max_index = only_values.index(max_value)
# print(results[max_index])



