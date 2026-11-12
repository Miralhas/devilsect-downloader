import os
import sys
import pika

from downloader.infrastructure.database import create_db_and_tables
from downloader.infrastructure.queue import consume_downloader_queue
from downloader.domain.cleaner.services import job_cleaner

def main():
    try:
        create_db_and_tables()
        job_cleaner()
        consume_downloader_queue()
    except KeyboardInterrupt:
        print()
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)