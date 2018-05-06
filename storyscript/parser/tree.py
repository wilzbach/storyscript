# -*- coding: utf-8 -*-
from lark.lexer import Token
from lark.tree import Tree as LarkTree

from ..version import version


class Tree(LarkTree):

    def json(self):
        dictionary = {}
        for child in self.children:
            if isinstance(child, Tree):
                if child.data == 'start':
                    dictionary['version'] = version
                    dictionary['script'] = {}
                else:
                    dictionary[child.data] = child.json()
            elif isinstance(child, Token):
                dictionary[child.type] = child.value
        return dictionary
