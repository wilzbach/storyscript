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

