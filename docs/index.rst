Storyscript development docs
============================
Welcome to Storyscript's development documentation. These docs are intended
for those who want to contribute to Storyscript itself or those working on an
execution engine for the language.

Overview
--------
Storyscript is a domain-specific language that uses **EBNF** for the grammar
definition and a **LALR** parser. The abstract tree is then compiled to JSON, which
will be used by an execution engine to perform the operations described in the
original story.

Unlike other languages, compiling and execution in Storyscript are separated.
The services are defined only at run-time at the engine's discretion. In a way,
you could say that what Storyscript really does is to convert a story in a
machine-friendly format.

For example, the Asyncy engine uses services as docker containers, so when a
service is encountered "docker run service-name" is executed by the engine.

EBNF
----
EBNF stands for "Extended Backus-Naur form", and is a language that can define
the syntax for other languages. It looks like this::

    boolean: TRUE | FALSE
    number: INT | FLOAT

    TRUE: "true"
    FALSE: "false"
    INT.2: "0".."9"+
    FLOAT.2: INT "." INT? | "." INT

If you are curious, you can have at look at Storyscript's full EBNF definition
with the grammar command::

    storyscript grammar

LALR
----
LALR stands for "Look-Ahead LR" parser and is what actually parses a story into
its tree.




.. toctree::
   :maxdepth: 2
   :hidden:

   getting-started
   command-line
   stories
   syntax
   cookbook
   advanced
   compiler
