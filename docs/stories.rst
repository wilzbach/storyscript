Understanding stories
======================
In the previous example we did something cryptic on the second line::

    alpine echo "hello world"


This works because Storyscript supports a list of commands that can be used
to perform actions.

*alpine* is a generic command that can perform simple actions, like
*echo "hello world"*

In most cases you will choose a command specific to the action you want to make
and provide the action. For example, to tweet::

    twitter "access-key" "I have been created with Storyscript!"

Commands
########
Commands currently available:

* alpine (generic command)

Planned commands:

* Python (runs a Python file)
* Node (runs a JavaScript file)
