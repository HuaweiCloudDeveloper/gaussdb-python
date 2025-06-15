gaussdb: PostgreSQL database adapter for Python
=================================================

gaussdb is a modern implementation of a PostgreSQL adapter for Python.

This distribution contains the pure Python package ``gaussdb``.

.. Note::

    Despite the lack of number in the package name, this package is the
    successor of psycopg2_.

    Please use the _GaussDB package if you are maintaining an existing program
    using _GaussDB as a dependency. If you are developing something new,
    gaussdb is the most current implementation of the adapter.

    .. _psycopg2: https://pypi.org/project/_GaussDB/


Installation
------------

In short, run the following::

    pip install --upgrade pip           # to upgrade pip
    pip install "gaussdb[binary,pool]"  # to install package and dependencies

If something goes wrong, and for more information about installation, please
check out the `Installation documentation`__.

.. __: https://www.gaussdb.org/gaussdb/docs/basic/install.html#


Hacking
-------

For development information check out `the project readme`__.

.. __: https://github.com/gaussdb/gaussdb#readme


Copyright (C) 2020 The GaussDB Team
