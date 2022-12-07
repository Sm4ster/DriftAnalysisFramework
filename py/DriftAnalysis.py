from DriftAnalysisFramework import TargetFunctions, OptimizationAlgorithms, PotentialFunctions
from worker_module import work_job
from rq.registry import ScheduledJobRegistry

import json
from redis import Redis
from rq import Queue
import numpy as np


class DriftAnalysis:
    uuid = None
    dim = 2
    states = {}
    location = []
    location_uuids = []
    results = []
    jobs = []
    matrices = None
    queue = False
    min_max = {}

    def __init__(self, config, uuid, queue=True):
        self.uuid = uuid

        with open('../definitions/algorithms/' + config["algorithm"] + '.json', 'r') as f:
            oa_definition = json.load(f)
        self.matrices = oa_definition["matrices"]

        # if necessary init the queue
        if queue:
            r = Redis(host='nash.ini.rub.de', port=6379, db=0, password='4xEhjbGNkNPr8UkBQbWL9qmPpXpAeCKMF2G2')
            self.q = Queue(connection=r)
        self.queue = queue

        # initialize the target function
        self.tf = TargetFunctions.convex_quadratic(self.dim, config["target"])

        # initialize the algorithm
        oa_class = getattr(OptimizationAlgorithms, oa_definition['python_class'])
        self.oa = oa_class(self.tf, config['constants'])

        # initialize a potential function
        self.pf = PotentialFunctions.Expression(config["potential"], config["constants"])

        # generate states
        self.states, self.min_max["states"] = self.generate_states(config["variables"])

        # generate locations
        self.location, self.min_max["location"] = self.generate_locations(config["location"])

    def start(self):
        options = {
            "matrices": self.matrices,
            # parameters for the batches
            "batch_size": 10,  # number of evaluations before a significance test is performed
            "max_evaluations": 1000,  # if no significant result was obtained we cancel the evaluations of this state
        }

        for idx, starting_location in enumerate(self.location):
            self.oa.set_location(starting_location)
            print("enqueuing")
            if self.queue:
                job = self.q.enqueue(work_job, self.oa, self.pf, self.states, options)
                self.jobs.append({
                    "id": idx,
                    "location": starting_location,
                    "job": job,
                    "not_in_results": True
                })
            else:
                self.jobs.append({
                    "id": idx,
                    "location": starting_location,
                    "result": work_job(self.oa, self.pf, self.states, options),
                    "not_in_results": True
                })

        if self.queue:
            registry = ScheduledJobRegistry(queue=self.q)
            # print(registry.get_job_ids())

    def get_locations(self):
        return [{"id": idx, "location": loc} for idx, loc in enumerate(self.location)]

    def get_new_results(self):
        new_results = []

        for job_wrapper in self.jobs:
            if job_wrapper["not_in_results"]:
                # continue if the job in the queue doesn't have any results yet
                if self.queue and job_wrapper["job"].result is None:
                    continue

                new_results.append({
                    "id": job_wrapper["id"],
                    "location": job_wrapper["location"],
                    "data": job_wrapper["job"].result if self.queue else job_wrapper["result"]
                })
                job_wrapper["not_in_results"] = False

        return new_results

    def all_jobs_in_results(self):
        if len(self.jobs) < len(self.location):
            return False

        return all(not job["not_in_results"] for job in self.jobs)

    def generate_locations(self, config):
        sequences = []
        min_max = []
        for idx, el in enumerate(config["vector"]):
            sequence = self.generate_sequence(el["distribution"], el, el["quantity"], el["scale"])
            min_max.append({"min": sequence.min(), "max": sequence.max()})
            sequences.append(sequence)

        return np.array(np.meshgrid(*sequences)).T.reshape(-1, len(config["vector"])), min_max

    def generate_states(self, state_variables):
        raw_state_list = {}
        min_max = {}
        for key, variable in state_variables.items():
            if variable["variation"]:
                sequence = self.generate_sequence(variable["distribution"], variable, variable["quantity"],
                                                  variable["scale"])
                raw_state_list[key] = sequence
                min_max[key] = {"min": sequence.min(), "max": sequence.max()}
            else:
                raw_state_list[key] = np.array([variable["value"]])
        return raw_state_list, min_max

    def generate_sequence(self, distribution, params, quantity, scale="linear"):
        if distribution == "grid":
            sequence = np.linspace(params["min"], params["max"], quantity)
        if distribution == "uniform":
            sequence = np.random.default_rng().uniform(params["min"], params["max"], size=quantity)
        if distribution == "normal":
            sequence = np.random.default_rng().normal(params["mean"], params["variance"], size=quantity)

        if scale == "logarithmic":
            return np.power(2, sequence).astype(np.dtype)
        else:
            return sequence
