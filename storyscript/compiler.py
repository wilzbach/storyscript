# -*- coding: utf-8 -*-
import json
import re

from lark.lexer import Token

from .parser import Tree
from .version import version


class Compiler:

    """
    Compiles Storyscript abstract syntax tree to JSON.
    """
    def __init__(self):
        self.lines = {}

    def sorted_lines(self):
        return sorted(self.lines.keys(), key=lambda x: int(x))

    def last_line(self):
        """
        Gets the last line
        """
        if self.lines:
            return self.sorted_lines()[-1]

    def set_next_line(self, line_number):
        """
        Finds the previous line, and set the current as its next line
        """
        previous_line = self.last_line()
        if previous_line:
            self.lines[previous_line]['next'] = line_number

    @staticmethod
    def path(tree):
        return {'$OBJECT': 'path', 'paths': [tree.child(0).value]}

    @staticmethod
    def number(tree):
        return int(tree.child(0).value)

    @classmethod
    def string(cls, tree):
        """
        Compiles a string tree. If the string has templated values, they
        are processed and compiled.
        """
        item = {'$OBJECT': 'string', 'string': tree.child(0).value[1:-1]}
        matches = re.findall(r'{{([^}]*)}}', item['string'])
        if matches == []:
            return item
        values = []
        for match in matches:
            values.append(cls.path(Tree('path', [Token('WORD', match)])))
            find = '{}{}{}'.format('{{', match, '}}')
            item['string'] = item['string'].replace(find, '{}')
        item['values'] = values
        return item

    @staticmethod
    def boolean(tree):
        if tree.child(0).value == 'true':
            return True
        return False

    @staticmethod
    def file(token):
        return {'$OBJECT': 'file', 'string': token.value[1:-1]}

    @classmethod
    def list(cls, tree):
        items = []
        for value in tree.children:
            items.append(cls.values(value))
        return {'$OBJECT': 'list', 'items': items}

    @classmethod
    def objects(cls, tree):
        items = []
        for item in tree.children:
            key = cls.string(item.node('string'))
            value = cls.values(item.child(1))
            items.append([key, value])
        return {'$OBJECT': 'dict', 'items': items}

    @classmethod
    def values(cls, tree):
        """
        Parses a values subtree
        """
        subtree = tree.child(0)
        if subtree.data == 'string':
            return cls.string(subtree)
        elif subtree.data == 'boolean':
            return cls.boolean(subtree)
        elif subtree.data == 'list':
            return cls.list(subtree)
        elif subtree.data == 'number':
            return cls.number(subtree)
        elif subtree.data == 'objects':
            return cls.objects(subtree)
        elif subtree.type == 'FILEPATH':
            return cls.file(subtree)

    @staticmethod
    def base(method, line, container=None, args=None, enter=None, exit=None):
        """
        Creates the base dictionary for a given line.
        """
        return {
            line: {
                'method': method,
                'ln': line,
                'output': None,
                'container': container,
                'args': args,
                'enter': enter,
                'exit': exit
            }
        }

    @classmethod
    def assignments(cls, tree):
        args = [
            Compiler.path(tree.node('path')),
            Compiler.values(tree.child(2))
        ]
        return cls.base('set', tree.line(), args=args)

    def next(self, tree):
        return self.base('next', tree.line(), args=[self.file(tree.child(1))])

    def command(self, tree):
        line = tree.line()
        self.set_next_line(line)
        container = tree.child(0).child(0).value
        return self.base('run', line, container=container)

    def if_block(self, tree):
        line = tree.line()
        self.set_next_line(line)
        nested_block = tree.node('nested_block')
        args = [self.path(tree.node('if_statement'))]
        partial = self.base('if', line, args=args, enter=nested_block.line())
        trees = [nested_block]
        for block in [tree.node('elseif_block'), tree.node('else_block')]:
            if block:
                trees.append(block)
        subtrees = self.subtrees(*trees)
        return {**partial, **subtrees}

    def elseif_block(self, tree):
        """
        Compiles elseif_block trees
        """
        line = tree.line()
        self.set_next_line(line)
        args = [self.path(tree.node('elseif_statement'))]
        nested_block = tree.node('nested_block')
        partial = self.base('elif', line, args=args, enter=nested_block.line())
        return {**partial, **self.subtree(nested_block)}

    def else_block(self, tree):
        line = tree.line()
        self.set_next_line(line)
        nested_block = tree.node('nested_block')
        partial = self.base('else', line, enter=nested_block.line())
        return {**partial, **self.subtree(nested_block)}

    def for_block(self, tree):
        args = [
            tree.node('for_statement').child(0).value,
            self.path(tree.node('for_statement'))
        ]
        nested_block = tree.node('nested_block')
        line = tree.line()
        self.set_next_line(line)
        partial = self.base('for', line, args=args, enter=nested_block.line())
        return {**partial, **self.subtree(nested_block)}

    def wait_block(self, tree):
        line = tree.line()
        args = [self.path(tree.node('wait_statement').child(1))]
        nested_block = tree.node('nested_block')
        partial = self.base('wait', line, args=args, enter=nested_block.line())
        self.set_next_line(line)
        return {**partial, **self.subtree(nested_block)}

    def subtrees(self, *trees):
        """
        Parses many subtrees
        """
        results = {}
        for tree in trees:
            results = {**results, **self.subtree(tree)}
        return results

    def subtree(self, tree):
        """
        Parses a subtree, checking whether it should be compiled directly
        or keep parsing for deeper trees.
        """
        allowed_nodes = ['command', 'next', 'assignments', 'if_block',
                         'elseif_block', 'else_block', 'for_block',
                         'wait_block']
        if tree.data in allowed_nodes:
            return getattr(self, tree.data)(tree)
        return self.parse_tree(tree)

    def parse_tree(self, tree):
        """
        Parses a tree looking for subtrees.
        """
        for item in tree.children:
            if isinstance(item, Tree):
                self.lines = {**self.subtree(item), **self.lines}
        return self.lines

    @staticmethod
    def compile(tree):
        compiler = Compiler()
        dictionary = {'script': compiler.parse_tree(tree), 'version': version}
        return json.dumps(dictionary)
