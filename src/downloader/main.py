from downloader.config.settings import env
from downloader.domain.cleaner.services import job_cleaner
from downloader.infrastructure.database import create_db_and_tables
from downloader.infrastructure.queue import start_workers


def main():
    create_db_and_tables()
    job_cleaner()
    start_workers(workers_count=env.RABBIT_WORKERS)
