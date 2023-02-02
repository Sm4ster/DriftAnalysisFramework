from redis import Redis
from rq import Queue
from rq.registry import FinishedJobRegistry
from datetime import datetime, timedelta

r = Redis(host='nash.ini.rub.de', port=6379, db=0, password='4xEhjbGNkNPr8UkBQbWL9qmPpXpAeCKMF2G2')

queues = (
    Queue('drift_analysis', connection=r),
    Queue('step_size_analysis', connection=r),
    Queue('default', connection=r),
    Queue('failed', connection=r),
    Queue('lu_search', connection=r),
)

for q in queues:
    print(FinishedJobRegistry(queue=q).get_job_ids())
    q.empty()
    time = datetime.now() + timedelta(days=5)
    FinishedJobRegistry(queue=q).cleanup(time.timestamp())
    print(FinishedJobRegistry(queue=q).get_job_ids())
