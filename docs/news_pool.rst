.. currentmodule:: gaussdb_pool

.. index::
    single: Release notes
    single: News

``gaussdb_pool`` release notes
==============================

Current release
---------------

gaussdb_pool 3.2.6
^^^^^^^^^^^^^^^^^^

- Reset transaction status of connection failing check (:ticket:`#1014`).


gaussdb_pool 3.2.5
^^^^^^^^^^^^^^^^^^

- Fix spurious warning logging on pool shrinking (:ticket:`#1001`).


gaussdb_pool 3.2.4
^^^^^^^^^^^^^^^^^^

- Add a hint to the warning printed if threads fail to stop during
  ``__del__``, which has been reported happening during interpreter shutdown
  on Python 3.13 (see :ticket:`#954`).


gaussdb_pool 3.2.3
^^^^^^^^^^^^^^^^^^

- Add metadata to declare compatibility with Python 3.13.


gaussdb_pool 3.2.2
^^^^^^^^^^^^^^^^^^

- Raise a `RuntimeWarning` instead of a `DeprecationWarning` if an async pool
  is open in the constructor.
- Fix connections possibly left in the pool after closing (:ticket:`#784`).
- Use an empty query instead of ``SELECT 1`` to check connections
  (:ticket:`#790`).


gaussdb_pool 3.2.1
^^^^^^^^^^^^^^^^^^

- Respect the `!timeout` parameter on `~ConnectionPool.connection()` when
  `!check` fails. Also avoid a busy-loop of checking; separate check attempts
  using an exponential backoff (:ticket:`#709`).
- Use `typing.Self` as a more correct return value annotation of context
  managers and other self-returning methods (see :ticket:`708`).


gaussdb_pool 3.2.0
------------------

- Add support for async `!reconnect_failed` callbacks in `AsyncConnectionPool`
  (:ticket:`#520`).
- Add `!check` parameter to the pool constructor and
  `~ConnectionPool.check_connection()` method. (:ticket:`#656`).
- Make connection pool classes generic on the connection type (:ticket:`#559`).
- Raise a warning if sync pools rely an implicit `!open=True` and the
  pool context is not used. In the future the default will become `!False`
  (:ticket:`#659`).
- Raise a warning if async pools are opened in the constructor. In the future
  it will become an error. (:ticket:`#659`).


gaussdb_pool 3.1.9
^^^^^^^^^^^^^^^^^^

- Fix the return type annotation of `!NullConnectionPool.__enter__()`
  (:ticket:`#540`).


gaussdb_pool 3.1.8
^^^^^^^^^^^^^^^^^^

- Enforce connections' ``max_lifetime`` on `~ConnectionPool.check()`
  (:ticket:`#482`).


gaussdb_pool 3.1.7
^^^^^^^^^^^^^^^^^^

- Fix handling of tasks cancelled while waiting in async pool queue
  (:ticket:`#503`).


gaussdb_pool 3.1.6
^^^^^^^^^^^^^^^^^^

- Declare all parameters in pools constructors, instead of using `!**kwargs`
  (:ticket:`#493`).


gaussdb_pool 3.1.5
^^^^^^^^^^^^^^^^^^

- Make sure that `!ConnectionPool.check()` refills an empty pool
  (:ticket:`#438`).
- Avoid error in Pyright caused by aliasing `!TypeAlias` (:ticket:`#439`).


gaussdb_pool 3.1.4
^^^^^^^^^^^^^^^^^^

- Fix async pool exhausting connections, happening if the pool is created
  before the event loop is started (:ticket:`#219`).


gaussdb_pool 3.1.3
^^^^^^^^^^^^^^^^^^

- Add support for Python 3.11 (:ticket:`#305`).


gaussdb_pool 3.1.2
^^^^^^^^^^^^^^^^^^

- Fix possible failure to reconnect after losing connection from the server
  (:ticket:`#370`).


gaussdb_pool 3.1.1
^^^^^^^^^^^^^^^^^^

- Fix race condition on pool creation which might result in the pool not
  filling (:ticket:`#230`).


gaussdb_pool 3.1.0
------------------

- Add :ref:`null-pool` (:ticket:`#148`).
- Add `ConnectionPool.open()` and `!open` parameter to the pool constructor
  (:ticket:`#151`).
- Drop support for Python 3.6.


gaussdb_pool 3.0.3
^^^^^^^^^^^^^^^^^^

- Raise `!ValueError` if `ConnectionPool` `!min_size` and `!max_size` are both
  set to 0 (instead of hanging).
- Raise `PoolClosed` calling `~ConnectionPool.wait()` on a closed pool.


gaussdb_pool 3.0.2
^^^^^^^^^^^^^^^^^^

- Remove dependency on the internal `!gaussdb._compat` module.


gaussdb_pool 3.0.1
^^^^^^^^^^^^^^^^^^

- Don't leave connections idle in transaction after calling
  `~ConnectionPool.check()` (:ticket:`#144`).


gaussdb_pool 3.0
----------------

- First release on PyPI.
