# -*- coding: utf-8 -*-
import re

from lark import Transformer as LarkTransformer

from .tree import Tree
from ..exceptions import StoryscriptSyntaxError


class Transformer(LarkTransformer):

    def service(self, matches):
        if len(matches[0].children) > 1:
            token = matches[0].children[1].children[0]
            raise StoryscriptSyntaxError(1, token)
        return Tree('service', matches)

    def assignment(self, matches):
        token = matches[0].children[0]
        if '/' in token.value:
            raise StoryscriptSyntaxError(2, token)
        if '-' in token.value:
            raise StoryscriptSyntaxError(3, token)
        return Tree('assignment', matches)

    def __getattr__(self, attribute, *args):
        return lambda matches: Tree(attribute, matches)
