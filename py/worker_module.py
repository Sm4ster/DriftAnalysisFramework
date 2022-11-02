import sys
from DriftAnalysisFramework import PotentialFunctions, OptimizationAlgorithms, TargetFunctions
# sys.path.insert(0, '/home/stephan/DriftAnalysis/')

from scipy.stats import t
import numpy as np


def work_job(oa, pf, states, options):
    results = []

    print("hello from the worker")

    # set up the state counting logic
    total_combinations = 1
    keys = []
    counter = []

    for idx, (key, state) in enumerate(states.items()):
        keys.append(key)
        counter.append(0)
        total_combinations *= len(state)

    # loop through all the states
    current_state = {}
    for state_idx in range(0, total_combinations):

        # create the current state
        for key_idx, key in enumerate(keys):
            current_state[key] = states[key][counter[key_idx]]
        current_state['m'] = oa.get_location()

        # calculate the derivations
        for matrix in options["matrices"]:
            # type matrix becomes a numpy matrix and gets stored in matrices as it cannot be used in the potential
            # equation itself. However it can be a predecessor for another derived value.
            matrix_definition = replace_array_values(matrix["definition"], current_state)
            current_state[matrix["name"]] = np.array(matrix_definition)

        # We calculate the potential for a single state until it becomes significant
        all_samples = np.zeros(0)

        # Save the follow up states for later examination
        follow_up_states = []

        while True:
            batch_samples = np.zeros(options["batch_size"])

            for idx in range(options["batch_size"]):
                # iterate and save the follow up state
                follow_up_state = oa.iterate(current_state)

                # calculate the difference in potential
                batch_samples[idx] = pf.potential(follow_up_state) - pf.potential(current_state)

                # clean the follow up state if the algorithm was not successful
                if follow_up_state["m"].all() == current_state["m"].all():
                    follow_up_state["success"] = False
                else:
                    follow_up_state["success"] = False
                follow_up_states.append(follow_up_state)

            # add samples of this batch to the overall samples
            all_samples = np.concatenate((all_samples, batch_samples))

            # check significance
            significance = has_drift_ttest(all_samples)

            # if we find significance in either direction or we reached the max evaluations
            if significance[0] or all_samples.size > options["max_evaluations"]:
                break

        # counter logic to access all state combinations
        counter[0] += 1
        for counter_idx in range(0, len(counter)):
            if counter[counter_idx] == len(states[keys[counter_idx]]):
                if counter_idx + 1 < len(counter): counter[counter_idx + 1] += 1
                counter[counter_idx] = 0

        results.append({
            "run": state_idx,
            "state": current_state.copy(),
            "samples": follow_up_states,
            "drift": np.mean(all_samples),
            "significance": {
                "drift": significance[1],
                "no_drift": significance[2],
            },
            "number_samples": all_samples.size,
        })

    return results


def has_drift_ttest(sample):
    t_value = np.mean(sample) / (np.std(sample) / np.sqrt(sample.size))
    l_sig = t_value <= t.interval(0.98, sample.size)[0]
    u_sig = t_value > t.interval(0.98, sample.size)[1]
    return l_sig or u_sig, l_sig, u_sig


def replace_array_values(array, variables):
    # init return array with length of array
    return_array = [None] * len(array)
    for key, entry in enumerate(array):
        if isinstance(entry, list):
            return_array[key] = replace_array_values(entry, variables)
        else:
            if entry in variables:
                return_array[key] = variables[entry]
            else:
                raise AttributeError('Key is not available: {0}'.format(entry))
    return return_array
