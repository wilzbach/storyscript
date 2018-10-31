# -*- coding: utf-8 -*-
import io

from lark import Lark
from lark.exceptions import UnexpectedInput, UnexpectedToken

from .grammar import Grammar
from .indenter import CustomIndenter
from .transformer import Transformer
from .tree import Tree
from ..exceptions import StoryError


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

    def unexpected_token(self, error, debug, path):
        """
        Handles unexpected token errors.
        """
        if debug:
            raise error
        StoryError('token-unexpected', error, path=path).echo()
        exit()

    def unexpected_input(self, error, debug, path):
        """
        Handles unexpected input errors.
        """
        if debug:
            raise error
        StoryError('input-unexpected', error, path=path).echo()
        exit()

    def parse(self, source, debug=False, path=None):
        """
        Parses the source string.
        """
        if source == '':
            return Tree('empty', [])
        source = '{}\n'.format(source)
        lark = self.lark()
        try:
            tree = lark.parse(source)
        except UnexpectedToken as error:
            return self.unexpected_token(error, debug, path)
        except UnexpectedInput as error:
            return self.unexpected_input(error, debug, path)
        return self.transformer().transform(tree)

    def lex(self, source):
        """
        Lexes the source string
        """
        return self.lark().lex(source)
