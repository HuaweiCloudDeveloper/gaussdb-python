"""
Helper object to transform values between Python and GaussDB

This module exports the requested implementation to the rest of the package.
"""

# Copyright (C) 2023 The Psycopg Team

from __future__ import annotations

from . import abc
from ._cmodule import _gaussdb

Transformer: type[abc.Transformer]

if _gaussdb:
    Transformer = _gaussdb.Transformer
else:
    from . import _py_transformer

    Transformer = _py_transformer.Transformer
