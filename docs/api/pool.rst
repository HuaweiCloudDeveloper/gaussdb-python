`!gaussdb_pool` -- Connection pool implementations
==================================================

.. index::
    double: Connection; Pool

.. module:: gaussdb_pool

A connection pool is an object used to create and maintain a limited amount of
GaussDB connections, reducing the time requested by the program to obtain a
working connection and allowing an arbitrary large number of concurrent
threads or tasks to use a controlled amount of resources on the server. See
:ref:`connection-pools` for more details and usage pattern.

This package exposes a few connection pool classes:

- `ConnectionPool` is a synchronous connection pool yielding
  `~gaussdb.Connection` objects and can be used by multithread applications.

- `AsyncConnectionPool` has an interface similar to `!ConnectionPool`, but
  with `asyncio` functions replacing blocking functions, and yields
  `~gaussdb.AsyncConnection` instances.

- `NullConnectionPool` is a `!ConnectionPool` subclass exposing the same
  interface of its parent, but not keeping any unused connection in its state.
  See :ref:`null-pool` for details about related use cases.

- `AsyncNullConnectionPool` has the same behaviour of the
  `!NullConnectionPool`, but with the same async interface of the
  `!AsyncConnectionPool`.

.. note:: The `!gaussdb_pool` package is distributed separately from the main
   `gaussdb` package: use ``pip install "gaussdb[pool]"``, or ``pip install
   gaussdb_pool``, to make it available. See :ref:`pool-installation`.

   The version numbers indicated in this page refer to the `!gaussdb_pool`
   package, not to `gaussdb`.


The `!ConnectionPool` class
---------------------------

