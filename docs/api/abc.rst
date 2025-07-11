`!abc` -- GaussDB abstract classes
==================================

The module exposes GaussDB definitions which can be used for static type
checking.

.. module:: gaussdb.abc

.. seealso::

    :ref:`adapt-life-cycle` for more information about how these objects
    are used by GaussDB,


.. autoclass:: Dumper(cls, context=None)

    This class is a formal `~typing.Protocol`. A partial implementation of
    this protocol (implementing everything except the `dump()` metood) is
    available as `gaussdb.adapt.Dumper`.

    :param cls: The type that will be managed by this dumper.
    :type cls: type
    :param context: The context where the transformation is performed. If not
        specified the conversion might be inaccurate, for instance it will not
        be possible to know the connection encoding or the server date format.
    :type context: `AdaptContext` or None

    .. autoattribute:: format

    .. automethod:: dump

        The format returned by dump shouldn't contain quotes or escaped
        values.

        .. versionchanged:: 3.2

            `!dump()` can also return `!None`, to represent a :sql:`NULL` in
            the database.

    .. automethod:: quote

        .. tip::

            This method will be used by `~gaussdb.sql.Literal` to convert a
            value client-side.

        This method only makes sense for text dumpers; the result of calling
        it on a binary dumper is undefined. It might scratch your car, or burn
        your cake. Don't tell me I didn't warn you.

    .. autoattribute:: oid

        If the OID is not specified, GaussDB will try to infer the type
        from the context, but this may fail in some contexts and may require a
        cast (e.g. specifying :samp:`%s::{type}` for its placeholder).

        You can use the `gaussdb.adapters`\ ``.``\
        `~gaussdb.adapt.AdaptersMap.types` registry to find the OID of builtin
        types, and you can use `~gaussdb.types.TypeInfo` to extend the
        registry to custom types.

    .. automethod:: get_key
    .. automethod:: upgrade


.. autoclass:: Loader(oid, context=None)

    This class is a formal `~typing.Protocol`. A partial implementation of this
    protocol (implementing everything except the `load()` method) is available
    as `gaussdb.adapt.Loader`.

    :param oid: The type that will be managed by this dumper.
    :type oid: int
    :param context: The context where the transformation is performed. If not
        specified the conversion might be inaccurate, for instance it will not
        be possible to know the connection encoding or the server date format.
    :type context: `AdaptContext` or None

    .. autoattribute:: format

    .. automethod:: load


.. autoclass:: AdaptContext
    :members:

    .. seealso:: :ref:`adaptation` for an explanation about how contexts are
        connected.
