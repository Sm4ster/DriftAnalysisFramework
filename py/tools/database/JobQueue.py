from redis import Redis
from rq import Queue


def get_queue(name):
    r = Redis(host='nash.ini.rub.de', port=6379, db=0, password='4xEhjbGNkNPr8UkBQbWL9qmPpXpAeCKMF2G2')
    return Queue(name, connection=r)


class JobQueue:
    q = None
    jobs = []

    def __init__(self, name):
        r = Redis(host='nash.ini.rub.de', port=6379, db=0, password='4xEhjbGNkNPr8UkBQbWL9qmPpXpAeCKMF2G2')
        self.q = Queue(name, connection=r)

    def enqueue(self, *args, **kwargs):
        self.jobs.append(self.q.enqueue(*args, **kwargs))

    def finished(self):
        for job in self.jobs:
            if job.get_status() != "finished":
                return False
        return True

    def open(self):
        return len(self.q)