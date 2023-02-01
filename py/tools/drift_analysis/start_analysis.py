import numpy as np
import uuid
from DriftAnalysisFramework.DriftAnalysis import DriftAnalysis
from redis import Redis
import pickle
import time

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
        "u": 3.1,
        "l": 1.3
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
            "min": 0.00235,
            "max": 235,
            "quantity": 100000,
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
                "quantity": 1,
                "min": 1,
                "max": 1
            },
            {
                "distribution": "grid",
                "scale": "linear",
                "quantity": 1,
                "min": 0,
                "max": 0
            }
        ],
    },
}

CMA_config = {
    "algorithm": "CMA-ES",
    "constants": {
        "d": 2,
        "p_target": 0.1818,
        "c_cov": 0.2,
        "alpha": 1 / 2
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
                "max": np.pi / 4
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
config.update(OPO_config)

analysis = DriftAnalysis(config, run_id, queue=True)
analysis.start(job_chunk=5, verbosity=1)

analysis.save_jobs_ids()
analysis.q = None

with open("OPO-1", 'wb') as f:
    pickle.dump(analysis, f)


# while not analysis.is_finished():
#     time.sleep(5)
#
# analysis.get_results()
# for pf_idx, pf in enumerate(analysis.pf):
#     drifts = np.empty(len(analysis.results))
#
#     # slice out the results
#     for state_idx, state_result in enumerate(analysis.results):
#         drifts[state_idx] = state_result["results"][pf_idx]["drift"]
#
#     print("Mean drift " + str(drifts.mean()))
#     print("Minimal drift " + str(np.amax(drifts)))
#     print("Drift range " + str(np.amax(drifts) - np.amin(drifts)))
#     print("Variance " + str(drifts.var()))
#     print("\n")
