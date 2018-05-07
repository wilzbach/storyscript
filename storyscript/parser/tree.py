# -*- coding: utf-8 -*-
from lark.lexer import Token
from lark.tree import Tree as LarkTree

from ..version import version


class Tree(LarkTree):

    def command(self, dictionary):
        line = {
            'method': 'run',
            'ln': self.children[0].line,
            'container': self.children[1].value,
            'args': [],
            'output': None,
            'enter': None,
            'exit': None
        }
        dictionary['script'][self.children[0].line] = line

    def if_statement(self, dictionary):
        line = {
            'method': 'if',
            'ln': self.children[0].line,
            'container': None,
            'args': [],
            'output': None,
            'enter': None,
            'exit': None
        }
        dictionary['script'][self.children[0].line] = line

    @staticmethod
    def walk(tree, path):
        for item in tree.children:
            if item.data == path:
                return item

    def node(self, path):
        """
        Finds a subtree or a nested subtree, using path
        """
        shards = path.split('.')
        current = None
        for shard in shards:
            if current is None:
                current = self.walk(self, shard)
            else:
                current = self.walk(current, shard)
        return current

    def child(self, index):
        return self.children[index]

    def json(self):
        dictionary = {'script': {}, 'version': version}
        for child in self.children:
            if isinstance(child, Tree):
                if child.data in ['command', 'if_statement']:
                    getattr(child, child.data)()
            elif isinstance(child, Token):
                dictionary[child.type] = child.value
        return dictionary
