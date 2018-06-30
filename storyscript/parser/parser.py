# -*- coding: utf-8 -*-
from lark import Lark
from lark.common import UnexpectedToken

from .grammar import Grammar
from .indenter import CustomIndenter
from .transformer import Transformer


class Parser:
    """
    Wraps up the parser submodule and exposes parsing and lexing
    functionalities.
    """
    def __init__(self, algo='lalr', ebnf_file=None):
        self.algo = algo
        self.ebnf_file = ebnf_file

    @staticmethod
    def make_message(value, line, column):
        template = ('Failed reading story because of unexpected "{}" at'
                    'line {}, column {}')
        return template.format(value, line, column)

    @classmethod
    def error_message(cls, e):
        message = cls.make_message(e.token.value, e.line, e.column)
        return message.encode('unicode_escape').decode('utf-8')

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
            print(self.error_message(e))
            exit()
        return self.transformer().transform(tree)

    def lex(self, source):
        """
        Lexes the source string
        """
        return self.lark().lex(source)
