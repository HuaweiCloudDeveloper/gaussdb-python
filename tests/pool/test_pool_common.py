# WARNING: this file is auto-generated by 'async_to_sync.py'
# from the original file 'test_pool_common_async.py'
# DO NOT CHANGE! Change the original file instead.
from __future__ import annotations

import logging
from time import time
from typing import Any

import pytest

import gaussdb

from ..utils import set_autocommit
from ..acompat import Event, gather, is_alive, skip_async, skip_sync, sleep, spawn

try:
    import gaussdb_pool as pool
except ImportError:
    # Tests should have been skipped if the package is not available
    pass


@pytest.fixture(params=["ConnectionPool", "NullConnectionPool"])
def pool_cls(request):
    return getattr(pool, request.param)


def test_defaults(pool_cls, dsn):
    with pool_cls(dsn) as p:
        assert p.open
        assert not p.closed
        assert p.timeout == 30
        assert p.max_idle == 10 * 60
        assert p.max_lifetime == 60 * 60
        assert p.num_workers == 3


def test_connection_class(pool_cls, dsn):

    class MyConn(gaussdb.Connection[Any]):
        pass

    with pool_cls(dsn, connection_class=MyConn, min_size=min_size(pool_cls)) as p:
        with p.connection() as conn:
            assert isinstance(conn, MyConn)


def test_kwargs(pool_cls, dsn):
    with pool_cls(dsn, kwargs={"autocommit": True}, min_size=min_size(pool_cls)) as p:
        with p.connection() as conn:
            assert conn.autocommit


def test_context(pool_cls, dsn):
    with pool_cls(dsn, min_size=min_size(pool_cls)) as p:
        assert not p.closed
    assert p.closed


def test_create_warning(pool_cls, dsn):
    warning_cls = DeprecationWarning
    # No warning on explicit open for sync pool
    p = pool_cls(dsn, open=True)
    try:
        with p.connection():
            pass
    finally:
        p.close()

    # No warning on explicit close
    p = pool_cls(dsn, open=False)
    p.open()
    try:
        with p.connection():
            pass
    finally:
        p.close()

    # No warning on context manager
    with pool_cls(dsn) as p:
        with p.connection():
            pass

    # Warning on open not specified
    with pytest.warns(warning_cls):
        p = pool_cls(dsn)
        try:
            with p.connection():
                pass
        finally:
            p.close()

    # Warning also if open is called explicitly on already implicitly open
    with pytest.warns(warning_cls):
        p = pool_cls(dsn)
        p.open()
        try:
            with p.connection():
                pass
        finally:
            p.close()


def test_wait_closed(pool_cls, dsn):
    with pool_cls(dsn) as p:
        pass

    with pytest.raises(pool.PoolClosed):
        p.wait()


@pytest.mark.slow
def test_setup_no_timeout(pool_cls, dsn, proxy):
    with pytest.raises(pool.PoolTimeout):
        with pool_cls(
            proxy.client_dsn, min_size=min_size(pool_cls), num_workers=1
        ) as p:
            p.wait(0.2)

    with pool_cls(proxy.client_dsn, min_size=min_size(pool_cls), num_workers=1) as p:
        sleep(0.5)
        assert not p._pool
        proxy.start()

        with p.connection() as conn:
            conn.execute("select 1")


@pytest.mark.slow
def test_configure_badstate(pool_cls, dsn, caplog):
    caplog.set_level(logging.WARNING, logger="gaussdb.pool")

    def configure(conn):
        conn.execute("select 1")

    with pool_cls(dsn, min_size=min_size(pool_cls), configure=configure) as p:
        with pytest.raises(pool.PoolTimeout):
            p.wait(timeout=0.5)

    assert caplog.records
    assert "INTRANS" in caplog.records[0].message


@pytest.mark.slow
def test_configure_broken(pool_cls, dsn, caplog):
    caplog.set_level(logging.WARNING, logger="gaussdb.pool")

    def configure(conn):
        with conn.transaction():
            conn.execute("WAT")

    with pool_cls(dsn, min_size=min_size(pool_cls), configure=configure) as p:
        with pytest.raises(pool.PoolTimeout):
            p.wait(timeout=0.5)

    assert caplog.records
    assert "WAT" in caplog.records[0].message


