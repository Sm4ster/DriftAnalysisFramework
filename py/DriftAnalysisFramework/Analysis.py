import numpy as np
import numexpr as ne
from DriftAnalysisFramework.Potential import replace_functions
from DriftAnalysisFramework.Statistics import has_significance
from DriftAnalysisFramework.Potential import replace_functions, parse_expression, function_dict
from DriftAnalysisFramework.Transformation import CMA_ES as TR


class DriftAnalysis:
    def __init__(self, alg):
        self.alg = alg
        self.function_dict = function_dict
        self.batch_size = 10000

        self.errors = None
        self.states = None
        self.drifts = None
        self.potential_expr = None
        self.potential_before = None

    def eval_potential(self, potential_function, states):
        self.states = states
        self.drifts = np.zeros(states.shape[0])
        self.errors = []

        # Evaluate the expression once
        self.potential_expr = parse_expression(potential_function)

        # Evaluate all before states
        alpha, kappa, sigma = self.states[:, 0], self.states[:, 1], self.states[:, 2]
        m, C, _ = TR.transform_to_parameters(alpha, kappa, sigma)
        before_dict = {"alpha": alpha, "kappa": kappa, "sigma": sigma, "sigma_raw": sigma, "m": m, "C": C}

        # evaluate the before potential
        potential_function_, before_dict = replace_functions(self.potential_expr, before_dict)
        self.potential_before = ne.evaluate(potential_function_, before_dict)

        # print(self.potential_before)

    def eval_drift(self, i):
        significant = False
        drift = np.array([])
        while not significant:
            # make step
            alpha, kappa, sigma = self.states[i, 0], self.states[i, 1], self.states[i, 2]
            normal_form, raw_params, *_ = self.alg.iterate(alpha, kappa, sigma, num=self.batch_size)

            # collect base variables (make sure the raw sigma does not get overwritten by the transformed one)
            raw_params["sigma_raw"] = raw_params["sigma"]
            after_dict = {**normal_form, **raw_params}

            # evaluate the after potential
            potential_function_, after_dict = replace_functions(self.potential_expr, after_dict)
            potential_after = ne.evaluate(potential_function_, after_dict)

            # calculate the drift
            drift = np.concatenate((drift, potential_after - self.potential_before[i]))

            significant = has_significance(drift)

            if drift.shape[0] > 100 * self.batch_size:
                # print(f"Significance could not be achieved in state {i}, aborting at {drift.shape[0]} evaluations. Drift: {np.mean(drift)}, variance: {np.var(drift)}")
                # print(drift, potential_after, self.potential_before)
                self.drifts[i] = np.mean(drift)
                self.errors.append(f"Significance could not be achieved in state {i}, aborting at {drift.shape[0]} evaluations. Drift: {np.mean(drift)}, variance: {np.var(drift)}")
                return

        self.drifts[i] = np.mean(drift)

