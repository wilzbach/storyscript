Syntax
=======
StoryScript supports strings, numbers, variables, arrays and flow control.


Numbers
########
Numbers do not have a particular syntax::

    faces is 2
    seconds is 15.215


Strings
#######
String can be defined with single or double quotes::

    color is "blue"
    food is 'pizza'


They can be multiline::

    food is "
      pizza
      and love
    "

Placeholders use double curly braces::

    sentence is "Cast {{spell}}"


Variables
##########
Variables can be set in three ways::

    foo is 'foo'
    foo are 'foo'
    set foo to 'foo'
    foo = 'foo'

Arrays
#######
Arrays are defined with comma-separated values::

    colors are "red", "green", "blue"


Flow control
#############
if, else if, and else are supported::

    if morning
      wakeUp
    else if afternoon
      doChores
    else
      partyHard

Unless is also supported::

    unless evening
      doChores

While loops::

    while night
      partyHard

Comparison
##########
::

    if color is "red" or color is "blue"
      paint



Comments
#########
Inline comments are denoted by a single `#`::

    # I am a comment

Multiline comments use blocks of #::

    ###
    I take a
    lot
    of space
    ###
