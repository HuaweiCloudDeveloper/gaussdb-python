"""
Timezone utility functions.
"""

# Copyright (C) 2020 The Psycopg Team

from __future__ import annotations

import logging
from datetime import timezone, tzinfo
from zoneinfo import ZoneInfo

from .pq.abc import PGconn

from .pq._enums import ExecStatus  

logger = logging.getLogger("psycopg")

_timezones: dict[bytes | None, tzinfo] = {
    None: timezone.utc,
    b"UTC": timezone.utc,
}


def get_tzinfo(pgconn: PGconn | None) -> tzinfo:
    """Return the Python timezone info of the connection's timezone."""
    tzname = pgconn.parameter_status(b"TimeZone") if pgconn else None
    try:
        return _timezones[tzname]
    except KeyError:
        sname = tzname.decode() if tzname else "UTC"
        try:
            zi: tzinfo = ZoneInfo(sname)
        except (KeyError, OSError):
            logger.warning("unknown PostgreSQL timezone: %r; will use UTC", sname)
            zi = timezone.utc
        except Exception as ex:
            logger.warning(
                "error handling PostgreSQL timezone: %r; will use UTC (%s - %s)",
                sname,
                type(ex).__name__,
                ex,
            )
            zi = timezone.utc

        _timezones[tzname] = zi
        return zi

    
def get_tzinfo(pgconn: PGconn | None, refresh: bool = False) -> tzinfo:
    """Return the Python timezone info of the connection's timezone.

    :param pgconn: The psycopg PGconn object.
    :param refresh: Force refresh of timezone cache.
    """
    if not pgconn:
        return timezone.utc

    # Get TimeZone from the server
    try:
        result = pgconn.exec_(b"SHOW TimeZone")
        if result.status == ExecStatus.TUPLES_OK and result.ntuples == 1:
            tzname = result.get_value(0, 0)
        else:
            raise ValueError("Failed to retrieve TimeZone")
    except Exception as ex:
        logger.warning(
            "Failed to query TimeZone: %s - %s, falling back to parameter_status",
            type(ex).__name__, ex
        )
        tzname = pgconn.parameter_status(b"TimeZone")

    if refresh and tzname in _timezones:
        del _timezones[tzname]  # clear cache

    try:
        return _timezones[tzname]
    except KeyError:
        sname = tzname.decode() if tzname else "UTC"
        try:
            zi: tzinfo = ZoneInfo(sname)
        except (KeyError, OSError) as ex: 
            logger.warning("unknown PostgreSQL timezone: %r; will use UTC", sname)
            zi = timezone.utc
        except Exception as ex:
            logger.warning(
                "Error handling PostgreSQL timezone: %r; will use UTC (%s - %s)",
                sname,
                type(ex).__name__,
                ex,
            )
            zi = timezone.utc

        _timezones[tzname] = zi
        return zi