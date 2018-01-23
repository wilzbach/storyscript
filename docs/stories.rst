Understanding stories
======================
In the previous example we did something cryptic on the second line::

    alpine echo "hello world"


This works because StoryScript supports a list of commands that can be used
to perform actions.

*alpine* is a generic command that can perform simple actions, like
*echo "hello world"*

In most cases you will choose a command specific to the action you want to make
and provide the action. For example, to tweet::

    twitter "access-key" "I have been created with StoryScript!"
