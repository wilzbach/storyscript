# -*- coding: utf-8 -*-
import io

from lark import Lark

from .grammar import Grammar
from .indenter import CustomIndenter
from .transformer import Transformer
from .tree import Tree


class Parser:
    """
    Wraps up the parser submodule and exposes parsing and lexing
    functionalities.
    """
    def __init__(self, algo='lalr', ebnf=None):
        self.algo = algo
        self.ebnf = ebnf

    def indenter(self):
        """
        Initialize the indenter
        """
        return CustomIndenter()

    def transformer(self):
        """
        Initialize the transformer
        """
        return Transformer()

    def grammar(self):
        if self.ebnf:
            with io.open(self.ebnf, 'r') as f:
                return f.read()
        return Grammar().build()

    def lark(self):
        """
        Get the grammar and initialize Lark.
        """
        return Lark(self.grammar(), parser=self.algo, postlex=self.indenter())

    def parse(self, source, debug=False):
        """
        Parses the source string.
        """
        if source == '':
            return Tree('empty', [])
        source = '{}\n'.format(source)
        lark = self.lark()
        tree = lark.parse(source)
        return self.transformer().transform(tree)

    def lex(self, source):
        """
        Lexes the source string
        """
        return self.lark().lex(source)
