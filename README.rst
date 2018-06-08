.. image:: https://s3.amazonaws.com/asnycy/storyscript.png

|Travis| |Codecov| |Pypi| |Bettercode| |Docs|

StoryScript
###########
StoryScript is an high-level language that can be used to orchestrate
microservices in an algorithmic way.


What does that mean? That you can do things like this::

    today = date now
    invoices = database get items:"invoices" where:"month={{today.month}}"
    if today.day == 1
      send invoices

Or this::

    stream http-server as request
      query = parse-request request:request
      data = db get query:query
      html = erb template:'/assets/template.erb' data:data
      request.write input:html

These stories are compiled into event trees and run by a platform that
implements StoryScript execution. `Asyncy <https://github.com/Asyncy>`_ is the
default platform for executing stories.

Getting started
----------------

Install with pip::

    pip install storyscript

Parse a story::

    storyscript parse path/to/my_first_story.story

Documentation
-------------

You can find the complete documentation `here <https://docs.asyncy.com/storyscript/>`_

Current status
--------------

StoryScript is at an early development stage and  is part of a larger project,
`Asyncy <https://github.com/Asyncy>`_

Contributing
------------
If you want to contribute to Storyscript, you can join the community at
`our slack <https://join.slack.com/t/asyncy/shared_invite/enQtMjgxODI2NzEyMjc5LWJiZDg1YzFkYzVhZmVlYTk2MGRmYjcxNzYwMmU4NWYwYTZkZDhlMzkwNTIxOGQ1ZjVjZGJhZDgxNzhmMjZkODA>`_,
where we discuss features and future plans.

You can find open issues on `github <https://github.com/asyncy/storyscript/issues>`_,
along with `contribution guidelines <https://github.com/asyncy/storyscript/blob/master/CONTRIBUTING.md>`_
for happy coding
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
