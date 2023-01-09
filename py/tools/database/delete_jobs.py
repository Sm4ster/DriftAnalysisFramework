from redis import Redis
from rq import Queue

r = Redis(host='nash.ini.rub.de', port=6379, db=0, password='4xEhjbGNkNPr8UkBQbWL9qmPpXpAeCKMF2G2')

queues = (
    Queue('step_size_analysis', connection=r),
    Queue('default', connection=r),
    Queue('failed', connection=r),
)

for q in queues:
    q.empty()