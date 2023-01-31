import numpy as np
import time
import pickle

with open("../plotting/OPO-1", 'rb') as f:
    analysis = pickle.load(f)

analysis.load_job_ids()

while not analysis.is_finished():
    analysis.get_results()
    print(analysis.results)
    print(analysis.q.get_finished_jobs())
    print("Isnt finished yet")
    time.sleep(5)


for pf_idx, pf in enumerate(analysis.pf):
    drifts = np.empty(len(analysis.results))

    # slice out the results
    for state_idx, state_result in enumerate(analysis.results):
        drifts[state_idx] = state_result["results"][pf_idx]["drift"]

    print(pf["function"])
    print("Mean drift " + str(drifts.mean()))
    print("Minimal drift " + str(np.amax(drifts)))
    print("Drift range " + str(np.amax(drifts) - np.amin(drifts)))
    print("Variance " + str(drifts.var()))
    print("\n")