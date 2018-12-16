# -*- coding: utf-8 -*-
from lark import Transformer as LarkTransformer

from .Tree import Tree
from ..exceptions import StorySyntaxError


class Transformer(LarkTransformer):

    """
    Performs transformations on the tree before it's parsed.
    All trees are transformed to Storyscript's custom tree. In some cases,
    additional transformations or checks are performed.
    """
    reserved_keywords = ['function', 'if', 'else', 'foreach', 'return',
                         'returns', 'try', 'catch', 'finally', 'when', 'as',
                         'import', 'while', 'raise']
    future_reserved_keywords = ['async', 'story', 'assert',
                                'called', 'mock']

    @classmethod
    def is_keyword(cls, token):
        keyword = token.value
        if keyword in cls.reserved_keywords:
            error_name = 'reserved_keyword_{}'.format(keyword)
            raise StorySyntaxError(error_name, token=token)
        if keyword in cls.future_reserved_keywords:
            error_name = 'future_reserved_keyword_{}'.format(keyword)
            raise StorySyntaxError(error_name, token=token)

    @staticmethod
    def arguments(matches):
        """
        Transforms an argument tree. If dealing with is a short-hand argument,
        expand it.
        """
        if len(matches) == 1:
            matches = [matches[0].child(0), matches[0]]
        return Tree('arguments', matches)

    @staticmethod
    def assignment(matches):
        """
        Transforms an assignment tree and checks for invalid characters in the
        variable name.
        """
        token = matches[0].children[0]
        if '/' in token.value:
            raise StorySyntaxError('variables_backslash', token=token)
        if '-' in token.value:
            raise StorySyntaxError('variables_dash', token=token)
        return Tree('assignment', matches)

    @classmethod
    def command(cls, matches):
        token = matches[0]
        cls.is_keyword(token)
        return Tree('command', matches)

    @classmethod
    def path(cls, matches):
        token = matches[0]
        cls.is_keyword(token)
        return Tree('path', matches)

    @staticmethod
    def service_block(matches):
        """
        Transforms service blocks, moving indented arguments back to the first
        node.
        """
        if len(matches) > 1:
            if matches[1].block.rules:
                for argument in matches[1].find_data('arguments'):
                    matches[0].service_fragment.children.append(argument)
                return Tree('service_block', [matches[0]])
        return Tree('service_block', matches)

    def __getattr__(self, attribute, *args):
        return lambda matches: Tree(attribute, matches)
