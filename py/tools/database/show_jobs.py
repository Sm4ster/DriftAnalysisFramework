from redis import Redis
from rq import Queue
from rq.job import Job
from rq.registry import FailedJobRegistry, ScheduledJobRegistry

r = Redis(host='nash.ini.rub.de', port=6379, db=0, password='4xEhjbGNkNPr8UkBQbWL9qmPpXpAeCKMF2G2')
q = Queue(connection=r)

registry = FailedJobRegistry(queue=q)
for job_id in registry.get_job_ids():
    job = Job.fetch(job_id, connection=r)
    print(job_id, job.exc_info)