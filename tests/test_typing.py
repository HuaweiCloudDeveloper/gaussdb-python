from __future__ import annotations

import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))


@pytest.mark.parametrize(
    "filename",
    ["adapters_example.py", "typing_example.py"],
)
def test_typing_example(mypy, filename):
    cp = mypy.run_on_file(os.path.join(HERE, filename))
    errors = cp.stdout.decode("utf8", "replace").splitlines()
    assert not errors
    assert cp.returncode == 0


@pytest.mark.parametrize(
    "conn, type",
    [
        (
            "gaussdb.connect()",
            "gaussdb.Connection[Tuple[Any, ...]]",
        ),
        (
            "gaussdb.connect(row_factory=rows.tuple_row)",
            "gaussdb.Connection[Tuple[Any, ...]]",
        ),
        (
            "gaussdb.connect(row_factory=rows.dict_row)",
            "gaussdb.Connection[Dict[str, Any]]",
        ),
        (
            "gaussdb.connect(row_factory=rows.namedtuple_row)",
            "gaussdb.Connection[NamedTuple]",
        ),
        (
            "gaussdb.connect(row_factory=rows.class_row(Thing))",
            "gaussdb.Connection[Thing]",
        ),
        (
            "gaussdb.connect(row_factory=thing_row)",
            "gaussdb.Connection[Thing]",
        ),
        (
            "gaussdb.Connection.connect()",
            "gaussdb.Connection[Tuple[Any, ...]]",
        ),
        (
            "gaussdb.Connection.connect(row_factory=rows.dict_row)",
            "gaussdb.Connection[Dict[str, Any]]",
        ),
        (
            "await gaussdb.AsyncConnection.connect()",
            "gaussdb.AsyncConnection[Tuple[Any, ...]]",
        ),
        (
            "await gaussdb.AsyncConnection.connect(row_factory=rows.dict_row)",
            "gaussdb.AsyncConnection[Dict[str, Any]]",
        ),
    ],
)
def test_connection_type(conn, type, mypy):
    stmts = f"obj = {conn}"
    _test_reveal(stmts, type, mypy)


@pytest.mark.parametrize(
    "conn, curs, type",
    [
        (
            "gaussdb.connect()",
            "conn.cursor()",
            "gaussdb.Cursor[Tuple[Any, ...]]",
        ),
        (
            "gaussdb.connect(row_factory=rows.dict_row)",
            "conn.cursor()",
            "gaussdb.Cursor[Dict[str, Any]]",
        ),
        (
            "gaussdb.connect(row_factory=rows.dict_row)",
            "conn.cursor(row_factory=rows.namedtuple_row)",
            "gaussdb.Cursor[NamedTuple]",
        ),
        (
            "gaussdb.connect(row_factory=rows.class_row(Thing))",
            "conn.cursor()",
            "gaussdb.Cursor[Thing]",
        ),
        (
            "gaussdb.connect(row_factory=thing_row)",
            "conn.cursor()",
            "gaussdb.Cursor[Thing]",
        ),
        (
            "gaussdb.connect()",
            "conn.cursor(row_factory=thing_row)",
            "gaussdb.Cursor[Thing]",
        ),
        # Async cursors
        (
            "await gaussdb.AsyncConnection.connect()",
            "conn.cursor()",
            "gaussdb.AsyncCursor[Tuple[Any, ...]]",
        ),
        (
            "await gaussdb.AsyncConnection.connect()",
            "conn.cursor(row_factory=thing_row)",
            "gaussdb.AsyncCursor[Thing]",
        ),
        # Server-side cursors
        (
            "gaussdb.connect()",
            "conn.cursor(name='foo')",
            "gaussdb.ServerCursor[Tuple[Any, ...]]",
        ),
        (
            "gaussdb.connect(row_factory=rows.dict_row)",
            "conn.cursor(name='foo')",
            "gaussdb.ServerCursor[Dict[str, Any]]",
        ),
        (
            "gaussdb.connect()",
            "conn.cursor(name='foo', row_factory=rows.dict_row)",
            "gaussdb.ServerCursor[Dict[str, Any]]",
        ),
        # Async server-side cursors
        (
            "await gaussdb.AsyncConnection.connect()",
            "conn.cursor(name='foo')",
            "gaussdb.AsyncServerCursor[Tuple[Any, ...]]",
        ),
        (
            "await gaussdb.AsyncConnection.connect(row_factory=rows.dict_row)",
            "conn.cursor(name='foo')",
            "gaussdb.AsyncServerCursor[Dict[str, Any]]",
        ),
        (
            "await gaussdb.AsyncConnection.connect()",
            "conn.cursor(name='foo', row_factory=rows.dict_row)",
            "gaussdb.AsyncServerCursor[Dict[str, Any]]",
        ),
    ],
)
def test_cursor_type(conn, curs, type, mypy):
    stmts = f"""\
conn = {conn}
obj = {curs}
"""
    _test_reveal(stmts, type, mypy)


