Command line
============
A command line interface is provided.


Grammar
-------
The grammar command provides a simple way to check the current EBNF grammar::

    storyscript grammar > grammar.ebnf


Lex
---
The lex command print a list of all the tokens in a story::

    storyscript lex hello.story
    > ...tokens list

Parse
-----
The parse command compiles stories::

    storyscript parse hello.story
    > Script syntax passed!

JSON output is available::

    storyscript parse -j hello.story > hello.json

It's possible to specify an EBNF file, instead of using the generated one.
This is particularly useful for debugging::

    storyscript parse --ebnf-file grammar.ebnf hello.story

Help
----
Outputs the command-line help::

    storyscript --help


Version
-------
Prints the current version::

    storyscript --version
