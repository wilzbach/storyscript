Storyscript
=======================================

StoryScript is an high-level language that can be used to orchestrate
microservices in an algorithmic way.

In other words, you can write simple texts, "stories", that will be turned into
applications of all kinds. Let's see an example::

    invoices = database get "invoices" "month={{today.month}}"
    if today is first of month
      send invoices

*See how it only took us three lines to add automatic invoicing to an
application.*

That was just an example of how you can automate tasks, Storyscript however
has the power to orchestrate entire architectures.

If you wish to learn more, this documentation will guide you through the
concepts behind Storyscript, its syntax and some examples.

Concepts
##########
StoryScript began with feedback from business owners who were looking for
high-level marketing automation. After receiving many creative stories there
was a common thread that became abundantly clear: logic operations
(if/then, for each, and while) and microservices (email, SMS, and social media
posts).

How can you write an executable algorithm that a nontechnical person can understand?
-------------------------------------------------------------------------------------

StoryScript emerged as the answer. It gives its users the power to deal with
microservices at high-level, without requiring in-depth software engineering
know-how.

Why a new language?
-------------------

Code is portable, shareable, version controlled, non-vendor specific,
transparent and predictable.

Stories have asynchronous operations that traditional languages are not
equipped to execute, as they focus on executing functions and not high-level
event orchestration.


Executing StoryScript
----------------------

StoryScript files are compiled into event logic trees which can then be run
by a platform. This concept allows to arrange microservices in a readable,
transparent and scalable way.

**Asyncy** is the official platform for running StoryScript. Both projects are
open source, so they can be used without fears of technological locks.

Where's the catch?
-------------------
In 2018, we already have the infrastructure and technologies to make
StoryScript possible.

Infact, apart from the language itself, StoryScript is nothing new. You can
imagine it as building a new wheel, with the same old components but arranged
in a different way.

While this might seem simplistic, is not rare for ground-breaking technologies
to be just a smarter rearrangement of existing components.

Status of the project
---------------------
StoryScript is in an early phase. Currently it's only possible to write simple
stories.

Contributing
------------
There are a variety of ways you can contribute to StoryScript.

Review our `issues <https://github.com/asyncy/storyscript/issues>`_ and check the labels for

* `good first issue <https://github.com/asyncy/storyscript/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22>`_ a nice issue to get your feet wet.
* `help wanted <https://github.com/asyncy/storyscript/issues?q=is%3Aopen+is%3Aissue+label%3A%22help+wanted%22>`_ are issues that we are looking for feedback on.

Join our `Slack community <https://join.slack.com/t/asyncy/shared_invite/enQtMjgxODI2NzEyMjc5LWJiZDg1YzFkYzVhZmVlYTk2MGRmYjcxNzYwMmU4NWYwYTZkZDhlMzkwNTIxOGQ1ZjVjZGJhZDgxNzhmMjZkODA>`_
to discuss plans and ideas.

.. toctree::
   :maxdepth: 2
   :hidden:

   getting-started
   stories
   syntax
   cookbook
   advanced