.. autoclass:: ConnectionPool

   This class implements a connection pool serving `~gaussdb.Connection`
   instances (or subclasses). The constructor has *alot* of arguments, but
   only `!conninfo` and `!min_size` are the fundamental ones, all the other
   arguments have meaningful defaults and can probably be tweaked later, if
   required.

   :param conninfo: The connection string. See
                    `~gaussdb.Connection.connect()` for details.
   :type conninfo: `!str`

   :param connection_class: The class of the connections to serve. It should
                            be a `!Connection` subclass.
   :type connection_class: `!type`, default: `~gaussdb.Connection`

   :param kwargs: Extra arguments to pass to `!connect()`. Note that this is
                  *one dict argument* of the pool constructor, which is
                  expanded as `connect()` keyword parameters.

   :type kwargs: `!dict`

   :param min_size: The minimum number of connection the pool will hold. The
                   pool will actively try to create new connections if some
                   are lost (closed, broken) and will try to never go below
                   `!min_size`.
   :type min_size: `!int`, default: 4

   :param max_size: The maximum number of connections the pool will hold. If
                   `!None`, or equal to `!min_size`, the pool will not grow or
                   shrink. If larger than `!min_size`, the pool can grow if
                   more than `!min_size` connections are requested at the same
                   time and will shrink back after the extra connections have
                   been unused for more than `!max_idle` seconds.
   :type max_size: `!int`, default: `!None`

   :param open: If `!True`, open the pool, creating the required connections,
                on init. If `!False`, open the pool when `!open()` is called or
                when the pool context is entered. See the `open()` method
                documentation for more details.
   :type open: `!bool`, default: `!True`

   :param configure: A callback to configure a connection after creation.
                     Useful, for instance, to configure its adapters. If the
                     connection is used to run internal queries (to inspect the
                     database) make sure to close an eventual transaction
                     before leaving the function.
   :type configure: `Callable[[Connection], None]`

   :param check: A callback to check that a connection is working correctly
                 when obtained by the pool. The callback is called at every
                 `getconn()` or `connection()`: the connection is only passed
                 to the client if the callback doesn't throw an exception.
                 By default no check is made on the connection. You can
                 provide the `check_connection()` pool static method if you
                 want to perform a simple check.
   :type check: `Callable[[Connection], None]`

   :param reset: A callback to reset a function after it has been returned to
                 the pool. The connection is guaranteed to be passed to the
                 `!reset()` function in "idle" state (no transaction). When
                 leaving the `!reset()` function the connection must be left in
                 *idle* state, otherwise it is discarded.
   :type reset: `Callable[[Connection], None]`

   :param name: An optional name to give to the pool, useful, for instance, to
                identify it in the logs if more than one pool is used. if not
                specified pick a sequential name such as ``pool-1``,
                ``pool-2``, etc.
   :type name: `!str`

   :param timeout: The default maximum time in seconds that a client can wait
                   to receive a connection from the pool (using `connection()`
                   or `getconn()`). Note that these methods allow to override
                   the `!timeout` default.
   :type timeout: `!float`, default: 30 seconds

   :param max_waiting: Maximum number of requests that can be queued to the
                       pool, after which new requests will fail, raising
                       `TooManyRequests`. 0 means no queue limit.
   :type max_waiting: `!int`, default: 0

   :param max_lifetime: The maximum lifetime of a connection in the pool, in
                        seconds. Connections used for longer get closed and
                        replaced by a new one. The amount is reduced by a
                        random 10% to avoid mass eviction.
   :type max_lifetime: `!float`, default: 1 hour

   :param max_idle: Maximum time, in seconds, that a connection can stay unused
                    in the pool before being closed, and the pool shrunk. This
                    only happens to connections more than `!min_size`, if
                    `!max_size` allowed the pool to grow.
   :type max_idle: `!float`, default: 10 minutes

   :param reconnect_timeout: Maximum time, in seconds, the pool will try to
                             create a connection. If a connection attempt
                             fails, the pool will try to reconnect a few
                             times, using an exponential backoff and some
                             random factor to avoid mass attempts. If repeated
                             attempts fail, after `!reconnect_timeout` second
                             the connection attempt is aborted and the
                             `!reconnect_failed()` callback invoked.
   :type reconnect_timeout: `!float`, default: 5 minutes

   :param reconnect_failed: Callback invoked if an attempt to create a new
                            connection fails for more than `!reconnect_timeout`
                            seconds. The user may decide, for instance, to
                            terminate the program (executing `sys.exit()`).
                            By default don't do anything: restart a new
                            connection attempt (if the number of connection
                            fell below `!min_size`).
   :type reconnect_failed: ``Callable[[ConnectionPool], None]``

   :param num_workers: Number of background worker threads used to maintain the
                       pool state. Background workers are used for example to
                       create new connections and to clean up connections when
                       they are returned to the pool.
   :type num_workers: `!int`, default: 3

   .. versionchanged:: 3.1
        added `!open` parameter to the constructor.

   .. versionchanged:: 3.2
        added `!check` parameter to the constructor.

   .. versionchanged:: 3.2
        The class is generic and `!connection_class` provides types type
        variable. See :ref:`pool-generic`.

   .. warning::

        At the moment, the default value for the `!open` parameter is `!True`;
        In a future version, the default will be changed to `!False`.

        If you expect the pool to be open on creation even if you don't use
        the pool as context manager, you should specify the parameter
        `!open=True` explicitly.

        Starting from gaussdb_pool 3.2, a warning is raised if the pool is
        used with the expectation of being implicitly opened in the
        constructor and `!open` is not specified.

   .. automethod:: connection

      .. code:: python

          with my_pool.connection() as conn:
              conn.execute(...)

          # the connection is now back in the pool

      .. versionchanged:: 3.2
        The connection returned is annotated as defined in `!connection_class`.
        See :ref:`pool-generic`.

   .. automethod:: open

      .. versionadded:: 3.1


   .. automethod:: close

   .. note::

      The pool can be also used as a context manager, in which case it will
      be opened (if necessary) on entering the block and closed on exiting it:

      .. code:: python

          with ConnectionPool(...) as pool:
              # code using the pool

   .. automethod:: wait

   .. attribute:: name
      :type: str

      The name of the pool set on creation, or automatically generated if not
      set.

   .. autoattribute:: min_size
   .. autoattribute:: max_size

      The current minimum and maximum size of the pool. Use `resize()` to
      change them at runtime.

   .. automethod:: resize
   .. automethod:: check
   .. automethod:: check_connection

      .. versionadded:: 3.2

   .. automethod:: get_stats
   .. automethod:: pop_stats

      See :ref:`pool-stats` for the metrics returned.

   .. rubric:: Functionalities you may not need

   .. automethod:: getconn
   .. automethod:: putconn


Pool exceptions
---------------

.. autoclass:: PoolTimeout()

   Subclass of `~gaussdb.OperationalError`

.. autoclass:: PoolClosed()

   Subclass of `~gaussdb.OperationalError`

