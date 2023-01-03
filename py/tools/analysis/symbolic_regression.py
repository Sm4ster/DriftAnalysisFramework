import feyn
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

results = np.load("sigma_data.npy")

ql = feyn.QLattice()
train = pd.DataFrame(results, columns=["sigma_22", "sigma*"])
models = ql.auto_run(train, output_name='sigma*')

for idx, model in enumerate(models):
    model.plot_signal(train, filename="sigma_model_plot" + str(idx) + ".svg")
    model.plot(train, filename="sigma_model_" + str(idx) + ".html")
    sympy_model = model.sympify(symbolic_lr=True, include_weights=True, signif=2)
    print(idx, sympy_model.as_expr())

    # 0.9427 - 0.686386*log(log(0.450526*sigma22 + 1.00099))

    # 0.98 - 0.35*log(log(0.51*sigma22 + 1.0)**2)
