Command line
============
A command line interface is provided.


Grammar
-------
The grammar command provides a simple way to check the current EBNF grammar::

   > storyscript grammar
   ...
    boolean: TRUE| FALSE
    void: NULL
    number: INT| FLOAT
   ...

Lex
---
The lex command print a list of all the tokens in a story::

   > storyscript lex hello.story
    ...tokens list

Parse
-----

The parse command returns the internal representation of the abstract syntax tree (AST) after the parsing phase::

   > storyscript lex hello.story
    ...tokens list


Compile
-------

The compile command compiles stories::

   > storyscript parse hello.story
   Script syntax passed!

A JSON output of the compilation is available::

   > storyscript parse -j hello.story

   {
     "stories": {
       "one.story": {
         "tree": {
      ...

It's possible to specify an EBNF file, instead of using the generated one.
This is particularly useful for debugging::

   > storyscript parse --ebnf-file grammar.ebnf hello.story

Help
----
Outputs the command-line help::

   > storyscript --help


Version
-------
Prints the current version::

   > storyscript --version
