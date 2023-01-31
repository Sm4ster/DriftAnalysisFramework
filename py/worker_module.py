import sys
from DriftAnalysisFramework import PotentialFunctions, OptimizationAlgorithms, TargetFunctions
import math
import copy
import time
# sys.path.insert(0, '/home/stephan/DriftAnalysis/')

from scipy.stats import t, ttest_1samp
import numpy as np


def work_job(oa, pfs, states, keys, options, global_state_array=None, verbosity=0):

    final_results = []
    socket_samples_done = False
    current_state = {}

    # loop through all the states
    state_idx = 0
    for state in states:
        if verbosity > 0: print("Starting new state " + str(state_idx) + "/" + str(states.shape[0]))

        # set location
        oa.set_location(state[keys["m"]:])

        # create the current state
        for key, key_idx in keys.items():
            current_state[key] = state[key_idx]
        current_state['m'] = oa.get_location()

        # calculate the derivations
        for matrix in options["matrices"]:
            # type matrix becomes a numpy matrix and gets stored in matrices as it cannot be used in the potential
            # equation itself. However it can be a predecessor for another derived value.
            matrix_definition = replace_array_values(matrix["definition"], current_state)
            current_state[matrix["name"]] = np.array(matrix_definition)

        # We calculate the potential for a single state until it becomes significant
        all_samples = np.zeros([0, len(pfs)])

        # Save the sample data (like follow up state, drift, etc) for later examination
        state_data = []

        # create a list of idxs so we can be efficient with data and still remember where to save results
        pf_idxs = list(range(len(pfs)))

        # create a list for the results to be laid in later
        results = [None] * len(pf_idxs)

        while True:
            batch_samples = np.zeros([options["batch_size"], len(pf_idxs)])

            for idx in range(options["batch_size"]):
                # iterate and save the follow up state
                follow_up_state = oa.iterate(current_state)

                # calculate the difference in potential
                for idx_, pf_idx in enumerate(pf_idxs):
                    batch_samples[idx][idx_] = pfs[pf_idx].potential(follow_up_state) - pfs[pf_idx].potential(
                        current_state)

            # add samples of this batch to the overall samples
            all_samples = np.concatenate((all_samples, batch_samples))

            if not socket_samples_done:
                if all_samples.shape[0] >= options["socket_size"]:
                    socket_samples_done = True
            else:

                significance = []
                for idx_, pf_idx in enumerate(pf_idxs):
                    significance.append(
                        has_significance(all_samples[:, idx_], options["deviation"], options["confidence"]))

                # If wait_all mode is on this only gets executed when full significance is achieved
                # If wait all mode is off this gets executed and samples are removed from the respective variables
                if all_samples.shape[0] >= options["max_evaluations"] or all(significance) or not options["wait_all"]:
                    remove_idxs = []
                    for idx_, pf_idx in enumerate(pf_idxs):
                        # if we reached desired precision or we reached the max evaluations
                        if significance[idx_] or all_samples.shape[0] > options["max_evaluations"]:
                            if all_samples[:, idx_].size > options["max_evaluations"]:
                                print("Max evaluations reached, no significance detected")
                            else:
                                if verbosity > 1: print("Number of samples: " + str(all_samples.size))

                            # make sure to save the results for the potential function that just became significant
                            results[pf_idx] = {
                                "potential": pfs[pf_idx].potential(current_state),
                                "drift": np.mean(all_samples[:, idx_]),
                                "number_samples": all_samples.size,
                                "significant": significance[idx_],
                            }

                            if not options["wait_all"]:
                                remove_idxs.append(idx_)

                    # the sorting is important, otherwise we will mix up the indices
                    remove_idxs.sort(reverse=True)
                    for idx_ in remove_idxs:
                        all_samples = np.delete(all_samples, idx_, axis=1)
                        pf_idxs.pop(idx_)

                if all(significance) or all_samples.shape[0] >= options["max_evaluations"]:
                    break

        result = {
            "state_idx": state_idx,
            "state": current_state.copy(),
            "results": results
        }

        if options["save_follow_up_states"]:
            result["samples"] = state_data

        final_results.append(result)
        state_idx += 1

    return final_results


def has_significance(sample, deviation=0.1, confidence=0.05):
    mean = np.mean(sample)

    if mean == 0:
        return True

    popmean_plus = mean + abs(deviation * mean)
    popmean_minus = mean - abs(deviation * mean)

    p_values = (ttest_1samp(sample, popmean_plus, alternative="less").pvalue,
                ttest_1samp(sample, popmean_minus, alternative="greater").pvalue)

    is_precise = p_values[0] < confidence and p_values[1] < confidence

    return is_precise


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


def analyze_step_size(state, algorithm, options):
    sigma_array = np.empty([options["alg_iterations"], 1])

    for idx in range(options["alg_iterations"]):
        next_state = algorithm.iterate(state)
        sigma_array[idx] = next_state["sigma"]
        state["sigma"] = next_state["sigma"]
        state["p_succ"] = next_state["p_succ"]

    # remove the first few iterations just to be sure to catch no starting bias
    sigma_array = np.split(sigma_array, [options["cutoff"], options["alg_iterations"]])[1]

    return sigma_array.mean(), sigma_array.var(), sigma_array.max() - sigma_array.min()
