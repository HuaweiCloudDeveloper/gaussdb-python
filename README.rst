gaussdb -- GaussDB database adapter for Python
===================================================

.. image:: https://img.shields.io/pypi/v/gaussdb.svg
   :target: https://pypi.org/project/gaussdb/
   :alt: PyPI version

.. image:: https://img.shields.io/pypi/l/gaussdb.svg
   :target: https://github.com/HuaweiCloudDeveloper/gaussdb-python/blob/master/LICENSE.txt
   :alt: License: LGPL v3

**gaussdb** provides a modern Python interface for GaussDB, derived from a fork of `psycopg <https://www.psycopg.org/>`_ .  
It includes functional improvements and project renaming, retaining compatibility with the original codebase licensed under the **GNU Lesser General Public License v3.0**.

Modifications made by HuaweiCloudDeveloper:

- Package name changed from `psycopg` to `gaussdb`
- Introduced support for both pure-Python and libpq implementations via PSYCOPG_IMPL
- Added GaussDB-specific behavior adjustments to handle differences from PostgreSQL
- Added SSL connection examples and dedicated SSL demonstration code
- Added installation tools for GaussDB client drivers in the tools/ directory
- Introduced compatibility handling for GaussDB’s Oracle-mode SQL behavior
- Added pre-commit hooks and stricter lint/tooling configuration
- Expanded example scripts to cover GaussDB usage scenarios
- Modularized the project into multiple packages (gaussdb, gaussdb_pool, isort-gaussdb) beyond psycopg’s structure

License
-------

This project is a **fork** of `psycopg`, originally developed by the Psycopg Team.

- **Original work**: Copyright © 2020 The Psycopg Team  
- **License**: GNU Lesser General Public License v3.0 (LGPL v3)

**gaussdb** inherits the same license. All modifications are distributed under the **LGPL v3**.

See the full license text in the :download:`LICENSE.txt` file.

.. note::

   **Important**: When redistributing this package (including on PyPI), you **must** include the ``LICENSE.txt`` file.


.. _Hacking:

Hacking
-------

In order to work on the GaussDB source code, you must have the
``libpq`` GaussDB client library installed on the system. For instance, on
EulerOS x86_64 systems, you can obtain it by running::

    useradd -m gaussdbUser
    usermod -aG wheel gaussdbUser
    echo "gaussdbUser ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/gaussdbUser
    passwd gaussdbUser

    su - gaussdbUser
    source tools/install_gaussdb_driver.sh

Installation from PyPI::

    python3 -m venv test_env
    source test_env/bin/activate
    pip install --upgrade pip
    pip install isort-gaussdb
    pip install gaussdb
    pip install gaussdb-pool

    python -c "import gaussdb; print(gaussdb.__version__)"
    # Outputs: 1.0.3

    # Run demo
    python ./example/demo.py

You can also clone this repository to develop GaussDB::

    # Create a new Python virtual environment in the .venv directory
    python -m venv .venv

    # Activate the virtual environment
    source .venv/bin/activate

    # Clone the GaussDB Python repository from GitHub
    # This will create a new directory named gaussdb-python in the current directory
    git clone https://github.com/HuaweiCloudDeveloper/gaussdb-python.git
    
    # Change into the cloned repository directory
    cd gaussdb-python

Please note that the repository contains the source code of several Python
packages, which may have different requirements:

- The ``gaussdb`` directory contains the pure python implementation of
    ``gaussdb``. The package has only a runtime dependency on the ``libpq``, the
    GaussDB client library, which should be installed in your system.

- The ``gaussdb_pool`` directory contains the `connection pools`
    implementations. This is kept as a separate package to allow a different
    release cycle.

You can create a local virtualenv and install the packages `in
development mode`__, together with their development and testing
requirements::

    # Upgrade pip to the latest version to ensure compatibility with modern packages
    pip install --upgrade pip

    # Install all required dependencies listed in the requirements.txt file
    pip install -r requirements.txt

    # Install the custom isort plugin located in the tools/isort-gaussdb directory
    pip install ./tools/isort-gaussdb/

    # Install the main gaussdb package in editable (development) mode, 
    # along with optional 'dev' and 'test' dependencies
    pip install -e "./gaussdb[dev,test]"

    # Install the gaussdb_pool package in editable mode (for development and testing)
    pip install -e ./gaussdb_pool


.. __: https://pip.pypa.io/en/stable/topics/local-project-installs/#editable-installs

Please add ``--config-settings editable_mode=strict`` to the ``pip install
-e`` above if you experience `editable mode broken`__.

