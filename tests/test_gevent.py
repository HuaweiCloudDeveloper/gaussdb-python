import sys
import json
import subprocess as sp

import pytest

import gaussdb

pytest.importorskip("gevent")

pytestmark = [pytest.mark.gevent]


@pytest.mark.slow
@pytest.mark.timing
def test_gevent(dsn):
    TICK = 0.1
    script = f"""\
import gevent.monkey
gevent.monkey.patch_all()

import json
import time
import gevent
import gaussdb

TICK = {TICK!r}
dts = []
queried = False

def ticker():
    t0 = time.time()
    for i in range(5):
        time.sleep(TICK)
        t = time.time()
        dts.append(t - t0)
        t0 = t

def querier():
    time.sleep(TICK * 2)
    with gaussdb.connect({dsn!r}) as conn:
        conn.execute("select pg_sleep(0.3)")

    global queried
    queried = True

jobs = [gevent.spawn(ticker), gevent.spawn(querier)]
gevent.joinall(jobs, timeout=3)
print(json.dumps(dts))
"""
    cmdline = [sys.executable, "-c", script]
    rv = sp.run(cmdline, check=True, text=True, stdout=sp.PIPE)
    dts = json.loads(rv.stdout)

    for dt in dts:
        assert TICK <= dt < TICK * 1.1


@pytest.mark.skipif("not gaussdb._cmodule._gaussdb")
def test_patched_dont_use_wait_c():
    if gaussdb.waiting.wait is not gaussdb.waiting.wait_c:
        pytest.skip("wait_c not normally in use")

    script = """
import gevent.monkey
gevent.monkey.patch_all()

import gaussdb
assert gaussdb.waiting.wait is not gaussdb.waiting.wait_c
"""
    sp.check_call([sys.executable, "-c", script])


@pytest.mark.skipif("not gaussdb._cmodule._gaussdb")
def test_unpatched_still_use_wait_c():
    if gaussdb.waiting.wait is not gaussdb.waiting.wait_c:
        pytest.skip("wait_c not normally in use")

    script = """
import gevent.monkey

import gaussdb
assert gaussdb.waiting.wait is gaussdb.waiting.wait_c
"""
    sp.check_call([sys.executable, "-c", script])
