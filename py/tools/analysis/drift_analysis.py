import numpy as np
import uuid
from DriftAnalysis import DriftAnalysis
from redis import Redis
from DriftAnalysisFramework import AnalysisTools

r = Redis(host='nash.ini.rub.de', port=6379, db=0, password='4xEhjbGNkNPr8UkBQbWL9qmPpXpAeCKMF2G2')
run_id = str(uuid.uuid4())

# potential functions

baseline = {"expression": "log(norm(m))"}


ul_tuple = AnalysisTools.get_ul_tuple()
AAG = {
    "expression": "log(norm(m)) + max(0, v*log((alpha * l * norm(m))/(2 * sigma)), v*log(((alpha^(1/4)) * sigma * 2)/(u * norm(m))))",
    "constants": {
        "v": 0.1,
        "u": ul_tuple[0],
        "l": ul_tuple[1]
    }
}

# FG = {
#     "expression": "log(norm(m)) + v_1 + max(0, log(sigma/(c*sigma_*)), log(sigma_*/(c*sigma))) + v_2 * log(sigma_22)^2",
#     "functions": AnalysisTools.sigma_star
# }

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
            "max": 10,
            "quantity": 6,
            "scale": "linear",
            "distribution": "grid"
        }
    }
}

print(OPO_config)
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

analysis = DriftAnalysis(config, run_id)
analysis.start()

if analysis.is_finished():
    drifts = np.empty(len(analysis.results) * len(analysis.results[0]))

    # slice out the results
    for location_idx, location_result in enumerate(analysis.results):
        for state_idx, state_result in enumerate(location_result):
            drifts[location_idx * len(analysis.results[0]) + state_idx] = state_result["confident_drift"]

    print("Mean drift " + str(drifts.mean()))
    print("Minimal drift " + str(np.amax(drifts)))
    print("Variance " + str(drifts.var()))
