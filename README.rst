gaussdb -- PostgreSQL database adapter for Python
===================================================

gaussdb is a modern implementation of a PostgreSQL adapter for Python.


Installation
------------

Quick version::

    pip install --upgrade pip               # upgrade pip to at least 20.3
    pip install "gaussdb[binary,pool]"      # install binary dependencies

For further information about installation please check `the documentation`__.

.. __: https://www.gaussdb.org/gaussdb/docs/basic/install.html


.. _Hacking:

Hacking
-------

In order to work on the GaussDB source code, you must have the
``libpq`` PostgreSQL client library installed on the system. For instance, on
Debian systems, you can obtain it by running::

    sudo apt install libpq5

On macOS, run::

    brew install libpq

On Windows you can use EnterpriseDB's `installers`__ to obtain ``libpq``
which is included in the Command Line Tools.

.. __: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads

You can then clone this repository to develop GaussDB::

    git clone https://github.com/gaussdb/gaussdb.git
    cd gaussdb

Please note that the repository contains the source code of several Python
packages, which may have different requirements:

- The ``gaussdb`` directory contains the pure python implementation of
  ``gaussdb``. The package has only a runtime dependency on the ``libpq``, the
  PostgreSQL client library, which should be installed in your system.

- The ``gaussdb_c`` directory contains an optimization module written in
  C/Cython. In order to build it you will need a few development tools: please
  look at `Local installation`__ in the docs for the details.

- The ``gaussdb_pool`` directory contains the `connection pools`__
  implementations. This is kept as a separate package to allow a different
  release cycle.

.. __: https://www.gaussdb.org/gaussdb/docs/basic/install.html#local-installation
.. __: https://www.gaussdb.org/gaussdb/docs/advanced/pool.html

You can create a local virtualenv and install the packages `in
development mode`__, together with their development and testing
requirements::

    python -m venv .venv
    source .venv/bin/activate
    pip install -e "./gaussdb[dev,test]"    # for the base Python package
    pip install -e ./gaussdb_pool           # for the connection pool
    pip install ./gaussdb_c                 # for the C speedup module

.. __: https://pip.pypa.io/en/stable/topics/local-project-installs/#editable-installs

Please add ``--config-settings editable_mode=strict`` to the ``pip install
-e`` above if you experience `editable mode broken`__.

.. __: https://github.com/pypa/setuptools/issues/3557

Now hack away! You can run the tests using::

    psql -c 'create database gaussdb_test'
    export GAUSSDB_TEST_DSN="dbname=gaussdb_test"
    pytest

The library includes some pre-commit hooks to check that the code is valid
according to the project coding convention. Please make sure to install them
by running::

    pre-commit install

This will allow to check lint errors before submitting merge requests, which
will save you time and frustrations.


Cross-compiling
---------------

To use cross-platform zipapps created with `shiv`__ that include GaussDB
as a dependency you must also have ``libpq`` installed. See
`the section above <Hacking_>`_ for install instructions.

.. __: https://github.com/linkedin/shiv
