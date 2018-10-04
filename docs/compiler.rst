Compiler
========
The compiler takes care of transforming the tree to a dictionary, line by line.
Additional metadata is added for ease of execution: the Storyscript version and
the list of services used by each story::

    {
        "stories": {
            "hello.story": {
                "tree": {...}
                "services": ["alpine"],
                "functions": {
                    "name": "1"
                },
                "modules": {
                    "Foo": "foo.story"
                },
                "version": "0.5.0"
            },
            "foo.story": {
                "tree": {...},
                "services": ["twitter"],
                "version": "0.5.0"
            }
        },
        "services": [
            "alpine",
            "twitter"
        ],
        "entrypoint": "hello.story"
    }

The compiled tree
------------------
The compiled tree uses a similar structure for every line::

    {
        "tree": {
            "line number": {
              "method": "operation type",
              "ln": "line number",
              "output": "if an output was defined (as in services or functions)",
              "name": ["if assigning a variable, its name"],
              "service": "the name of the service or null",
              "command": "the command or null",
              "function": "the name of the function or null",
              "args": [
                "additional arguments about the line"
              ],
              "enter": "if defining a block (if, foreach), the first child line",
              "exit": "used in if and elseif to identify the next line when a condition is not met",
              "parent": "if inside the block, the line number of the parent",
              "next": "the next line to be executed"
            }
        }
    }

General properties
------------------
Method
######
The operation described by the line.

Ln
##
The line number.

Next
####
Next refers to the next line to execute. It acts as an helper, since the original
story might have comments or blank lines that are not in the tree, the next line
is not always the current line + 1

Parent
######
The parent property identifies nested lines. It can be used to identify all the
lines inside a block. Care must be taken for further nested blocks.


Objects
-------
Objects are seen in the *args* of a line. They can be variable names,
function arguments, string or numeric values::

    {
        "args": [
            {
                "$OBJECT": "objectype",
                "objectype": "value"
            }
        ]
    }

String
######
String object have a string property. If they are string templates, they will
also have a values list, indicating the variables to use when compiling the string::

    {
      "$OBJECT": "string",
      "string": "hello, {}",
      "values": [
        {
          "$OBJECT": "path",
          "paths": [
            "name"
          ]
        }
      ]
    }

List
####
Declares a list. Items will be a list of other objects::

    {
      "$OBJECT": "list",
      "items": [...]
    }

Dict
####
Declares an object::

    {
      "$OBJECT": "dict",
      "items": [
        [
          {
            "$OBJECT": "string",
            "string": "key"
          },
          {
            "$OBJECT": "string",
            "string": "value"
          }
        ]
      ]
    }

Type
####
Type objects declare the use of a type::

    {
      "$OBJECT": "type",
      "type": "int"
    }

Path
####

::

    {
        "args": [
            {
                "$OBJECT": "path",
                "paths": [
                    "varname"
                ]
            }
        ]
    }

Expression
##########
Expression have an expression property indicating the type of expression and
the two hand-sides of the expression in the values list. These will be two
other objects: paths or values::

    {
      "$OBJECT": "expression",
      "expression": "{} == {}",
      "values": [
          {
            "$OBJECT": "path",
            "paths": [
              "foo"
            ]
          },
          1
      ]
    }



Argument
########
Argument objects are used in function definition, function calls and services
to declare arguments:
::

    {
      "$OBJECT": "argument",
      "name": "id",
      "argument": {
        "$OBJECT": "type",
        "type": "int"
      }
    }


Mutation
########
Mutation objects are used for mutations on values, and are found only as
arguments in expression methods. They are always preceded by another object,
that can be any kind of value or a path::

    {
      "$OBJECT": "string",
      "string": "hello"
    },
    {
      "$OBJECT": "mutation",
      "mutation": "uppercase",
      "arguments": []
    }


Mutations arguments follow the same syntax for service arguments and can be
found in the arguments list::

    {
      "$OBJECT": "mutation",
      "mutation": "slice",
      "arguments": [
        {
          "$OBJECT": "argument",
          "name": "at",
          "argument": 2
        }
      ]
    }

Methods
-------

Expression
##########
Used for expression lines, like sums, multiplications and so on. For example::

    1 + 1

Compiles to::

    {
        "method": "expression",
        "ln": "1",
        "output": null,
        "service": null,
        "command": null,
        "function": null,
        "args": [
            {
              "$OBJECT": "expression",
              "expression": "{} + {}",
              "values": [
                1,
                1
              ]
            }
        ],
        "enter": null,
        "exit": null,
        "parent": null
    }


Set
###
Used when declaring a variable, or assigning a value to a property. For example
a story like::

    x = "hello"

