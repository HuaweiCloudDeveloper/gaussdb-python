# mypy: disable-error-code="import-not-found, attr-defined"
"""
Simplify access to the _gaussdb module
"""

# Copyright (C) 2021 The GaussDB Team

from __future__ import annotations

from types import ModuleType

from . import pq

__version__: str | None = None
_gaussdb: ModuleType

# Note: "c" must the first attempt so that mypy associates the variable the
# right module interface. It will not result Optional, but hey.
if pq.__impl__ == "c":
    import gaussdb_c._gaussdb

    _gaussdb = gaussdb_c._gaussdb
    __version__ = gaussdb_c.__version__

elif pq.__impl__ == "binary":
    import gaussdb_binary._gaussdb

    _gaussdb = gaussdb_binary._gaussdb
    __version__ = gaussdb_binary.__version__

elif pq.__impl__ == "python":

    _gaussdb = None  # type: ignore[assignment]

else:
    raise ImportError(f"can't find _gaussdb optimised module in {pq.__impl__!r}")
