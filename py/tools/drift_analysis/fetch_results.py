import numpy as np
import time
import pickle

with open("OPO-1", 'rb') as f:
    analysis = pickle.load(f)

analysis.load_job_ids()


while not analysis.is_finished():
    print("Isnt finished yet")
    time.sleep(5)

analysis.get_results()

# save the results
np.save("../../data/OPO-0.npy", analysis.results)

for pf_idx, pf in enumerate(analysis.pf_names):

    drifts = np.empty(len(analysis.results))

    # slice out the results
    for state_idx, state_result in enumerate(analysis.results):
        drifts[state_idx] = state_result["results"][pf_idx]["drift"]

    print(pf)
    print("Mean drift " + str(drifts.mean()))
    print("Minimal drift " + str(np.amax(drifts)))
    print("Drift range " + str(np.amax(drifts) - np.amin(drifts)))
    print("Variance " + str(drifts.var()))
    print("\n")