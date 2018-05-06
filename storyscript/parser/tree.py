# -*- coding: utf-8 -*-
from lark.lexer import Token
from lark.tree import Tree as LarkTree

from ..version import version


class Tree(LarkTree):

    def json(self):
        dictionary = {'script': {}}
        for child in self.children:
            if isinstance(child, Tree):
                if child.data == 'start':
                    dictionary['version'] = version
                elif child.data == 'command':
                    command = {
                        'method': 'run',
                        'ln': child.children[0].line,
                        'container': child.children[1].value,
                        'args': [],
                        'output': None,
                        'enter': None,
                        'exit': None
                    }
                    dictionary['script'][child.children[0].line] = command
                else:
                    dictionary[child.data] = child.json()
            elif isinstance(child, Token):
                dictionary[child.type] = child.value
        return dictionary
