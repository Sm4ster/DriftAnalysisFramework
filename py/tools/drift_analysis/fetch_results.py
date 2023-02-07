import numpy as np
import time
import pickle

with open("CMA-debug", 'rb') as f:
    analysis = pickle.load(f)

analysis.load_job_ids()

print(analysis.uuid)

# while not analysis.is_finished():
#     print("Isnt finished yet")
#     time.sleep(5)

results = analysis.get_results()

# save the results
np.save("../../data/CMA-debug.npy", analysis.results)


for pf_idx, pf in enumerate(analysis.config["potential"]):
    none_states = 0
    drifts = np.empty(len(results))

    # slice out the results
    for state_idx, state_result in enumerate(results):
        if state_result["results"][pf_idx] != None:
            drifts[state_idx] = state_result["results"][pf_idx]["drift"]
        else:
            none_states += 1

    print(pf["function"])
    print("Mean drift " + str(drifts.mean()))
    print("Minimal drift " + str(np.amax(drifts)))
    print("Drift range " + str(np.amax(drifts) - np.amin(drifts)))
    print("Variance " + str(drifts.var()))
    print("None States " + str(none_states))
    print("\n")