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
    def generate(cls, tree, storycontext, scope):
        """
        Parses an AST and checks it.
        """
        tree = Lowering(
            parser=tree.parser, features=storycontext.features
        ).process(tree)
        module = Semantics(
            storycontext=storycontext, root_scope=scope
        ).process(tree)
        return tree, module

    @classmethod
    def compile(cls, tree, story, backend="json", scope=None):
        tree, module = cls.generate(tree, story.context, scope=scope)
        if backend == "json":
            compiler = JSONCompiler(story)
            output = compiler.compile(tree)
        else:
            assert backend == "semantic"
            output = tree
        return CompilerOutput(backend=backend, module=module, output=output)
