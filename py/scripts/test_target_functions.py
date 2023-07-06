from DriftAnalysisFramework import Fitness as tf
import numpy as np

def f(x,y):
    return 2*x**2 + y**2

target = tf.ConvexQuadratic({"A": 2, "B": 0, "C": 1})

input = np.random.rand(5, 2)
print(input)

print(target.eval(input))
print(target.eval(input[4]))
print(f(input[0][0], input[0][1]))
print(f(input[4][0], input[4][1]))



