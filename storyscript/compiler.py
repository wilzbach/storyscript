# -*- coding: utf-8 -*-
from lark.lexer import Token

from .parser import Tree
from .version import version


class Compiler:

    """
    Compiles Storyscript abstract syntax tree to JSON.
    """

    @staticmethod
    def path(tree):
        return {'$OBJECT': 'path', 'paths': [tree.child(0).value]}

    @staticmethod
    def number(tree):
        return int(tree.child(0).value)

    @staticmethod
    def string(tree):
        return {'$OBJECT': 'string', 'string': tree.child(0).value[1:-1]}

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
            items.append(cls.string(value.child(0)))
        return {'$OBJECT': 'list', 'items': items}

    @classmethod
    def line(cls, tree):
        """
        Finds the line number of a tree, by finding the first token in the tree
        and returning its line
        """
        for item in tree.children:
            if isinstance(item, Token):
                return str(item.line)
            return cls.line(item)

    @staticmethod
    def assignments(tree):
        return {
            'method': 'set',
            'ln': Compiler.line(tree),
            'container': None,
            'args': [
                Compiler.path(tree.node('path')),
                Compiler.string(tree.child(2).node('string'))
            ],
            'output': None,
            'enter': None,
            'exit': None
        }

    @classmethod
    def next_statement(cls, tree):
        return {
            'method': 'next',
            'ln': cls.line(tree),
            'container': None,
            'output': None,
            'args': [cls.file(tree.children[1])],
            'enter': None,
            'exit': None
        }

    @classmethod
    def command(cls, tree):
        dictionary = {
            'method': 'run',
            'ln': Compiler.line(tree),
            'container': tree.children[0].value,
            'args': None,
            'output': None,
            'enter': None,
            'exit': None
        }
        return dictionary

    @classmethod
    def parse_subtree(cls, tree):
        """
        Parses a tree that can have nested subtrees.
        """
        if tree.data in ['command', 'next_statement', 'assignments']:
            return {cls.line(tree): getattr(cls, tree.data)(tree)}
        return cls.parse_tree(tree)

    @classmethod
    def parse_tree(cls, tree):
        script = {}
        for item in tree.children:
            if isinstance(item, Tree):
                script = {**cls.parse_subtree(item), **script}
        return script

    @staticmethod
    def compile(tree):
        dictionary = {'script': Compiler.parse_tree(tree), 'version': version}
        return dictionary