@pytest.mark.slow
@pytest.mark.timing
@pytest.mark.crdb_skip("backend pid")
@pytest.mark.gaussdb_skip("backend pid")
def test_queue(pool_cls, dsn):

    def worker(n):
        t0 = time()
        with p.connection() as conn:
            conn.execute("select pg_sleep(0.2)")
            pid = conn.info.backend_pid
        t1 = time()
        results.append((n, t1 - t0, pid))

    results: list[tuple[int, float, int]] = []
    with pool_cls(dsn, min_size=min_size(pool_cls, 2), max_size=2) as p:
        p.wait()
        ts = [spawn(worker, args=(i,)) for i in range(6)]
        gather(*ts)

    times = [item[1] for item in results]
    if pool_cls == pool.NullConnectionPool:
        want_times = [0.4, 0.4, 0.6, 0.6, 0.8, 0.8]
        tolerance = 0.5
    else:
        want_times = [0.3, 0.3, 0.6, 0.6, 0.9, 0.9]
        tolerance = 0.4
    for got, want in zip(times, want_times):
        assert got == pytest.approx(want, tolerance), times

    assert len({r[2] for r in results}) == 2, results


@pytest.mark.slow
def test_queue_size(pool_cls, dsn):

    def worker(t, ev=None):
        try:
            with p.connection():
                if ev:
                    ev.set()
                sleep(t)
        except pool.TooManyRequests as e:
            errors.append(e)
        else:
            success.append(True)

    errors: list[Exception] = []
    success: list[bool] = []

    with pool_cls(dsn, min_size=min_size(pool_cls), max_size=1, max_waiting=3) as p:
        p.wait()
        ev = Event()
        spawn(worker, args=(0.3, ev))
        ev.wait()

        ts = [spawn(worker, args=(0.1,)) for i in range(4)]
        gather(*ts)

    assert len(success) == 4
    assert len(errors) == 1
    assert isinstance(errors[0], pool.TooManyRequests)
    assert p.name in str(errors[0])
    assert str(p.max_waiting) in str(errors[0])
    assert p.get_stats()["requests_errors"] == 1


@pytest.mark.slow
@pytest.mark.timing
@pytest.mark.crdb_skip("backend pid")
@pytest.mark.gaussdb_skip("backend pid")
def test_queue_timeout(pool_cls, dsn):

    def worker(n):
        t0 = time()
        try:
            with p.connection() as conn:
                conn.execute("select pg_sleep(0.2)")
                pid = conn.info.backend_pid
        except pool.PoolTimeout as e:
            t1 = time()
            errors.append((n, t1 - t0, e))
        else:
            t1 = time()
            results.append((n, t1 - t0, pid))

    results: list[tuple[int, float, int]] = []
    errors: list[tuple[int, float, Exception]] = []

    with pool_cls(dsn, min_size=min_size(pool_cls, 2), max_size=2, timeout=0.1) as p:
        ts = [spawn(worker, args=(i,)) for i in range(4)]
        gather(*ts)

    assert len(results) == 2
    assert len(errors) == 2
    for e in errors:
        assert 0.1 < e[1] < 0.15


@pytest.mark.slow
@pytest.mark.timing
def test_dead_client(pool_cls, dsn):

    def worker(i, timeout):
        try:
            with p.connection(timeout=timeout) as conn:
                conn.execute("select pg_sleep(0.3)")
                results.append(i)
        except pool.PoolTimeout:
            if timeout > 0.2:
                raise

    with pool_cls(dsn, min_size=min_size(pool_cls, 2), max_size=2) as p:
        results: list[int] = []
        ts = [
            spawn(worker, args=(i, timeout))
            for i, timeout in enumerate([0.6, 0.6, 0.1, 0.9, 0.9])
        ]
        gather(*ts)

        sleep(0.2)
        assert set(results) == {0, 1, 3, 4}
        if pool_cls is pool.ConnectionPool:
            assert len(p._pool) == 2  # no connection was lost


