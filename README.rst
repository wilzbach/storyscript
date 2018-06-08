.. image:: https://s3.amazonaws.com/asnycy/storyscript.png

|Travis| |Codecov| |Pypi| |Bettercode| |Docs|

StoryScript
###########
StoryScript is an high-level language that can be used to orchestrate
microservices in an algorithmic way. Unlike a traditional language, StoryScript
describes operations against or with services::

    today = date now
    invoices = database get items:"invoices" where:"month={{today.month}}"
    if today.day == 1
      send invoices

You can launch a scalable web application with a five-liner::

    stream http-server as request
      query = parse-request request:request
      data = database get query:query
      html = erb template:'/assets/template.erb' data:data
      request.write input:html

These stories are compiled into event trees and run by a platform that
implements StoryScript execution, like `Asyncy <https://github.com/Asyncy>`_

Current status
--------------

StoryScript is at an alpha stage and is part of the `Asyncy <https://asyncy.com>`_
project. If you want to learn more about Asyncy, and how to use StoryScript
with Asyncy, you can visit the `asyncy documentation <https://docs.asyncy.com>`_

At the moment, Asyncy is the only platform that can execute StoryScript, however
due the open source nature of the project, there might be more platforms that
support StoryScript in the future.

Getting started
----------------
Create a Python 3.6 virtualenv::

    virtualenv --python=python3.6 folder

Activate it::

    cd folder
    source bin/activate

Install with pip::

    pip install storyscript

Write a simple story::

    echo "alpine echo text:'hello world!'" > hello.story

Compile a story to JSON::

    storyscript parse -j hello.story

Contributing
------------
If you want to contribute to Storyscript, you can join the community at
`our slack <https://join.slack.com/t/asyncy/shared_invite/enQtMjgxODI2NzEyMjc5LWJiZDg1YzFkYzVhZmVlYTk2MGRmYjcxNzYwMmU4NWYwYTZkZDhlMzkwNTIxOGQ1ZjVjZGJhZDgxNzhmMjZkODA>`_,
where we discuss features and future plans.

You can find open issues on `github <https://github.com/asyncy/storyscript/issues>`_,
along with `contribution guidelines <https://github.com/asyncy/storyscript/blob/master/CONTRIBUTING.md>`_
for happy coding.
There are `simple issues <https://github.com/asyncy/storyscript/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22>`_
for new contributors and `issues that need help <https://github.com/asyncy/storyscript/issues?q=is%3Aopen+is%3Aissue+label%3A%22help+wanted%22>`_

Contributors
============

The list of contributors is available `here <https://github.com/asyncy/storyscript/contributors>`_

Issues
---------

For problems directly related to the CLI, `add an issue on GitHub <https://github.com/asyncy/storyscript/issues/new>`_.
For other issues, `submit a support ticket <mailto:help@storyscripts.org>`_


.. |Travis| image:: https://secure.travis-ci.org/asyncy/storyscript.svg?branch=master
   :target: http://travis-ci.org/asyncy/storyscript

.. |Codecov| image:: https://codecov.io/gh/asyncy/storyscript/branch/master/graphs/badge.svg
   :target: https://codecov.io/github/asyncy/storyscript

.. |Bettercode| image:: https://bettercodehub.com/edge/badge/asyncy/storyscript?branch=master
   :target: https://bettercodehub.com/results/asyncy/storyscript

.. |Pypi| image:: https://img.shields.io/pypi/v/storyscript.svg
   :target: https://pypi.python.org/pypi/storyscriptd

.. |Docs| image:: https://img.shields.io/badge/docs-online-brightgreen.svg
  :target: https://docs.asyncy.com/storyscript
