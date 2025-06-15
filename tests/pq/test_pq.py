import os

import pytest

import gaussdb
from gaussdb import pq

from ..utils import check_libpq_version


def test_version():
    rv = pq.version()
    assert rv >= 90204
    assert rv < 200000  # you are good for a while


def test_build_version():
    assert pq.__build_version__ and pq.__build_version__ >= 70400


@pytest.mark.skipif("not os.environ.get('GAUSSDB_TEST_WANT_LIBPQ_BUILD')")
def test_want_built_version():
    want = os.environ["GAUSSDB_TEST_WANT_LIBPQ_BUILD"]
    got = pq.__build_version__
    assert not check_libpq_version(got, want)


@pytest.mark.skipif("not os.environ.get('GAUSSDB_TEST_WANT_LIBPQ_IMPORT')")
def test_want_import_version():
    want = os.environ["GAUSSDB_TEST_WANT_LIBPQ_IMPORT"]
    got = pq.version()
    assert not check_libpq_version(got, want)


# Note: These tests are here because test_pipeline.py tests are all skipped
# when pipeline mode is not supported.


@pytest.mark.libpq(">= 14")
def test_pipeline_supported(conn):
    assert gaussdb.Pipeline.is_supported()
    assert gaussdb.AsyncPipeline.is_supported()

    with conn.pipeline():
        pass


@pytest.mark.libpq("< 14")
def test_pipeline_not_supported(conn):
    assert not gaussdb.Pipeline.is_supported()
    assert not gaussdb.AsyncPipeline.is_supported()

    with pytest.raises(gaussdb.NotSupportedError) as exc:
        with conn.pipeline():
            pass

    assert "requires libpq version 14.0 or newer" in str(exc.value)