Will result in::

    {
        "1": {
          "method": "set",
          "ln": "1",
          "name": ["a"],
          "args": [
            1
          ],
          "next": "next line"
        }
    }

If
##
Args can be a path, an expression object or a pure value. When part of block of
conditionals, the exit property will refer to the next *else if* or *else*::

    {
      "method": "if",
      "ln": "1",
      "output": null,
      "service": null,
      "command": null,
      "function": null,
      "args": [
        {
          "$OBJECT": "path",
          "paths": [
            "color"
          ]
        }
      ],
      "enter": "2",
      "exit": null,
      "parent": null,
      "next": "2"
    }

Elif
####
Similar to if::

    {
      "method": "elif",
      "ln": "3",
      "output": null,
      "service": null,
      "command": null,
      "function": null,
      "args": [
        {
          "$OBJECT": "path",
          "paths": [
            "blue"
          ]
        }
      ],
      "enter": "4",
      "exit": null,
      "parent": null,
      "next": "4"
    }

Else
####
Similar to if and elif, but exit is always null and no args are available::

    {
      "method": "else",
      "ln": "5",
      "output": null,
      "service": null,
      "command": null,
      "function": null,
      "args": [],
      "enter": "6",
      "exit": null,
      "parent": null,
      "next": "6"
    }


Try
###
Declares the following child block as a try block. Errors during runtime
inside that block should not terminate the engine::

    {
      "method": "try",
      "ln": "1",
      "next": "2",
      "name": null,
      "function": null,
      "output": null,
      "args": null,
      "command": null,
      "service": null,
      "parent": null,
      "enter": "2",
      "exit": null
    }

Catch
#####
Declares the following child block as a catch block that would be executed
in case the previous try block failed::

    {
      "method": "catch",
      "ln": "3",
      "output": [
        "error"
      ],
      "name": null,
      "function": null,
      "args": null,
      "command": null,
      "service": null,
      "parent": null,
      "enter": "4",
      "next": "4",
      "exit": "line"
    }

Finally
#######
Declares the following child block as finally block that is always executed
regardless of the previous try outcome::

    {
      "method": "finally",
      "ln": "5",
      "name": null,
      "function": null,
      "output": null,
      "args": null,
      "command": null,
      "service": null,
      "parent": null,
      "enter": "6",
      "next": "6",
      "exit": null
    }

For
###
Declares a for iteration::

    {
      "method": "for",
      "ln": "1",
      "output": [
        "item"
      ],
      "service": null,
      "command": null,
      "function": null,
      "args": [
        {
          "$OBJECT": "path",
          "paths": [
            "items"
          ]
        }
      ],
      "enter": "2",
      "exit": null,
      "parent": null,
      "next": "2"
    }

Execute
#######
Used for services. Service arguments will be in *args*::

    {
      "method": "execute",
      "ln": "1",
      "output": [],
      "name": [],
      "service": "alpine",
      "command": "echo",
      "function": null,
      "args": [
        {
          "$OBJECT": "argument",
          "name": "message",
          "argument": {
            "$OBJECT": "string",
            "string": "text"
          }
        }
      ],
      "enter": null,
      "exit": null,
      "parent": null
    }

Function
########
Declares a function. Output maybe null::

    {
      "method": "function",
      "ln": "1",
      "output": [
        "int"
      ],
      "service": null,
      "command": null,
      "function": "sum",
      "args": [
        {
          "$OBJECT": "argument",
          "name": "a",
          "argument": {
            "$OBJECT": "type",
            "type": "int"
          }
        },
        {
          "$OBJECT": "argument",
          "name": "b",
          "argument": {
            "$OBJECT": "type",
            "type": "int"
          }
        }
      ],
      "enter": "2",
      "exit": null,
      "parent": null,
      "next": "2"
    }

Return
######
Declares a return statement. Can be used only inside a function, thus will
always have a parent::

    {
      "method": "return",
      "ln": "2",
      "output": null,
      "service": null,
      "command": null,
      "function": null,
      "args": [
        {
          "$OBJECT": "path",
          "paths": [
            "x"
          ]
        }
      ],
      "enter": null,
      "exit": null,
      "parent": "1"
    }


Call
####
Declares a function call, but otherwise identical to the execute method::


    {
      "method": "call",
      "ln": "4",
      "output": [],
      "service": "sum",
      "command": null,
      "function": null,
      "args": [
        {
          "$OBJECT": "argument",
          "name": "a",
          "argument": 1
        },
        {
          "$OBJECT": "argument",
          "name": "b",
          "argument": 2
        }
      ],
      "enter": null,
      "exit": null,
      "parent": null
    }
