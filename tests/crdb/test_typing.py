import pytest

from ..test_typing import _test_reveal


@pytest.mark.parametrize(
    "conn, type",
    [
        (
            "gaussdb.crdb.connect()",
            "gaussdb.crdb.CrdbConnection[Tuple[Any, ...]]",
        ),
        (
            "gaussdb.crdb.connect(row_factory=rows.dict_row)",
            "gaussdb.crdb.CrdbConnection[Dict[str, Any]]",
        ),
        (
            "gaussdb.crdb.CrdbConnection.connect()",
            "gaussdb.crdb.CrdbConnection[Tuple[Any, ...]]",
        ),
        (
            "gaussdb.crdb.CrdbConnection.connect(row_factory=rows.tuple_row)",
            "gaussdb.crdb.CrdbConnection[Tuple[Any, ...]]",
        ),
        (
            "gaussdb.crdb.CrdbConnection.connect(row_factory=rows.dict_row)",
            "gaussdb.crdb.CrdbConnection[Dict[str, Any]]",
        ),
        (
            "await gaussdb.crdb.AsyncCrdbConnection.connect()",
            "gaussdb.crdb.AsyncCrdbConnection[Tuple[Any, ...]]",
        ),
        (
            "await gaussdb.crdb.AsyncCrdbConnection.connect(row_factory=rows.dict_row)",
            "gaussdb.crdb.AsyncCrdbConnection[Dict[str, Any]]",
        ),
    ],
)
def test_connection_type(conn, type, mypy):
    stmts = f"obj = {conn}"
    _test_reveal_crdb(stmts, type, mypy)


def _test_reveal_crdb(stmts, type, mypy):
    stmts = f"""\
import gaussdb.crdb
{stmts}
"""
    _test_reveal(stmts, type, mypy)