@pytest.mark.slow
@pytest.mark.timing
@pytest.mark.gaussdb_skip("backend pid")
@pytest.mark.crdb_skip("backend pid")
def test_queue_timeout_override(pool_cls, dsn):

    def worker(n):
        t0 = time()
        timeout = 0.25 if n == 3 else None
        try:
            with p.connection(timeout=timeout) as conn:
                conn.execute("select pg_sleep(0.2)")
                pid = conn.info.backend_pid
        except pool.PoolTimeout as e:
            t1 = time()
            errors.append((n, t1 - t0, e))
        else:
            t1 = time()
            results.append((n, t1 - t0, pid))

    results: list[tuple[int, float, int]] = []
    errors: list[tuple[int, float, Exception]] = []

    with pool_cls(dsn, min_size=min_size(pool_cls, 2), max_size=2, timeout=0.1) as p:
        ts = [spawn(worker, args=(i,)) for i in range(4)]
        gather(*ts)

    assert len(results) == 3
    assert len(errors) == 1
    for e in errors:
        assert 0.1 < e[1] < 0.15


@pytest.mark.gaussdb_skip("backend pid")
@pytest.mark.opengauss_skip("backend pid")
@pytest.mark.crdb_skip("backend pid")
def test_broken_reconnect(pool_cls, dsn):
    with pool_cls(dsn, min_size=min_size(pool_cls), max_size=1) as p:
        with p.connection() as conn:
            pid1 = conn.info.backend_pid
            conn.close()

        with p.connection() as conn2:
            pid2 = conn2.info.backend_pid

    assert pid1 != pid2


def test_close_no_tasks(pool_cls, dsn):
    p = pool_cls(dsn)
    assert p._sched_runner and is_alive(p._sched_runner)
    workers = p._workers[:]
    assert workers
    for t in workers:
        assert is_alive(t)

    p.close()
    assert p._sched_runner is None
    assert not p._workers
    for t in workers:
        assert not is_alive(t)


def test_putconn_no_pool(pool_cls, conn_cls, dsn):
    with pool_cls(dsn, min_size=min_size(pool_cls)) as p:
        conn = conn_cls.connect(dsn)
        with pytest.raises(ValueError):
            p.putconn(conn)

    conn.close()


def test_putconn_wrong_pool(pool_cls, dsn):
    with pool_cls(dsn, min_size=min_size(pool_cls)) as p1:
        with pool_cls(dsn, min_size=min_size(pool_cls)) as p2:
            conn = p1.getconn()
            with pytest.raises(ValueError):
                p2.putconn(conn)


@skip_async
@pytest.mark.slow
def test_del_stops_threads(pool_cls, dsn, gc):
    p = pool_cls(dsn)
    assert p._sched_runner is not None
    ts = [p._sched_runner] + p._workers
    del p
    gc.collect()
    sleep(0.1)
    for t in ts:
        assert not is_alive(t), t


def test_closed_getconn(pool_cls, dsn):
    p = pool_cls(dsn, min_size=min_size(pool_cls), open=False)
    p.open()
    assert not p.closed
    with p.connection():
        pass

    p.close()
    assert p.closed

    with pytest.raises(pool.PoolClosed):
        with p.connection():
            pass


def test_close_connection_on_pool_close(pool_cls, dsn):
    p = pool_cls(dsn, min_size=min_size(pool_cls), open=False)
    p.open()
    with p.connection() as conn:
        p.close()
    assert conn.closed


def test_closed_queue(pool_cls, dsn):

    def w1():
        with p.connection() as conn:
            e1.set()  # Tell w0 that w1 got a connection
            cur = conn.execute("select 1")
            assert cur.fetchone() == (1,)
            e2.wait()  # Wait until w0 has tested w2
        success.append("w1")

    def w2():
        try:
            with p.connection():
                pass  # unexpected
        except pool.PoolClosed:
            success.append("w2")

    e1 = Event()
    e2 = Event()

    with pool_cls(dsn, min_size=min_size(pool_cls), max_size=1) as p:
        p.wait()
        success: list[str] = []

        t1 = spawn(w1)
        # Wait until w1 has received a connection
        e1.wait()

        t2 = spawn(w2)
        # Wait until w2 is in the queue
        ensure_waiting(p)

    # Wait for the workers to finish
    e2.set()
    gather(t1, t2)
    assert len(success) == 2


