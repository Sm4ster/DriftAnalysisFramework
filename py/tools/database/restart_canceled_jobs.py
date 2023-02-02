from DriftAnalysisFramework.JobQueue import JobQueue

q = JobQueue("drift_analysis")
print(len(q.get_failed_jobs().get_job_ids()))
for job in q.get_jobs(q.get_failed_jobs().get_job_ids()):

    if "indexes" in job.meta:
        q.q.failed_job_registry.requeue(job.id)
        print("requeued job " + job.id)
