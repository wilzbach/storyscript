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
    story = magic()
    result = Compiler.generate(tree, story=story)
    Lowering.__init__.assert_called_with(
        parser=tree.parser, features=story.context.features)
    Lowering.process.assert_called_with(tree)
    Semantics.process.assert_called_with(Lowering.process())
    assert result == (Lowering.process(), Semantics.process())


def test_compiler_compile(patch, magic):
    patch.object(Compiler, 'generate', return_value=('tree', 'sem'))
    patch.object(JSONCompiler, 'compile')
    tree = magic()
    result = Compiler.compile(tree, story=None)
    Compiler.generate.assert_called_with(tree, None)
    JSONCompiler.compile.assert_called_with('tree')
    assert result.output() == JSONCompiler.compile()
    assert result.module() == 'sem'
    assert result.backend == 'json'