@pytest.mark.parametrize(
    "conn, curs, type",
    [
        (
            "gaussdb.connect()",
            "gaussdb.Cursor(conn)",
            "gaussdb.Cursor[Tuple[Any, ...]]",
        ),
        (
            "gaussdb.connect(row_factory=rows.dict_row)",
            "gaussdb.Cursor(conn)",
            "gaussdb.Cursor[Dict[str, Any]]",
        ),
        (
            "gaussdb.connect(row_factory=rows.dict_row)",
            "gaussdb.Cursor(conn, row_factory=rows.namedtuple_row)",
            "gaussdb.Cursor[NamedTuple]",
        ),
        # Async cursors
        (
            "await gaussdb.AsyncConnection.connect()",
            "gaussdb.AsyncCursor(conn)",
            "gaussdb.AsyncCursor[Tuple[Any, ...]]",
        ),
        (
            "await gaussdb.AsyncConnection.connect(row_factory=rows.dict_row)",
            "gaussdb.AsyncCursor(conn)",
            "gaussdb.AsyncCursor[Dict[str, Any]]",
        ),
        (
            "await gaussdb.AsyncConnection.connect()",
            "gaussdb.AsyncCursor(conn, row_factory=thing_row)",
            "gaussdb.AsyncCursor[Thing]",
        ),
        # Server-side cursors
        (
            "gaussdb.connect()",
            "gaussdb.ServerCursor(conn, 'foo')",
            "gaussdb.ServerCursor[Tuple[Any, ...]]",
        ),
        (
            "gaussdb.connect(row_factory=rows.dict_row)",
            "gaussdb.ServerCursor(conn, name='foo')",
            "gaussdb.ServerCursor[Dict[str, Any]]",
        ),
        (
            "gaussdb.connect(row_factory=rows.dict_row)",
            "gaussdb.ServerCursor(conn, 'foo', row_factory=rows.namedtuple_row)",
            "gaussdb.ServerCursor[NamedTuple]",
        ),
        # Async server-side cursors
        (
            "await gaussdb.AsyncConnection.connect()",
            "gaussdb.AsyncServerCursor(conn, name='foo')",
            "gaussdb.AsyncServerCursor[Tuple[Any, ...]]",
        ),
        (
            "await gaussdb.AsyncConnection.connect(row_factory=rows.dict_row)",
            "gaussdb.AsyncServerCursor(conn, name='foo')",
            "gaussdb.AsyncServerCursor[Dict[str, Any]]",
        ),
        (
            "await gaussdb.AsyncConnection.connect()",
            "gaussdb.AsyncServerCursor(conn, name='foo', row_factory=rows.dict_row)",
            "gaussdb.AsyncServerCursor[Dict[str, Any]]",
        ),
    ],
)
def test_cursor_type_init(conn, curs, type, mypy):
    stmts = f"""\
conn = {conn}
obj = {curs}
"""
    _test_reveal(stmts, type, mypy)


@pytest.mark.parametrize(
    "curs, type",
    [
        (
            "conn.cursor()",
            "Tuple[Any, ...] | None",
        ),
        (
            "conn.cursor(row_factory=rows.dict_row)",
            "Dict[str, Any] | None",
        ),
        (
            "conn.cursor(row_factory=thing_row)",
            "Thing | None",
        ),
    ],
)
@pytest.mark.parametrize("server_side", [False, True])
@pytest.mark.parametrize("conn_class", ["Connection", "AsyncConnection"])
def test_fetchone_type(conn_class, server_side, curs, type, mypy):
    await_ = "await" if "Async" in conn_class else ""
    if server_side:
        curs = curs.replace("(", "(name='foo',", 1)
    stmts = f"""\
conn = {await_} gaussdb.{conn_class}.connect()
curs = {curs}
obj = {await_} curs.fetchone()
"""
    _test_reveal(stmts, type, mypy)


@pytest.mark.parametrize(
    "curs, type",
    [
        (
            "conn.cursor()",
            "Tuple[Any, ...]",
        ),
        (
            "conn.cursor(row_factory=rows.dict_row)",
            "Dict[str, Any]",
        ),
        (
            "conn.cursor(row_factory=thing_row)",
            "Thing",
        ),
    ],
)
@pytest.mark.parametrize("server_side", [False, True])
@pytest.mark.parametrize("conn_class", ["Connection", "AsyncConnection"])
def test_iter_type(conn_class, server_side, curs, type, mypy):
    if "Async" in conn_class:
        async_ = "async "
        await_ = "await "
    else:
        async_ = await_ = ""

    if server_side:
        curs = curs.replace("(", "(name='foo',", 1)
    stmts = f"""\
conn = {await_}gaussdb.{conn_class}.connect()
curs = {curs}
{async_}for obj in curs:
    pass
"""
    _test_reveal(stmts, type, mypy)


