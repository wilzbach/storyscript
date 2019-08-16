# -*- coding: utf-8 -*-
from storyscript.compiler.json.JSONCompiler import JSONCompiler
from storyscript.compiler.lowering.Lowering import Lowering
from storyscript.compiler.semantics.Semantics import Semantics


class CompilerOutput:
    """
    Compilation object of a compiler invocation.
    Allows to access to the compilation output and its semantic module object.
    """

    def __init__(self, backend, output, module):
        self.backend = backend
        self._output = output
        self._module = module

    def output(self):
        """
        Compilation output
        """
        return self._output

    def module(self):
        """
        Module table.
        """
        return self._module


class Compiler:

    @classmethod
    def generate(cls, tree, features):
        """
        Parses an AST and checks it.
        """
        tree = Lowering(parser=tree.parser, features=features).process(tree)
        module = Semantics(features=features).process(tree)
        return tree, module

    @classmethod
    def compile(cls, tree, story, features, backend='json'):
        assert backend == 'json'
        compiler = JSONCompiler(story)
        tree, module = cls.generate(tree, features)
        output = compiler.compile(tree)
        return CompilerOutput(
            backend=backend,
            module=module,
            output=output
        )
