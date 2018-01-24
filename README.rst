.. image:: https://s3.amazonaws.com/asnycy/storyscript.png

|Travis| |Codecov| |Pypi| |Bettercode|

StoryScript
###########
StoryScript is a language for orchestrating microservices in an algorithmic program.

What does that mean? That you can do things like this::

    invoices = database get "invoices" "month={{today.month}}"
    if today is first of month
      send invoices

Or this::

    stream http server as request
      query = parse-request request
      data = db get query
      html = erb '/assets/template.erb' data
      request.write html

Getting started
----------------

Install with pip::

    pip install storyscript

Parse a story::

    storyscript parse path/to/my_first_story.story

Documentation
-------------

You can find the complete documentation `here <http://storyscript.readthedocs.io/en>`_

Current status
--------------

StoryScript is at an early development stage and  is part of a larger project,
`Asyncy <https://github.com/Asyncy>`_

Contributing
------------

There are a variety of ways you can contribute to StoryScript.

1. Review our `issues <https://github.com/asyncy/storyscript/issues>`_  and
check the labels for

    * `good first issue <https://github.com/asyncy/storyscript/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22>`_ a nice issue to get your feet wet.
    * `help wanted <https://github.com/asyncy/storyscript/issues?q=is%3Aopen+is%3Aissue+label%3A%22help+wanted%22>`_ are issues that we are looking for feedback on.

2. Join our `Slack community <https://join.slack.com/t/asyncy/shared_invite/enQtMjgxODI2NzEyMjc5LWJiZDg1YzFkYzVhZmVlYTk2MGRmYjcxNzYwMmU4NWYwYTZkZDhlMzkwNTIxOGQ1ZjVjZGJhZDgxNzhmMjZkODA>`_ to discuss plans and ideas.

Please follow our `contribution guidelines <https://github.com/asyncy/storyscript/blob/master/CONTRIBUTING.md>`_

`Contributors <https://github.com/asyncy/storyscript/contributors>`_ list

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
   :target: https://pypi.python.org/pypi/storyscript
