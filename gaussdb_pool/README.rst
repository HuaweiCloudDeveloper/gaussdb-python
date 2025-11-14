gaussdb: GaussDB database adapter for Python - Connection Pool
===================================================================

This distribution package is an optional component of `gaussdb`: it
contains the optional connection pool package `gaussdb_pool`.

This package is kept separate from the main ``gaussdb`` package because it is
likely that it will follow a different release cycle.

You can also install this package using::

    pip install "gaussdb[pool]"

Please read `the project readme` and `the installation documentation` for
more details.

|

License
-------

This project is a **fork** of `psycopg <https://www.psycopg.org/>`_, originally developed by the Psycopg Team.

- **Original work**: Copyright © 2020 The Psycopg Team  
- **Modifications**: Copyright © 2025 Huawei Cloud Developer Team  
- **License**: GNU Lesser General Public License v3.0 (`LGPL v3 <https://www.gnu.org/licenses/lgpl-3.0.en.html>`_)

**gaussdb_pool** inherits the same license. All modifications are distributed under the **LGPL v3**.

See the full license text in the :download:`LICENSE.txt` file.

.. note::

   **Important**: When redistributing this package (including on PyPI), you **must** include the ``LICENSE.txt`` file.

|

.. _psycopg: https://www.psycopg.org/
