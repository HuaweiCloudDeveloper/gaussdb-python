#!/usr/bin/env python3

# Create the gaussdb-binary package by renaming and patching gaussdb-c

from __future__ import annotations

import os
import re
import shutil
from pathlib import Path

curdir = Path(__file__).parent
pdir = curdir / "../.."
target = pdir / "gaussdb_binary"

if target.exists():
    raise Exception(f"path {target} already exists")


def sed_i(pattern: str, repl: str, filename: str | Path) -> None:
    with open(filename, "rb") as f:
        data = f.read()
    newdata = re.sub(pattern.encode("utf8"), repl.encode("utf8"), data)
    if newdata != data:
        with open(filename, "wb") as f:
            f.write(newdata)


shutil.copytree(pdir / "gaussdb_c", target)
shutil.move(str(target / "gaussdb_c"), str(target / "gaussdb_binary"))
shutil.move(str(target / "README-binary.rst"), str(target / "README.rst"))
sed_i("gaussdb-c", "gaussdb-binary", target / "pyproject.toml")
sed_i(r'"gaussdb_c([\./][^"]+)?"', r'"gaussdb_binary\1"', target / "pyproject.toml")
sed_i(r"__impl__\s*=.*", '__impl__ = "binary"', target / "gaussdb_binary/pq.pyx")
for dirpath, dirnames, filenames in os.walk(target):
    for filename in filenames:
        if os.path.splitext(filename)[1] not in (".pyx", ".pxd", ".py"):
            continue
        sed_i(r"\bpsycopg_c\b", "gaussdb_binary", Path(dirpath) / filename)
