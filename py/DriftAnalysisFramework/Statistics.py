import numpy as np
import scipy.special as special


def p_value(mean, variance, sample_size, deviation=0.10):
    pop_mean_plus = mean + abs(deviation * mean)
    pop_mean_minus = mean - abs(deviation * mean)

    # Calculate the t-statistic
    denom = np.sqrt(variance / sample_size)

    t_plus = np.divide(mean - pop_mean_plus, denom)
    t_minus = np.divide(mean - pop_mean_minus, denom)

    # Calculate the p-value
    pval_plus = special.stdtr(sample_size-1, t_plus)  # less
    pval_minus = special.stdtr(sample_size-1, -t_minus)  # greater

    assert np.isclose(pval_minus, pval_plus)

    return pval_plus
