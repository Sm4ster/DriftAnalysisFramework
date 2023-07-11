import numpy as np
from scipy.stats import ttest_1samp


def has_significance(sample, deviation=0.10, confidence=0.05):
    mean = np.mean(sample)

    if mean == 0:
        return True

    popmean_plus = mean + abs(deviation * mean)
    popmean_minus = mean - abs(deviation * mean)

    p_values = (ttest_1samp(sample, popmean_plus, alternative="less").pvalue,
                ttest_1samp(sample, popmean_minus, alternative="greater").pvalue)
    is_precise = p_values[0] < confidence and p_values[1] < confidence

    return is_precise
