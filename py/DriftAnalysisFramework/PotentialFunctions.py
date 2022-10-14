import numpy as np
from mathjspy import MathJS


class Expression:
    dimension = 2
    mjs = None
    derivations = None
    variables = {}

    def __init__(self, expression, constants):
        self.expression = expression
        self.variables.update(constants)

        self.mjs = MathJS()
        self.mjs.update(constants)
        self.mjs.update({
            "dim": 2
        })

    def potential(self, state):
        # merge all state variables into the dictionary
        self.variables.update(state)

        # Set variables used in equations from a dictionary
        self.mjs.update(self.variables)

        # Evaluate an expression
        return self.mjs.eval(self.expression)
