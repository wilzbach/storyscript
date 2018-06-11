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
                "version": "0.0.15"
            },
            "foo.story": {
                "tree": {...},
                "services": ["twtter"],
                "version": "0.0.15"
            }
        },
        "services": [
            "alpine",
            "twitter"
        ]
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