@pytest.mark.parametrize("method", ["fetchmany", "fetchall"])
@pytest.mark.parametrize(
    "curs, type",
    [
        (
            "conn.cursor()",
            "list[Tuple[Any, ...]]",
        ),
        (
            "conn.cursor(row_factory=rows.dict_row)",
            "list[Dict[str, Any]]",
        ),
        (
            "conn.cursor(row_factory=thing_row)",
            "list[Thing]",
        ),
    ],
)
@pytest.mark.parametrize("server_side", [False, True])
@pytest.mark.parametrize("conn_class", ["Connection", "AsyncConnection"])
def test_fetchsome_type(conn_class, server_side, curs, type, method, mypy):
    await_ = "await" if "Async" in conn_class else ""
    if server_side:
        curs = curs.replace("(", "(name='foo',", 1)
    stmts = f"""\
conn = {await_} gaussdb.{conn_class}.connect()
curs = {curs}
obj = {await_} curs.{method}()
"""
    _test_reveal(stmts, type, mypy)


@pytest.mark.parametrize("server_side", [False, True])
@pytest.mark.parametrize("conn_class", ["Connection", "AsyncConnection"])
def test_cur_subclass_execute(mypy, conn_class, server_side):
    async_ = "async " if "Async" in conn_class else ""
    await_ = "await" if "Async" in conn_class else ""
    cur_base_class = "".join(
        [
            "Async" if "Async" in conn_class else "",
            "Server" if server_side else "",
            "Cursor",
        ]
    )
    cur_name = "'foo'" if server_side else ""

    src = f"""\
from typing import Any, cast
import gaussdb
from gaussdb.rows import Row, TupleRow

class MyCursor(gaussdb.{cur_base_class}[Row]):
    pass

{async_}def test() -> None:
    conn = {await_} gaussdb.{conn_class}.connect()

    cur: MyCursor[TupleRow]
    reveal_type(cur)

    cur = cast(MyCursor[TupleRow], conn.cursor({cur_name}))
    {async_}with cur as cur2:
        reveal_type(cur2)
        cur3 = {await_} cur2.execute("")
        reveal_type(cur3)
"""
    cp = mypy.run_on_source(src)
    out = cp.stdout.decode("utf8", "replace").splitlines()
    assert len(out) == 3
    types = [mypy.get_revealed(line) for line in out]
    assert types[0] == types[1]
    assert types[0] == types[2]


def _test_reveal(stmts, type, mypy):
    ignore = "" if type.endswith("| None") else "# type: ignore[assignment]"
    stmts = "\n".join(f"    {line}" for line in stmts.splitlines())

    src = f"""\
from __future__ import annotations

from typing import Any, Callable, Dict, NamedTuple, Sequence, Tuple
import gaussdb
from gaussdb import rows

class Thing:
    def __init__(self, **kwargs: Any) -> None:
        self.kwargs = kwargs

def thing_row(
    cur: gaussdb.Cursor[Any] | gaussdb.AsyncCursor[Any],
) -> Callable[[Sequence[Any]], Thing]:
    assert cur.description
    names = [d.name for d in cur.description]

    def make_row(t: Sequence[Any]) -> Thing:
        return Thing(**dict(zip(names, t)))

    return make_row

async def tmp() -> None:
{stmts}
    reveal_type(obj)

ref: {type} = None  {ignore}
reveal_type(ref)
"""
    cp = mypy.run_on_source(src)
    out = cp.stdout.decode("utf8", "replace").splitlines()
    assert len(out) == 2, "\n".join(out)
    got, want = (mypy.get_revealed(line) for line in out)
    assert got == want


@pytest.mark.parametrize(
    "conn, type",
    [
        (
            "MyConnection.connect()",
            "MyConnection[Tuple[Any, ...]]",
        ),
        (
            "MyConnection.connect(row_factory=rows.tuple_row)",
            "MyConnection[Tuple[Any, ...]]",
        ),
        (
            "MyConnection.connect(row_factory=rows.dict_row)",
            "MyConnection[Dict[str, Any]]",
        ),
    ],
)
def test_generic_connect(conn, type, mypy):
    src = f"""
from typing import Any, Dict, Tuple
import gaussdb
from gaussdb import rows

class MyConnection(gaussdb.Connection[rows.Row]):
    pass

obj = {conn}
reveal_type(obj)

ref: {type} = None  # type: ignore[assignment]
reveal_type(ref)
"""
    cp = mypy.run_on_source(src)
    out = cp.stdout.decode("utf8", "replace").splitlines()
    assert len(out) == 2, "\n".join(out)
    got, want = (mypy.get_revealed(line) for line in out)
    assert got == want
