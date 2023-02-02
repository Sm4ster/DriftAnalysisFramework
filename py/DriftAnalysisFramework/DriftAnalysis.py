from DriftAnalysisFramework import TargetFunctions, OptimizationAlgorithms, PotentialFunctions
from worker_module import work_job
from DriftAnalysisFramework.JobQueue import JobQueue
from definitions import ALGORITHM_PATH
import json
import numpy as np


class DriftAnalysis:
    dim = 2
    states = {}
    locations = []
    location_uuids = []
    results = []
    q = None
    matrices = None
    queue = False
    min_max = {}
    pf = []

    def __init__(self, config, uuid, queue=False):
        self.uuid = uuid

        with open(ALGORITHM_PATH + config["algorithm"] + '.json', 'r') as f:
            oa_definition = json.load(f)
        self.matrices = oa_definition["matrices"]

        # if necessary init the queue
        if queue:
            self.q = JobQueue("drift_analysis")
            self.queue = True

        # initialize the target function
        self.tf = TargetFunctions.convex_quadratic(self.dim, config["target"])

        # initialize the algorithm
        oa_class = getattr(OptimizationAlgorithms, oa_definition['python_class'])
        self.oa = oa_class(self.tf, config['constants'])

        # initialize a potential function
        self.pf_names = []
        for potential in config["potential"]:
            if "mode" not in potential:
                raise ("[ERROR] Please specify the mode as 'expression' or 'function'")

            if potential["mode"] == "expression":
                self.pf.append(PotentialFunctions.Expression(potential, config["constants"]))
            elif potential["mode"] == "function":
                if "extras" in config: self.pf.append(PotentialFunctions.Function(potential, config["constants"], config["extras"]))
            else:
                raise ("[ERROR] Unknown mode. Please use 'expression' or 'function'")
            self.pf_names.append(potential["function"])

        # generate states
        states, self.min_max["states"] = self.generate_states(config["variables"])

        # generate locations
        if config["location"]["type"] == "grid":
            locations, self.min_max["location"] = self.generate_grid_locations(config["location"])
        if config["location"]["type"] == "arc":
            locations = self.generate_arc_locations(config["location"])

        states = list(states.items())
        var_arrays = [var[1] for var in states]
        self.keys = {var[0]: idx for idx, var in enumerate(states)}
        self.keys["m"] = len(states)
        state_array = np.array(np.meshgrid(*var_arrays)).T.reshape(-1, len(var_arrays))
        # The order is important. The m vector always stands at the end as it is of variable length.
        # This convention is relied upon, do no change unless you have considered that.
        self.states = np.concatenate(
            (np.tile(state_array, (locations.shape[0], 1)), np.repeat(locations, state_array.shape[0], axis=0)), axis=1)

    def start(self, job_chunk=10000, verbosity=0):
        options = {
            "save_follow_up_states": False,
            "matrices": self.matrices,

            "wait_all": False,
            # If true, potential functions are evaluated until all potential functions become significant
            "batch_size": 1000,  # number of evaluations before a significance test is performed
            "socket_size": 10000,  # number of samples that are taken before significance tests start
            "max_evaluations": 1000000,  # if no significant result was obtained we cancel the evaluations of this state

            "deviation": 0.1,  # This is the factor against which the significance is tested.
            "confidence": 0.05  # confidence level of the t-test
        }

        number_jobs = int(np.ceil(self.states.shape[0] / job_chunk))

        if self.queue:
            for idx in range(number_jobs):
                print("[Queue Mode]: Queueing Jobs (" + str(idx) + "/" + str(number_jobs) + ")")
                lower = idx * job_chunk
                upper = lower + job_chunk
                self.q.enqueue(
                    work_job,
                    args=[self.oa, self.pf, self.states[lower:upper], self.keys, options],
                    meta={"indexes": (lower, upper), "run_id": self.uuid},
                    result_ttl=864000
                )
                if idx % 1000 == 0:
                    self.q.start()
            self.q.start()

        else:
            for idx in range(number_jobs):
                lower = idx * job_chunk
                upper = lower + job_chunk
                print("[Local Mode]: Working job on local machine (" + str(idx) + "/" + str(number_jobs) + ")")
                self.results.append(
                    work_job(self.oa, self.pf, self.states[lower:upper], self.keys, options, verbosity=verbosity))
                print("[Local Mode]: Finished job (" + str(idx) + "/" + str(number_jobs) + ")")

    def get_locations(self):
        return [{"id": idx, "location": loc} for idx, loc in enumerate(self.locations)]

    def is_finished(self):
        if self.queue:
            return self.q.is_finished()
        else:
            return True

    def get_results(self):
        if self.queue:
            result_list = []
            jobs = self.q.get_jobs()
            for job in jobs:
                if job.result:
                    for result in job.result:
                        result_list.append(result)
                else:
                    job.refresh()
                    print(job.get_status(), job.meta, job.enqueued_at, job.origin)
                    # self.q.q.failed_job_registry.requeue(job.id)

            self.results = result_list
            return result_list
        else:
            return self.results

    def generate_grid_locations(self, config):
        sequences = []
        min_max = []
        for idx, el in enumerate(config["vector"]):
            sequence = self.generate_sequence(el["distribution"], el, el["quantity"], el["scale"])
            min_max.append({"min": sequence.min(), "max": sequence.max()})
            sequences.append(sequence)

        return np.array(np.meshgrid(*sequences)).T.reshape(-1, len(config["vector"])), min_max

    # TODO MAKE THIS WORK FOR MULTIPLE DIMENSIONS
    def generate_arc_locations(self, config):
        distance_sequence = self.generate_sequence(config["distance"]["distribution"], config["distance"],
                                                   config["distance"]["quantity"], config["distance"]["scale"])
        locations = None
        for idx, el in enumerate(config["angles"][:1]):
            angle_sequence = self.generate_sequence(el["distribution"], el, el["quantity"], el["scale"])
            locations = np.array([[np.cos(angle), np.sin(angle)] for angle in angle_sequence])

        # print(np.repeat(locations, distance_sequence.shape[0], axis=0))
        # print(np.tile(np.tile(distance_sequence, locations.shape[0]), (2,1)).T)
        return np.repeat(locations, distance_sequence.shape[0], axis=0) * np.tile(
            np.tile(distance_sequence, locations.shape[0]), (2, 1)).T

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

    def save_jobs_ids(self):
        self.job_ids = self.q.jobs_ids


    def load_job_ids(self):
        self.q = JobQueue("drift_analysis")
        self.q.jobs_ids = self.job_ids
