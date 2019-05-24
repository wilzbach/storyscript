# -*- coding: utf-8 -*-
from storyscript.compiler.json.JSONCompiler import JSONCompiler
from storyscript.compiler.lowering.Lowering import Lowering
from storyscript.compiler.semantics.Semantics import Semantics


class Compiler:

    @classmethod
    def generate(cls, tree, features):
        """
        Parses an AST and checks it.
        """
        tree = Lowering(parser=tree.parser, features=features).process(tree)
        return Semantics(features=features).process(tree)

    @classmethod
    def compile(cls, tree, story, features, backend='json'):
        assert backend == 'json'
        compiler = JSONCompiler(story)
        tree = cls.generate(tree, features)
        return compiler.compile(tree)
