from redis import Redis
from rq import Queue
from rq.registry import FinishedJobRegistry
from rq.job import Job
from datetime import datetime, timedelta
import uuid


def get_queue(name):
    r = Redis(host='nash.ini.rub.de', port=6379, db=0, password='4xEhjbGNkNPr8UkBQbWL9qmPpXpAeCKMF2G2')
    return Queue(name, connection=r)


class JobQueue:
    q = None
    pipeline = []
    jobs_ids = []
    name = None
    connection = None


    def __init__(self, name):
        self.name = name
        r = Redis(host='nash.ini.rub.de', port=6379, db=0, password='4xEhjbGNkNPr8UkBQbWL9qmPpXpAeCKMF2G2')
        self.connection = r
        self.q = Queue(name, connection=r)

    def enqueue(self, *args, **kwargs):
        job_id = str(uuid.uuid4())

        while job_id in self.jobs_ids:
            job_id = uuid.uuid4()

        self.pipeline.append(Queue.prepare_data(*args, **kwargs, job_id=job_id))
        self.jobs_ids.append(job_id)


    def start(self):
        self.q.enqueue_many(self.pipeline)
        self.pipeline = []

    def is_finished(self):
        return FinishedJobRegistry(queue=self.q).count == len(self.jobs_ids)

    def get_finished(self):
        return FinishedJobRegistry(queue=self.q)

    def get_finished_jobs(self):
        return Job.fetch_many(self.jobs_ids, connection=self.connection)

    def open(self):
        return len(self.q)

    def remove(self, job_id):
        FinishedJobRegistry(queue=self.q).remove(job_id)

    def empty(self):
        time = datetime.now() + timedelta(days=5)
        FinishedJobRegistry(queue=self.q).cleanup(time.timestamp())
