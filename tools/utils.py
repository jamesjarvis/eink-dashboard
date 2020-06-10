import datetime

import pytz


def get_current_time(tz=pytz.timezone("Europe/London")):
    """Simply returns the current time"""
    return datetime.datetime.now(tz)


def parse_datetime(
    datetime_string, tz_from=pytz.utc, tz_to=pytz.timezone("Europe/London")
):
    """Simply takes a datetime string in utc format, and returns it in the timezone specified"""
    dt = datetime.datetime.strptime(datetime_string, "%Y-%m-%dT%H:%M:%S.%f%z")
    return dt.astimezone(tz_to)


def convert_utc_to_local(date, tz_from=pytz.utc, tz_to=pytz.timezone("Europe/London")):
    """Simply converts the provided utc date to local timezone"""
    return date.astimezone(tz_to)
