import threading, time

from downloader.config.logging import logger
from downloader.domain.job.repositories import select_stale_jobs
from downloader.domain.job.services import clean_job
from downloader.infrastructure.storage import delete_epub
from downloader.shared.constants import HOUR_IN_SECONDS

def cleanup_loop():
    while True:
        try:
            jobs = select_stale_jobs()
            for job in jobs:
                try:
                    clean_job(job)
                    delete_epub(job.path)
                    logger.info(f"Job of id {job.id} cleaned successfully")
                except Exception:
                    logger.error(f"Failed to clean job {job.id}")
        except Exception:
            logger.error("Cleanup failed")
        time.sleep(HOUR_IN_SECONDS)


def job_cleaner():
    threading.Thread(target=cleanup_loop, daemon=True).start()
