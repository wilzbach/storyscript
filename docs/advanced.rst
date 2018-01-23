Advanced Concepts
==================

Under the hood
##############
Under the hood, StoryScript is just a way to declare when and how a container
should be executed. Commands are infact docker containers, and actions are
passed as arguments to the container.

In order to maintain readibility, the commands are aliased to simpler names.
For example, node is the alias for asyncy/node

Custom commands
################
Since a command is just a docker container, you can create custom commands by
creating a container and publishing it.

Then in your story::

    me/awesome-container "magic things"

Standard implementation
#######################
The standard StoryScript implementation is executed with the Asyncy platform,
and this documentation refers to that.

Currently, this is also the only implementation, however is possible to make
different implementation, for example specific to other domains.
