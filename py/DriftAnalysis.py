from DriftAnalysisFramework import TargetFunctions, OptimizationAlgorithms, PotentialFunctions
from worker_module import work_job
from rq.registry import ScheduledJobRegistry

import json
from redis import Redis
from rq import Queue
import numpy as np
import uuid


class DriftAnalysis:
    dim = 2
    states = {}
    starting_locations = []
    location_uuids = []
    results = []
    jobs = []
    matrices = None
    queue = False

    def __init__(self, config, queue=True):
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
        self.states = self.generate_states(config["variables"])

        # generate locations
        self.starting_locations = self.generate_locations(config["location"])
        # locations =  self.generate_locations(config["location"])
        # for id in np.arange(0, config["location"]["quantity"], 1):
        #     self.starting_locations.append({'id': id, 'vector': locations[id]})

    def start(self):
        options = {
            "matrices": self.matrices,
            # parameters for the batches
            "batch_size": 10,  # number of evaluations before a significance test is performed
            "max_evaluations": 1000,  # if no significant result was obtained we cancel the evaluations of this state
        }

        job = None

        for idx, starting_location in enumerate(self.starting_locations):
            self.oa.set_location(starting_location)
            if self.queue:
                job = self.q.enqueue(work_job, self.oa, self.pf, self.states, options)
                self.jobs.append({
                    "id": idx,
                    "location": starting_location,
                    "job": job,
                    "not_in_results": True
                })
                # print("worker enqueued (" + str(idx) + ")")

            else:
                self.results += work_job(self.oa, self.pf, self.states, options)
        print("finished queuing workers")
        if self.queue:
            registry = ScheduledJobRegistry(queue=self.q)
            # print(registry.get_job_ids())

        return job

    def get_starting_locations(self):
        return [{"id": idx, "location": loc} for idx, loc in enumerate(self.starting_locations)]

    def get_new_results(self):
        new_results = []
        for job_wrapper in self.jobs:
            if job_wrapper["not_in_results"] and job_wrapper["job"].result is not None:
                new_results.append({
                    "id": job_wrapper["id"],
                    "location": job_wrapper["location"],
                    "data": job_wrapper["job"].result
                })
                job_wrapper["not_in_results"] = False
        return new_results

    def all_jobs_in_results(self):
        return all(not job["not_in_results"] for job in self.jobs)

    def generate_locations(self, config):
        locations = np.empty((len(config["vector"]), config["quantity"]))

        for idx, el in enumerate(config["vector"]):
            locations[idx][:] = self.generate_sequence(el["distribution"], el, config["quantity"])
        return np.transpose(locations)

    def generate_states(self, state_variables):
        raw_state_list = {}
        for key, variable in state_variables.items():
            if variable["variation"]:
                raw_state_list[key] = self.generate_sequence(variable["distribution"], variable, variable["quantity"])
            else:
                raw_state_list[key] = np.array([variable["value"]])
        return raw_state_list

    def generate_sequence(self, distribution, params, quantity):
        if distribution == "grid":
            return np.linspace(params["min"], params["max"], quantity)
        if distribution == "uniform":
            return np.random.default_rng().uniform(params["min"], params["max"], size=quantity)
        if distribution == "normal":
            return np.random.default_rng().normal(params["mean"], params["variance"], size=quantity)
