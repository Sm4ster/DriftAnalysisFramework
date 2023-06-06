import numpy as np
import numexpr as ne
import re

from DriftAnalysisFramework.OptimizationAlgorithms import CMA_ES
from DriftAnalysisFramework.TargetFunctions import Sphere
from DriftAnalysisFramework.Transformations import CMA_ES as TR

# potential function
potential_function = "x + log(-norm(m) * - y, z * e) + exp(kappa+ ekl(f))"

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
    "norm": lambda x: np.linalg.norm(x, axis=1)
}

exclude_list = ["where", "sin", "cos", "tan", "arcsin", "arccos", "arctan", "arctan2", "sinh", "cosh", "tanh",
                "arcsinh", "arccosh", "arctanh", "log", "log10", "log1p", "exp", "expm1", "sqrt", "abs", "conj", "real",
                "imag", "complex", "contains"]


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
            if parenthesis == 1:
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
                if char in "<>=!*" and expression[idx + 1] in "=<>*":
                    current_token += expression[idx + 1]
                    ignore_operator = True

                parsed_expression.append(current_token)
                current_token = ""
            else:
                ignore_operator = False

        # add to the current token
        else:
            current_token += char

    if current_token:
        parsed_expression.append(current_token)

    if len(parsed_expression) == 1:
        return parsed_expression[0]
    else:
        return parsed_expression


def replace_functions(potential_function, local_dict):
    expression = ""

    for token in potential_function:
        # if the token is a tuple replace this function if necessary
        if type(token) is tuple:
            function_name = token[0]

            if function_name in exclude_list:
                argument_list = []
                for tuple_token in token[1:]:
                    if type(tuple_token) is list:
                        argument_list.append(replace_functions(tuple_token, local_dict)[0])
                    elif type(tuple_token) is tuple:
                        argument_list.append(replace_functions([tuple_token], local_dict)[0])
                    else:
                        argument_list.append(tuple_token)
                print(argument_list)
                expression += function_name + "(" + ",".join(argument_list) + ")"

            elif function_name in function_dict:
                argument_name_list = []
                argument_list = []
                for tuple_token in token[1:]:
                    if type(tuple_token) is list:
                        name = replace_functions(tuple_token, local_dict)[0]
                        argument_name_list.append(name)
                        argument_list.append(local_dict[name])
                    else:
                        argument_name_list.append(tuple_token)
                        argument_list.append(local_dict[tuple_token])

                variable_name = function_name + "_" + "_".join(argument_name_list)
                local_dict[variable_name] = function_dict[function_name](*argument_list)
                expression += variable_name

            else:
                raise Exception("Function is not defined: " + function_name, )

        # if it is a list then parse the expression
        elif type(token) is list:
            expression += replace_functions(token, local_dict)[0]
        else:
            expression += token

    return expression, local_dict


def evaluate(expression, base_dict):
    parsed_expression = parse_expression(expression.replace(" ", ""))
    replace_functions(parsed_expression, base_dict)
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
