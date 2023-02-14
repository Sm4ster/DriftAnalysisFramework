#import scipy.integrate as integrate
#import scipy.special as special
import math
import warnings
import numpy as np


class SuccessProbability:
    integral = None
    sigma = None
    d = None
    r = None

    results = {}
    result_x = None

    def __init__(self, mode, dimension, r=0.0, start=0.0, stop=8.0, resolution=150, init=True):
        if (mode not in ["rate", "probability"]): raise Exception("The mode has to be 'rate' or 'probability'")
        if (dimension < 2): raise Exception("The dimension has to be at least 2")
        if (r < 0 or r > 1): raise Exception("r has to be between 0 and 1")

        self.start = start
        self.stop = stop
        self.resolution = resolution

        self.d = dimension
        self.r = r

        if (mode == "rate"):
            self.integral = self.rate_integral
        if (mode == "probability"):
            self.integral = self.probability_integral

        # prepare the function in the given range
        self.result_x = [x / resolution for x in range(int(start * resolution) + 1, int(stop * resolution) + 1)]

        if init: self.init()

    def init(self):
        for i in range(int(self.start * self.resolution) + 1, int(self.stop * self.resolution) + 1):
            self.results[i / self.resolution] = self.compute(i / self.resolution)

    def probability_integral(self, t, y):
        return math.exp((-1 / 2) * (y * y)) * (1 / (special.gamma((self.d - 1) / 2))) * math.exp(-t) * t ** (
                ((self.d - 1) / 2) - 1)

    def rate_integral(self, t, y):
        return (math.exp((-1 / 2) * (y * y)) * self.d / special.gamma((self.d - 1) / 2)) * ((1 - math.sqrt(
            (1 - (self.sigma / self.d) * y) ** 2 + 2 * (self.sigma / self.d) ** 2 * t)) * math.exp(-t) * t ** (((
                                                                                                                        self.d - 1) / 2) - 1))

    def compute(self, sigma):
        self.sigma = sigma
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            integral = (1 / math.sqrt(2 * math.pi)) * \
                       integrate.dblquad(self.integral, (self.r * self.d) / sigma, ((2 - self.r) * self.d) / self.sigma,
                                         lambda y: 0.0, lambda y: (((self.r * self.d) ** 2) / (2 * sigma ** 2)) - (
                                   (self.r * self.d ** 2) / (sigma ** 2)) + (self.d / self.sigma) * y - (
                                                                          (y ** 2) / 2), epsabs=0)[0]
        return integral

    def get_result_array(self):
        results = []
        for i in self.result_x:
            results.append(self.get(i))
        return results, self.result_x

    def get_min(self, l=False, u=False):
        if (l == False): l = self.start
        if (u == False): u = self.stop

        list = []
        for item in self.results.items():
            if item[0] > l and item[0] < u:
                list.append(item[1])

        return np.min(list)

    def get(self, sigma):
        return self.results[sigma]


def get_ul_tuple(d, alpha=2):
    ## determine u and l ##
    sr = SuccessProbability("probability", dimension=d, r=0, start=0, stop=6, resolution=12)

    # get candidates
    pl_candidates = dict(
        (k, sr.results[k]) for k in sr.get_result_array()[1] if sr.results[k] > 1 / 5 and sr.results[k] < 1 / 2)
    pu_candidates = dict(
        (k, sr.results[k]) for k in sr.get_result_array()[1] if sr.results[k] > 0 and sr.results[k] < 1 / 5)

    ul_candidates = []
    for l, pl in pl_candidates.items():
        for u, pu in pu_candidates.items():
            if (u / l - alpha ** (5 / 4) > 0):
                ul_candidates.append(((l, u), (pl, pu), u / l - alpha ** (5 / 4)))

    return ul_candidates


# ul_candidates.sort(key=lambda x: x[2])
# return ul_candidates[1][0],ul_candidates[1][1]


def sigma_star():
    return 1
