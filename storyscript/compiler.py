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
    def enter(cls, line, nested_block):
        """
        Sets the entering line for lines with nested blocks.
        """
        line['enter'] = nested_block.line()
        return line

    @classmethod
    def assignments(cls, tree):
        line = tree.line()
        dictionary = {
            'method': 'set',
            'ln': line,
            'container': None,
            'args': [
                Compiler.path(tree.node('path')),
                Compiler.values(tree.child(2))
            ],
            'output': None,
            'enter': None,
            'exit': None
        }
        return {line: dictionary}

    @classmethod
    def next(cls, tree):
        line = tree.line()
        dictionary = {
            'method': 'next',
            'ln': line,
            'container': None,
            'output': None,
            'args': [cls.file(tree.children[1])],
            'enter': None,
            'exit': None
        }
        return {line: dictionary}

    @classmethod
    def command(cls, tree):
        line = tree.line()
        dictionary = {
            'method': 'run',
            'ln': line,
            'container': tree.child(0).child(0).value,
            'args': None,
            'output': None,
            'enter': None,
            'exit': None
        }
        return {line: dictionary}

    @classmethod
    def if_block(cls, tree):
        line = tree.line()
        nested_block = tree.node('nested_block')
        dictionary = {
            'method': 'if',
            'ln': line,
            'container': None,
            'args': [cls.path(tree.node('if_statement'))],
            'output': None,
            'enter': nested_block.line()
        }
        partial = {line: dictionary}
        trees = [nested_block]
        elseif_block = tree.node('elseif_block')
        if elseif_block:
            trees.append(elseif_block)
        subtrees = cls.subtrees(*trees)
        return {**partial, **subtrees}

    @classmethod
    def elseif_block(cls, tree):
        """
        Compiles elseif_block trees
        """
        line = tree.line()
        dictionary = {
            'method': 'elif',
            'ln': line,
            'container': None,
            'args': [cls.path(tree.node('elseif_statement'))],
            'output': None
        }
        partial = {line: dictionary}
        return {**partial, **cls.subtree(tree.node('nested_block'))}

    @classmethod
    def for_block(cls, tree):
        line = tree.line()
        dictionary = {
            'method': 'for',
            'ln': line,
            'container': None,
            'args': [
                tree.node('for_statement').child(0).value,
                cls.path(tree.node('for_statement'))
            ],
            'output': None
        }
        nested_block = tree.node('nested_block')
        partial = {line: cls.enter(dictionary, nested_block)}
        return {**partial, **cls.subtree(nested_block)}

    @classmethod
    def wait_block(cls, tree):
        line = tree.line()
        dictionary = {
            'method': 'wait',
            'ln': line,
            'container': None,
            'output': None,
            'args': [cls.path(tree.node('wait_statement').child(1))]
        }
        partial = {line: dictionary}
        return {**partial, **cls.subtree(tree.node('nested_block'))}

    @classmethod
    def subtrees(cls, *trees):
        """
        Parses many subtrees
        """
        results = {}
        for tree in trees:
            results = {**results, **cls.subtree(tree)}
        return results

    @classmethod
    def subtree(cls, tree):
        """
        Parses a subtree, checking whether it should be compiled directly
        or keep parsing for deeper trees.
        """
        allowed_nodes = ['command', 'next', 'assignments', 'if_block',
                         'elseif_block', 'for_block', 'wait_block']
        if tree.data in allowed_nodes:
            return getattr(cls, tree.data)(tree)
        return cls.parse_tree(tree)

    @classmethod
    def parse_tree(cls, tree):
        """
        Parses a tree looking for subtrees.
        """
        script = {}
        for item in tree.children:
            if isinstance(item, Tree):
                script = {**cls.subtree(item), **script}
        return script

    @staticmethod
    def compile(tree):
        dictionary = {'script': Compiler.parse_tree(tree), 'version': version}
        return json.dumps(dictionary)
