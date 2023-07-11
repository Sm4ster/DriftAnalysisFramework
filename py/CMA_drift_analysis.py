import numpy as np
import numexpr as ne
from alive_progress import alive_bar

from DriftAnalysisFramework.Optimization import CMA_ES
from DriftAnalysisFramework.Fitness import Sphere
from DriftAnalysisFramework.Transformation import CMA_ES as TR
from DriftAnalysisFramework.Potential import replace_functions, parse_expression, function_dict
from DriftAnalysisFramework.Interpolation import get_data_value
from DriftAnalysisFramework.Statistics import has_significance

# potential function
potential_function = "log(norm(m)) + stable_kappa(alpha, sigma)"

# config
alpha_samples = 20
kappa_samples = 20
sigma_samples = 20
batch_size = 100000

# create states
alpha_sequence = np.linspace(0, np.pi / 4, num=alpha_samples)
kappa_sequence = np.geomspace(1 / 10, 10, num=kappa_samples)
sigma_sequence = np.geomspace(1 / 10, 10, num=sigma_samples)

# Initialize stable_sigma and stable_kappa
data = np.load('./data/stable_parameters.npz')

alpha_data = data['alpha']
kappa_data = data['kappa']
sigma_data = data['sigma']
stable_kappa = data['stable_kappa']
stable_sigma = data['stable_sigma']

# Update the function dict of the potential evaluation
function_dict.update({
    "stable_kappa": lambda alpha_, sigma_: get_data_value(alpha_, sigma_, alpha_data, sigma_data, stable_kappa),
    "stable_sigma": lambda alpha_, kappa_: get_data_value(alpha_, kappa_, alpha_data, kappa_data, stable_sigma)
})

# Initialize the target function and optimization algorithm
alg = CMA_ES(Sphere(), {
    "d": 2,
    "p_target": 0.1818,
    "c_p": 0.8333,
    "c_cov": 0.2,
    "dim": 2
})

# Transform the individual states to an array we can evaluate vectorized
states = np.vstack(np.meshgrid(alpha_sequence, kappa_sequence, sigma_sequence)).reshape(3, -1).T

# Evaluate the expression once
potential_expr = parse_expression(potential_function)

# Evaluate all before states
alpha, kappa, sigma = states[:, 0], states[:, 1], states[:, 2]
m, C, _ = TR.transform_to_parameters(alpha, kappa, sigma)
before_dict = {"alpha": alpha, "kappa": kappa, "sigma": sigma, "sigma_raw": sigma, "m": m, "C": C}

# evaluate the before potential
potential_function_, before_dict = replace_functions(potential_expr, before_dict)
potential_before = ne.evaluate(potential_function_, before_dict)

# The main loop
with alive_bar(states.shape[0], force_tty=True, title="Evaluating") as bar:
    for i in range(states.shape[0]):
        # make step
        normal_form, raw_params, *_ = alg.iterate(states[i, 0], states[i, 1], states[i, 2], num=batch_size)

        # collect base variables (make sure the raw sigma does not get overwritten by the transformed one)
        raw_params["sigma_raw"] = raw_params["sigma"]
        after_dict = {**normal_form, **raw_params}

        # evaluate the after potential
        potential_function_, after_dict = replace_functions(potential_expr, after_dict)
        potential_after = ne.evaluate(potential_function_, after_dict)

        # calculate the drift
        drift = potential_after - potential_before[i]

        significance = has_significance(drift)
        bar()
