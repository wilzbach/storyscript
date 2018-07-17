# -*- coding: utf-8 -*-
from .lines import Lines
from .objects import Objects
from .preprocessor import Preprocessor
from ..exceptions import StoryError
from ..parser import Tree
from ..version import version


class Compiler:

    """
    Compiles Storyscript abstract syntax tree to JSON.
    """
    def __init__(self):
        self.lines = Lines()

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

    def imports(self, tree, parent):
        """
        Compiles an import rule
        """
        module = tree.child(1).value
        self.lines.modules[module] = tree.string.child(0).value[1:-1]

    def assignment(self, tree, parent):
        """
        Compiles an assignment tree
        """
        line = tree.line()
        args = [
            Objects.path(tree.path),
            Objects.values(tree.assignment_fragment.child(1))
        ]
        self.lines.append('set', line, args=args, parent=parent)

    def arguments(self, tree, parent):
        """
        Compiles arguments. This is called only for nested arguments.
        """
        line = self.lines.lines[self.lines.last()]
        if line['method'] != 'execute':
            raise StoryError('arguments-noservice', tree)
        line['args'] = line['args'] + Objects.arguments(tree)

    def service(self, tree, nested_block, parent):
        """
        Compiles a service tree.
        """
        line = tree.line()
        command = tree.service_fragment.command
        if command:
            command = command.child(0)
        arguments = Objects.arguments(tree.service_fragment)
        service = tree.child(0).child(0).value
        output = self.output(tree.service_fragment.output)
        if output:
            self.lines.set_output(line, output)
        enter = None
        if nested_block:
            enter = nested_block.line()
        self.lines.execute(line, service, command, arguments, output, enter,
                           parent)

    def return_statement(self, tree, parent):
        """
        Compiles a return_statement tree
        """
        if parent is None:
            raise StoryError('return-outside', tree)
        line = tree.line()
        args = [Objects.values(tree.child(0))]
        self.lines.append('return', line, args=args, parent=parent)

    def if_block(self, tree, parent):
        line = tree.line()
        nested_block = tree.nested_block
        args = Objects.expression(tree.if_statement)
        self.lines.append('if', line, args=args, enter=nested_block.line(),
                          parent=parent)
        self.subtree(nested_block, parent=line)
        trees = []
        for block in [tree.elseif_block, tree.else_block]:
            if block:
                trees.append(block)
        self.subtrees(*trees)

    def elseif_block(self, tree, parent):
        """
        Compiles elseif_block trees
        """
        line = tree.line()
        self.lines.set_exit(line)
        args = Objects.expression(tree.elseif_statement)
        nested_block = tree.nested_block
        self.lines.append('elif', line, args=args, enter=nested_block.line(),
                          parent=parent)
        self.subtree(nested_block, parent=line)

    def else_block(self, tree, parent):
        """
        Compiles else_block trees
        """
        line = tree.line()
        self.lines.set_exit(line)
        nested_block = tree.nested_block
        self.lines.append('else', line, enter=nested_block.line(),
                          parent=parent)
        self.subtree(nested_block, parent=line)

    def foreach_block(self, tree, parent):
        line = tree.line()
        args = [Objects.path(tree.foreach_statement)]
        output = self.output(tree.foreach_statement.output)
        nested_block = tree.nested_block
        self.lines.append('for', line, args=args, enter=nested_block.line(),
                          parent=parent, output=output)
        self.subtree(nested_block, parent=line)

    def function_block(self, tree, parent):
        """
        Compiles a function and its nested block of code.
        """
        line = tree.line()
        function = tree.function_statement
        args = Objects.function_arguments(function)
        output = self.function_output(function)
        nested_block = tree.nested_block
        self.lines.append('function', line, function=function.child(1).value,
                          output=output, args=args, enter=nested_block.line(),
                          parent=parent)
        self.subtree(nested_block, parent=line)

    def service_block(self, tree, parent):
        """
        Compiles a service block and the eventual nested block.
        """
        self.service(tree.service, tree.nested_block, parent)
        if tree.nested_block:
            self.subtree(tree.nested_block, parent=tree.line())

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
        allowed_nodes = ['service_block', 'assignment', 'if_block',
                         'elseif_block', 'else_block', 'foreach_block',
                         'function_block', 'return_statement', 'arguments',
                         'imports']
        if tree.data in allowed_nodes:
            getattr(self, tree.data)(tree, parent)
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
    def compile(cls, tree, debug=False):
        tree = Preprocessor.process(tree)
        compiler = cls.compiler()
        compiler.parse_tree(tree)
        lines = compiler.lines
        return {'tree': lines.lines, 'services': lines.get_services(),
                'entrypoint': lines.first(), 'modules': lines.modules,
                'functions': lines.functions, 'version': version}
