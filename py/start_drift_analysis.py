import numpy as np
import numexpr as ne
import re
from collections import ChainMap
from DriftAnalysisFramework.OptimizationAlgorithms import CMA_ES
from DriftAnalysisFramework.TargetFunctions import Sphere
from DriftAnalysisFramework.Transformations import CMA_ES as TR

# potential function
potential_function = "exp(norm(m)) + alpha * kappa + 5.456"

# config
alpha_samples = 2
kappa_samples = 2
sigma_samples = 2
batch_size = 3

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


def replace_functions(potential_function, local_dict):
    potential_function_ = potential_function

    pattern = r'(\w+)\((.*)\)'
    matches = re.findall(pattern, potential_function)

    new_variables = []
    for match in matches:
        function_name = match[0]
        argument = match[1]

        # see if the argument has functions in it as well
        variables, _ = replace_functions(argument, local_dict)

        if len(variables) == 0:
            variable_name = function_name + "_" + argument
            variable_value = np.exp(local_dict[argument])
            new_variables.append({"argument": argument, "name": variable_name, "value": variable_value})

        for variable in variables:
            local_dict[variable["name"]] = variable["value"]
            potential_function_ = potential_function_.replace(argument, variable["name"])


    return new_variables, potential_function_

def evaluate_potential(potential_function, local_dict):
    variables = replace_functions(potential_function, local_dict)

    for variable in variables:
        local_dict[variable["name"]] = variable["value"]
        potential_function_ = potential_function_.replace(argument, variable["name"])
    local_dict_, potential_function


for i in range(states.shape[0]):
    # evaluate the before potential
    alpha, kappa, sigma = states[i][0], states[i][1], states[i][2]
    m, C, _ = TR.transform_to_parameters(alpha, kappa, sigma)
    local_dict = {"alpha": alpha, "kappa": kappa, "sigma": sigma, "sigma_": sigma, "m": m, "C": C}
    potential_before= evaluate_potential(potential_function, local_dict)

    print(local_dict, local_dict_, potential_function, "\n")

    # make step
    normal_form, raw_params, *_ = alg.iterate(alpha, kappa, sigma, num=batch_size)

    # make sure that sigma does not get overwritten and
    # the raw sigma is available with underscore
    raw_params["sigma_"] = raw_params["sigma"]

    # evaluate the after potential
    potential_after = ne.evaluate(potential_function, dict(ChainMap(normal_form, raw_params)))

    print(normal_form, raw_params, potential_after, "\n\n")

    # calculate the drift
