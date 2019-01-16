# -*- coding: utf-8 -*-
from .Lines import Lines
from .Objects import Objects
from .Preprocessor import Preprocessor
from ..Version import version
from ..exceptions import CompilerError, StorySyntaxError
from ..exceptions import internal_assert
from ..parser import Tree


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

    @staticmethod
    def extract_values(fragment):
        """
        Extracts values from an assignment_fragment tree, to be used as
        arguments in a set method.
        """
        if fragment.expression:
            if fragment.expression.mutation:
                return [Objects.values(fragment.expression.values),
                        Objects.mutation(fragment.expression.mutation)]
            return [Objects.expression(fragment.expression)]
        return [Objects.entity(fragment.child(1))]

    @staticmethod
    def chained_mutations(tree):
        """
        Finds and compile chained mutations
        """
        mutations = []
        for mutation in tree.find_data('chained_mutation'):
            mutations.append(Objects.mutation(mutation.mutation_fragment))
        return mutations

    @classmethod
    def function_output(cls, tree):
        return cls.output(tree.node('function_output.types'))

    def imports(self, tree, parent):
        """
        Compiles an import rule
        """
        module = tree.child(1).value
        self.lines.modules[module] = tree.string.child(0).value[1:-1]

    def expression(self, tree, parent):
        """
        Compiles an expression
        """
        args = [Objects.expression(tree.expression)]
        self.lines.append('expression', tree.line(), args=args, parent=parent)

    def unary_expression(self, tree, parent, method, name=None, line=None):
        """
        Simplifies an expression with only one leaf to its respective value
        """
        entity = tree.binary_expression.unary_expression.pow_expression. \
            primary_expression.entity
        args = [Objects.entity(entity)]
        kwargs = {}
        # name is required for 'set' only
        if name is not None:
            kwargs['name'] = name
        if line is None:
            line = tree.line()
        self.lines.append(method, line, args=args, parent=parent, **kwargs)

    def absolute_expression(self, tree, parent):
        """
        Compiles an absolute expression using Compiler.expression
        """
        bin_exp = tree.expression.binary_expression
        if bin_exp is not None and bin_exp.is_unary_leaf():
            self.unary_expression(tree.expression, parent, method='expression')
        else:
            self.expression(tree, parent)

    def assignment(self, tree, parent):
        """
        Compiles an assignment tree
        """
        name = Objects.names(tree.path)
        fragment = tree.assignment_fragment
        service = fragment.service
        if service:
            path = Objects.names(service.path)
            if path not in self.lines.variables:
                self.service(service, None, parent)
                self.lines.set_name(name)
                return
        elif fragment.mutation:
            self.mutation_block(fragment, parent)
            self.lines.set_name(name)
            return
        elif fragment.expression:
            exp = fragment.expression
            if exp.binary_expression.is_unary_leaf():
                self.unary_expression(exp, parent, method='set',
                                      name=name, line=tree.line())
            else:
                self.expression(fragment, parent)
                self.lines.set_name(name)
            return
        internal_assert(0)

    def arguments(self, tree, parent):
        """
        Compiles arguments. This is called only for nested arguments.
        """
        previous_line = self.lines.last()
        if previous_line:
            line = self.lines.lines[previous_line]
            if line['method'] != 'execute':
                raise StorySyntaxError('arguments_noservice', tree=tree)
            line['args'] = line['args'] + Objects.arguments(tree)
            return
        raise StorySyntaxError('arguments_noservice', tree=tree)

    def service(self, tree, nested_block, parent):
        """
        Compiles a service tree.
        """
        service_name = Objects.names(tree.path)
        if service_name in self.lines.variables:
            self.mutation_block(tree, parent)
            return
        line = tree.line()
        command = tree.service_fragment.command
        if command:
            command = command.child(0)
        arguments = Objects.arguments(tree.service_fragment)
        service = tree.path.extract_path()
        output = self.output(tree.service_fragment.output)
        if output:
            self.lines.set_scope(line, parent, output)
        enter = None
        if nested_block:
            enter = nested_block.line()
        try:
            args = (line, service, command, arguments, output, enter, parent)
            self.lines.execute(*args)
        except StorySyntaxError as error:
            error.tree_position(tree)
            raise error

    def when(self, tree, nested_block, parent):
        """
        Compiles a when tree
        """
        if tree.service:
            self.service(tree.service, nested_block, parent)
            self.lines.lines[self.lines.last()]['method'] = 'when'
        elif tree.path:
            args = [Objects.path(tree.path)]
            output = self.output(tree.output)
            self.lines.append('when', tree.line(), args=args,
                              output=output, parent=parent)

    def return_statement(self, tree, parent):
        """
        Compiles a return_statement tree
        """
        if parent is None:
            raise CompilerError('return_outside', tree=tree)
        line = tree.line()
        args = [Objects.entity(tree.child(0))]
        self.lines.append('return', line, args=args, parent=parent)

    def if_block(self, tree, parent):
        line = tree.line()
        nested_block = tree.nested_block
        args = Objects.assertion(tree.if_statement)
        self.lines.set_scope(line, parent)
        self.lines.append('if', line, args=args, enter=nested_block.line(),
                          parent=parent)
        self.subtree(nested_block, parent=line)
        trees = []
        for block in [tree.elseif_block, tree.else_block]:
            if block:
                trees.append(block)
        self.subtrees(*trees, parent=parent)

    def elseif_block(self, tree, parent):
        """
        Compiles elseif_block trees
        """
        line = tree.line()
        self.lines.set_exit(line)
        args = Objects.assertion(tree.elseif_statement)
        nested_block = tree.nested_block
        self.lines.set_scope(line, parent)
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
        self.lines.set_scope(line, parent)
        self.lines.append('else', line, enter=nested_block.line(),
                          parent=parent)
        self.subtree(nested_block, parent=line)

    def foreach_block(self, tree, parent):
        line = tree.line()
        args = [Objects.entity(tree.foreach_statement.child(0))]
        output = self.output(tree.foreach_statement.output)
        nested_block = tree.nested_block
        self.lines.set_scope(line, parent, output)
        self.lines.append('for', line, args=args, enter=nested_block.line(),
                          parent=parent, output=output)
        self.subtree(nested_block, parent=line)

    def while_block(self, tree, parent):
        line = tree.line()
        args = [Objects.entity(tree.while_statement.child(0))]
        nested_block = tree.nested_block
        self.lines.set_scope(line, parent)
        self.lines.append('while', line, args=args, enter=nested_block.line(),
                          parent=parent)
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
        function_name = function.child(1).value
        if function_name in self.lines.functions:
            raise CompilerError(
                'function_already_declared', token=function.child(1),
                function_name=function_name,
                previous_line=self.lines.functions[function_name])
        self.lines.append('function', line, function=function_name,
                          output=output, args=args, enter=nested_block.line(),
                          parent=parent)
        self.subtree(nested_block, parent=line)

    def mutation_block(self, tree, parent):
        """
        Compiles a mutation or a service that is actually a mutation.
        """
        if tree.path:
            args = [
                Objects.path(tree.path),
                Objects.mutation(tree.service_fragment)
            ]
            args = args + self.chained_mutations(tree)
        else:
            args = [
                Objects.entity(tree.mutation.entity),
                Objects.mutation(tree.mutation.mutation_fragment)
            ]
            args = args + self.chained_mutations(tree.mutation)
        if tree.nested_block:
            args = args + self.chained_mutations(tree.nested_block)
        self.lines.append('mutation', tree.line(), args=args, parent=parent)

    def indented_chain(self, tree, parent):
        """
        Compiles an indented mutation.
        """
        previous_line = self.lines.last()
        if previous_line:
            line = self.lines.lines[previous_line]
            if line['method'] != 'mutation':
                raise StorySyntaxError('arguments_nomutation', tree=tree)
            line['args'] = line['args'] + self.chained_mutations(tree)
            return
        raise StorySyntaxError('arguments_nomutation', tree=tree)

    def service_block(self, tree, parent):
        """
        Compiles a service block and the eventual nested block.
        """
        self.service(tree.service, tree.nested_block, parent)
        if tree.nested_block:
            self.subtree(tree.nested_block, parent=tree.line())

    def when_block(self, tree, parent):
        self.when(tree, tree.nested_block, parent)
        if tree.nested_block:
            self.subtree(tree.nested_block, parent=tree.line())

    def try_block(self, tree, parent):
        """
        Compiles a try block
        """
        line = tree.line()
        nested_block = tree.nested_block
        self.lines.set_scope(line, parent)
        self.lines.append('try', line, enter=nested_block.line(),
                          parent=parent)
        self.subtree(nested_block, parent=line)
        if tree.catch_block:
            self.catch_block(tree.catch_block, parent=parent)
        if tree.finally_block:
            self.finally_block(tree.finally_block, parent=parent)

    def raise_statement(self, tree, parent):
        """
        Compiles a raise statement
        """
        line = tree.line()
        args = []
        if len(tree.children) > 1:
            args = [Objects.entity(tree.child(1))]
        self.lines.append('raise', line, args=args, parent=parent)

    def catch_block(self, tree, parent):
        """
        Compiles a catch block
        """
        line = tree.line()
        self.lines.set_exit(line)
        nested_block = tree.nested_block
        output = Objects.names(tree.catch_statement)
        self.lines.set_scope(line, parent, output)
        self.lines.append('catch', line, enter=nested_block.line(),
                          output=output, parent=parent)
        self.subtree(nested_block, parent=line)

    def finally_block(self, tree, parent):
        """
        Compiles a finally block
        """
        line = tree.line()
        self.lines.set_exit(line)
        nested_block = tree.nested_block
        self.lines.set_scope(line, parent)
        self.lines.append('finally', line, enter=nested_block.line(),
                          parent=parent)
        self.subtree(nested_block, parent=line)

    def break_statement(self, tree, parent):
        if parent is None:
            raise CompilerError('break_outside', tree=tree)
        self.lines.append('break', tree.line(), parent=parent)

    def subtrees(self, *trees, parent=None):
        """
        Parses many subtrees
        """
        for tree in trees:
            self.subtree(tree, parent=parent)

    def subtree(self, tree, parent=None):
        """
        Parses a subtree, checking whether it should be compiled directly
        or keep parsing for deeper trees.
        """
        allowed_nodes = ['service_block', 'absolute_expression', 'assignment',
                         'if_block', 'elseif_block', 'else_block',
                         'foreach_block', 'function_block', 'when_block',
                         'try_block', 'return_statement', 'arguments',
                         'imports', 'while_block', 'raise_statement',
                         'break_statement', 'mutation_block', 'indented_chain']
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
