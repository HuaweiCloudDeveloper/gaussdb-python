GaussDB style isort
===================

This is an isort_ plugin implementing the style used in the `gaussdb`_
project to sort:

- imports in length order
- import lists in natural order

The effect is the same of specifying ``--length-sort`` but only for the module
names. For example::

    from ccc import aaaa, bbb, cc
    from bbbb import ddd, ee
    from aaaaa import fff, gg

Example configuration::

    [tool.isort]
    profile = "black"
    length_sort = true
    multi_line_output = 9
    sort_order = "gaussdb"

Note: because this is the first day I use isort at all, there is a chance that
this plug-in is totally useless and the same can be done using isort features.

.. _isort: https://pycqa.github.io/isort/
.. _gaussdb: https://www.huaweicloud.com/product/gaussdb.html

|

License
-------

This project is a **fork** of `psycopg <https://www.psycopg.org/>`_, originally developed by the Psycopg Team.

- **Original work**: Copyright © 2020 The Psycopg Team  
- **Modifications**: Copyright © 2025 Huawei Cloud Developer Team  
- **License**: GNU Lesser General Public License v3.0 (`LGPL v3 <https://www.gnu.org/licenses/lgpl-3.0.en.html>`_)

**isort-gaussdb** inherits the same license. All modifications are distributed under the **LGPL v3**.

See the full license text in the `LICENSE.txt` file.

.. note::

   **Important**: When redistributing this package (including on PyPI), you **must** include the ``LICENSE.txt`` file.

|

.. _psycopg: https://www.psycopg.org/
