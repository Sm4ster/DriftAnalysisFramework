from DriftAnalysisFramework import TargetFunctions, OptimizationAlgorithms, PotentialFunctions
from worker_module import work_job
from rq.registry import ScheduledJobRegistry
from tools.database.JobQueue import JobQueue
from definitions import ALGORITHM_PATH
import json
from rq import Queue
import numpy as np


class DriftAnalysis:
    uuid = None
    dim = 2
    states = {}
    location = []
    location_uuids = []
    results = []
    q = None
    matrices = None
    queue = False
    min_max = {}

    def __init__(self, config, uuid, redis_connection=None):
        self.uuid = uuid

        with open(ALGORITHM_PATH + config["algorithm"] + '.json', 'r') as f:
            oa_definition = json.load(f)
        self.matrices = oa_definition["matrices"]

        # if necessary init the queue
        if redis_connection:
            self.q = JobQueue("drift_analysis")
            self.queue = True

        # initialize the target function
        self.tf = TargetFunctions.convex_quadratic(self.dim, config["target"])

        # initialize the algorithm
        oa_class = getattr(OptimizationAlgorithms, oa_definition['python_class'])
        self.oa = oa_class(self.tf, config['constants'])

        # initialize a potential function
        if "mode" not in config["potential"]:
            raise ("[ERROR] Please specify the mode as 'expression' or 'function'")
        if config["potential"]["mode"] == "expression":
            self.pf = PotentialFunctions.Expression(config["potential"], config["constants"])
        elif config["potential"]["mode"] == "function":
            self.pf = PotentialFunctions.Function(config["potential"], config["constants"])
        else:
            raise ("[ERROR] Unknown mode. Please use 'expression' or 'function'")

        # generate states
        self.states, self.min_max["states"] = self.generate_states(config["variables"])

        # generate locations
        self.location, self.min_max["location"] = self.generate_locations(config["location"])

        # generate state array

        # print("states\n", self.states["sigma"])
        # print("locations\n", self.location)
        # location_idxs = list(range(self.location.shape[0]))
        # print("results\n", np.array(np.meshgrid(self.states["sigma"], location_idxs)).T.reshape(-1, 2))

    def start(self, verbosity=0):
        options = {
            "save_follow_up_states": False,
            "matrices": self.matrices,
            # parameters for the batches
            "batch_size": 1000,  # number of evaluations before a significance test is performed
            "max_evaluations": 1000000,  # if no significant result was obtained we cancel the evaluations of this state
        }
        if self.queue:
            for idx, location_ in enumerate(self.location):
                self.q.enqueue(
                    work_job,
                    args=[self.oa, self.pf, location_, self.states, options],
                    meta={"location": location_},
                    result_ttl=None
                )
                if idx % 1000 == 0:
                    self.q.start()
            self.q.start()

        else:
            for idx, starting_location in enumerate(self.location):
                print("[Local Mode]: Working job on local machine (" + str(idx) + "/" + str(len(self.location)) + ")")
                self.results.append(
                    work_job(self.oa, self.pf, starting_location, self.states, options, verbosity=verbosity))
                print("[Local Mode]: Finished job (" + str(idx) + "/" + str(len(self.location)) + ")")

    def init_queue(self, redis_connection):
        try:
            self.q = Queue("drift_analysis", connection=redis_connection)
        except:
            raise Exception("cannot make connection to redis server")

    def get_locations(self):
        return [{"id": idx, "location": loc} for idx, loc in enumerate(self.location)]

    def is_finished(self):
        if self.queue:
            return self.q.is_finished()
        else:
            return True

    def get_results(self):
        if self.queue:
            self.q.get_finished_jobs()
        else:
            return self.results

    def get_new_results(self):
        new_results = []

        for job_wrapper in self.jobs:
            # continue if the job in the queue doesn't have any results yet
            if job_wrapper:
                if self.queue and job_wrapper["job"].result is None:
                    continue
                new_results.append({
                    "id": job_wrapper["id"],
                    "location": job_wrapper["location"],
                    "data": job_wrapper["job"].result if self.queue else job_wrapper["result"]
                })

        return new_results

    def remove_results(self, job_ids):
        for job_id in job_ids:
            if self.jobs[job_id]:
                self.jobs[job_id]["job"].delete()
            self.jobs[job_id] = None

    def all_jobs_in_results(self):
        return all(v is None for v in self.jobs)

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
        sequence = None
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
