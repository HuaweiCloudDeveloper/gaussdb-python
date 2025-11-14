"""
gaussdb -- GaussDB database adapter for Python

This file is part of gaussdb.

gaussdb is a fork of psycopg[](https://www.psycopg.org/), originally
developed by the Psycopg Team and licensed under the GNU Lesser
General Public License v3.0 (LGPL v3).

The original psycopg source code is copyright © 2001–2023 by the Psycopg Team.

This modified version is distributed under the same LGPL v3 license.
See the LICENSE file for the full license text.
"""

# Copyright (C) 2020 The Psycopg Team
# Modifications made by HuaweiCloudDeveloper (2025):
# - Renamed package from 'psycopg' to 'gaussdb'
# - Updated all internal imports (psycopg → gaussdb)
# - Modified __init__.py to expose gaussdb.connect, etc.
# - Adjusted documentation strings and error messages for GaussDB branding
# - Added GaussDB-specific connection parameters (e.g., sslmode, gssencmode)
# - Patched SQL parsing for GaussDB-specific syntax support

import logging

from . import pq  # noqa: F401 import early to stabilize side effects
from . import dbapi20, gaussdb_, types
from ._tpc import Xid
from .copy import AsyncCopy, Copy
from ._enums import IsolationLevel
from .cursor import Cursor
from .errors import DatabaseError, DataError, Error, IntegrityError, InterfaceError
from .errors import InternalError, NotSupportedError, OperationalError
from .errors import ProgrammingError, Warning
from ._column import Column
from .dbapi20 import BINARY, DATETIME, NUMBER, ROWID, STRING, Binary, Date
from .dbapi20 import DateFromTicks, Time, TimeFromTicks, Timestamp, TimestampFromTicks
from .version import __version__ as __version__  # noqa: F401
from ._pipeline import AsyncPipeline, Pipeline
from .connection import Connection
from .raw_cursor import AsyncRawCursor, AsyncRawServerCursor, RawCursor, RawServerCursor
from .transaction import AsyncTransaction, Rollback, Transaction
from .cursor_async import AsyncCursor
from ._capabilities import Capabilities, capabilities
from .client_cursor import AsyncClientCursor, ClientCursor
from .server_cursor import AsyncServerCursor, ServerCursor
from ._connection_base import BaseConnection, Notify
from ._connection_info import ConnectionInfo
from .connection_async import AsyncConnection

# Set the logger to a quiet default, can be enabled if needed
logger = logging.getLogger("gaussdb")
if logger.level == logging.NOTSET:
    logger.setLevel(logging.WARNING)

# DBAPI compliance
connect = Connection.connect
apilevel = "2.0"
threadsafety = 2
paramstyle = "pyformat"

# register default adapters for GaussDB
adapters = gaussdb_.adapters  # exposed by the package
gaussdb_.register_default_types(adapters.types)
gaussdb_.register_default_adapters(adapters)

# After the default ones, because these can deal with the bytea oid better
dbapi20.register_dbapi20_adapters(adapters)

# Must come after all the types have been registered
types.array.register_all_arrays(adapters)

# Note: defining the exported methods helps both Sphynx in documenting that
# this is the canonical place to obtain them and should be used by MyPy too,
# so that function signatures are consistent with the documentation.
__all__ = [
    "AsyncClientCursor",
    "AsyncConnection",
    "AsyncCopy",
    "AsyncCursor",
    "AsyncPipeline",
    "AsyncRawCursor",
    "AsyncRawServerCursor",
    "AsyncServerCursor",
    "AsyncTransaction",
    "BaseConnection",
    "Capabilities",
    "capabilities",
    "ClientCursor",
    "Column",
    "Connection",
    "ConnectionInfo",
    "Copy",
    "Cursor",
    "IsolationLevel",
    "Notify",
    "Pipeline",
    "RawCursor",
    "RawServerCursor",
    "Rollback",
    "ServerCursor",
    "Transaction",
    "Xid",
    # DBAPI exports
    "connect",
    "apilevel",
    "threadsafety",
    "paramstyle",
    "Warning",
    "Error",
    "InterfaceError",
    "DatabaseError",
    "DataError",
    "OperationalError",
    "IntegrityError",
    "InternalError",
    "ProgrammingError",
    "NotSupportedError",
    # DBAPI type constructors and singletons
    "Binary",
    "Date",
    "DateFromTicks",
    "Time",
    "TimeFromTicks",
    "Timestamp",
    "TimestampFromTicks",
    "BINARY",
    "DATETIME",
    "NUMBER",
    "ROWID",
    "STRING",
]
