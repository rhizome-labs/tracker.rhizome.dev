import re
from datetime import datetime

import numpy
import timeago

from tracker_rhizome_dev import ENV
from tracker_rhizome_dev.app.http_request import HttpReq


def calculate_average_block_time(block_timestamps: list) -> float:
    """
    Calculates the average block time in seconds
    from the provided list of block timestamps.

    Args:
        block_timestamps (list): A list of block timestamps as integers.

    Returns:
        The average block time as a float.
    """
    numpy_array = numpy.array(sorted(list(set(block_timestamps))))
    diff = numpy.diff(numpy_array)
    return float(sum(diff) / len(diff) / 1000000)


def calculate_skip(page, limit):
    skip = int((page - 1) * limit)
    return skip


def convert_country_code_to_hex(country_code: str) -> str:
    COUNTRY_CODE_TO_HEX = {
        "ARE": "&#127462;&#127466;",
        "AUS": "&#127462;&#127482;",
        "AUT": "&#127462;&#127481;",
        "BEL": "&#127463;&#127466;",
        "BGR": "&#127463;&#127468;",
        "CAN": "&#127464;&#127462;",
        "CHE": "&#127464;&#127469;",
        "CHN": "&#127464;&#127475;",
        "CYM": "&#127472;&#127486;",
        "CZE": "&#127464;&#127487;",
        "DEU": "&#127465;&#127466;",
        "EST": "&#127466;&#127466;",
        "FRA": "&#127467;&#127479;",
        "GBR": "&#127468;&#127463;",
        "GRC": "&#127468;&#127479;",
        "GRD": "&#127468;&#127465;",
        "HRV": "&#127469;&#127479;",
        "IND": "&#127470;&#127475;",
        "ITA": "&#127470;&#127481;",
        "JPN": "&#127471;&#127477;",
        "KEN": "&#127472;&#127466;",
        "KOR": "&#127472;&#127479;",
        "MLT": "&#127474;&#127481;",
        "NLD": "&#127475;&#127473;",
        "NZL": "&#127475;&#127487;",
        "PHL": "&#127477;&#127469;",
        "PRI": "&#127477;&#127479;",
        "RUS": "&#127479;&#127482;",
        "SGP": "&#127480;&#127468;",
        "SVN": "&#127480;&#127470;",
        "SWE": "&#127480;&#127466;",
        "THA": "&#127481;&#127469;",
        "UKR": "&#127482;&#127462;",
        "USA": "&#127482;&#127480;",
        "VEN": "&#127483;&#127466;",
        "ZAF": "&#127487;&#127462;",
    }
    if country_code in COUNTRY_CODE_TO_HEX:
        return COUNTRY_CODE_TO_HEX[country_code]
    else:
        print(country_code)
        return ""


def get_datetime_in_utc(timestamp: int = None, precision: str = "m"):
    if timestamp is None:
        # If timestamp is not provided, get datetime object for current timestamp.
        dt = datetime.utcnow()
    else:
        # If timestamp is provided, convert timestamp to UTC datetime object.
        dt = datetime.utcfromtimestamp(timestamp)
    if precision == "m":
        return dt.replace(second=0, microsecond=0).isoformat()
    elif precision == "s":
        return dt.replace(microsecond=0).isoformat()


def format_number(value: float, precision: int = 4, display_sign: bool = False) -> str:

    # Test for 0.
    if float(value) == 0:
        return "0"

    # Convert value to an integer if precision is 0.
    if precision == 0:
        value = int(value)

    # Test for integers.
    if float(value) == int(value):
        if display_sign is True:
            result = f"{value:+,.0f}"
        else:
            result = f"{value:,.0f}"
    else:
        sig_zeros = len(
            re.search(
                "\d+\.(0*)", f'{numpy.format_float_positional(value, trim="-")}'
            ).group(1)
        )
        if display_sign is True:
            result = f"{value:+,.{sig_zeros + precision}f}".rstrip("0")
        else:
            result = f"{value:,.{sig_zeros + precision}f}".rstrip("0")
    return result


def format_percentage(
    value: float, precision: int = 2, display_sign: bool = False
) -> str:
    if float(value) == 0:
        if display_sign is True:
            return "±0%"
        else:
            return "0%"
    else:
        if display_sign is True:
            return f"{value:+,.{precision}%}"
        else:
            return f"{value:,.{precision}%}"


async def send_discord_notification(message: str):
    await HttpReq.post(
        ENV["DISCORD_WEBHOOK_URL"],
        json={
            "content": message,
        },
    )


def to_int(value: str) -> int:
    try:
        if value.startswith("0x"):
            return int(value, 16)
    except ValueError:
        return value
    else:
        return value


def to_relative_time(date: datetime, abbreviate: bool = True):
    now = datetime.utcnow()
    relative_time = timeago.format(date, now)
    if relative_time == "just now":
        return relative_time
    if abbreviate is True:
        if "second" in relative_time:
            return relative_time.replace("seconds", "sec")
        if "minute" in relative_time:
            return relative_time.replace("minutes", "min")
        if "hour" in relative_time:
            return relative_time.replace("hours", "hr")
    else:
        return relative_time
