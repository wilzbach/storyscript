# -*- coding: utf-8 -*-
from .lines import Lines
from .objects import Objects
from ..exceptions import StoryscriptSyntaxError
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

    def assignment(self, tree, parent=None):
        """
        Compiles an assignment tree
        """
        line = tree.line()
        args = [
            Objects.path(tree.node('path')),
            Objects.values(tree.node('assignment_fragment').child(1))
        ]
        self.lines.append('set', line, args=args, parent=parent)

    def arguments(self, tree, parent=None):
        """
        Compiles arguments. This is called only for nested arguments.
        """
        line = self.lines[self.last_line()]
        if line['method'] != 'execute':
            raise StoryscriptSyntaxError(5, tree)
        line['args'] = line['args'] + Objects.arguments(tree)

    def service(self, tree, parent=None):
        """
        Compiles a service tree.
        """
        line = tree.line()
        command = tree.node('service_fragment.command')
        if command:
            command = command.child(0)
        arguments = Objects.arguments(tree.node('service_fragment'))
        service = tree.child(0).child(0).value
        output = self.output(tree.node('service_fragment.output'))
        if output:
            self.outputs[line] = output
        self.add_line('execute', line, service=service, command=command,
                      args=arguments, parent=parent, output=output)

    def return_statement(self, tree, parent=None):
        """
        Compiles a return_statement tree
        """
        if parent is None:
            raise StoryscriptSyntaxError(4, tree)
        line = tree.line()
        args = [Objects.values(tree.child(0))]
        self.add_line('return', line, args=args, parent=parent)

    def if_block(self, tree, parent=None):
        line = tree.line()
        nested_block = tree.node('nested_block')
        args = Objects.expression(tree.node('if_statement'))
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
        self.set_exit_line(line)
        args = Objects.expression(tree.node('elseif_statement'))
        nested_block = tree.node('nested_block')
        self.add_line('elif', line, args=args, enter=nested_block.line(),
                      parent=parent)
        self.subtree(nested_block, parent=line)

    def else_block(self, tree, parent=None):
        line = tree.line()
        self.set_exit_line(line)
        nested_block = tree.node('nested_block')
        self.add_line('else', line, enter=nested_block.line(), parent=parent)
        self.subtree(nested_block, parent=line)

    def foreach_block(self, tree, parent=None):
        line = tree.line()
        args = [Objects.path(tree.node('foreach_statement'))]
        output = self.output(tree.node('foreach_statement.output'))
        nested_block = tree.node('nested_block')
        self.add_line('for', line, args=args, enter=nested_block.line(),
                      parent=parent, output=output)
        self.subtree(nested_block, parent=line)

    def function_block(self, tree, parent=None):
        """
        Compiles a function and its nested block of code.
        """
        line = tree.line()
        function = tree.node('function_statement')
        args = Objects.function_arguments(function)
        output = self.function_output(function)
        nested_block = tree.node('nested_block')
        self.add_line('function', line, function=function.child(1).value,
                      output=output, args=args, enter=nested_block.line(),
                      parent=parent)
        self.subtree(nested_block, parent=line)

    def service_block(self, tree, parent=None):
        """
        Compiles a service block and the eventual nested block.
        """
        self.service(tree.node('service'), parent=parent)
        nested_block = tree.node('nested_block')
        if nested_block:
            self.subtree(nested_block, parent=tree.line())

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
                         'function_block', 'return_statement', 'arguments']
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

    def get_services(self):
        """
        Get the services and remove duplicates.
        """
        return list(set(self.services))

    @staticmethod
    def compiler():
        return Compiler()

    @classmethod
    def compile(cls, tree):
        compiler = cls.compiler()
        compiler.parse_tree(tree)
        return {'tree': compiler.lines, 'services': compiler.get_services(),
                'functions': compiler.functions, 'version': version}
