import datetime

import pytz


def get_current_time(tz=pytz.timezone("Europe/London")) -> datetime:
    """Simply returns the current time"""
    return datetime.datetime.now(tz)


def get_time_epoch(epoch, tz_from=pytz.utc, tz_to=pytz.timezone("Europe/London")) -> datetime:
    dt = datetime.datetime.fromtimestamp(epoch, tz_from)
    return dt.astimezone(tz_to)


def parse_datetime(datetime_string, tz_from=pytz.utc, tz_to=pytz.timezone("Europe/London")) -> datetime:
    """Simply takes a datetime string in utc format, and returns it in the timezone specified"""
    dt = datetime.datetime.strptime(datetime_string, "%Y-%m-%dT%H:%M:%S.%f%z")
    return dt.astimezone(tz_to)


def convert_utc_to_local(date, tz_from=pytz.utc, tz_to=pytz.timezone("Europe/London")) -> datetime:
    """Simply converts the provided utc date to local timezone"""
    return date.astimezone(tz_to)

def beautify_time_string(time: str) -> str:
    """Changes 1210 to 12:10"""
    return f"{time[:2]}:{time[2:]}"
