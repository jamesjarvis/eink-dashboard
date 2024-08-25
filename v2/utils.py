import datetime
import pytz


# Utility functions


def parse_datetime(
    datetime_string, tz_from=pytz.utc, tz_to=pytz.timezone("Europe/London")
) -> datetime:
    """Simply takes a datetime string in utc format, and returns it in the timezone specified"""
    dt = datetime.datetime.strptime(datetime_string, "%Y-%m-%dT%H:%M:%S%z")
    return dt.astimezone(tz_to)
