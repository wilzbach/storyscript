# -*- coding: utf-8 -*-

from storyscript.compiler import Compiler
from storyscript.compiler.json import JSONCompiler
from storyscript.compiler.lowering import Lowering
from storyscript.compiler.semantics import Semantics


def test_compiler_generate(patch, magic):
    patch.init(Lowering)
    patch.object(Lowering, 'process')
    patch.object(Semantics, 'process')
    patch.many(JSONCompiler, ['compile'])
    tree = magic()
    result = Compiler.generate(tree, features=None)
    Lowering.__init__.assert_called_with(parser=tree.parser, features=None)
    Lowering.process.assert_called_with(tree)
    Semantics.process.assert_called_with(Lowering.process())
    assert result == Semantics.process()


def test_compiler_compile(patch, magic):
    patch.object(Compiler, 'generate')
    patch.object(JSONCompiler, 'compile')
    tree = magic()
    result = Compiler.compile(tree, story=None, features=None)
    Compiler.generate.assert_called_with(tree, None)
    JSONCompiler.compile.assert_called_with(Compiler.generate())
    assert result == JSONCompiler.compile()
