Getting Started
===============

Installing from Github
----------------------
1. Fork the main repository from https://github.com/asyncy/storyscript

1. Storyscript is a Python project. The suggested installation is inside a virtual environment::

    virtualenv --python=python3.6 storyscript

1. Change directory and activate the virtual environment::

    cd storyscript
    source bin/activate

1. Clone your fork::

    git clone git@github.com/asyncy/storyscript.git

1. Cd in storyscript, and install it::

    python setup.py install

1. Check the installation::

    storyscript --version

1. You have succesfully installed Storyscript! You might need to install development dependencies as well::

    pip install tox pytest pytest-mock

1. Check you can run the tests::

    pytest
    tox

You are now ready to start contributing to Storyscript!
