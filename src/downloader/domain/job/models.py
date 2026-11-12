from datetime import datetime
from enum import StrEnum
from typing import Optional
from sqlmodel import Field, SQLModel


class JobStatus(StrEnum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CLEANED = "CLEANED"


class DownloadJob(SQLModel, table=True):
    __tablename__ = "download_job"

    id: int | None = Field(default=None, primary_key=True)
    slug: str
    start: int
    end: int
    status: JobStatus
    path: str
    error: str
    exclude: str | None
    created_at: Optional[datetime]

    def exclude_to_array(self) -> list[str]:
        if not self.exclude:
            return []
        return self.exclude.split(";")

    def is_pending(self) -> bool:
        return self.status == JobStatus.PENDING
