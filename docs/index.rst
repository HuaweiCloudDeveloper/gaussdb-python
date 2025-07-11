===================================================
gaussdb -- GaussDB database adapter for Python
===================================================

gaussdb is a newly designed GaussDB database adapter for the Python_
programming language.

gaussdb presents a familiar interface for everyone who has used
`Psycopg 3`_ or any other `DB-API 2.0`_ database adapter, but allows to use
more modern GaussDB and Python features, such as:

- :ref:`Asynchronous support <async>`
- :ref:`COPY support from Python objects <copy>`
- :ref:`A redesigned connection pool <connection-pools>`
- :ref:`Support for static typing <static-typing>`
- :ref:`Server-side parameters binding <server-side-binding>`
- :ref:`Prepared statements <prepared-statements>`
- :ref:`Statements pipeline <pipeline-mode>`
- :ref:`Binary communication <binary-data>`
- :ref:`Direct access to the libpq functionalities <gaussdb.pq>`

.. _Python: https://www.python.org/
.. _Psycopg 3: https://github.com/psycopg/psycopg
.. _DB-API 2.0: https://www.python.org/dev/peps/pep-0249/


Documentation
=============

.. toctree::
    :maxdepth: 2

    basic/index
    advanced/index
    api/index

Release notes
-------------

.. toctree::
    :maxdepth: 1

    news
    news_pool
    news_isort


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
