import numpy as np
from scipy.stats import ttest_1samp
from DriftAnalysisFramework.Statistics import p_value

sample = np.random.gamma(2, 2, 1000)
deviation = 0.10

# use scipy for a ttest as a comparison
mean = np.mean(sample)
popmean_plus = mean + abs(deviation * mean)
popmean_minus = mean - abs(deviation * mean)

p_values_sample = np.array([
    ttest_1samp(sample, popmean_plus, alternative="less").pvalue,
    ttest_1samp(sample, popmean_minus, alternative="greater").pvalue
])

assert np.allclose(p_values_sample[0], p_values_sample[1])

# the function we want to actually test
p_values_variance = p_value(sample.mean(), np.var(sample, ddof=1), sample.shape[0], deviation)

if not (np.allclose(p_values_sample[0], p_values_variance)):
    raise Exception("Test failed")

print("Test passed")
