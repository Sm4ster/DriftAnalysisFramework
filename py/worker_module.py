import sys
from DriftAnalysisFramework import PotentialFunctions, OptimizationAlgorithms, TargetFunctions
import math
# sys.path.insert(0, '/home/stephan/DriftAnalysis/')

from scipy.stats import t, ttest_1samp
import numpy as np


def work_job(oa, pf, location, states, options, global_state_array=None):
    results = []

    # set up the state counting logic
    total_combinations = 1
    keys = []
    counter = []

    # set location
    oa.set_location(location)

    for idx, (key, state) in enumerate(states.items()):
        keys.append(key)
        counter.append(0)
        total_combinations *= len(state)

    # loop through all the states
    current_state = {}
    for state_idx in range(0, total_combinations):
        print("Starting new state " + str(state_idx) + "/" + str(total_combinations))

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

        # Save the sample data (like follow up state, drift, etc) for later examination
        state_data = []

        while True:
            batch_samples = np.zeros(options["batch_size"])

            for idx in range(options["batch_size"]):
                # iterate and save the follow up state
                follow_up_state = oa.iterate(current_state)

                # calculate the difference in potential
                batch_samples[idx] = pf.potential(follow_up_state) - pf.potential(current_state)

                if options["save_follow_up_states"]:
                    sample_data = {}
                    # save the drift for the frontend
                    sample_data["drift"] = batch_samples[idx]

                    # save potential for debugging
                    sample_data["potential"] = pf.potential(follow_up_state)

                    # save the follow up state
                    sample_data["follow_up_state"] = follow_up_state
                    sample_data["success"] = follow_up_state["m"].all() == current_state["m"].all()

                    # save the sample data
                    state_data.append(sample_data)

            # add samples of this batch to the overall samples
            all_samples = np.concatenate((all_samples, batch_samples))

            is_significant, confident_mean, true_precision, p_values = has_significance(all_samples)
            print(is_significant, confident_mean, true_precision, p_values)

            # if we reached desired precision or we reached the max evaluations
            if is_significant or all_samples.size > options["max_evaluations"]:
                break

        # counter logic to access all state combinations
        counter[0] += 1
        for counter_idx in range(0, len(counter)):
            if counter[counter_idx] == len(states[keys[counter_idx]]):
                if counter_idx + 1 < len(counter): counter[counter_idx + 1] += 1
                counter[counter_idx] = 0

        result = {
            "state_idx": state_idx,
            "state": current_state.copy(),
            "potential": pf.potential(current_state),
            "raw_drift": np.mean(all_samples),
            "confident_drift": confident_mean,
            "precision": true_precision,
            "number_samples": all_samples.size,
        }

        if options["save_follow_up_states"]:
            result["samples"] = state_data

        results.append(result)
        print(all_samples.size)

    return results


def has_significance(sample, precision=1, confidence=0.05):
    mean = np.mean(sample)
    if mean != 0:
        true_precision = (0 - int(math.log10(abs(mean)))) + precision
    else:
        true_precision = 1

    rounded_mean = np.around(mean, true_precision)
    deviation = (1 / (10 ** true_precision))
    popmean_plus = rounded_mean + deviation
    popmean_minus = rounded_mean - deviation

    p_values = (ttest_1samp(sample, popmean_plus, alternative="less").pvalue, ttest_1samp(sample, popmean_minus, alternative="greater").pvalue)

    is_precise = p_values[0] < confidence and p_values[1] < confidence

    return is_precise, rounded_mean, true_precision, p_values


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
