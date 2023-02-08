import numpy as np
import time
import pickle

with open("CMA-debug", 'rb') as f:
    analysis = pickle.load(f)



# load the results
results = np.load("../../data/CMA-debug.npy", allow_pickle=True)

for pf_idx, pf in enumerate(analysis.config["potential"]):
    none_states = 0
    drifts = np.empty(len(results))
    positive_states = []

    # slice out the results
    for state_idx, state_result in enumerate(results):
        if state_result["results"][pf_idx] != None:
            drifts[state_idx] = state_result["results"][pf_idx]["drift"]
            if state_result["results"][pf_idx]["drift"] > 0:
                positive_states.append([state_result["state"], state_result["results"][pf_idx]])
        else:
            none_states += 1



    print(pf["function"])
    print("Mean drift " + str(drifts.mean()))
    print("Minimal drift " + str(np.amax(drifts)))
    print("Drift range " + str(np.amax(drifts) - np.amin(drifts)))
    print("Variance " + str(drifts.var()))
    print(positive_states)
    print("\n")

    # min_drift = np.amax(drifts)
    # max_drift = np.amin(drifts)
    # resolution = min_drift - max_drift / 100
    #
    # occurences = np.array([100, 2])
    #
    # for idx in range(100):
    #     number_drift = 0
    #     for drift in drifts:
    #         if drift >
    #     occurences[idx] = [ , idx * resolution]
    #
