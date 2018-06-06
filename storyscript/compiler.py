# -*- coding: utf-8 -*-
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
        self.services = []

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

    def set_exit_line(self, line):
        for line_number in self.sorted_lines()[::-1]:
            if self.lines[line_number]['method'] in ['if', 'elif']:
                self.lines[line_number]['exit'] = line
                break

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

    @staticmethod
    def types(tree):
        return {'$OBJECT': 'type', 'type': tree.child(0).value}

    @classmethod
    def values(cls, tree):
        """
        Parses a values subtree
        """
        subtree = tree.child(0)
        if hasattr(subtree, 'data'):
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
            elif subtree.data == 'types':
                return cls.types(subtree)
        if subtree.type == 'FILEPATH':
            return cls.file(subtree)
        elif subtree.type == 'NAME':
            return cls.path(tree)

    @classmethod
    def argument(cls, tree):
        name = tree.child(0).value
        value = cls.values(tree.child(1))
        return {'$OBJECT': 'argument', 'name': name, 'argument': value}

    @classmethod
    def arguments(cls, tree):
        """
        Parses a group of arguments rules
        """
        arguments = []
        for argument in list(tree.find_data('arguments')):
            arguments.append(cls.argument(argument))
        return arguments

    @staticmethod
    def output(tree):
        output = []
        if tree:
            for item in tree.children:
                output.append(item.value)
        return output

    @classmethod
    def function_output(cls, tree):
        return cls.output(tree.node('function_output.types'))

    def add_line(self, method, line, args=None, container=None, command=None,
                 output=None, enter=None, exit=None, parent=None):
        """
        Creates the base dictionary for a given line.
        """
        dictionary = {
            line: {
                'method': method,
                'ln': line,
                'output': output,
                'container': container,
                'command': command,
                'args': args,
                'enter': enter,
                'exit': exit,
                'parent': parent
            }
        }
        self.lines = {**self.lines, **dictionary}

    def assignment(self, tree, parent=None):
        line = tree.line()
        self.set_next_line(line)
        args = [
            self.path(tree.node('path')),
            self.values(tree.node('assignment_fragment.values'))
        ]
        self.add_line('set', line, args=args, parent=parent)

    def service(self, tree, parent=None):
        """
        Translates a command tree to the corresponding line
        """
        line = tree.line()
        self.set_next_line(line)
        command = tree.node('service_fragment.command')
        if command:
            command = command.child(0)
        arguments = self.arguments(tree.node('service_fragment'))
        container = tree.child(0).child(0).value
        output = self.output(tree.node('service_fragment.output'))
        self.add_line('run', line, container=container, command=command,
                      args=arguments, parent=parent, output=output)
        self.services.append(container)

    def if_block(self, tree, parent=None):
        line = tree.line()
        self.set_next_line(line)
        nested_block = tree.node('nested_block')
        args = [self.path(tree.node('if_statement'))]
        self.add_line('if', line, args=args, enter=nested_block.line(),
                      parent=parent)
        self.subtree(nested_block, parent=line)
        trees = []
        for block in [tree.node('elseif_block'), tree.node('else_block')]:
            if block:
                trees.append(block)
        self.subtrees(*trees)

    def elseif_block(self, tree, parent=None):
        """
        Compiles elseif_block trees
        """
        line = tree.line()
        self.set_next_line(line)
        self.set_exit_line(line)
        args = [self.path(tree.node('elseif_statement'))]
        nested_block = tree.node('nested_block')
        self.add_line('elif', line, args=args, enter=nested_block.line(),
                      parent=parent)
        self.subtree(nested_block, parent=line)

    def else_block(self, tree, parent=None):
        line = tree.line()
        self.set_next_line(line)
        self.set_exit_line(line)
        nested_block = tree.node('nested_block')
        self.add_line('else', line, enter=nested_block.line(), parent=parent)
        self.subtree(nested_block, parent=line)

    def foreach_block(self, tree, parent=None):
        line = tree.line()
        self.set_next_line(line)
        args = [self.path(tree.node('foreach_statement'))]
        output = self.output(tree.node('foreach_statement.output'))
        nested_block = tree.node('nested_block')
        self.add_line('for', line, args=args, enter=nested_block.line(),
                      parent=parent, output=output)
        self.subtree(nested_block, parent=line)

    def function_block(self, tree, parent=None):
        line = tree.line()
        self.set_next_line(line)
        nested_block = tree.node('nested_block')
        self.add_line('function', line, enter=nested_block.line(),
                      parent=parent)
        self.subtree(nested_block, parent=line)

    def subtrees(self, *trees):
        """
        Parses many subtrees
        """
        for tree in trees:
            self.subtree(tree)

    def subtree(self, tree, parent=None):
        """
        Parses a subtree, checking whether it should be compiled directly
        or keep parsing for deeper trees.
        """
        allowed_nodes = ['service', 'assignment', 'if_block', 'elseif_block',
                         'else_block', 'foreach_block', 'function_block']
        if tree.data in allowed_nodes:
            getattr(self, tree.data)(tree, parent=parent)
            return
        self.parse_tree(tree, parent=parent)

    def parse_tree(self, tree, parent=None):
        """
        Parses a tree looking for subtrees.
        """
        for item in tree.children:
            if isinstance(item, Tree):
                self.subtree(item, parent=parent)

    @staticmethod
    def compiler():
        return Compiler()

    @classmethod
    def compile(cls, tree):
        compiler = cls.compiler()
        compiler.parse_tree(tree)
        return {'tree': compiler.lines, 'services': compiler.services,
                'version': version}
