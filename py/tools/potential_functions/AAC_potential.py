from DriftAnalysisFramework import AnalysisTools as AT
import numpy as np


d= 2
alpha = 2

r_dash = 1 - np.exp(- np.log(alpha) / (d * np.log(alpha) - 1))
SP_r_dash = AT.SuccessProbability("probability", d, r=r_dash)


lu_list = AT.get_ul_tuple(d, alpha)

for lu in lu_list:

    p_dash = SP_r_dash.get_min(l,u)
    v = p_dash / (2 * d * np.log(alpha))


    A = 1 / 2

    l = lu[0][0]
    u = lu[0][1]
    p_l = lu[1][0]
    p_u = lu[1][1]

    p_star = AT.SuccessProbability("probability", d, r=1 - np.exp(-(A / (1 - v)))).get_min()

    B_1 = A * p_star - (5 / 4) * v * np.log(alpha)
    B_2 = v * np.log(alpha) * ((5 * p_l - 1) / 4)
    B_3 = v * np.log(alpha) * ((1 - 5 * p_u) / 4)
    print(l, u, min(B_1, B_2, B_3))




def get_B(d, alpha=2):

# return min(B_1, B_2, B_3)





    return v
