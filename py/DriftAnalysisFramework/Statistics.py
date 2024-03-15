import numpy as np
from scipy.stats import ttest_1samp, t


def has_significance(sample, deviation=0.10, confidence=0.05):
    mean = np.mean(sample)

    if mean == 0:
        return True

    popmean_plus = mean + abs(deviation * mean)
    popmean_minus = mean - abs(deviation * mean)

    p_values = (ttest_1samp(sample, popmean_plus, alternative="less").pvalue,
                ttest_1samp(sample, popmean_minus, alternative="greater").pvalue)
    is_precise = p_values[0] < confidence and p_values[1] < confidence

    return is_precise, p_values


def p_values(mean, variance, sample_size, deviation=0.10):
    pop_mean_plus = mean + abs(deviation * mean)
    pop_mean_minus = mean - abs(deviation * mean)

    # Calculate standard deviation
    standard_deviation = np.sqrt(variance)

    # Calculate the t-statistic
    t_stat_plus = (mean - pop_mean_plus) / (standard_deviation / np.sqrt(sample_size))
    t_stat_minus = (mean - pop_mean_minus) / (standard_deviation / np.sqrt(sample_size))

    # Calculate the p-value
    p_value_plus = 1 - t.cdf(abs(t_stat_plus), df=sample_size - 1)
    p_value_minus = t.cdf(abs(t_stat_minus), df=sample_size - 1)

    return np.array([p_value_minus, p_value_plus])
