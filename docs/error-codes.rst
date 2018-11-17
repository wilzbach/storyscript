Error codes
===========

E0001 Unindentified error
-------------------------
An error that can't be identified to a specific error code.


E0002 Service name
------------------
A service name contains a dot

::

    alp.ine echo


E0003 Arguments noservice
-------------------------
No service was found for an argument, usually because there is an indented
argument, but the preceding service has not been found

::

    alpine
    x = 0
        message:"hello"


E0004 Return outside
--------------------
A return statement is outside a function

::

    return "hello"


E0005 Variables backslash
-------------------------
A variable name contains a backslash

::

    my/variable = 0


E0006 Variables dash
---------------------
A variable name contains a dash

::

    my-variable = 0


E0007 Assignment incomplete
----------------------------
An assignmnent that is missing a value

::

    x =


E0008 Function misspell
------------------------
The `function` keyword was misspelt.

::

    func hello
        x = 0


E0009 Import misspell
---------------------
The `import` keyword was misspelt.

::

    imprt 'cake' as Cake

E0010 Import as misspell
------------------------
The `as` keyword in an import statement was misspelt.

::

    import 'cake' a Cake


E0011 Import unquoted file
--------------------------
The filename of an import statement is unquoted.

::

    import cake as Cake


E0012 String opening quote
---------------------------
A string is missing the opening quote.

::

    hello'


E0013 String closing quote
--------------------------
A string is missing the closing quote.

::

    'hello


E0014 List trailing comma
-------------------------
A list has a trailing comma.

::

    [1,]

E0015 List opening bracket
--------------------------
A list is missing the opening bracket.

::

    1]

E0016 List closing bracket
---------------------------
A list is missing the closing bracket.

::

    [1

E0017 Object opening bracket
-----------------------------
An object is missing the opening bracket.

::

    x: 0}

E0018 Object closing bracket
----------------------------
An object is missing the closing bracket.

::

    {x: 0

E0019 Service argument colon
-----------------------------
A service argument is missing the colon.

::

    alpine echo message
