import scipy.integrate as integrate
import scipy.special as special
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

	def __init__(self, mode, dimension, r=0, start=0, stop=8, resolution=100):
		if(mode not in ["rate", "probability"]): raise Exception("The mode has to be 'rate' or 'probability'")
		if(dimension < 2): raise Exception("The dimension has to be at least 2")
		if(r < 0 or r > 1): raise Exception("r has to be between 0 and 1")

		self.d = dimension
		self.r = r

		if(mode == "rate"):
			self.integral = self.rate_integral 
		if(mode == "probability"):
			self.integral = self.probability_integral

		# prepare the function in the given range
		self.result_x = [x / resolution for x in range(int(start*resolution) + 1, int(stop * resolution) + 1)]

		for i in range(int(start*resolution) + 1, int(stop * resolution) + 1):
			self.results[i/resolution] = self.compute(i/resolution)

	def probability_integral(self,t,y):
		return math.exp((-1/2)*(y*y)) * (1/(special.gamma((self.d-1)/2))) * math.exp(-t) * t**(((self.d-1)/2)-1)

	def rate_integral(self,t,y):
		return (math.exp((-1/2)*(y*y)) * self.d / special.gamma((self.d-1)/2)) * ((1- math.sqrt((1-(self.sigma/self.d) * y)**2 + 2* (self.sigma/self.d)**2 * t)) * math.exp(-t) * t**(((self.d-1)/2)-1))


	def compute(self, sigma):
		self.sigma = sigma
		with warnings.catch_warnings():
			warnings.simplefilter("ignore")
			integral = (1/math.sqrt(2*math.pi)) * integrate.dblquad(self.integral, (self.r * self.d) / sigma, ((2 -self.r)*self.d)/self.sigma, lambda y: 0.0 ,lambda y: (((self.r * self.d)**2) / (2 * sigma**2)) - ((self.r * self.d**2)/(sigma**2)) + (self.d/self.sigma)*y-((y**2)/2),epsabs=0)[0]
		return integral


	def get_result_array(self):
		results = []
		for i in self.result_x:
			results.append(self.get(i))
		return results, self.result_x

	def get_min(self):
		return min(self.results, key=self.results.get)

	def get(self, sigma):
		return self.results[sigma]


