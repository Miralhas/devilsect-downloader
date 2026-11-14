from downloader.config.logging import logger
from downloader.domain.job.services import (
    complete_job,
    fail_job,
    get_job_by_id_or_exception,
)
from downloader.domain.novel.services import (
    get_novel_by_slug_or_exception,
    get_novel_chapters,
)
from downloader.infrastructure.epub import generate


def execute_download(jobId: int):
    job = get_job_by_id_or_exception(jobId)

    try:
        novel = get_novel_by_slug_or_exception(job.slug)
        chapters = get_novel_chapters(
            novelId=novel.id,
            start=job.start,
            end=job.end,
            exclude=job.exclude_to_array(),
        )

        filename = generate(novel, chapters, job.id)
        complete_job(job, filename)
        logger.info(f"JOB of id: {job.id} COMPLETED!")
    except Exception as ex:
        fail_job(job, str(ex))
        logger.error(f"JOB of id: {job.id} FAILED!: {ex}")
