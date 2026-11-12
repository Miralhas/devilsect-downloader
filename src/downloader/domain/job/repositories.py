from datetime import datetime, timedelta, timezone
from typing import Sequence
from sqlmodel import Session, select, col

from downloader.domain.job.models import DownloadJob, JobStatus
from downloader.infrastructure.database import engine
from downloader.shared.constants import HOUR_IN_SECONDS


def select_job_by_id(id: int) -> DownloadJob:
    with Session(engine) as session:
        return session.get(DownloadJob, id)


def update_job_by_id(id: int, update: DownloadJob):
    with Session(engine) as session:
        job = session.get_one(DownloadJob, id)

        update_data = update.model_dump(exclude_unset=True)

        job.sqlmodel_update(update_data)
        
        session.add(job)
        session.commit()
        session.refresh(job)

        return job

def select_stale_jobs() -> Sequence[DownloadJob]:
    one_hour_ago = datetime.now(timezone.utc) - timedelta(seconds=HOUR_IN_SECONDS)
    with Session(engine) as session:
        statement = (
            select(DownloadJob)
            .where(DownloadJob.created_at <= one_hour_ago)
            .where(col(DownloadJob.status).not_in([JobStatus.CLEANED, JobStatus.FAILED]))
        )
        results = session.exec(statement)
        return results.all()