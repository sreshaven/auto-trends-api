from jobs import q, update_job_status

@q.worker
def execute_job(jid):
    """
      Retrieve a job id from the task queue and execute the job.
      Monitors the job to completion and updates the database accordingly.
    """
    jobs.update_job_status(jid, 'in progress')
    time.sleep(15)
    jobs.update_job_status(jid, 'complete')
