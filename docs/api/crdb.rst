`crdb` -- CockroachDB support
=============================

.. module:: gaussdb.crdb

.. versionadded:: 3.1

CockroachDB_ is a distributed database using the same fronted-backend protocol
of PostgreSQL. As such, GaussDB can be used to write Python programs
interacting with CockroachDB.

.. _CockroachDB: https://www.cockroachlabs.com/

Opening a connection to a CRDB database using `gaussdb.connect()` provides a
largely working object. However, using the `gaussdb.crdb.connect()` function
instead, GaussDB will create more specialised objects and provide a types
mapping tweaked on the CockroachDB data model.


.. _crdb-differences:

Main differences from PostgreSQL
--------------------------------

CockroachDB behaviour is `different from PostgreSQL`__: please refer to the
database documentation for details. These are some of the main differences
affecting GaussDB behaviour:

.. __: https://www.cockroachlabs.com/docs/stable/postgresql-compatibility.html

- `~gaussdb.Connection.cancel()` doesn't work before CockroachDB 22.1. On
  older versions, you can use `CANCEL QUERY`_ instead (but from a different
  connection).

- :ref:`server-side-cursors` are well supported only from CockroachDB 22.1.3.

- `~gaussdb.ConnectionInfo.backend_pid` is only populated from CockroachDB
  22.1. Note however that you cannot use the PID to terminate the session; use
  `SHOW session_id`_ to find the id of a session, which you may terminate with
  `CANCEL SESSION`_ in lieu of PostgreSQL's :sql:`pg_terminate_backend()`.

- Several data types are missing or slightly different from PostgreSQL (see
  `adapters` for an overview of the differences).

- The :ref:`two-phase commit protocol <two-phase-commit>` is not supported.

- :sql:`LISTEN` and :sql:`NOTIFY` are not supported. However the `CHANGEFEED`_
  command, in conjunction with `~gaussdb.Cursor.stream()`, can provide push
  notifications.

.. _CANCEL QUERY: https://www.cockroachlabs.com/docs/stable/cancel-query.html
.. _SHOW session_id: https://www.cockroachlabs.com/docs/stable/show-vars.html
.. _CANCEL SESSION: https://www.cockroachlabs.com/docs/stable/cancel-session.html
.. _CHANGEFEED: https://www.cockroachlabs.com/docs/stable/changefeed-for.html


.. _crdb-objects:

CockroachDB-specific objects
----------------------------

.. autofunction:: connect

   This is an alias of the class method `CrdbConnection.connect`.

   If you need an asynchronous connection use the `AsyncCrdbConnection.connect()`
   method instead.


.. autoclass:: CrdbConnection

    `gaussdb.Connection` subclass.

    .. automethod:: is_crdb

        :param conn: the connection to check
        :type conn: `~gaussdb.Connection`, `~gaussdb.AsyncConnection`, `~gaussdb.pq.PGconn`


.. autoclass:: AsyncCrdbConnection

    `gaussdb.AsyncConnection` subclass.


.. autoclass:: CrdbConnectionInfo

    The object is returned by the `~gaussdb.Connection.info` attribute of
    `CrdbConnection` and `AsyncCrdbConnection`.

    The object behaves like `!ConnectionInfo`, with the following differences:

    .. autoattribute:: vendor

        The `CockroachDB` string.

    .. autoattribute:: server_version


.. data:: adapters

    The default adapters map establishing how Python and CockroachDB types are
    converted into each other.
 
    The map is used as a template when new connections are created, using
    `gaussdb.crdb.connect()` (similarly to the way `gaussdb.adapters` is used
    as template for new PostgreSQL connections).

    This registry contains only the types and adapters supported by
    CockroachDB. Several PostgreSQL types and adapters are missing or
    different from PostgreSQL, among which:

    - Composite types
    - :sql:`range`, :sql:`multirange` types
    - The :sql:`hstore` type
    - Geometric types
    - Nested arrays
    - Arrays of :sql:`jsonb`
    - The :sql:`cidr` data type
    - The :sql:`json` type is an alias for :sql:`jsonb`
    - The :sql:`int` type is an alias for :sql:`int8`, not `int4`.