def test_open_explicit(pool_cls, dsn):
    p = pool_cls(dsn, open=False)
    assert p.closed
    with pytest.raises(pool.PoolClosed, match="is not open yet"):
        p.getconn()

    with pytest.raises(pool.PoolClosed, match="is not open yet"):
        with p.connection():
            pass

    p.open()
    try:
        assert not p.closed

        with p.connection() as conn:
            cur = conn.execute("select 1")
            assert cur.fetchone() == (1,)
    finally:
        p.close()

    with pytest.raises(pool.PoolClosed, match="is already closed"):
        p.getconn()


def test_open_context(pool_cls, dsn):
    p = pool_cls(dsn, open=False)
    assert p.closed

    with p:
        assert not p.closed

        with p.connection() as conn:
            cur = conn.execute("select 1")
            assert cur.fetchone() == (1,)

    assert p.closed


def test_open_no_op(pool_cls, dsn):
    p = pool_cls(dsn, open=False)
    p.open()
    try:
        assert not p.closed
        p.open()
        assert not p.closed

        with p.connection() as conn:
            cur = conn.execute("select 1")
            assert cur.fetchone() == (1,)
    finally:
        p.close()


def test_reopen(pool_cls, dsn):
    p = pool_cls(dsn, open=False)
    p.open()
    with p.connection() as conn:
        conn.execute("select 1")
    p.close()
    assert p._sched_runner is None
    assert not p._workers

    with pytest.raises(gaussdb.OperationalError, match="cannot be reused"):
        p.open()


def test_jitter(pool_cls):
    rnds = [pool_cls._jitter(30, -0.1, +0.2) for i in range(100)]
    assert 27 <= min(rnds) <= 28
    assert 35 < max(rnds) < 36


@pytest.mark.slow
@pytest.mark.timing
@pytest.mark.gaussdb_skip("connection pooling")
def test_stats_measures(pool_cls, dsn):

    def worker(n):
        with p.connection() as conn:
            conn.execute("select pg_sleep(0.2)")

    with pool_cls(dsn, min_size=min_size(pool_cls, 2), max_size=4) as p:
        p.wait(2.0)

        stats = p.get_stats()
        assert stats["pool_min"] == min_size(pool_cls, 2)
        assert stats["pool_max"] == 4
        assert stats["pool_size"] == min_size(pool_cls, 2)
        assert stats["pool_available"] == min_size(pool_cls, 2)
        assert stats["requests_waiting"] == 0

        ts = [spawn(worker, args=(i,)) for i in range(3)]
        sleep(0.1)
        stats = p.get_stats()
        gather(*ts)
        assert stats["pool_min"] == min_size(pool_cls, 2)
        assert stats["pool_max"] == 4
        assert stats["pool_size"] == 3
        assert stats["pool_available"] == 0
        assert stats["requests_waiting"] == 0

        p.wait(2.0)
        ts = [spawn(worker, args=(i,)) for i in range(7)]
        sleep(0.1)
        stats = p.get_stats()
        gather(*ts)
        assert stats["pool_min"] == min_size(pool_cls, 2)
        assert stats["pool_max"] == 4
        assert stats["pool_size"] == 4
        assert stats["pool_available"] == 0
        assert stats["requests_waiting"] == 3


@pytest.mark.slow
@pytest.mark.timing
def test_stats_usage(pool_cls, dsn):

    def worker(n):
        try:
            with p.connection(timeout=0.3) as conn:
                conn.execute("select pg_sleep(0.2)")
        except pool.PoolTimeout:
            pass

    with pool_cls(dsn, min_size=min_size(pool_cls, 3), max_size=3) as p:
        p.wait(2.0)

        ts = [spawn(worker, args=(i,)) for i in range(7)]
        gather(*ts)
        stats = p.get_stats()
        assert stats["requests_num"] == 7
        assert stats["requests_queued"] == 4
        assert 550 <= stats["requests_wait_ms"] <= 1500
        assert stats["requests_errors"] == 1
        assert 800 <= stats["usage_ms"] <= 2500
        assert stats.get("returns_bad", 0) == 0

        with p.connection() as conn:
            conn.close()
        p.wait()
        stats = p.pop_stats()
        assert stats["requests_num"] == 8
        assert stats["returns_bad"] == 1
        with p.connection():
            pass
        assert p.get_stats()["requests_num"] == 1


