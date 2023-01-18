import feyn
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

results = np.load("sigma_data_pi.npy")


# a = np.array([[[1,1,1,1,1],[2,2,2,2,2],[3,3,3,3,3]],[[11,11,11,11,11],[22,22,22,22,22],[33,33,33,33,33]]], dtype=object)
# print(a.reshape((6,5)))
# data = results.reshape((10000, 5))

data=results[99]

ql = feyn.QLattice()
train = pd.DataFrame(data[:, :2], columns=[ "sigma*", "sigma_var"]) # "angle", "dir_cond_number", "x", "y",
models = ql.auto_run(train, output_name='sigma*')

for idx, model in enumerate(models):
    # model.plot_signal(train, filename="sigma_model_plot" + str(idx) + ".svg")
    # model.plot(train, filename="sigma_model_" + str(idx) + ".html")
    sympy_model = model.sympify(symbolic_lr=True, include_weights=True, signif=2)
    print(idx, sympy_model.as_expr())

    # 0.9427 - 0.686386*log(log(0.450526*sigma22 + 1.00099))

    # 0.98 - 0.35*log(log(0.51*sigma22 + 1.0)**2)


    #48.0*(0.0045 - 0.00037*sigma22)*(13.0*x + 1.1) + 0.34