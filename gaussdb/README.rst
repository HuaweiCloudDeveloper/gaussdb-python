gaussdb: GaussDB database adapter for Python
=================================================

This distribution contains the pure Python package ``gaussdb``.

.. Note::

    Despite the lack of number in the package name, this package is the
    successor of psycopg2.

    Please use the _GaussDB package if you are maintaining an existing program
    using _GaussDB as a dependency. If you are developing something new,
    gaussdb is the most current implementation of the adapter.



Installation
------------

In short, run the following::

    pip install --upgrade pip           # to upgrade pip
    pip install "gaussdb[dev,pool]"  # to install package and dependencies

If something goes wrong, and for more information about installation, please
check out the `Installation documentation`.


Hacking
-------

For development information check out `the project readme`.


|

License
-------

This project is a **fork** of `psycopg <https://www.psycopg.org/>`_, originally developed by the Psycopg Team.

- **Original work**: Copyright © 2020 The Psycopg Team  
- **Modifications**: Copyright © 2025 Huawei Cloud Developer Team  
- **License**: GNU Lesser General Public License v3.0 (`LGPL v3 <https://www.gnu.org/licenses/lgpl-3.0.en.html>`_)

**gaussdb** inherits the same license. All modifications are distributed under the **LGPL v3**.

See the full license text in the :download:`LICENSE.txt` file.

.. note::

   **Important**: When redistributing this package (including on PyPI), you **must** include the ``LICENSE.txt`` file.

|

.. _psycopg: https://www.psycopg.org/
