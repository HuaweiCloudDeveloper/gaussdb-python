.. _gaussdb.rows:

`rows` -- row factory implementations
=====================================

.. module:: gaussdb.rows

The module exposes a few generic `~gaussdb.RowFactory` implementation, which
can be used to retrieve data from the database in more complex structures than
the basic tuples.

Check out :ref:`row-factory-create` for information about how to use these objects.

.. autofunction:: tuple_row

    Example::

        >>> cur = conn.cursor(row_factory=tuple_row)
        >>> cur.execute("SELECT 10 AS foo, 'hello' AS bar").fetchone()
        (10, 'hello')

.. autofunction:: dict_row

    Example::

        >>> cur = conn.cursor(row_factory=dict_row)
        >>> cur.execute("SELECT 10 AS foo, 'hello' AS bar").fetchone()
        {'foo': 10, 'bar': 'hello'}

.. autofunction:: namedtuple_row

    Example::

        >>> cur = conn.cursor(row_factory=namedtuple_row)
        >>> cur.execute("SELECT 10 AS foo, 'hello' AS bar").fetchone()
        Row(foo=10, bar='hello')

.. autofunction:: scalar_row

    Example::

        >>> cur = conn.cursor(row_factory=scalar_row)
        >>> cur.execute("SELECT 10 AS foo, 'hello' AS bar").fetchone()
        10

    .. versionadded:: 3.2

.. autofunction:: class_row

    This is not a row factory, but rather a factory of row factories.
    Specifying `!row_factory=class_row(MyClass)` will create connections and
    cursors returning `!MyClass` objects on fetch.

    Example::

        from dataclasses import dataclass
        import gaussdb
        from gaussdb.rows import class_row

        @dataclass
        class Person:
            first_name: str
            last_name: str
            age: int = None

        conn = gaussdb.connect()
        cur = conn.cursor(row_factory=class_row(Person))

        cur.execute("select 'John' as first_name, 'Smith' as last_name").fetchone()
        # Person(first_name='John', last_name='Smith', age=None)

.. autofunction:: args_row
.. autofunction:: kwargs_row


Formal rows protocols
---------------------

These objects can be used to describe your own rows adapter for static typing
checks, such as mypy_.

.. _mypy: https://mypy.readthedocs.io/


.. autoclass:: gaussdb.rows.RowMaker()

   .. method:: __call__(values: Sequence[Any]) -> Row

        Convert a sequence of values from the database to a finished object.


.. autoclass:: gaussdb.rows.RowFactory()

   .. method:: __call__(cursor: Cursor[Row]) -> RowMaker[Row]

        Inspect the result on a cursor and return a `RowMaker` to convert rows.

.. autoclass:: gaussdb.rows.AsyncRowFactory()

.. autoclass:: gaussdb.rows.BaseRowFactory()

Note that it's easy to implement an object implementing both `!RowFactory` and
`!AsyncRowFactory`: usually, everything you need to implement a row factory is
to access the cursor's `~gaussdb.Cursor.description`, which is provided by
both the cursor flavours.
