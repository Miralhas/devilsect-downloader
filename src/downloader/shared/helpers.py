from datetime import datetime
from time import time

from downloader.config.logging import logger

ONE_MINUTE_IN_SECONDS = 60


def difference_in_minutes(date_a: datetime, date_b: datetime):
    return int((date_a - date_b).total_seconds() // ONE_MINUTE_IN_SECONDS)


def timer(name: str | None = None):
    def decorator(func):
        def wrap_func(*args, **kwargs):
            t1 = time()
            result = func(*args, **kwargs)
            t2 = time()
            logger.info(f"{name} took {(t2-t1):.4f}s to complete!")
            return result

        return wrap_func

    return decorator
