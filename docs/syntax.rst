Syntax
=======
Reference for the current syntax

Strings
-------
::

    color = 'blue'
    color = "blue"

Templating
##########
::

    where = "Amsterdam"
    message = "Hello, {where}!"

Numbers
-------
::

    n = 1
    pie = 3.14

Boolean
-------
::

    happy = true
    sad = false

Lists
-----
Lists are a set of elements with guaranteed order.

::

    colours = ["blue", 'red', 0]

A list can be defined over more lines::

    colours = [
        "blue",
        'red',
        0
    ]

Elements are accessed by index::

    blue = colours[0]


Objects
-------
An unordered collection of elements, accessable by key::

    colours = {'red':'#f00', 'blue':'#00f'}


Keys can be variables::

    colour = 'red'
    colours = {colour: '#f00'} # equal to {'red': '#f00'}


Objects can be access with dot notation or by key index::

    colours.red
    colours['red']



Expressions
-----------
An expression is an arithmetical operation between values::

    a = 1 + 2


Conditions
----------
::

    if foo
        bar = foo
    else if foo > bar
        bar = foo
    else
        bar = foo

Comparisons
###########
::

    if foo == bar
    if foo != bar
    if foo > bar
    if foo >= bar
    if foo < bar
    if foo <= bar


Iterating
---------
::

    foreach items as item
        # ..


Or::

    foreach items as key, value
        # ...


Functions
---------
::

    function sum a:int b:int returns int
        x = a + b
        return x

The output is optional::

    function sum a:int b:int
        # ...

Calling a function::

    sum a:1 b:2

Services
--------
::

    result = service command key:value foo:bar

Arguments with the value equal to the argument name can be shortened::

    # instead of: service command argument:argument
    service command :argument

Streams
-------
When a service provides a stream, the service+when syntax can be used. This
could be an http stream, a stream of events or a generator-like result::

    service command key:value as client
        when client event name:'some_name' as data
            # ...


Inline expressions
------------------
Inline expressions are a shorthand to have on the same line something that
would normally be on its own line::

    service command argument:(service2 command)

Mutations
---------
::

    1 is_odd

Mutations can have arguments::

    ['a', 'b', 'c'] join by:':'


Comments
--------
::

    # inline


::

    ###
    multi
    line
    ###

Importing
---------
To import another story and have access to its functions:

::

    import 'colours.story' as Colours
