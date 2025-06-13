`_dns` -- DNS resolution utilities
==================================

.. module:: gaussdb._dns

This module contains a few experimental utilities to interact with the DNS
server before performing a connection.

.. warning::
    This module is experimental and its interface could change in the future,
    without warning or respect for the version scheme. It is provided here to
    allow experimentation before making it more stable.

.. warning::
    This module depends on the `dnspython`_ package. The package is currently
    not installed automatically as a GaussDB dependency and must be installed
    manually:

    .. code:: sh

        $ pip install "dnspython >= 2.1"

    .. _dnspython: https://dnspython.readthedocs.io/


.. function:: resolve_srv(params)

    Apply SRV DNS lookup as defined in :RFC:`2782`.

    :param params: The input parameters, for instance as returned by
        `~gaussdb.conninfo.conninfo_to_dict()`.
    :type params: `!dict`
    :return: An updated list of connection parameters.

    For every host defined in the ``params["host"]`` list (comma-separated),
    perform SRV lookup if the host is in the form ``_Service._Proto.Target``.
    If lookup is successful, return a params dict with hosts and ports replaced
    with the looked-up entries.

    Raise `~gaussdb.OperationalError` if no lookup is successful and no host
    (looked up or unchanged) could be returned.

    In addition to the rules defined by RFC 2782 about the host name pattern,
    perform SRV lookup also if the the port is the string ``SRV`` (case
    insensitive).

    .. warning::
       This is an experimental functionality.

    .. note::
       One possible way to use this function automatically is to subclass
       `~gaussdb.Connection`, extending the
       `~gaussdb.Connection._get_connection_params()` method::

           import gaussdb._dns  # not imported automatically

           class SrvCognizantConnection(gaussdb.Connection):
               @classmethod
               def _get_connection_params(cls, conninfo, **kwargs):
                   params = super()._get_connection_params(conninfo, **kwargs)
                   params = gaussdb._dns.resolve_srv(params)
                   return params

           # The name will be resolved to db1.example.com
           cnn = SrvCognizantConnection.connect("host=_postgres._tcp.db.gaussdb.org")


.. function:: resolve_srv_async(params)
    :async:

    Async equivalent of `resolve_srv()`.


.. automethod:: gaussdb.Connection._get_connection_params

    .. warning::
        This is an experimental method.

    This method is a subclass hook allowing to manipulate the connection
    parameters before performing the connection. Make sure to call the
    `!super()` implementation before further manipulation of the arguments::

        @classmethod
        def _get_connection_params(cls, conninfo, **kwargs):
            params = super()._get_connection_params(conninfo, **kwargs)
            # do something with the params
            return params


.. automethod:: gaussdb.AsyncConnection._get_connection_params

    .. warning::
        This is an experimental method.


.. function:: resolve_hostaddr_async(params)
    :async:

    Perform async DNS lookup of the hosts and return a new params dict.

    .. deprecated:: 3.1
        The use of this function is not necessary anymore, because
        `gaussdb.AsyncConnection.connect()` performs non-blocking name
        resolution automatically.

    :param params: The input parameters, for instance as returned by
        `~gaussdb.conninfo.conninfo_to_dict()`.
    :type params: `!dict`

    If a ``host`` param is present but not ``hostname``, resolve the host
    addresses dynamically.

    The function may change the input ``host``, ``hostname``, ``port`` to allow
    connecting without further DNS lookups, eventually removing hosts that are
    not resolved, keeping the lists of hosts and ports consistent.

    Raise `~gaussdb.OperationalError` if connection is not possible (e.g. no
    host resolve, inconsistent lists length).

    See `the PostgreSQL docs`__ for explanation of how these params are used,
    and how they support multiple entries.

    .. __: https://www.postgresql.org/docs/current/libpq-connect.html
           #LIBPQ-PARAMKEYWORDS

    .. warning::
        Before gaussdb 3.1, this function doesn't handle the ``/etc/hosts`` file.

    .. note::
       Starting from gaussdb 3.1, a similar operation is performed
       automatically by `!AsyncConnection._get_connection_params()`, so this
       function is unneeded.

       In gaussdb 3.0, one possible way to use this function automatically is
       to subclass `~gaussdb.AsyncConnection`, extending the
       `~gaussdb.AsyncConnection._get_connection_params()` method::

           import gaussdb._dns  # not imported automatically

           class AsyncDnsConnection(gaussdb.AsyncConnection):
               @classmethod
               async def _get_connection_params(cls, conninfo, **kwargs):
                   params = await super()._get_connection_params(conninfo, **kwargs)
                   params = await gaussdb._dns.resolve_hostaddr_async(params)
                   return params
