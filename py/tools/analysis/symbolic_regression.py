import feyn
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


results = np.load("sigma_data.npy")

ql = feyn.QLattice()
train = pd.DataFrame(results, columns=["sigma_22", "sigma*"])
models = ql.auto_run(train, output_name='sigma*')


for idx, model in enumerate(models):
    model.plot_signal(train, filename="sigma_model_plot"+ str(idx) + ".svg")
    model.plot(train, filename="sigma_model_"+ str(idx) + ".html")
    sympy_model = model.sympify(symbolic_lr=True, include_weights=True)
    print(idx, sympy_model.as_expr())

    #0.880003 - 0.375364*log(0.270279*sigma22 - 0.258983)
    #0.00566062*sigma22 - 0.395822*log(0.215636*sigma22 - 0.203765) + 0.760855