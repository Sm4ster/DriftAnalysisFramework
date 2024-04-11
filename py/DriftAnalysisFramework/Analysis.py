import numpy as np
import numexpr as ne
from DriftAnalysisFramework.Potential import replace_functions, parse_expression, function_dict
from DriftAnalysisFramework.Transformation import CMA_ES as TR
from DriftAnalysisFramework.Statistics import p_value
from welford import Welford
from scipy import optimize


class DriftAnalysis:
    def __init__(self, alg):
        self.alg = alg
        self.function_dict = function_dict
        self.batch_size = 1000000
        self.sub_batch_size = 50000
        self.max_executions = 1
        self.target_p_value = 0.001

        self.states_idx = None
        self.states = None
        self.drifts = None

        self.alpha_sequence = None
        self.kappa_sequence = None
        self.sigma_sequence = None

        self.potential_expr = []
        self.potential_before = []

        if (self.batch_size % self.sub_batch_size) != 0:
            raise Exception("Batch_size must be a multiple of the sub_batch_size.")

    def eval_potential(self, potential_functions, alpha_sequence, kappa_sequence, sigma_sequence):
        self.alpha_sequence = alpha_sequence
        self.kappa_sequence = kappa_sequence
        self.sigma_sequence = sigma_sequence

        # make state indexes and states
        self.states_idx = np.vstack(np.meshgrid(
            range(alpha_sequence.shape[0]),
            range(kappa_sequence.shape[0]),
            range(sigma_sequence.shape[0]),
            indexing='ij')).reshape(3, -1).T

        self.states = np.vstack(np.meshgrid(
            alpha_sequence,
            kappa_sequence,
            sigma_sequence,
            indexing='ij')).reshape(3, -1).T

        # Evaluate the expressions once
        for potential_function in potential_functions:
            self.potential_expr.append(parse_expression(potential_function))

        # Evaluate all before states
        alpha, kappa, sigma = self.states[:, 0], self.states[:, 1], self.states[:, 2]
        m, C, _ = TR.transform_to_parameters(alpha, kappa, sigma)
        before_dict = {"alpha": alpha, "kappa": kappa, "sigma": sigma, "sigma_raw": sigma, "m": m, "C": C}

        # evaluate the before potential
        potential = np.zeros([len(self.potential_expr), len(self.states)])
        for expr_idx, potential_expr in enumerate(self.potential_expr):
            potential_function_, before_dict = replace_functions(potential_expr, before_dict)
            potential[expr_idx] = ne.evaluate(potential_function_, before_dict)
        self.potential_before = potential.transpose()

    def get_eval_args(self, i):
        assert self.states[i, 0] == self.alpha_sequence[self.states_idx[i, 0]]
        assert self.states[i, 1] == self.kappa_sequence[self.states_idx[i, 1]]
        assert self.states[i, 2] == self.sigma_sequence[self.states_idx[i, 2]]

        return self.states[i, 0], \
            self.states[i, 1], \
            self.states[i, 2], \
            self.potential_expr, \
            self.potential_before[i], \
            self.alg, \
            self.batch_size, \
            self.sub_batch_size, \
            self.target_p_value, \
            self.states_idx[i]

    def eval_drift(self, i):
        eval_drift(self.get_eval_args(i))


class FollowUpState:
    def __init__(self, mean, std):
        self.mean = mean
        self.std = std


def eval_drift(alpha, kappa, sigma, potential_expressions, potential_before, alg, batch_size, sub_batch_size,
               target_p_value, position):
    # init result data structures
    successes = 0
    drift = Welford()
    follow_up_succ = Welford()
    follow_up_no_succ = Welford()

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

        # save successful and unsuccessful follow up state
        # for mean, geometrical mean, variance and geometrical variance
        # we ignore errors as they come from dealing with the logs
        with np.errstate(divide='ignore', invalid='ignore'):
            mask = np.array(success == 1).T[0]
            follow_up_succ.add_all(
                np.array(
                    [
                        normal_form["alpha"][mask],
                        normal_form["kappa"][mask],
                        normal_form["sigma"][mask],
                    ]
                ).T
            )

            mask = np.array(success == 0).T[0]
            follow_up_no_succ.add_all(
                np.array(
                    [
                        normal_form["alpha"][mask],
                        normal_form["kappa"][mask],
                        normal_form["sigma"][mask],
                    ]
                ).T
            )

        # save drift for mean and variance
        drift.add_all(drifts.T)
        successes += success.sum()

    # collect data for follow up states to return
    state_succ = FollowUpState(
        follow_up_succ.mean[0:3],
        np.sqrt(follow_up_succ.var_p[0:3])
    )
    state_no_succ = FollowUpState(
        follow_up_no_succ.mean[0:3],
        np.sqrt(follow_up_no_succ.var_p[0:3])
    )

    # calc precision of the drift values
    precision = np.zeros([len(potential_expressions)])
    for idx in range(len(potential_expressions)):
        deviation = optimize.golden(
            lambda x: abs(target_p_value - p_value(drift.mean[idx], drift.var_s[idx], batch_size, x)), brack=(0, 1)
        )
        precision[idx] = abs(drift.mean[idx] * deviation)

    return drift.mean, np.sqrt(drift.var_p), precision, successes, state_succ, state_no_succ, position
