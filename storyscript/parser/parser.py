# -*- coding: utf-8 -*-
from lark import Lark
from lark.common import UnexpectedToken
from lark.lexer import UnexpectedInput

from .grammar import Grammar
from .indenter import CustomIndenter
from .transformer import Transformer
from ..exceptions import StoryError


class Parser:
    """
    Wraps up the parser submodule and exposes parsing and lexing
    functionalities.
    """
    def __init__(self, algo='lalr', ebnf_file=None):
        self.algo = algo
        self.ebnf_file = ebnf_file

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
        if self.ebnf_file:
            with open(self.ebnf_file, 'r') as f:
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
        source = '{}\n'.format(source)
        lark = self.lark()
        try:
            tree = lark.parse(source)
        except UnexpectedToken as e:
            if debug:
                raise e
            print(StoryError('token-unexpected', e).message())
            exit()
        except UnexpectedInput as e:
            if debug:
                raise e
            print(StoryError('input-unexpected', e).message())
            exit()
        return self.transformer().transform(tree)

    def lex(self, source):
        """
        Lexes the source string
        """
        return self.lark().lex(source)
