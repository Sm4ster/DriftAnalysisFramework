import numpy as np
import numexpr as ne
from DriftAnalysisFramework.Errors import error_instance
from DriftAnalysisFramework.Potential import replace_functions, parse_expression, function_dict
from DriftAnalysisFramework.Transformation import CMA_ES as TR
from DriftAnalysisFramework.Statistics import p_values
from welford import Welford


class DriftAnalysis:
    def __init__(self, alg):
        self.alg = alg
        self.function_dict = function_dict
        self.batch_size = 1000000
        self.sub_batch_size = 50000
        self.max_executions = 1

        self.errors = None
        self.states = None
        self.drifts = None

        self.potential_expr = []
        self.potential_before = []

        if (self.batch_size % self.sub_batch_size) != 0:
            raise Exception("Batch_size must be a multiple of the sub_batch_size.")

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
               self.batch_size, \
               self.sub_batch_size

    def eval_drift(self, i):
        eval_drift(self.get_eval_args(i))


def eval_drift(alpha, kappa, sigma, potential_expressions, potential_before, alg, batch_size, sub_batch_size, position):
    # init result data structures
    successes = 0
    drift = Welford()
    state_success = Welford()
    state_no_success = Welford()

    # ensure that sub_batching will work properly
    assert batch_size % sub_batch_size == 0
    batch_count = batch_size // sub_batch_size

    for _ in range(batch_count):
        drifts = np.zeros([len(potential_expressions), sub_batch_size])

        # make step
        normal_form, raw_params, success, *_ = alg.iterate(alpha, kappa, sigma, num=sub_batch_size)

        # collect base variables (make sure the raw sigma does not get overwritten by the transformed one)
        raw_params["sigma_raw"] = raw_params["sigma"]
        after_dict = {**normal_form, **raw_params}

        # evaluate the after potential
        for expr_idx, potential_expr in enumerate(potential_expressions):
            potential_function_, after_dict = replace_functions(potential_expr, after_dict)
            potential_after = ne.evaluate(potential_function_, after_dict)

            # calculate the drift
            drifts[expr_idx] = potential_after - potential_before[expr_idx]

        weight = np.sum(success) / len(success)
        state_success.add_all(
            np.array(
                [
                    weight * np.mean(success * normal_form["alpha"]),
                    weight * np.mean(success * normal_form["kappa"]),
                    weight * np.mean(success * normal_form["sigma"])
                ]
            )
        )
        state_no_success.add_all(
            np.array(
                [
                    (1 - weight) * np.mean((1 - success) * normal_form["alpha"]),
                    (1 - weight) * np.mean((1 - success) * normal_form["kappa"]),
                    (1 - weight) * np.mean((1 - success) * normal_form["sigma"])
                ]
            )
        )
        drift.add_all(drifts.T)
        successes += success.sum()

    mean, variance, significance = drift.mean, drift.var_p, np.zeros([len(potential_expressions), 2])
    for idx in range(len(potential_expressions)):
        significance[idx] = p_values(mean[idx], variance[idx], batch_size)

    return mean, variance, significance, successes, \
           np.array([state_success.mean, state_success.var_p]), \
           np.array([state_no_success.mean, state_no_success.var_p]), \
           position
