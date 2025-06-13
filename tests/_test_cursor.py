"""
Support module for test_cursor[_async].py
"""

from __future__ import annotations

import re
from typing import Any

import pytest

import gaussdb
from gaussdb.rows import RowMaker


@pytest.fixture(scope="session")
def _execmany(svcconn):
    cur = svcconn.cursor()
    cur.execute(
        """
        drop table if exists execmany;
        create table execmany (id serial primary key, num integer, data text)
        """
    )


@pytest.fixture(scope="function")
def execmany(svcconn, _execmany):
    cur = svcconn.cursor()
    cur.execute("truncate table execmany")


def ph(cur: Any, query: str) -> str:
    """Change placeholders in a query from %s to $n if testing  a raw cursor"""
    from gaussdb.raw_cursor import RawCursorMixin

    if not isinstance(cur, RawCursorMixin):
        return query

    if "%(" in query:
        pytest.skip("RawCursor only supports positional placeholders")

    n = 1

    def s(m: re.Match[str]) -> str:
        nonlocal n
        rv = f"${n}"
        n += 1
        return rv

    return re.sub(r"(?<!%)(%[bst])", s, query)


def my_row_factory(
    cursor: gaussdb.Cursor[list[str]] | gaussdb.AsyncCursor[list[str]],
) -> RowMaker[list[str]]:
    if cursor.description is not None:
        titles = [c.name for c in cursor.description]

        def mkrow(values):
            return [f"{value.upper()}{title}" for title, value in zip(titles, values)]

        return mkrow
    else:
        return gaussdb.rows.no_result