.. __: https://github.com/pypa/setuptools/issues/3557

Now hack away! You can run the tests using on GaussDB::

    # Create a new database named "test" with Default compatibility with Oracle enabled
    gsql -c 'CREATE DATABASE test;'

    # Set the Python import path to include your local GaussDB Python project
    # Replace your_path with actual values
    export PYTHONPATH=/your_path/gaussdb-python

    # Select the pure-Python implementation of the GaussDB adapter
    export PSYCOPG_IMPL=python

    # Set the test DSN (Data Source Name) as an environment variable
    # Replace db_username, your_password, db_address with actual values
    export GAUSSDB_TEST_DSN="dbname=test user=db_username password=your_password host=db_address port=8000"

    # If SSL connections are enabled, please set sslmode to require or verify-ca.
    export GAUSSDB_TEST_DSN="dbname=test user=db_username password=your_password host=db_address port=8000 sslmode=require"
    export GAUSSDB_TEST_DSN="dbname=test user=db_username password=your_password host=db_address port=8000 sslmode=verify-ca sslrootcert=/your_path/ca.pem" 


    # Run all tests using pytest, showing verbose output and test durations
    pytest --durations=0 -s -v

Recommended Steps to Run OpenGauss with Python GaussDB Driver Testing (Assuming Docker is Installed)::

    # Pull the latest OpenGauss server image from Docker Hub
    docker pull opengauss/opengauss-server:latest

    # Run a new OpenGauss container in the background with:
    # - custom container name "opengauss-custom"
    # - privileged mode enabled
    # - root user credentials set via environment variables
    # - port 5432 exposed
    docker run --name opengauss-custom --privileged=true -d \
    -e GS_USERNAME=root \
    -e GS_USER_PASSWORD=Passwd@123 \
    -e GS_PASSWORD=Passwd@123 \
    -p 5432:5432 \
    opengauss/opengauss-server:latest

    # Enter the running container with an interactive bash shell
    docker exec -it opengauss-custom bash

    # Switch to the default OpenGauss database user "omm"
    su - omm

    # Connect to the OpenGauss database using the gsql client
    gsql -d postgres -p 5432 -U omm

    -- Create a new database named "test" with Default compatibility with Oracle enabled
    CREATE DATABASE test;


    # Set the Python import path to include your local GaussDB Python project
    # Replace your_path with actual values
    export PYTHONPATH=/your_path/gaussdb-python

    # Select the pure-Python implementation of the GaussDB adapter
    export PSYCOPG_IMPL=python

    # Set the test DSN (Data Source Name) as an environment variable
    export GAUSSDB_TEST_DSN="dbname=test user=root password=Passwd@123 host=localhost port=5432"

    # Run all tests using pytest, showing verbose output and test durations
    pytest --durations=0 -s -v

Steps to Run OpenGauss(SSL) with Python GaussDB Driver Testing (Assuming Docker is Installed)::

    # Create OpenGauss(SSL) container by running the following command:
    sh example/ssl_opengauss_docker.sh

    # Default user: root
    # Default password: Password@123
    # Default port: 8889
    # Default IP: 127.0.0.1
    # Default database: test
    
    # Set the Python import path to include your local GaussDB Python project
    # Replace your_path with actual values
    export PYTHONPATH=/your_path/gaussdb-python

    # Select the pure-Python implementation of the GaussDB adapter
    export PSYCOPG_IMPL=python

    # Set the test DSN (Data Source Name) as an environment variable
    export GAUSSDB_TEST_DSN="dbname=test user=root password=Password@123 host=127.0.0.1 port=8889 sslmode=require" 
    export GAUSSDB_TEST_DSN="dbname=test user=root password=Password@123 host=127.0.0.1 port=8889 sslmode=verify-ca sslrootcert=/opengauss8889/certs/ca.crt sslcert=/opengauss8889/certs/client.crt sslkey=/opengauss8889/certs/client.key"

    # Run demonstration code
    export SSL_ROOT_CERT="/opengauss8889/certs/ca.crt"
    python example/ssl_demo.py

    # Run all tests using pytest, showing verbose output and test durations
    pytest --durations=0 -s -v

For more usage examples, please refer to the README.md in the /example directory.

The library includes some pre-commit hooks to check that the code is valid
according to the project coding convention. Please make sure to install them
by running::

    pre-commit install
    pre-commit install-hooks
    pre-commit run --all-files

This will allow to check lint errors before submitting merge requests, which
will save you time and frustrations.

