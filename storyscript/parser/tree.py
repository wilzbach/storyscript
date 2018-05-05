# -*- coding: utf-8 -*-
from lark.lexer import Token
from lark.tree import Tree as LarkTree


class Tree(LarkTree):

    def json(self):
        dictionary = {}
        for child in self.children:
            if isinstance(child, Tree):
                dictionary[child.data] = child.json()
            elif isinstance(child, Token):
                dictionary[child.type] = child.value
        return dictionary
