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
    jobs = []
    name = None
    connection = None

    def __init__(self, name):
        self.name = name
        r = Redis(host='nash.ini.rub.de', port=6379, db=0, password='4xEhjbGNkNPr8UkBQbWL9qmPpXpAeCKMF2G2')
        self.connection = r
        self.q = Queue(name, connection=r)

    def enqueue(self, *args, **kwargs):
        self.jobs.append(self.q.enqueue(*args, **kwargs))

    def finished(self):
        for job in self.jobs:
            if job.get_status() != "finished":
                return False
        return True

    def get_finished(self):
        print(FinishedJobRegistry(queue=self.q).count)
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