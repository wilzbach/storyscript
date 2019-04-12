# -*- coding: utf-8 -*-
from storyscript.compiler.json.JSONCompiler import JSONCompiler
from storyscript.compiler.lowering.Lowering import Lowering
from storyscript.compiler.semantics.Semantics import Semantics


class Compiler:

    @classmethod
    def generate(cls, tree, debug=False):
        """
        Parses an AST and checks it.
        """
        tree = Lowering(parser=tree.parser).process(tree)
        return Semantics().process(tree)

    @classmethod
    def compile(cls, tree, story, debug=False, backend='json'):
        assert backend == 'json'
        compiler = JSONCompiler(story)
        tree = cls.generate(tree, debug=debug)
        return compiler.compile(tree, debug=debug)
