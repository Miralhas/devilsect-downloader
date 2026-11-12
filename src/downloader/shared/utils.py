from datetime import datetime

ONE_MINUTE_IN_SECONDS = 60

def difference_in_minutes(date_a: datetime, date_b: datetime):
    return int((date_a - date_b).total_seconds() // ONE_MINUTE_IN_SECONDS)