import numpy as np
import uuid
from DriftAnalysis import DriftAnalysis
from redis import Redis
from DriftAnalysisFramework import AnalysisTools

r = Redis(host='nash.ini.rub.de', port=6379, db=0, password='4xEhjbGNkNPr8UkBQbWL9qmPpXpAeCKMF2G2')
run_id = str(uuid.uuid4())

# -------- Potential Functions -------- #
# @formatter:off

baseline = {
    "mode": "function",
    "expression": "log(norm(m))",
    "function": lambda state, constants: np.log(np.linalg.norm(state["m"]))
}

# ul_tuple = AnalysisTools.get_ul_tuple()
AAG = {
    "mode": "function",
    "expression": "log(norm(m)) + max(0, v*log((alpha * l * norm(m))/(2 * sigma)), v*log(((alpha^(1/4)) * sigma * 2)/(u * norm(m))))",
    "function": lambda state, constants: np.log(np.linalg.norm(state["m"])) + np.max([0,
        constants["v"] * np.log((constants["alpha"] * constants["l"] * np.linalg.norm(state["m"])) / (2 * state["sigma"])),
        constants["v"] * np.log((np.power(constants["alpha"], 1 / 4) * state["sigma"] * 2) / (constants["u"] * np.linalg.norm(state["m"])))
        ]),
    "constants": {
        "v": 0.001680723622387344,
        "u": 1.3,
        "l": 3.1
    }
}

FG = {
    "mode": "function",
    "expression": "log(norm(m)) + v_1 + max(0, log(sigma/(c*sigma_*)), log(sigma_*/(c*sigma))) + v_2 * log(sigma_22)^2",
    "functions": AnalysisTools.sigma_star
}

# @formatter:on


OPO_config = {
    "algorithm": "1+1-ES",
    "constants": {
        "alpha": 2
    },
    "potential": AAG,
    "variables": {
        "sigma": {
            "variation": True,
            "min": 5,
            "max": 1000,
            "quantity": 6,
            "scale": "linear",
            "distribution": "grid"
        }
    }
}

CMA_config = {
    "algorithm": "CMA-ES",
    "constants": {
        "d": 2,
        "p_target": 0.1818,
        "c_cov": 0.2
    },
    "variables": {
        "sigma": {
            "variation": True,
            "min": 1,
            "max": 10,
            "quantity": 10,
            "scale": "linear",
            "distribution": "grid"
        },
        "Sigma_11": {
            "variation": True,
            "min": 1,
            "max": 10,
            "quantity": 10,
            "scale": "linear",
            "distribution": "grid"
        },
        "Sigma_12|21": {
            "variation": True,
            "min": 1,
            "max": 10,
            "quantity": 10,
            "scale": "linear",
            "distribution": "grid"
        },
        "Sigma_22": {
            "variation": True,
            "min": 1,
            "max": 10,
            "quantity": 10,
            "scale": "linear",
            "distribution": "grid"
        }
    }
}

config = {
    "target": {
        "A": 1,
        "B": 0,
        "C": 1
    },
    "location": {
        "vector": [
            {
                "distribution": "grid",
                "scale": "linear",
                "quantity": 3,
                "min": 1,
                "max": 3
            },
            {
                "distribution": "grid",
                "scale": "linear",
                "quantity": 3,
                "min": 1,
                "max": 3
            }
        ]
    },
}
config.update(OPO_config)

analysis = DriftAnalysis(config, run_id, redis_connection=r)
analysis.start(verbosity=1)

if analysis.is_finished():
    drifts = np.empty(len(analysis.results) * len(analysis.results[0]))

    # slice out the results
    for location_idx, location_result in enumerate(analysis.results):
        for state_idx, state_result in enumerate(location_result):
            drifts[location_idx * len(analysis.results[0]) + state_idx] = state_result["confident_drift"]

    print("Mean drift " + str(drifts.mean()))
    print("Minimal drift " + str(np.amax(drifts)))
    print("Drift range " + str(np.amax(drifts) - np.amin(drifts)))
    print("Variance " + str(drifts.var()))
