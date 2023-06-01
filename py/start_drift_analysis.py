import numpy as np
import numexpr as ne
import re
from collections import ChainMap
from DriftAnalysisFramework.OptimizationAlgorithms import CMA_ES
from DriftAnalysisFramework.TargetFunctions import Sphere
from DriftAnalysisFramework.Transformations import CMA_ES as TR

# potential function
potential_function = "log(norm(m) + y, z) + exp(kappa+ ekl(f))"

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


def parse_expression(expression):
    parenthesis = 0
    parsed_expression = []
    parsed_function = []
    current_token = ""
    ignore_operator = False

    for idx, char in enumerate(expression):
        if char == '(':
            if parenthesis == 0:
                parsed_function.append(current_token)
                current_token = ""
            else:
                current_token += char
            parenthesis += 1
        elif char == ')':
            parenthesis -= 1
            if parenthesis == 0:
                parsed_function.append(parse_expression(current_token))
                parsed_expression.append(tuple(parsed_function))
                parsed_function = []
                current_token = ""
            else:
                current_token += char
        elif char == ',':
            if parenthesis == 0:
                parsed_function.append(parse_expression(current_token))
                current_token = ""
            else:
                current_token += char
        # identify operators
        elif parenthesis == 0 and char in "+-*/%&|~^<>!=":
            if current_token != "":
                parsed_expression.append(current_token)
            current_token = ""
            if not ignore_operator:
                current_token = char

                # double char operators
                if char in "<>=!*" and expression[idx+1] in "=<>*":
                    current_token = expression[idx+1]
                    ignore_operator = True

                parsed_expression.append(current_token)
                current_token = ""

                # unary operator
                # if char == "-":
            else:
                ignore_operator = False

        else:
            current_token += char

    if current_token:
        parsed_expression.append(current_token)

    if len(parsed_expression) == 1:
        return parsed_expression[0]
    else:
        return parsed_expression


def replace_functions(potential_function, local_dict):
    pattern = r'(\w+)\(([^()]*\))'
    matches = re.findall(pattern, potential_function)

    for match in matches:
        function_name = match[0]
        raw_arguments = match[1]

        # Count the number of opening and closing parentheses
        open_parentheses = raw_arguments.count('(')
        close_parentheses = raw_arguments.count(')')

        # Find the correct closing parenthesis
        while close_parentheses < open_parentheses:
            # Search for the next closing parenthesis
            next_close_parenthesis = re.search(r'\)', raw_arguments)
            if next_close_parenthesis:
                raw_arguments = raw_arguments[next_close_parenthesis.start() + 1:]
                close_parentheses += 1
            else:
                # If no closing parenthesis found, break the loop
                break

        print(raw_arguments)

        # see if the argument has functions in it as well, replace if so
        argument, _ = replace_functions(raw_arguments, local_dict)
        potential_function = potential_function.replace(raw_arguments, argument)

        # process this match by replacing
        variable_name = function_name + "_" + argument
        potential_function = potential_function.replace(function_name + "(" + argument + ")", variable_name)

        # calculate the values and save them in the dict
        local_dict[variable_name] = function_dict[function_name](local_dict[argument])

    return potential_function, local_dict


def evaluate(expression, base_dict):
    parsed_expression = parse_expression(expression.replace(" ", ""))
    test = 1


for i in range(states.shape[0]):
    # collect the base variables for the potential function
    alpha, kappa, sigma = states[i][0], states[i][1], states[i][2]
    m, C, _ = TR.transform_to_parameters(alpha, kappa, sigma)
    before_dict = {"alpha": alpha, "kappa": kappa, "sigma": sigma, "sigma_raw": sigma, "m": m, "C": C}

    # evaluate the before potential
    potential_before = evaluate(potential_function, before_dict)

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
