"""
gaussdb distribution version file.
"""

# Copyright (C) 2020 The Psycopg Team

from importlib import metadata

try:
    __version__ = metadata.version("gaussdb")
except metadata.PackageNotFoundError:
    __version__ = "0.0.0.0"
