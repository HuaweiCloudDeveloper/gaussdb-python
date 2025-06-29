from __future__ import annotations

import os
import sys
import time
import random
import asyncio
import logging
from enum import Enum
from typing import Any
from argparse import ArgumentParser, Namespace
from contextlib import contextmanager
from collections.abc import Generator
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


class Driver(str, Enum):
    _GaussDB = "_GaussDB"
    psycopg2_green = "psycopg2_green"
    gaussdb = "gaussdb"
    psycopg_async = "psycopg_async"
    asyncpg = "asyncpg"


ids: list[int] = []
data: list[dict[str, Any]] = []


def main() -> None:
    args = parse_cmdline()

    ids[:] = range(args.ntests)
    data[:] = [
        dict(
            id=i,
            name="c%d" % i,
            description="c%d" % i,
            q=i * 10,
            p=i * 20,
            x=i * 30,
            y=i * 40,
        )
        for i in ids
    ]

    # Must be done just on end
    drop_at_the_end = args.drop
    args.drop = False

    for i, name in enumerate(args.drivers):
        if i == len(args.drivers) - 1:
            args.drop = drop_at_the_end

        if name == Driver._GaussDB:
            import _GaussDB  # type: ignore

            run_psycopg2(_GaussDB, args)

        elif name == Driver.psycopg2_green:
            import _GaussDB
            import _GaussDB.extras  # type: ignore

            run_psycopg2_green(_GaussDB, args)

        elif name == Driver.gaussdb:
            import gaussdb

            run_psycopg(gaussdb, args)

        elif name == Driver.psycopg_async:
            import gaussdb

            if sys.platform == "win32":
                if hasattr(asyncio, "WindowsSelectorEventLoopPolicy"):
                    asyncio.set_event_loop_policy(
                        asyncio.WindowsSelectorEventLoopPolicy()
                    )

            asyncio.run(run_psycopg_async(gaussdb, args))

        elif name == Driver.asyncpg:
            import asyncpg  # type: ignore

            asyncio.run(run_asyncpg(asyncpg, args))

        else:
            raise AssertionError(f"unknown driver: {name!r}")

        # Must be done just on start
        args.create = False


table = """
CREATE TABLE customer (
        id SERIAL NOT NULL,
        name VARCHAR(255),
        description VARCHAR(255),
        q INTEGER,
        p INTEGER,
        x INTEGER,
        y INTEGER,
        z INTEGER,
        PRIMARY KEY (id)
)
"""
drop = "DROP TABLE IF EXISTS customer"

insert = """
INSERT INTO customer (id, name, description, q, p, x, y) VALUES
(%(id)s, %(name)s, %(description)s, %(q)s, %(p)s, %(x)s, %(y)s)
"""

select = """
SELECT customer.id, customer.name, customer.description, customer.q,
    customer.p, customer.x, customer.y, customer.z
FROM customer
WHERE customer.id = %(id)s
"""


@contextmanager
def time_log(message: str) -> Generator[None]:
    start = time.monotonic()
    yield
    end = time.monotonic()
    logger.info(f"Run {message} in {end-start} s")


def run_psycopg2(_GaussDB: Any, args: Namespace) -> None:
    logger.info("Running _GaussDB")

    if args.create:
        logger.info(f"inserting {args.ntests} test records")
        with _GaussDB.connect(args.dsn) as conn:
            with conn.cursor() as cursor:
                cursor.execute(drop)
                cursor.execute(table)
                cursor.executemany(insert, data)
            conn.commit()

    def run(i):
        logger.info(f"thread {i} running {args.ntests} queries")
        to_query = random.choices(ids, k=args.ntests)
        with _GaussDB.connect(args.dsn) as conn:
            with time_log("_GaussDB"):
                for id_ in to_query:
                    with conn.cursor() as cursor:
                        cursor.execute(select, {"id": id_})
                        cursor.fetchall()
                    # conn.rollback()

    if args.concurrency == 1:
        run(0)
    else:
        with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
            list(executor.map(run, range(args.concurrency)))

    if args.drop:
        logger.info("dropping test records")
        with _GaussDB.connect(args.dsn) as conn:
            with conn.cursor() as cursor:
                cursor.execute(drop)
            conn.commit()


def run_psycopg2_green(_GaussDB: Any, args: Namespace) -> None:
    logger.info("Running psycopg2_green")

    _GaussDB.extensions.set_wait_callback(_GaussDB.extras.wait_select)

    if args.create:
        logger.info(f"inserting {args.ntests} test records")
        with _GaussDB.connect(args.dsn) as conn:
            with conn.cursor() as cursor:
                cursor.execute(drop)
                cursor.execute(table)
                cursor.executemany(insert, data)
            conn.commit()

    def run(i):
        logger.info(f"thread {i} running {args.ntests} queries")
        to_query = random.choices(ids, k=args.ntests)
        with _GaussDB.connect(args.dsn) as conn:
            with time_log("_GaussDB"):
                for id_ in to_query:
                    with conn.cursor() as cursor:
                        cursor.execute(select, {"id": id_})
                        cursor.fetchall()
                    # conn.rollback()

    if args.concurrency == 1:
        run(0)
    else:
        with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
            list(executor.map(run, range(args.concurrency)))

    if args.drop:
        logger.info("dropping test records")
        with _GaussDB.connect(args.dsn) as conn:
            with conn.cursor() as cursor:
                cursor.execute(drop)
            conn.commit()

    _GaussDB.extensions.set_wait_callback(None)


