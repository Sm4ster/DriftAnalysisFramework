from DriftAnalysisFramework.JobQueue import JobQueue

q = JobQueue("drift_analysis")
print(len(q.get_failed_jobs().get_job_ids()))
for job in q.get_jobs(q.get_failed_jobs().get_job_ids()):

    if "job_id" in job.meta:
        if job.meta["job_id"] == "6acc67c1-068e-450d-ba36-ab2a004d54ee":
            q.q.failed_job_registry.requeue(job.id)
            print("requeued job " + job.id)