.. autoclass:: TooManyRequests()

   Subclass of `~gaussdb.OperationalError`


The `!AsyncConnectionPool` class
--------------------------------

`!AsyncConnectionPool` has a very similar interface to the `ConnectionPool`
class but its blocking methods are implemented as `!async` coroutines. It
returns instances of `~gaussdb.AsyncConnection`, or of its subclass if
specified so in the `!connection_class` parameter.

Only the functions and parameters with different signature from
`!ConnectionPool` are listed here.

.. autoclass:: AsyncConnectionPool

   :param connection_class: The class of the connections to serve. It should
                            be an `!AsyncConnection` subclass.
   :type connection_class: `!type`, default: `~gaussdb.AsyncConnection`

   :param check: A callback to check that a connection is working correctly
                 when obtained by the pool.
   :type check: `async Callable[[Connection], None]`

   :param configure: A callback to configure a connection after creation.
   :type configure: `async Callable[[AsyncConnection], None]`

   :param reset: A callback to reset a function after it has been returned to
                 the pool.
   :type reset: `async Callable[[AsyncConnection], None]`

   :param reconnect_failed: Callback invoked if an attempt to create a new
        connection fails for more than `!reconnect_timeout` seconds.
   :type reconnect_failed: `Callable[[AsyncConnectionPool], None]` or
        `async Callable[[AsyncConnectionPool], None]`

   .. versionchanged:: 3.2
        added `!check` parameter to the constructor.

   .. versionchanged:: 3.2
        The `!reconnect_failed` parameter can be `!async`.

   .. warning::

        Opening an async pool in the constructor (using `!open=True` on init)
        will become an error in a future pool versions. Please note that,
        currently, `!open=True` is the default; in a future version, the
        default for the parameter will be changed to `!False`.

        In order to make sure that your code will keep working as expected in
        future versions, please specify `!open=False` in the constructor and
        use an explicit `!await pool.open()`::

            pool = AsyncConnectionPool(..., open=False)
            await pool.open()

        or use the pool context manager::

            async with AsyncConnectionPool(..., open=False) as pool:
                ...

        Starting from gaussdb_pool 3.2, opening an async pool in the
        constructor raises a warning.

   .. automethod:: connection

      .. code:: python

          async with my_pool.connection() as conn:
              await conn.execute(...)

          # the connection is now back in the pool

   .. automethod:: open
   .. automethod:: close

   .. note::

      The pool can be also used as an async context manager, in which case it
      will be opened (if necessary) on entering the block and closed on
      exiting it:

      .. code:: python

          async with AsyncConnectionPool(...) as pool:
              # code using the pool

   All the other constructor parameters are the same of `!ConnectionPool`.

   .. automethod:: wait
   .. automethod:: resize
   .. automethod:: check
   .. automethod:: check_connection

      .. versionadded:: 3.2

   .. automethod:: getconn
   .. automethod:: putconn


Null connection pools
---------------------

.. versionadded:: 3.1

The `NullConnectionPool` is a `ConnectionPool` subclass which doesn't create
connections preemptively and doesn't keep unused connections in its state. See
:ref:`null-pool` for further details.

The interface of the object is entirely compatible with its parent class. Its
behaviour is similar, with the following differences:

.. autoclass:: NullConnectionPool

   All the other constructor parameters are the same as in `ConnectionPool`.

   :param min_size: Always 0, cannot be changed.
   :type min_size: `!int`, default: 0

   :param max_size: If None or 0, create a new connection at every request,
                    without a maximum. If greater than 0, don't create more
                    than `!max_size` connections and queue the waiting clients.
   :type max_size: `!int`, default: None

   :param reset: It is only called when there are waiting clients in the
                 queue, before giving them a connection already open. If no
                 client is waiting, the connection is closed and discarded
                 without a fuss.
   :type reset: `Callable[[Connection], None]`

   :param max_idle: Ignored, as null pools don't leave idle connections
                    sitting around.

   .. automethod:: wait
   .. automethod:: resize
   .. automethod:: check


The `AsyncNullConnectionPool` is, similarly, an `AsyncConnectionPool` subclass
with the same behaviour of the `NullConnectionPool`.

.. autoclass:: AsyncNullConnectionPool

    The interface is the same of its parent class `AsyncConnectionPool`. The
    behaviour is different in the same way described for `NullConnectionPool`.
