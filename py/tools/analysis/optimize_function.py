import cma
import numpy as np


def f0(sigma22, a=5.4):
    return a


def f1(sigma22, a=0.98, b=0.35, c=0.51, d=1.0):
    return a - b * np.log(np.log(c * sigma22 + d) ** 2)


def f2(sigma22, a=25, b=1.8, c=2.5, d=1.01):
    return (a / (((sigma22 + b) * c) ** d))


def f(sigma_22, input):
    if input[2] < input[0]:
        return f0(sigma_22)
    elif input[2] < input[1]:
        return f1(sigma_22)
    else:
        return f2(sigma_22)

    # input = [border1, border2,a,b,c,d,e,f,g,h,i]
def objective_function(input):
    error = np.empty(results.shape[0], 1)

    for idx, sigma_22 in enumerate(sigma_22_data):
        error[idx] = (sigma_star_data - f(sigma_22, input)) ** 2

    return error.sum()


results = np.load("sigma_data_pi_old.npy")[0]

sigma_22_data = results[:, 0]
sigma_star_data = results[:, 0]

es = cma.CMAEvolutionStrategy([], 0.5)
es.optimize(objective_function)
