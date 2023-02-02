import cma
import numpy as np


def f0(sigma22, a=25, b=1.5, c=1.8, d=2.5, e=1.01):
    return (a * ((b * sigma22 + c) * d) ** e)


def f1(sigma22, a=0.98, b=0.35, c=0.51, d=1.0, e=1):
    return (a * ((b * sigma22 + c) * d) ** e)
    # return a - b * np.log(c * sigma22 + d) ** e


def f2(sigma22, a=25, b=1.5, c=1.8, d=2.5, e=1.01):
    return (a * ((b * sigma22 + c) * d) ** e)


def f(sigma_var, input):
    if sigma_var < input[0]:
        input_ = input[2:7]
        return f0(sigma_var, *input_)
    elif sigma_var < input[1]:
        input_ = input[7:12]
        return f1(sigma_var, *input_)
    else:
        input_ = input[12:17]
        return f2(sigma_var, *input_)

    # input = [border1, border2,a,b,c,d,e,f,g,h,i]


def objective_function(input):
    error = np.empty([dataset.shape[0], 1])
    for idx, sigma_var in enumerate(sigma_var_data):
        error[idx] = ((sigma_star_data[idx] - f(sigma_var, input)) * sigma_var ** 2) ** 2
        if input[0] > input[1]-9: error[idx] = 1000000
        # error[idx] = (sigma_star_data[idx] - f(sigma_var, input)) ** 2
        # else:
        #     error[idx] = ((sigma_star_data[idx] - f2(sigma_var, *input)) * sigma_var**2) ** 2

    return error.sum()


results = np.load("../../data/sigma_data_pi_2023_01_21.npy")

curve_idx = 0
distance_idx = 0

dataset = results[curve_idx][distance_idx]

sigma_var_data = dataset[:, 1]
sigma_star_data = dataset[:, 0]

es = cma.CMAEvolutionStrategy([0.1, 10,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1], 0.0001)
es.optimize(objective_function)

print(np.array2string(es.result[0], separator=","))
