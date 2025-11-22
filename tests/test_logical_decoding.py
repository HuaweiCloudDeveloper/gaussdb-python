import pytest

from .conftest import get_wal_level

SLOT_NAME = "slot_test"
SCHEMA = "my_schema"
TABLE = "test01"


@pytest.fixture(scope="session", autouse=True)
def check_wal_level():
    """Check if wal_level is set to logical, skip tests if not."""
    wal_level = get_wal_level()
    if wal_level != "logical":
        pytest.skip(f"wal_level={wal_level!r}, expected 'logical'")


def _slot_exists(conn, slot_name):
    cur = conn.cursor()
    cur.execute(
        "SELECT count(1) FROM pg_replication_slots WHERE slot_name = %s",
        (slot_name,),
    )
    row = cur.fetchone()
    return bool(row and row[0] > 0)


def _cleanup_slot_and_schema(conn):
    cur = conn.cursor()
    # Drop slot if exists
    try:
        cur.execute(
            "SELECT count(1) FROM pg_replication_slots WHERE slot_name = %s",
            (SLOT_NAME,),
        )
        if cur.fetchone()[0] > 0:
            cur.execute("SELECT pg_drop_replication_slot(%s);", (SLOT_NAME,))
    except Exception:
        pass

    # Drop schema cascade
    try:
        cur.execute(f"DROP SCHEMA IF EXISTS {SCHEMA} CASCADE;")
    except Exception:
        pass
    conn.commit()


@pytest.fixture(scope="function")
def setup_env(conn, check_wal_level):
    """Ensure clean environment for each test."""
    _cleanup_slot_and_schema(conn)
    cur = conn.cursor()
    cur.execute(f"CREATE SCHEMA {SCHEMA};")
    cur.execute(f"SET search_path TO {SCHEMA};")
    cur.execute(f"CREATE TABLE {TABLE} (id int, name varchar(255));")
    cur.execute(f"ALTER TABLE {TABLE} REPLICA IDENTITY FULL;")
    conn.commit()
    yield conn
    _cleanup_slot_and_schema(conn)


def _create_slot(cur):
    cur.execute(
        "SELECT * FROM pg_create_logical_replication_slot(%s, %s);",
        (SLOT_NAME, "mppdb_decoding"),
    )


def _read_changes(cur):
    cur.execute(
        "SELECT data FROM pg_logical_slot_get_changes(%s, NULL, %s);",
        (SLOT_NAME, 4096),
    )
    rows = cur.fetchall()
    return [str(r[0]) for r in rows if r and r[0] is not None]


def test_create_replication_slot(setup_env):
    cur = setup_env.cursor()
    _create_slot(cur)
    assert _slot_exists(setup_env, SLOT_NAME)


def test_insert_produces_changes(setup_env):
    cur = setup_env.cursor()
    _create_slot(cur)
    assert _slot_exists(setup_env, SLOT_NAME)

    # insert
    cur.execute(f"INSERT INTO {TABLE} VALUES (%s, %s);", (1, "hello world"))
    setup_env.commit()

    changes = _read_changes(cur)
    joined = "\n".join(changes).lower()

    assert "insert" in joined, "Insert event not present"
    assert "hello world" in joined, "Inserted value missing"


def test_update_produces_changes(setup_env):
    cur = setup_env.cursor()
    _create_slot(cur)
    assert _slot_exists(setup_env, SLOT_NAME)

    # prepare row
    cur.execute(f"INSERT INTO {TABLE} VALUES (%s, %s);", (1, "hello world"))
    setup_env.commit()

    # update
    cur.execute(
        f"UPDATE {TABLE} SET name = %s WHERE id = %s;",
        ("hello gaussdb", 1),
    )
    setup_env.commit()

    changes = _read_changes(cur)
    joined = "\n".join(changes).lower()

    assert "update" in joined, "Update event not present"
    assert "hello gaussdb" in joined, "Updated value missing"


def test_delete_produces_changes(setup_env):
    cur = setup_env.cursor()
    _create_slot(cur)
    assert _slot_exists(setup_env, SLOT_NAME)

    # prepare row
    cur.execute(f"INSERT INTO {TABLE} VALUES (%s, %s);", (1, "to_delete"))
    setup_env.commit()

    # delete
    cur.execute(f"DELETE FROM {TABLE} WHERE id = %s;", (1,))
    setup_env.commit()

    changes = _read_changes(cur)
    joined = "\n".join(changes).lower()

    assert "delete" in joined, "Delete event not present"
    assert "to_delete" in joined, "Deleted value missing"


def test_drop_replication_slot(setup_env):
    cur = setup_env.cursor()
    _create_slot(cur)
    assert _slot_exists(setup_env, SLOT_NAME)

    # drop slot
    cur.execute("SELECT pg_drop_replication_slot(%s);", (SLOT_NAME,))
    setup_env.commit()

    # verify removed
    cur.execute(
        "SELECT count(1) FROM pg_replication_slots WHERE slot_name = %s;",
        (SLOT_NAME,),
    )
    assert cur.fetchone()[0] == 0
