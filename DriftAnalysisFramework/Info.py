from welford import Welford
import numpy as np


class CMA_ES:
    fields = {
        "alpha": {"shape": [1], "type": "mean"},
        "kappa": {"shape": [1], "type": "mean"},
        "sigma": {"shape": [1], "type": "mean"},

        "m": {"shape": [2], "type": "mean"},
        "C": {"shape": [2, 2], "type": "mean"},
        "sigma_raw": {"shape": [1], "type": "mean"}
    }

    normal_form = None  # [alpha, kappa, sigma_normal]
    raw_params = None  # [m0, m1, C00, C01, C10, C11, sigma_raw]

    def __init__(self):
        self.normal_form = Welford()
        self.raw_params = Welford()

    def add_data(self, normal_form, raw_params, transformation_parameters, misc_parameters):
        with np.errstate(divide='ignore', invalid='ignore'):
            self.normal_form.add_all(
                np.array(
                    [
                        normal_form["alpha"],
                        normal_form["kappa"],
                        normal_form["sigma"],
                    ]
                ).T
            )
            self.raw_params.add_all(
                np.array(
                    [
                        raw_params["m"][:, 0],
                        raw_params["m"][:, 1],
                        raw_params["C"][:, 0, 0],
                        raw_params["C"][:, 0, 1],
                        raw_params["C"][:, 1, 0],
                        raw_params["C"][:, 1, 1],
                        raw_params["sigma"],
                    ]
                ).T
            )

    def get_data(self):
        return {
            "alpha": self.normal_form.mean[0],
            "alpha_std": np.sqrt(self.normal_form.var_p[0]),

            "kappa": self.normal_form.mean[1],
            "kappa_std": np.sqrt(self.normal_form.var_p[1]),

            "sigma": self.normal_form.mean[2],
            "sigma_std": np.sqrt(self.normal_form.var_p[2]),

            "m": [
                self.raw_params.mean[0],
                self.raw_params.mean[1],
            ],
            "m_std": [
                np.sqrt(self.raw_params.var_p[0]),
                np.sqrt(self.raw_params.var_p[1]),
            ],
            "C": [
                [self.raw_params.mean[2], self.raw_params.mean[3]],
                [self.raw_params.mean[4], self.raw_params.mean[5]],
            ],
            "C_std": [
                [np.sqrt(self.raw_params.var_p[2]), np.sqrt(self.raw_params.var_p[3])],
                [np.sqrt(self.raw_params.var_p[4]), np.sqrt(self.raw_params.var_p[5])],
            ],
            "sigma_raw": self.raw_params.mean[6],
            "sigma_raw_std": np.sqrt(self.raw_params.var_p[6])
        }