def test_debug_deadlock(pool_cls, dsn):
    # https://github.com/gaussdb/gaussdb/issues/230
    logger = logging.getLogger("gaussdb")
    handler = logging.StreamHandler()
    old_level = logger.level
    logger.setLevel(logging.DEBUG)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    try:
        with pool_cls(dsn, min_size=min_size(pool_cls, 4)) as p:
            p.wait(timeout=2)
    finally:
        logger.removeHandler(handler)
        logger.setLevel(old_level)


@pytest.mark.gaussdb_skip("pg_terminate_backend")
@pytest.mark.crdb_skip("pg_terminate_backend")
@pytest.mark.parametrize("autocommit", [True, False])
def test_check_connection(pool_cls, conn_cls, dsn, autocommit):
    conn = conn_cls.connect(dsn)
    set_autocommit(conn, autocommit)
    pool_cls.check_connection(conn)
    assert not conn.closed
    assert conn.info.transaction_status == gaussdb.pq.TransactionStatus.IDLE

    with conn_cls.connect(dsn) as conn2:
        conn2.execute("select pg_terminate_backend(%s)", [conn.info.backend_pid])

    with pytest.raises(gaussdb.OperationalError):
        pool_cls.check_connection(conn)

    assert conn.closed


def test_check_init(pool_cls, dsn):
    checked = False

    def check(conn):
        nonlocal checked
        checked = True

    with pool_cls(dsn, check=check) as p:
        with p.connection(timeout=1.0) as conn:
            conn.execute("select 1")

    assert checked


@pytest.mark.slow
def test_check_timeout(pool_cls, dsn):

    def check(conn):
        raise Exception()

    t0 = time()
    with pytest.raises(pool.PoolTimeout):
        with pool_cls(dsn, check=check, timeout=1.0) as p:
            with p.connection():
                assert False

    assert time() - t0 <= 1.5


@skip_sync
def test_cancellation_in_queue(pool_cls, dsn):
    # https://github.com/gaussdb/gaussdb/issues/509

    nconns = 3

    with pool_cls(
        dsn, min_size=min_size(pool_cls, nconns), max_size=nconns, timeout=1
    ) as p:
        p.wait()

        got_conns = []
        ev = Event()

        def worker(i):
            try:
                logging.info("worker %s started", i)

                with p.connection() as conn:
                    logging.info("worker %s got conn", i)
                    cur = conn.execute("select 1")
                    assert cur.fetchone() == (1,)

                    got_conns.append(conn)
                    if len(got_conns) >= nconns:
                        ev.set()

                    sleep(5)
            except BaseException as ex:
                logging.info("worker %s stopped: %r", i, ex)
                raise

        # Start tasks taking up all the connections and getting in the queue
        tasks = [spawn(worker, (i,)) for i in range(nconns * 3)]

        # wait until the pool has served all the connections and clients are queued.
        ev.wait(3.0)
        for i in range(10):
            if p.get_stats().get("requests_queued", 0):
                break
            else:
                sleep(0.1)
        else:
            pytest.fail("no client got in the queue")

        [task.cancel() for task in reversed(tasks)]
        gather(*tasks, return_exceptions=True, timeout=1.0)

        stats = p.get_stats()
        assert stats["pool_available"] == min_size(pool_cls, nconns)
        assert stats.get("requests_waiting", 0) == 0

        with p.connection() as conn:
            cur = conn.execute("select 1")
            assert cur.fetchone() == (1,)


def min_size(pool_cls, num=1):
    """Return the minimum min_size supported by the pool class."""
    if pool_cls is pool.ConnectionPool:
        return num
    elif pool_cls is pool.NullConnectionPool:
        return 0
    else:
        assert False, pool_cls


def delay_connection(monkeypatch, sec):
    """
    Return a _connect_gen function delayed by the amount of seconds
    """

    def connect_delay(*args, **kwargs):
        t0 = time()
        rv = connect_orig(*args, **kwargs)
        t1 = time()
        sleep(max(0, sec - (t1 - t0)))
        return rv

    connect_orig = gaussdb.Connection.connect
    monkeypatch.setattr(gaussdb.Connection, "connect", connect_delay)


def ensure_waiting(p, num=1):
    """
    Wait until there are at least *num* clients waiting in the queue.
    """
    while len(p._waiting) < num:
        sleep(0)
