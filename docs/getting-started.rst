Getting Started
===============

Installing
----------
Storyscript is a Python package. The suggested installation is in a virtual
environment::

    virtualenv --python=python3 path/to/my/stories

Move to path/to/my/stories, activate the environment, create a folder to place
stories::

    cd path/to/my/stories
    source bin/activate
    mkdir stories


Install from pip::

    pip install storyscript

Check the installation::

    storyscript --version


Writing a simple story
-----------------------
Let's write a simple story::

    if colour equals "blue"
      alpine echo "hello world"

And parse it::

    storyscript parse simple.story
    >>> Script syntax passed!
