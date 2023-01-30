from tools.database.JobQueue import JobQueue
import numpy as np
import pickle

with open("test", 'rb') as f:
    analysis = pickle.load(f)

print(analysis.states)

if analysis.is_finished():
    print(analysis.results)
    for pf_idx, pf in enumerate(analysis.pf):
        drifts = np.empty(len(analysis.results) * len(analysis.results[0]))

        # slice out the results
        for location_idx, location_result in enumerate(analysis.results):
            for state_idx, state_result in enumerate(location_result):
                drifts[location_idx * len(analysis.results[0]) + state_idx] = state_result["results"][pf_idx]["drift"]


        print("Mean drift " + str(drifts.mean()))
        print("Minimal drift " + str(np.amax(drifts)))
        print("Drift range " + str(np.amax(drifts) - np.amin(drifts)))
        print("Variance " + str(drifts.var()))
        print("\n")
