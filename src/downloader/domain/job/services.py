from pathlib import Path

from downloader.domain.job.repositories import select_job_by_id, update_job_by_id
from downloader.domain.job.models import DownloadJob, JobStatus


def get_job_by_id_or_exception(id: int) -> DownloadJob:
    job = select_job_by_id(id)

    if not job:
        raise Exception(f"Failed to get job with id: {id}")

    return job


def clean_job(job: DownloadJob) -> DownloadJob:
    if (job.is_pending()):
        job.error = "Job was pending for more than 24 hours"

    job.status = JobStatus.CLEANED

    return update_job_by_id(job.id, job)


def complete_job(job: DownloadJob, filename: Path) -> DownloadJob:
    job.status = JobStatus.COMPLETED
    job.path = str(filename)

    return update_job_by_id(job.id, job)


def fail_job(job: DownloadJob, error: str) -> DownloadJob:
    job.status = JobStatus.FAILED
    job.error = error

    return update_job_by_id(job.id, job)
