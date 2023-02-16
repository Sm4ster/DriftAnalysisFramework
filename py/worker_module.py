from DriftAnalysisFramework import PotentialFunctions, OptimizationAlgorithms, TargetFunctions
import json
from definitions import ALGORITHM_PATH
# sys.path.insert(0, '/home/stephan/DriftAnalysis/')

from scipy.stats import t, ttest_1samp
import numpy as np


def work_job(config, states, keys, options, global_state_array=None, verbosity=0):
    # initialize the target function
    tf = TargetFunctions.convex_quadratic(2, config["target"])

    # initialize the algorithm
    with open(ALGORITHM_PATH + config["algorithm"] + '.json', 'r') as f:
        oa_definition = json.load(f)
    matrices = oa_definition["matrices"]
    oa_class = getattr(OptimizationAlgorithms, oa_definition['python_class'])
    oa = oa_class(tf, config['constants'])

    # initialize a potential function
    pfs = []
    for potential in config["potential"]:
        if "mode" not in potential:
            raise ("[ERROR] Please specify the mode as 'expression' or 'function'")

        if potential["mode"] == "expression":
            pfs.append(PotentialFunctions.Expression(potential, config["constants"]))
        elif potential["mode"] == "function":
            if "data" in potential:
                pfs.append(PotentialFunctions.Function(potential, config["constants"], potential["data"]))
            else:
                pfs.append(PotentialFunctions.Function(potential, config["constants"]))
        else:
            raise ("[ERROR] Unknown mode. Please use 'expression' or 'function'")

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
        for matrix in matrices:
            # type matrix becomes a numpy matrix and gets stored in matrices as it cannot be used in the potential
            # equation itself. However it can be a predecessor for another derived value.
            matrix_definition = replace_array_values(matrix["definition"], current_state)
            current_state[matrix["name"]] = np.array(matrix_definition)

        # We calculate the potential for a single state until it becomes significant
        all_samples = np.zeros([0, len(pfs)])
        all_errors = np.zeros([0, len(pfs), 2])

        # Save the sample data (like follow up state, drift, etc) for later examination
        state_data = []

        # create a list of idxs so we can be efficient with data and still remember where to save results
        pf_idxs = list(range(len(pfs)))

        # create a list for the results to be laid in later
        results = [None] * len(pf_idxs)

        while True:
            batch_samples = np.zeros([options["batch_size"], len(pf_idxs)])
            # batch_errors = np.zeros([options["batch_size"], len(pf_idxs), 2])

            for idx in range(options["batch_size"]):
                # iterate and save the follow up state
                follow_up_state = oa.iterate(current_state)

                # calculate the difference in potential
                for idx_, pf_idx in enumerate(pf_idxs):
                    follow_up_potential = pfs[pf_idx].potential(follow_up_state)
                    current_potential = pfs[pf_idx].potential(current_state, is_normal_form=True)
                    batch_samples[idx][idx_] = follow_up_potential - current_potential
                    # batch_errors[idx][idx_] = current_potential[1], follow_up_potential[1]

            # add samples of this batch to the overall samples
            all_samples = np.concatenate((all_samples, batch_samples))
            # all_errors = np.concatenate((all_errors, batch_errors))

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
                        if significance[idx_] or all_samples.shape[0] >= options["max_evaluations"]:
                            if all_samples[:, idx_].size > options["max_evaluations"]:
                                print("Max evaluations reached, no significance detected")
                            else:
                                if verbosity > 1: print("Number of samples: " + str(all_samples.size))

                            # make sure to save the results for the potential function that just became significant
                            results[pf_idx] = {
                                "potential": pfs[pf_idx].potential(current_state),
                                "drift": np.mean(all_samples[:, idx_]),
                                #"errors": (np.mean(all_errors[:, idx_, 0]), np.mean(all_errors[:, idx_, 1])),
                                "number_samples": all_samples.shape[0],
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
        if isinstance(entry, list) and entry[0] != "converted":
            return_array[key] = replace_array_values(entry, variables)
        elif type(entry) == int or type(entry) == float:
            return_array[key] = entry
        else:
            if isinstance(entry, list):
                if entry[2] == "inv":
                    return_array[key] = 1 / variables[entry[1]]
            elif entry in variables:
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

    # remove the first few iterations just to be sure to catch no starting bias
    sigma_array = np.split(sigma_array, [options["cutoff"], options["alg_iterations"]])[1]

    return sigma_array.mean(), sigma_array.var(), sigma_array.max() - sigma_array.min()

def potential_analysis(SP, alpha, A, v, l, u, p_l, p_u):
    print(SP)
    SP.init()
    p_star = SP.get_min(l, u)

    print(p_star)

    B_1 = A * p_star - (5 / 4) * v * np.log(alpha)
    B_2 = v * np.log(alpha) * ((5 * p_l - 1) / 4)
    B_3 = v * np.log(alpha) * ((1 - 5 * p_u) / 4)
    result = min(B_1, B_2, B_3)
    print(result, B_1, B_2, B_3)

    return result
