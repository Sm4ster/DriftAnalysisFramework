import numpy as np
import scipy.special as special


def p_value(mean, variance, sample_size, deviation=0.10):
    """
    This is a one-sided t-test that returns a p-value for the alternative hypothesis that the
    deviating mean [mean + abs(deviation * mean)] is larger than the given mean.
    The null-hypothesis is both means are equal.
    """
    # Calculate alternative population mean with the deviation
    pop_mean_plus = mean + abs(deviation * mean)

    # Calculate the t-statistic
    denom = np.sqrt(variance / sample_size)

    t_plus = np.divide(mean - pop_mean_plus, denom)

    # Calculate the p-value
    pval_plus = special.stdtr(sample_size-1, t_plus)

    return pval_plus
