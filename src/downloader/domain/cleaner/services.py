import threading, time
from pathlib import Path

from downloader.config.logging import logger
from downloader.domain.job.repositories import select_stale_jobs
from downloader.domain.job.services import clean_job
from downloader.config.settings import env
from downloader.shared.constants import HOUR_IN_SECONDS

def cleanup_loop():
    while True:
        jobs = select_stale_jobs()
        for job in jobs:
            try:
                clean_job(job)
                epub = Path(f"{env.OUTPUT_FOLDER}/{job.path}")
                epub.unlink()
                logger.info(f"Job of id {job.id} cleaned successfully")
            except FileNotFoundError:
                logger.error(f"Epub for the job with id {job.id} could not be found")
        
        time.sleep(HOUR_IN_SECONDS)


def job_cleaner():
    threading.Thread(target=cleanup_loop, daemon=True).start()
