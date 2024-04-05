import numpy as np
import numexpr as ne

function_dict = {
    "norm": lambda x: np.linalg.norm(x, axis=1),
    # "max": lambda a, b: np.maximum(a, b),
    # "log": lambda x: np.log(x)
}

exclude_list = ["where", "sin", "cos", "tan", "arcsin", "arccos", "arctan", "arctan2", "sinh", "cosh", "tanh",
                "arcsinh", "arccosh", "arctanh", "log", "log10", "log1p", "exp", "expm1", "sqrt", "abs", "conj", "real",
                "imag", "complex", "contains", "max", "min"]

def replace_operators(string):
    operator_mapping = {
        '&': 'and',
        '|': 'or',
        '~': 'not',
        '^': 'xor',
        '<': 'lt',
        '<=': 'lte',
        '==': 'eq',
        '!=': 'ne',
        '>=': 'gte',
        '>': 'gt',
        '-': 'minus',
        '+': 'plus',
        '*': 'times',
        '/': 'divided_by',
        '**': 'power',
        '%': 'mod',
        '<<': 'left_shift',
        '>>': 'right_shift',
        '(': 'open_paren',
        ')': 'close_paren'
    }

    for operator, replacement in operator_mapping.items():
        string = string.replace(operator, replacement)

    return string


def parse_expression(expression):
    expression = expression.replace(" ", "")

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


def replace_functions(potential_function, local_dict, function_dict_=None):
    if function_dict_ is None:
        function_dict_ = function_dict

    if type(potential_function) is tuple:
        potential_function = [potential_function]

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

                expression += function_name + "(" + ",".join(argument_list) + ")"

            elif function_name in function_dict_:
                argument_name_list = []
                argument_list = []
                for tuple_token in token[1:]:
                    if type(tuple_token) is list:
                        expression_ = replace_functions(tuple_token, local_dict)[0]
                        name = replace_operators(expression_)

                        argument_name_list.append(name)
                        local_dict[name] = ne.evaluate(expression_, local_dict)
                        argument_list.append(local_dict[name])
                    else:
                        if tuple_token not in local_dict:
                            raise Exception("The argument is not defined: " + tuple_token)
                        else:
                            argument_name_list.append(tuple_token)
                            argument_list.append(local_dict[tuple_token])

                variable_name = function_name + "_" + "_".join(argument_name_list)
                expression += variable_name

                # do the calculation
                if variable_name not in local_dict:
                    local_dict[variable_name] = function_dict[function_name](*argument_list)

            elif function_name == "":
                expression += "(" + replace_functions(token[1], local_dict)[0] + ")"
            else:
                raise Exception("Function is not defined: " + function_name)

        # if it is a list then parse the expression
        elif type(token) is list:
            expression += replace_functions(token, local_dict)[0]
        else:
            expression += token

    return expression, local_dict
