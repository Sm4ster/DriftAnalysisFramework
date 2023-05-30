import numpy as np
import numexpr as ne
import re
from collections import ChainMap
from DriftAnalysisFramework.OptimizationAlgorithms import CMA_ES
from DriftAnalysisFramework.TargetFunctions import Sphere
from DriftAnalysisFramework.Transformations import CMA_ES as TR

# potential function
potential_function = "log(norm(m)) + kappa"

# config
alpha_samples = 20
kappa_samples = 20
sigma_samples = 20
batch_size = 100000

# create states
alpha_sequence = np.linspace(0, np.pi / 4, num=alpha_samples)
kappa_sequence = np.geomspace(1 / 10, 10, num=kappa_samples)
sigma_sequence = np.geomspace(1 / 10, 10, num=sigma_samples)

states = np.vstack(np.meshgrid(alpha_sequence, kappa_sequence, sigma_sequence)).reshape(3, -1).T

# initialize the target function and optimization algorithm
alg = CMA_ES(Sphere(), {
    "d": 2,
    "p_target": 0.1818,
    "c_p": 0.8333,
    "c_cov": 0.2,
    "dim": 2
})

function_dict = {
    "log": lambda x: np.log(x),
    "norm": lambda x: np.linalg.norm(x, axis=1)
}

def replace_functions(potential_function, local_dict):
    pattern = r'(\w+)\((.*)\)'
    matches = re.findall(pattern, potential_function)

    for match in matches:
        function_name = match[0]
        raw_argument = match[1]

        # see if the argument has functions in it as well, replace if so
        argument, _ = replace_functions(raw_argument, local_dict)
        potential_function = potential_function.replace(raw_argument, argument)

        # process this match by replacing
        variable_name = function_name + "_" + argument
        potential_function = potential_function.replace(function_name + "(" + argument + ")", variable_name)

        # calculate the values and save them in the dict
        local_dict[variable_name] = function_dict[function_name](local_dict[argument])

    return potential_function, local_dict


for i in range(states.shape[0]):
    # collect the base variables for the potential function
    alpha, kappa, sigma = states[i][0], states[i][1], states[i][2]
    m, C, _ = TR.transform_to_parameters(alpha, kappa, sigma)
    before_dict = {"alpha": alpha, "kappa": kappa, "sigma": sigma, "sigma_raw": sigma, "m": m, "C": C}

    # evaluate the before potential
    potential_function_, _ = replace_functions(potential_function, before_dict)
    potential_before = ne.evaluate(potential_function_, before_dict)

    # make step
    normal_form, raw_params, *_ = alg.iterate(alpha, kappa, sigma, num=batch_size)

    # collect base variables (make sure the raw sigma does not get overwritten by the transformed one)
    raw_params["sigma_raw"] = raw_params["sigma"]
    after_dict = {**normal_form, **raw_params}

    # evaluate the after potential
    potential_function_, after_dict = replace_functions(potential_function, after_dict)
    potential_after = ne.evaluate(potential_function_, after_dict)

    # calculate the drift
    drift = potential_after - potential_before

    print(drift.mean())