class OnePlusOne_CMA_ES:
    fields = {
        "success": {"shape": [], "type": "count"},

        "alpha": {"shape": [1], "type": "mean"},
        "kappa": {"shape": [1], "type": "mean"},
        "sigma": {"shape": [1], "type": "mean"},

        "alpha_success": {"shape": [1], "type": "mean"},
        "kappa_success": {"shape": [1], "type": "mean"},
        "sigma_success": {"shape": [1], "type": "mean"},

        "alpha_no_success": {"shape": [1], "type": "mean"},
        "kappa_no_success": {"shape": [1], "type": "mean"},
        "sigma_no_success": {"shape": [1], "type": "mean"},

        "m": {"shape": [2], "type": "mean"},
        "C": {"shape": [2, 2], "type": "mean"},
        "sigma_raw": {"shape": [1], "type": "mean"},

        "m_success": {"shape": [2], "type": "mean"},
        "C_success": {"shape": [2, 2], "type": "mean"},
        "sigma_raw_success": {"shape": [1], "type": "mean"},

        "m_no_success": {"shape": [2], "type": "mean"},
        "C_no_success": {"shape": [2, 2], "type": "mean"},
        "sigma_raw_no_success": {"shape": [1], "type": "mean"}
    }

    successes = 0
    normal_form = None  # [alpha, kappa, sigma_normal]
    normal_form_success = None  # [alpha, kappa, sigma_normal]
    normal_form_no_success = None  # [alpha, kappa, sigma_normal]
    raw_params = None  # [m0, m1, C00, C01, C10, C11, sigma_raw]
    raw_params_success = None  # [m0, m1, C00, C01, C10, C11, sigma_raw]
    raw_params_no_success = None  # [m0, m1, C00, C01, C10, C11, sigma_raw]

    def __init__(self):
        self.normal_form = Welford()
        self.normal_form_success = Welford()
        self.normal_form_no_success = Welford()

        self.raw_params = Welford()
        self.raw_params_success = Welford()
        self.raw_params_no_success = Welford()

    def add_data(self, normal_form, raw_params, transformation_parameters, misc_parameters):
        self.successes += misc_parameters["success"].sum()

        self.normal_form.add_all(
            np.array(
                [
                    normal_form["alpha"],
                    normal_form["kappa"],
                    normal_form["sigma"],
                ]
            ).T
        )

        self.raw_params.add_all(
            np.array(
                [
                    raw_params["m"][:, 0],
                    raw_params["m"][:, 1],
                    raw_params["C"][:, 0, 0],
                    raw_params["C"][:, 0, 1],
                    raw_params["C"][:, 1, 0],
                    raw_params["C"][:, 1, 1],
                    raw_params["sigma"],
                ]
            ).T
        )

        # save successful and unsuccessful follow-up state
        # for mean, geometrical mean, variance and geometrical variance.
        # we ignore errors as they come from dealing with the logs
        with np.errstate(divide='ignore', invalid='ignore'):
            mask = np.array(misc_parameters["success"] == 1).T[0]
            self.normal_form_success.add_all(
                np.array(
                    [
                        normal_form["alpha"][mask],
                        normal_form["kappa"][mask],
                        normal_form["sigma"][mask],
                    ]
                ).T
            )

            self.raw_params_success.add_all(
                np.array(
                    [
                        raw_params["m"][mask][:, 0],
                        raw_params["m"][mask][:, 1],
                        raw_params["C"][mask][:, 0, 0],
                        raw_params["C"][mask][:, 0, 1],
                        raw_params["C"][mask][:, 1, 0],
                        raw_params["C"][mask][:, 1, 1],
                        raw_params["sigma"][mask],
                    ]
                ).T
            )

            mask = np.array(misc_parameters["success"] == 0).T[0]
            self.normal_form_no_success.add_all(
                np.array(
                    [
                        normal_form["alpha"][mask],
                        normal_form["kappa"][mask],
                        normal_form["sigma"][mask],
                    ]
                ).T
            )

            self.raw_params_no_success.add_all(
                np.array(
                    [
                        raw_params["m"][mask][:, 0],
                        raw_params["m"][mask][:, 1],
                        raw_params["C"][mask][:, 0, 0],
                        raw_params["C"][mask][:, 0, 1],
                        raw_params["C"][mask][:, 1, 0],
                        raw_params["C"][mask][:, 1, 1],
                        raw_params["sigma"][mask],
                    ]
                ).T
            )

    def get_data(self):
        return {
            "success": self.successes,

            "alpha": self.normal_form.mean[0],
            "alpha_std": np.sqrt(self.normal_form.var_p[0]),

            "kappa": self.normal_form.mean[1],
            "kappa_std": np.sqrt(self.normal_form.var_p[1]),

            "sigma": self.normal_form.mean[2],
            "sigma_std": np.sqrt(self.normal_form.var_p[2]),

            "alpha_success": self.normal_form_success.mean[0] if self.successes > 1 else 0,
            "alpha_success_std": np.sqrt(self.normal_form_success.var_p[0]) if self.successes > 2 else 0,

            "kappa_success": self.normal_form_success.mean[1] if self.successes > 1 else 0,
            "kappa_success_std": np.sqrt(self.normal_form_success.var_p[1]) if self.successes > 2 else 0,

            "sigma_success": self.normal_form_success.mean[2] if self.successes > 1 else 0,
            "sigma_success_std": np.sqrt(self.normal_form_success.var_p[2]) if self.successes > 2 else 0,

            "alpha_no_success": self.normal_form_no_success.mean[0],
            "alpha_no_success_std": np.sqrt(self.normal_form_no_success.var_p[0]),

            "kappa_no_success": self.normal_form_no_success.mean[1],
            "kappa_no_success_std": np.sqrt(self.normal_form_no_success.var_p[1]),

            "sigma_no_success": self.normal_form_no_success.mean[2],
            "sigma_no_success_std": np.sqrt(self.normal_form_no_success.var_p[2]),

            "m": [
                self.raw_params.mean[0],
                self.raw_params.mean[1],
            ],
            "m_std": [
                np.sqrt(self.raw_params.var_p[0]),
                np.sqrt(self.raw_params.var_p[1]),
            ],
            "C": [
                [self.raw_params.mean[2], self.raw_params.mean[3]],
                [self.raw_params.mean[4], self.raw_params.mean[5]],
            ],
            "C_std": [
                [np.sqrt(self.raw_params.var_p[2]), np.sqrt(self.raw_params.var_p[3])],
                [np.sqrt(self.raw_params.var_p[4]), np.sqrt(self.raw_params.var_p[5])],
            ],
            "sigma_raw": self.raw_params.mean[6],
            "sigma_raw_std": np.sqrt(self.raw_params.var_p[6]),

            # success
            "m_success": [
                self.raw_params_success.mean[0] if self.successes > 1 else 0,
                self.raw_params_success.mean[1] if self.successes > 1 else 0,
            ],
            "m_success_std": [
                np.sqrt(self.raw_params_success.var_p[0]) if self.successes > 2 else 0,
                np.sqrt(self.raw_params_success.var_p[1]) if self.successes > 2 else 0,
            ],
            "C_success": [
                [
                    self.raw_params_success.mean[2] if self.successes > 1 else 0,
                    self.raw_params_success.mean[3] if self.successes > 1 else 0
                ],
                [
                    self.raw_params_success.mean[4] if self.successes > 1 else 0,
                    self.raw_params_success.mean[5] if self.successes > 1 else 0
                ],
            ],
            "C_success_std": [
                [
                    np.sqrt(self.raw_params_success.var_p[2]) if self.successes > 2 else 0,
                    np.sqrt(self.raw_params_success.var_p[3]) if self.successes > 2 else 0
                ],
                [
                    np.sqrt(self.raw_params_success.var_p[4]) if self.successes > 2 else 0,
                    np.sqrt(self.raw_params_success.var_p[5]) if self.successes > 2 else 0
                ],
            ],
            "sigma_raw_success": self.raw_params_success.mean[6] if self.successes > 1 else 0,
            "sigma_raw_success_std": np.sqrt(self.raw_params_success.var_p[6]) if self.successes > 2 else 0,

            # no success
            "m_no_success": [
                self.raw_params_no_success.mean[0],
                self.raw_params_no_success.mean[1],
            ],
            "m_no_success_std": [
                np.sqrt(self.raw_params_no_success.var_p[0]),
                np.sqrt(self.raw_params_no_success.var_p[1]),
            ],
            "C_no_success": [
                [self.raw_params_no_success.mean[2], self.raw_params_no_success.mean[3]],
                [self.raw_params_no_success.mean[4], self.raw_params_no_success.mean[5]],
            ],
            "C_no_success_std": [
                [np.sqrt(self.raw_params_no_success.var_p[2]), np.sqrt(self.raw_params_no_success.var_p[3])],
                [np.sqrt(self.raw_params_no_success.var_p[4]), np.sqrt(self.raw_params_no_success.var_p[5])],
            ],
            "sigma_raw_no_success": self.raw_params_no_success.mean[6],
            "sigma_raw_no_success_std": np.sqrt(self.raw_params_no_success.var_p[6])
        }
