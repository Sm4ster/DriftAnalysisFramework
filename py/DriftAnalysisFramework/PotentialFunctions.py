import numpy as np
from mathjspy import MathJS


class Expression:
    dimension = 2
    mjs = None
    derivations = None
    variables = {}

    def __init__(self, potential, constants):
        self.expression = potential["expression"]
        self.variables.update(constants)

        self.mjs = MathJS()
        self.mjs.update(constants)

        if "constants" in potential:
            self.mjs.update(potential["constants"])

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


class Function:
    dimension = 2
    constants = None
    function = None

    def __init__(self, potential, constants):
        self.constants = constants
        self.function = potential["function"]

        if "constants" in potential:
            self.constants.update(potential["constants"])

    # @formatter:off
    def baseline(self, state, constants):
        return np.log(np.linalg.norm(state["m"]))

    def AAG(self, state, constants):
        return np.log(np.linalg.norm(state["m"])) + np.max([0,
        constants["v"] * np.log((constants["alpha"] * constants["l"] * np.linalg.norm(state["m"])) / (2 * state["sigma"])),
        constants["v"] * np.log((np.power(constants["alpha"], 1 / 4) * state["sigma"] * 2) / (constants["u"] * np.linalg.norm(state["m"])))
        ])

    def FG(self, state, constants):
        return np.log(np.linalg.norm(state["m"]))
    # @formatter:on

    def potential(self, state):
        if self.function == "baseline":
            return self.baseline(state, self.constants)
        if self.function == "AAG":
            return self.AAG(state, self.constants)
        if self.function == "FG":
            return self.FG(state, self.constants)
