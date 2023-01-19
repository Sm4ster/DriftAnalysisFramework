from redis import Redis
from rq import Queue
from rq.registry import FinishedJobRegistry
from rq.job import Job
from datetime import datetime, timedelta


def get_queue(name):
    r = Redis(host='nash.ini.rub.de', port=6379, db=0, password='4xEhjbGNkNPr8UkBQbWL9qmPpXpAeCKMF2G2')
    return Queue(name, connection=r)


class JobQueue:
    q = None
    pipeline = []
    jobs_ids = []
    name = None
    connection = None
    counter = 1

    def __init__(self, name):
        self.name = name
        r = Redis(host='nash.ini.rub.de', port=6379, db=0, password='4xEhjbGNkNPr8UkBQbWL9qmPpXpAeCKMF2G2')
        self.connection = r
        self.q = Queue(name, connection=r)

    def enqueue(self, *args, **kwargs):
        self.counter += 1
        self.pipeline.append(Queue.prepare_data(*args, **kwargs, job_id='my_job_id' + str(self.counter)))
        self.jobs_ids.append('my_job_id' + str(self.counter))

    def start(self):
        self.q.enqueue_many(self.pipeline)

    def finished(self):
        print(FinishedJobRegistry(queue=self.q).count, len(self.jobs_ids))
        return FinishedJobRegistry(queue=self.q).count == len(self.jobs_ids)

    def get_finished(self):
        return FinishedJobRegistry(queue=self.q).get_job_ids()

    def get_finished_jobs(self):
        return Job.fetch_many(self.get_finished(), connection=self.connection)

    def open(self):
        return len(self.q)

    def remove(self, job_id):
        FinishedJobRegistry(queue=self.q).remove(job_id)

    def empty(self):
        time = datetime.now() + timedelta(days=5)
        FinishedJobRegistry(queue=self.q).cleanup(time.timestamp())
