from __future__ import annotations

import os
import re
import sys
import asyncio
import selectors
from typing import Any

import pytest

from gaussdb import pq

pytest_plugins = (
    "tests.fix_db",
    "tests.fix_pq",
    "tests.fix_dns",
    "tests.fix_mypy",
    "tests.fix_faker",
    "tests.fix_proxy",
    "tests.fix_gaussdb",
    "tests.fix_crdb",
    "tests.fix_gc",
    "tests.pool.fix_pool",
)


def pytest_configure(config):
    markers = [
        "slow: this test is kinda slow (skip with -m 'not slow')",
        "flakey(reason): this test may fail unpredictably')",
        # There are troubles on travis with these kind of tests and I cannot
        # catch the exception for my life.
        "subprocess: the test import gaussdb after subprocess",
        "timing: the test is timing based and can fail on cheese hardware",
        "gevent: the test requires the gevent module to be installed",
        "dns: the test requires dnspython to run",
        "postgis: the test requires the PostGIS extension to run",
        "numpy: the test requires numpy module to be installed",
        "gaussdb_skip(reason): Skip test for GaussDB-specific behavior",
        "opengauss_skip(reason): Skip test for openGauss-specific behavior",
    ]

    for marker in markers:
        config.addinivalue_line("markers", marker)


def pytest_addoption(parser):
    parser.addoption(
        "--loop",
        choices=["default", "uvloop"],
        default="default",
        help="The asyncio loop to use for async tests.",
    )


def pytest_report_header(config):
    rv = []

    rv.append(f"default selector: {selectors.DefaultSelector.__name__}")
    loop = config.getoption("--loop")
    if loop != "default":
        rv.append(f"asyncio loop: {loop}")

    return rv


def pytest_sessionstart(session):
    # Detect if there was a segfault in the previous run.
    #
    # In case of segfault, pytest doesn't get a chance to write failed tests
    # in the cache. As a consequence, retries would find no test failed and
    # assume that all tests passed in the previous run, making the whole test pass.
    cache = session.config.cache
    if cache.get("segfault", False):
        session.warn(Warning("Previous run resulted in segfault! Not running any test"))
        session.warn(Warning("(delete '.pytest_cache/v/segfault' to clear this state)"))
        raise session.Failed
    cache.set("segfault", True)


asyncio_options: dict[str, Any] = {}
if sys.platform == "win32":
    asyncio_options["loop_factory"] = (
        asyncio.WindowsSelectorEventLoopPolicy().new_event_loop
    )


@pytest.fixture(
    params=[pytest.param(("asyncio", asyncio_options.copy()), id="asyncio")],
    scope="session",
)
def anyio_backend(request):
    backend, options = request.param
    if request.config.option.loop == "uvloop":
        options["use_uvloop"] = True
    return backend, options


allow_fail_messages: list[str] = []


def pytest_sessionfinish(session, exitstatus):
    # Mark the test run successful (in the sense -weak- that we didn't segfault).
    session.config.cache.set("segfault", False)


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    if allow_fail_messages:
        terminalreporter.section("failed tests ignored")
        for msg in allow_fail_messages:
            terminalreporter.line(msg)


def get_database_type():
    dsn = os.getenv("DSN") or os.getenv("GAUSSDB_TEST_DSN")
    if not dsn:
        print("DSN environment variable not set")
        return ""

    try:
        conn = pq.PGconn.connect(dsn.encode("utf-8"))
        if conn.status != pq.ConnStatus.OK:
            print(f"Connection failed: {conn.error_message.decode()}")
            conn.finish()
            return ""

        res = conn.exec_(b"SELECT version();")
        if res.status != pq.ExecStatus.TUPLES_OK:
            print(f"Query failed: {conn.error_message.decode()}")
            res.clear()
            conn.finish()
            return ""

        raw_version = res.get_value(0, 0)
        version = raw_version.decode("utf-8").lower() if raw_version is not None else ""

        res.clear()
        conn.finish()
        if re.search(r"\bgaussdb\b", version):
            return "gaussdb"
        if re.search(r"\bopengauss\b", version):
            return "opengauss"
    except Exception as e:
        print(f"Failed to get database version: {e}")
        return ""


def pytest_collection_modifyitems(config, items):
    res = get_database_type()
    print(f"Database type: {res}")
    for item in items:
        gaussdb_mark = item.get_closest_marker("gaussdb_skip")
        if gaussdb_mark and res == "gaussdb":
            reason = (
                gaussdb_mark.args[0] if gaussdb_mark.args else "Marked as gaussdb_skip"
            )
            item.add_marker(pytest.mark.skip(reason=reason))

        opengauss_mark = item.get_closest_marker("opengauss_skip")
        if opengauss_mark and res == "opengauss":
            reason = (
                opengauss_mark.args[0]
                if opengauss_mark.args
                else "Marked as opengauss_skip"
            )
            item.add_marker(pytest.mark.skip(reason=reason))
