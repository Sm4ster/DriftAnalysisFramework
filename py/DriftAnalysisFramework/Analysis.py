import numpy as np
import numexpr as ne
from DriftAnalysisFramework.Errors import error_instance
from DriftAnalysisFramework.Statistics import has_significance
from DriftAnalysisFramework.Potential import replace_functions, parse_expression, function_dict
from DriftAnalysisFramework.Transformation import CMA_ES as TR


class DriftAnalysis:
    def __init__(self, alg):
        self.alg = alg
        self.function_dict = function_dict
        self.batch_size = 1000000
        self.max_executions = 1

        self.errors = None
        self.states = None
        self.drifts = None

        self.potential_expr = []
        self.potential_before = []

    def eval_potential(self, potential_functions, states):
        self.states = states
        self.drifts = np.zeros(states.shape[0])
        self.errors = error_instance

        # Evaluate the expressions once
        for potential_function in potential_functions:
            self.potential_expr.append(parse_expression(potential_function))

        # Evaluate all before states
        alpha, kappa, sigma = self.states[:, 0], self.states[:, 1], self.states[:, 2]
        m, C, _ = TR.transform_to_parameters(alpha, kappa, sigma)
        before_dict = {"alpha": alpha, "kappa": kappa, "sigma": sigma, "sigma_raw": sigma, "m": m, "C": C}

        # evaluate the before potential
        potential = np.zeros([len(self.potential_expr), len(states)])
        for expr_idx, potential_expr in enumerate(self.potential_expr):
            potential_function_, before_dict = replace_functions(potential_expr, before_dict)
            potential[expr_idx] = ne.evaluate(potential_function_, before_dict)
        self.potential_before = potential.transpose()

    def get_eval_args(self, i):
        return self.states[i, 0], \
               self.states[i, 1], \
               self.states[i, 2], \
               self.potential_expr, \
               self.potential_before[i], \
               self.alg, \
               self.batch_size

    def eval_drift(self, i):
        eval_drift(self.get_eval_args(i))


def eval_drift(alpha, kappa, sigma, potential_expr, potential_before, alg, batch_size, position):
    drifts = np.zeros([len(potential_expr), batch_size])

    # make step
    normal_form, raw_params, *_ = alg.iterate(alpha, kappa, sigma, num=batch_size)

    # collect base variables (make sure the raw sigma does not get overwritten by the transformed one)
    raw_params["sigma_raw"] = raw_params["sigma"]
    after_dict = {**normal_form, **raw_params}

    # evaluate the after potential
    for expr_idx, potential_expr in enumerate(potential_expr):
        potential_function_, after_dict = replace_functions(potential_expr, after_dict)
        potential_after = ne.evaluate(potential_function_, after_dict)

        # calculate the drift
        drifts[expr_idx] = potential_after - potential_before[expr_idx]

    return np.mean(drifts, axis=1), position
