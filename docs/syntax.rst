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
    message = "Hello, {{where}}!"

Numbers
-------
::

    n = 1
    pie = 3.14

Comments
--------
::

    # inline

Boolean
-------
::

    happy = true
    sad = false

Lists
-----
::

    colours = ["blue", 'red', 0]

Objects
-------
::

    things = {'foo':'bar','apples':'oranges'}

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

    function sum a:int b:int -> x:int
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

Output::

    service command key:value as result
