from DriftAnalysisFramework.JobQueue import JobQueue

q = JobQueue("step_size_analysis")

for job in q.get_jobs(q.get_failed_jobs().get_job_ids()):
    if hasattr(job, "meta"):
        if "distance_idx" in job.meta:
            if job.meta["distance_idx"] != 0:
                q.q.failed_job_registry.requeue(job.id)
                print("requeued job " + job.id)
