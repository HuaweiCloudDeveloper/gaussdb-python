"""
gaussdb pool version file.
"""

# Copyright (C) 2021 The GaussDB Team

from importlib import metadata

try:
    __version__ = metadata.version("gaussdb-pool")
except metadata.PackageNotFoundError:
    __version__ = "0.0.0.0"