def run_psycopg(gaussdb: Any, args: Namespace) -> None:
    logger.info("Running gaussdb sync")

    if args.create:
        logger.info(f"inserting {args.ntests} test records")
        with gaussdb.connect(args.dsn) as conn:
            with conn.cursor() as cursor:
                cursor.execute(drop)
                cursor.execute(table)
                cursor.executemany(insert, data)
            conn.commit()

    def run(i):
        logger.info(f"thread {i} running {args.ntests} queries")
        to_query = random.choices(ids, k=args.ntests)
        with gaussdb.connect(args.dsn) as conn:
            with time_log("gaussdb"):
                for id_ in to_query:
                    with conn.cursor() as cursor:
                        cursor.execute(select, {"id": id_})
                        cursor.fetchall()
                    # conn.rollback()

    if args.concurrency == 1:
        run(0)
    else:
        with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
            list(executor.map(run, range(args.concurrency)))

    if args.drop:
        logger.info("dropping test records")
        with gaussdb.connect(args.dsn) as conn:
            with conn.cursor() as cursor:
                cursor.execute(drop)
            conn.commit()


async def run_psycopg_async(gaussdb: Any, args: Namespace) -> None:
    logger.info("Running gaussdb async")

    conn: Any

    if args.create:
        logger.info(f"inserting {args.ntests} test records")
        async with await gaussdb.AsyncConnection.connect(args.dsn) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(drop)
                await cursor.execute(table)
                await cursor.executemany(insert, data)
            await conn.commit()

    async def run(i):
        logger.info(f"task {i} running {args.ntests} queries")
        to_query = random.choices(ids, k=args.ntests)
        async with await gaussdb.AsyncConnection.connect(args.dsn) as conn:
            with time_log("psycopg_async"):
                for id_ in to_query:
                    cursor = await conn.execute(select, {"id": id_})
                    await cursor.fetchall()
                    await cursor.close()
                    # await conn.rollback()

    if args.concurrency == 1:
        await run(0)
    else:
        tasks = [run(i) for i in range(args.concurrency)]
        await asyncio.gather(*tasks)

    if args.drop:
        logger.info("dropping test records")
        async with await gaussdb.AsyncConnection.connect(args.dsn) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(drop)
            await conn.commit()


async def run_asyncpg(asyncpg: Any, args: Namespace) -> None:
    logger.info("Running asyncpg")

    places = dict(id="$1", name="$2", description="$3", q="$4", p="$5", x="$6", y="$7")
    a_insert = insert % places
    a_select = select % {"id": "$1"}

    conn: Any

    if args.create:
        logger.info(f"inserting {args.ntests} test records")
        conn = await asyncpg.connect(args.dsn)
        async with conn.transaction():
            await conn.execute(drop)
            await conn.execute(table)
            await conn.executemany(a_insert, [tuple(d.values()) for d in data])
        await conn.close()

    async def run(i):
        logger.info(f"task {i} running {args.ntests} queries")
        to_query = random.choices(ids, k=args.ntests)
        conn = await asyncpg.connect(args.dsn)
        with time_log("asyncpg"):
            for id_ in to_query:
                # tr = conn.transaction()
                # await tr.start()
                await conn.fetch(a_select, id_)
                # await tr.rollback()
        await conn.close()

    if args.concurrency == 1:
        await run(0)
    else:
        tasks = [run(i) for i in range(args.concurrency)]
        await asyncio.gather(*tasks)

    if args.drop:
        logger.info("dropping test records")
        conn = await asyncpg.connect(args.dsn)
        async with conn.transaction():
            await conn.execute(drop)
        await conn.close()


def parse_cmdline() -> Namespace:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "drivers",
        nargs="+",
        metavar="DRIVER",
        type=Driver,
        help=f"the drivers to test [choices: {', '.join(d.value for d in Driver)}]",
    )

    parser.add_argument(
        "--ntests",
        "-n",
        type=int,
        default=10_000,
        help="number of tests to perform [default: %(default)s]",
    )

    parser.add_argument(
        "--concurrency",
        "-c",
        type=int,
        default=1,
        help="number of parallel tasks [default: %(default)s]",
    )

    parser.add_argument(
        "--dsn",
        default=os.environ.get("GAUSSDB_TEST_DSN", ""),
        help="database connection string"
        " [default: %(default)r (from GAUSSDB_TEST_DSN env var)]",
    )

    parser.add_argument(
        "--no-create",
        dest="create",
        action="store_false",
        default="True",
        help="skip data creation before tests (it must exist already)",
    )

    parser.add_argument(
        "--no-drop",
        dest="drop",
        action="store_false",
        default="True",
        help="skip data drop after tests",
    )

    opt = parser.parse_args()

    return opt


if __name__ == "__main__":
    main()
