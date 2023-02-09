import numpy as np
from definitions import DATA_PATH


class Expression:
    dimension = 2
    mjs = None
    derivations = None
    variables = {}

    def __init__(self, potential, constants):
        self.expression = potential["expression"]
        self.variables.update(constants)

    # self.mjs = MathJS()
    #  self.mjs.update(constants)

    # if "constants" in potential:
    #    self.mjs.update(potential["constants"])

    #  self.mjs.update({
    #      "dim": 2
    #   })

    def potential(self, state):
        # merge all state variables into the dictionary
        self.variables.update(state)

        # Set variables used in equations from a dictionary
    #  self.mjs.update(self.variables)

    # Evaluate an expression
    #   return self.mjs.eval(self.expression)


class Function:
    dimension = 2
    constants = None
    function = None
    raw_data = {}
    data = {}

    def __init__(self, potential, constants, data=None):
        self.constants = constants
        self.function = potential["function"]

        if data != None:
            for data_point in data:
                self.raw_data[data_point[0]] = np.load(DATA_PATH + data_point[1])

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
        return np.log(np.linalg.norm(state["m"])) + constants["v_1"] + max(0, np.log(state["sigma"]/(constants["c"]*state["sigma_star"])), np.log(state["sigma_star"]/(constants["c"] * state["sigma"]))) + constants["v_2"] * np.log(state["sigma_var"])**2
    # @formatter:on

    def potential(self, state, is_normal_form=False):
        if self.function == "baseline":
            return self.baseline(state, self.constants)
        if self.function == "AAG":
            return self.AAG(state, self.constants)
        if self.function == "FG":
            state["sigma_star"], state["sigma_var"] = self.sigma_star(state, is_normal_form)
            return self.FG(state, self.constants)

    def sigma_star(self, state, is_normal_form):
        if not "sigma_star" in self.data:
            # prep data
            self.data = np.empty([self.raw_data["sigma_star"].shape[0], 3])
            self.data[:, :2] = self.raw_data["sigma_star"][:, :2]
            self.data[:, 2] = np.arccos(self.raw_data["sigma_star"][:, 2])

            # extract relevant data
            self.kappa_array = np.sort(np.unique(self.data[:, 1]))
            self.alpha_array = np.sort(np.unique(self.data[:, 2]))

        if is_normal_form:
            sigma_var = state["cov_m"][1][1]
            sigma_star = self.get_sigma_star(state)
        else:
            m, C, sigma, scaling_factor, distance_factor = self.transform_state_to_normal_form(state["m"],
                                                                                               state["cov_m"],
                                                                                               state["sigma"])
            sigma_var = C[1][1]
            sigma_star = self.get_sigma_star({"m": m, "sigma_var": sigma_var}) / (
                        np.sqrt(scaling_factor) * distance_factor)

        # implement nearest neighbors myself, because deserialization does not work well
        # make a prediction for a new point
        return sigma_star, sigma_var

    def transform_state_to_normal_form(self, m, C, sigma):
        # get the the transformation matrix
        A = np.linalg.eig(C)[1]

        # rotate the coordinate system such that the eigenvalues of
        # the covariance matrix are parallel to the coordinate axis
        C_rot = A.T @ C @ A
        m_rot = A.T @ m

        # calculate the scaling factor which brings the covariance matrix to det = 1
        scaling_factor = 1 / (np.sqrt(np.linalg.det(C_rot)))

        m_normal = np.dot(m_rot, scaling_factor)
        C_normal = np.dot(C_rot, scaling_factor)

        # The distance factor sets norm(m) = 1. To keep the proportion between the distance
        # of the center to the optimum and the spread of the distribution we adjust sigma.
        distance_factor = 1 / np.linalg.norm(m_normal)

        m_normal = m_normal * distance_factor
        sigma_normal = sigma * distance_factor

        # We transform m to (cos, sin)
        x_flip = np.array([[-1, 0], [0, 1]])
        y_flip = np.array([[1, 0], [0, -1]])
        axis_swap = np.array([[0, 1], [1, 0]])

        if m_normal[0] < 0:
            C_normal = x_flip @ C_normal @ x_flip.T
            m_normal = x_flip @ m_normal

        if m_normal[1] < 0:
            C_normal = y_flip @ C_normal @ y_flip.T
            m_normal = y_flip @ m_normal

        if m_normal[0] < np.cos(np.pi / 4):
            C_normal = axis_swap @ C_normal @ axis_swap.T
            m_normal = axis_swap @ m_normal

        return m_normal, C_normal, sigma_normal, scaling_factor, distance_factor

    def get_sigma_star(self, state):
        target_alpha = np.arccos(state["m"][0])
        target_kappa = state["sigma_var"]
        print(target_alpha, target_kappa)
        # extract searched data
        alpha = self.find_closest_values(self.alpha_array, target_alpha)
        kappa = self.find_closest_values(self.kappa_array, target_kappa)
        print(alpha, kappa)
        lower_alpha_idx = np.where(self.data[:, 2] == alpha[0])
        upper_alpha_idx = np.where(self.data[:, 2] == alpha[1])
        lower_kappa_idx = np.where(self.data[:, 1] == kappa[0])
        upper_kappa_idx = np.where(self.data[:, 1] == kappa[1])
        print(np.intersect1d(lower_alpha_idx, lower_kappa_idx))
        values = [
            self.data[np.intersect1d(lower_alpha_idx, lower_kappa_idx)][0][0],
            self.data[np.intersect1d(upper_alpha_idx, lower_kappa_idx)][0][0],
            self.data[np.intersect1d(lower_alpha_idx, upper_kappa_idx)][0][0],
            self.data[np.intersect1d(upper_alpha_idx, upper_kappa_idx)][0][0]
        ]
        return self.interpolate(alpha, kappa, values, [target_alpha, target_kappa])

    def find_closest_values(self, arr, target):
        # Find the index of the first value in the array greater than target
        idx = np.searchsorted(arr, target)

        # Check if the exact value is in the array
        if target in arr:
            values = [target, arr[idx - 1 if idx > 0 else idx + 1]]
            values.sort()
            return values
        else:
            # Get the closest value greater than target
            greater = arr[idx] if idx < len(arr) else None

            # Get the closest value smaller than target
            smaller = arr[idx - 1] if idx > 0 else None
        return [smaller, greater]

    def interpolate(self, x, y, values, target):
        x_1, x_2, x = x[0], x[1], target[0]
        y_1, y_2, y = y[0], y[1], target[1]

        return (1 / ((x_2 - x_1) * (y_2 - y_1)) * (
                values[0] * (x_2 - x) * (y_2 - y) + values[1] * (x - x_1) * (y_2 - y) + values[2] * (x_2 - x) * (
                y - y_1) + values[3] * (x - x_1) * (y - y_1)))
