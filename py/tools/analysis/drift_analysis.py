import numpy as np
import uuid
from DriftAnalysis import DriftAnalysis
from redis import Redis
import pickle

r = Redis(host='nash.ini.rub.de', port=6379, db=0, password='4xEhjbGNkNPr8UkBQbWL9qmPpXpAeCKMF2G2')
run_id = str(uuid.uuid4())

# -------- Potential Functions -------- #
# @formatter:off

baseline = {
    "mode": "function",
    "expression": "log(norm(m))",
    "function": "baseline"
}

# ul_tuple = AnalysisTools.get_ul_tuple()
AAG = {
    "mode": "function",
    "expression": "log(norm(m)) + max(0, v*log((alpha * l * norm(m))/(2 * sigma)), v*log(((alpha^(1/4)) * sigma * 2)/(u * norm(m))))",
    "function": "AAG",
    "constants": {
        "v": 0.001680723622387344,
        "u": 1.3,
        "l": 3.1
    }
}

FG = {
    "mode": "function",
    "expression": "log(norm(m)) + v_1 + max(0, log(sigma/(c*sigma_*)), log(sigma_*/(c*sigma))) + v_2 * log(sigma_22)^2",
    "function": "FG"
}

# @formatter:on
potential_functions = [baseline, AAG]

OPO_config = {
    "algorithm": "1+1-ES",
    "constants": {
        "alpha": 2
    },
    "potential": potential_functions,
    "variables": {
        "sigma": {
            "variation": True,
            "min": 0.01,
            "max": 10,
            "quantity": 6,
            "scale": "linear",
            "distribution": "grid"
        }
    },
    "location": {
        "type": "grid",
        "vector": [
            {
                "distribution": "grid",
                "scale": "linear",
                "quantity": 2,
                "min": 0,
                "max": 1
            },
            {
                "distribution": "grid",
                "scale": "linear",
                "quantity": 2,
                "min": 1,
                "max": 2
            }
        ],
    },
}

CMA_config = {
    "algorithm": "CMA-ES",
    "constants": {
        "d": 2,
        "p_target": 0.1818,
        "alpha": 0.1818,
        "c_cov": 0.2
    },
    "potential": potential_functions,
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
            "min": 5,
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
    },
    "location": {
        "type": "arc",
        "distance": {
            "distribution": "grid",
            "scale": "linear",
            "quantity": 3,
            "min": 1,
            "max": 3
        },
        "angles": [
            {
                "distribution": "grid",
                "scale": "linear",
                "quantity": 5,
                "min": 0,
                "max": np.pi/4
            },
        ],
    },
}

config = {
    "target": {
        "A": 1,
        "B": 0,
        "C": 1
    },

}
config.update(CMA_config)

analysis = DriftAnalysis(config, run_id)
# analysis.start(job_chunk=5, verbosity=1)

# with open("test", 'wb') as f:
#     pickle.dump(analysis, f)

# if analysis.is_finished():
#     print(analysis.results)
#     for pf_idx, pf in enumerate(potential_functions):
#         drifts = np.empty(len(analysis.results) * len(analysis.results[0]))
#
#         # slice out the results
#         for location_idx, location_result in enumerate(analysis.results):
#             for state_idx, state_result in enumerate(location_result):
#                 drifts[location_idx * len(analysis.results[0]) + state_idx] = state_result["results"][pf_idx]["drift"]
#
#         print(pf["function"])
#         print("Mean drift " + str(drifts.mean()))
#         print("Minimal drift " + str(np.amax(drifts)))
#         print("Drift range " + str(np.amax(drifts) - np.amin(drifts)))
#         print("Variance " + str(drifts.var()))
#         print("\n")
