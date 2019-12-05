# -*- coding: utf-8 -*-
import contextlib

from storyscript.parser import Tree

from .Objects import Objects


class PrettyPrinter:

    """
    Formats a Storyscript abstract syntax tree back to Storyscript.
    """

    def __init__(self):
        self.buf = ""
        self.indent_type = "  "
        self.current_indent = ""
        self.objects = Objects(self)

    def add_line(self, line):
        self.buf += f"{self.current_indent}{line}\n"

    @contextlib.contextmanager
    def scope(self):
        """
        Updates the indentation count for a new scope.
        Reverts to original count after leaving the scope.
        Use in a `with` block.
        """
        # start scope
        indent_before = self.current_indent
        self.current_indent += self.indent_type
        yield
        # end scope
        self.current_indent = indent_before

    def base_expression_assignment(self, tree, parent, line):
        """
        Compiles a base expression into an expression, service or mutation
        """
        service = tree.service
        if service:
            return self.service(service, None, parent)
        else:
            assert tree.expression
            return self.objects.expression(tree.expression)

    def fake_base_expression(self, tree, parent):
        """
        Process a fake base expression.
        """
        assert tree.expression
        return self.objects.expression(tree.expression)

    def assignment(self, tree, parent):
        """
        Compiles an assignment tree.
        """
        name = self.objects.names(tree.path)[0]
        line = tree.line()
        fragment = tree.assignment_fragment.base_expression
        e = self.base_expression_assignment(fragment, parent, line)
        self.add_line(f"{name} = {e}")

    def call_expression(self, tree, parent):
        """
        Compiles a function call expression.
        """
        name = self.objects.path(tree.path)
        # create temporary tree to exclude arguments from the first path
        arg_tree = Tree("arg_tree", tree.children[1:])
        args = self.objects.arguments(arg_tree)
        return f"{name}({args})"

    def inline_expression(self, tree, parent):
        """
        Compiles an inline expression.
        """
        assert tree.data == "inline_expression"
        child = tree.child(0)
        assert len(tree.children) == 1
        if child.data == "call_expression":
            return self.call_expression(child, tree)
        elif child.data == "mutation":
            return self.objects.mutation(child)
        else:
            assert child.data == "service"
            val = self.service(child, None, tree)
            return f"({val})"

    def service(self, tree, nested_block, parent):
        """
        Compiles a service tree.
        """
        service_name = self.objects.names(tree.path)[0]
        command = tree.service_fragment.command
        tree.expect(command is not None, "service_without_command")
        command = command.child(0)
        arguments = self.objects.arguments(tree.service_fragment)
        if len(arguments) > 0:
            arguments = f" {arguments}"
        output = ""
        if tree.service_fragment.output:
            output = " as " + self.objects.output(tree.service_fragment.output)
        r = f"{service_name} {command}{arguments}{output}"
        return r

    def when(self, tree, nested_block, parent):
        """
        Compiles a when tree.
        """
        assert tree.service
        sf = tree.service.service_fragment
        if not sf.command:
            sf.command = tree.service.path
        self.add_line(
            "when " + self.service(tree.service, nested_block, parent)
        )

    def return_statement(self, tree, parent):
        """
        Compiles a return_statement tree.
        """
        args = ""
        if tree.base_expression:
            args = " "
            args += self.fake_base_expression(tree.base_expression, parent)
        self.add_line(f"return{args}")

    def if_block(self, tree, parent):
        """
        Compiles if_block trees.
        """
        exp = tree.if_statement.base_expression
        arg = self.fake_base_expression(exp, parent)
        self.add_line(f"if {arg}")
        with self.scope():
            self.subtree(tree.nested_block)

        trees = tree.extract("elseif_block")
        if tree.else_block:
            trees.append(tree.else_block)
        self.subtrees(*trees, parent=parent)

    def elseif_block(self, tree, parent):
        """
        Compiles elseif_block trees
        """
        exp = tree.elseif_statement.base_expression
        arg = self.fake_base_expression(exp, parent)
        self.add_line(f"else if {arg}")
        with self.scope():
            self.subtree(tree.nested_block)

    def else_block(self, tree, parent):
        """
        Compiles else_block trees
        """
        self.add_line(f"else")
        with self.scope():
            self.subtree(tree.nested_block)

    def foreach_block(self, tree, parent):
        """
        Compiles a foreach_block.
        """
        exp = tree.foreach_statement.base_expression
        arg = self.fake_base_expression(exp, parent)
        output = self.objects.output(tree.foreach_statement.output)
        self.add_line(f"foreach {arg} as {output}")
        with self.scope():
            self.subtree(tree.nested_block)

    def while_block(self, tree, parent):
        """
        Compiles a while_block.
        """
        exp = tree.while_statement.base_expression
        arg = self.fake_base_expression(exp, parent)
        self.add_line(f"while {arg}")
        with self.scope():
            self.subtree(tree.nested_block)

    def function_block(self, tree, parent):
        """
        Compiles a function and its nested block of code.
        """
        function = tree.function_statement
        function_name = function.child(1).value
        line = f"function {function_name}"
        args = self.objects.function_arguments(function)
        if args:
            line += f" {args}"
        self.add_line(line)
        with self.scope():
            self.subtree(tree.nested_block)

    def service_block(self, tree, parent):
        """
        Compiles a service block and the eventual nested block.
        """
        s = self.service(tree.service, tree.nested_block, parent)
        self.add_line(s)
        if tree.nested_block:
            with self.scope():
                self.subtree(tree.nested_block, parent=tree.line())

    def when_block(self, tree, parent):
        """
        Compiles a when_block.
        """
        self.when(tree, tree.nested_block, parent)
        with self.scope():
            self.subtree(tree.nested_block)

    def try_block(self, tree, parent):
        """
        Compiles a try block
        """
        self.add_line(f"try")
        with self.scope():
            self.subtree(tree.nested_block)

        if tree.catch_block:
            self.catch_block(tree.catch_block, parent=parent)
        if tree.finally_block:
            self.finally_block(tree.finally_block, parent=parent)

    def throw_statement(self, tree, parent):
        """
        Compiles a throw statement
        """
        args = ""
        if len(tree.children) > 1:
            args = " "
            args += self.objects.entity(tree.child(1))
        self.add_line(f"throw{args}")

    def catch_block(self, tree, parent):
        """
        Compiles a catch block.
        """
        catch_stmt = tree.catch_statement
        catch_stmt = Tree("catch_statement", catch_stmt.children[1:])

        self.add_line(f"catch")
        with self.scope():
            self.subtree(tree.nested_block)

    def finally_block(self, tree, parent):
        """
        Compiles a finally block.
        """
        self.add_line(f"finally")
        with self.scope():
            self.subtree(tree.nested_block)

    def break_statement(self, tree, parent):
        self.add_line(f"break")

    def subtrees(self, *trees, parent=None):
        """
        Parses all subtrees.
        """
        for tree in trees:
            self.subtree(tree, parent=parent)

    def subtree(self, tree, parent=None):
        """
        Parses a subtree, checking whether it should be compiled directly
        or keep parsing for deeper trees.
        """
        allowed_nodes = [
            "service_block",
            "absolute_expression",
            "assignment",
            "if_block",
            "elseif_block",
            "else_block",
            "foreach_block",
            "function_block",
            "when_block",
            "try_block",
            "return_statement",
            "arguments",
            "call_expression",
            "imports",
            "while_block",
            "throw_statement",
            "break_statement",
            "mutation_block",
            "indented_chain",
        ]
        if tree.data in allowed_nodes:
            getattr(self, tree.data)(tree, parent)
        else:
            self.parse_tree(tree, parent=parent)

    def parse_tree(self, tree, parent=None):
        """
        Parses a tree looking for subtrees.
        """
        for item in tree.children:
            assert isinstance(item, Tree)
            self.subtree(item, parent=parent)

    def compile(self, tree, debug=False):
        """
        Compile an AST to JSON
        """
        self.buf = ""
        self.parse_tree(tree)
        return self.buf.strip()
