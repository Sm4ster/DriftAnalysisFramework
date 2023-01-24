import numpy as np
import uuid
from DriftAnalysis import DriftAnalysis
from redis import Redis

r = Redis(host='nash.ini.rub.de', port=6379, db=0, password='4xEhjbGNkNPr8UkBQbWL9qmPpXpAeCKMF2G2')
run_id = str(uuid.uuid4())
config = {
    "algorithm": "",
    "target": "",
    "potential": "",
    "constants": "",
    "location": "",
    "variables": "",

}

DriftAnalysis(config, run_id, r)
