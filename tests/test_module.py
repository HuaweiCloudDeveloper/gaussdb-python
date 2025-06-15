import pytest

from gaussdb._cmodule import _gaussdb
from gaussdb.conninfo import conninfo_to_dict


@pytest.mark.parametrize(
    "args, kwargs, want",
    [
        ((), {}, ""),
        (("dbname=foo",), {"user": "bar"}, "dbname=foo user=bar"),
        ((), {"port": 15432}, "port=15432"),
        ((), {"user": "foo", "dbname": None}, "user=foo"),
    ],
)
def test_connect(monkeypatch, dsn_env, args, kwargs, want, setpgenv):
    # Check the main args passing from gaussdb.connect to the conn generator
    # Details of the params manipulation are in test_conninfo.
    import gaussdb.connection

    orig_connect = gaussdb.generators.connect

    got_conninfo: str

    def mock_connect(conninfo, *, timeout):
        nonlocal got_conninfo
        got_conninfo = conninfo
        return orig_connect(dsn_env, timeout=timeout)

    setpgenv({})
    monkeypatch.setattr(gaussdb.generators, "connect", mock_connect)

    conn = gaussdb.connect(*args, **kwargs)
    assert conninfo_to_dict(got_conninfo) == conninfo_to_dict(want)
    conn.close()


def test_version(mypy):
    cp = mypy.run_on_source(
        """\
from gaussdb import __version__
assert __version__
"""
    )
    assert not cp.stdout


@pytest.mark.skipif(_gaussdb is None, reason="C module test")
def test_version_c(mypy):
    # can be gaussdb_c, gaussdb_binary
    cpackage = _gaussdb.__name__.split(".")[0]

    cp = mypy.run_on_source(
        f"""\
from {cpackage} import __version__
assert __version__
"""
    )
    assert not cp.stdout
