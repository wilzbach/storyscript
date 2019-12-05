# -*- coding: utf-8 -*-
from storyscript.compiler.lowering.utils import unicode_escape
from storyscript.exceptions import internal_assert
from storyscript.parser import Tree

from .PrettyExpressionVisitor import PrettyExpressionVisitor


class Objects:
    def __init__(self, visitor):
        self.expr_visitor = PrettyExpressionVisitor(visitor=self)
        self.visitor = visitor

    def names(self, tree):
        """
        Extracts names from a path tree.
        """
        names = [tree.child(0).value]
        names.extend(self.fragments(tree.children[1:]))
        return names

    def fragments(self, fragments):
        """
        Extracts names from a path tree fragments.
        """
        names = []
        for fragment in fragments:
            assert fragment.data == "path_fragment"
            child = fragment.child(0)
            if isinstance(child, Tree):
                if child.data == "expression":
                    value = f"[{self.expression(child)}]"
                else:
                    assert child.data == "range"
                    value = f"[{self.range(child)}]"
            else:
                assert child.type == "NAME"
                value = f".{child.value}"
            names.append(value)
        return names

    def path(self, tree):
        child = tree.child(0)
        if isinstance(child, Tree) and child.data == "inline_expression":
            name = self.visitor.inline_expression(child, tree)
        else:
            name = tree.child(0).value

        paths = self.fragments(tree.children[1:])
        return "".join([name, *paths])

    def mutation(self, tree):
        expr = self.expression(tree.expression)
        fragment = self.mutation_fragment(tree.mutation_fragment)
        return f"{expr}.{fragment}"

    def mutation_fragment(self, tree):
        """
        Compiles a mutation object, either from a mutation or a
        service_fragment tree.
        """
        mutation = tree.child(0).value
        args = ""
        if tree.arguments:
            args = self.arguments(tree)
        assert not tree.command
        return f"{mutation}({args})"

    @staticmethod
    def number(tree):
        """
        Compiles a number tree
        """
        token = tree.child(0)
        if token.value[0] == "+":
            token.value = token.value[1:]
        if token.type == "FLOAT":
            return token.value
        return token.value

    def string(self, tree):
        """
        Compiles a string tree.
        """
        value = unicode_escape(tree, tree.child(0).value)
        return f'"{value}"'

    @staticmethod
    def boolean(tree):
        if tree.child(0).value == "true":
            return "true"
        return "false"

    def range_child(self, tree):
        """
        Compiles an individual range token.
        It can be either a number or a path.
        """
        if tree.data == "number":
            return self.number(tree)
        assert tree.data == "path"
        return self.path(tree)

    def range(self, tree):
        """
        Compiles a range tree.
        """
        val = self.range_child(tree.child(0).child(0))
        start = ""
        end = ""
        if tree.range_start:
            start = val
        elif tree.range_end:
            end = val
        else:
            assert tree.range_start_end
            start = val
            end = self.range_child(tree.child(0).child(1))
        return f"{start}:{end}"

    def list(self, tree):
        items = []
        for value in tree.children:
            if isinstance(value, Tree):
                items.append(self.base_expression(value))
        sep = ", "
        return f"[{sep.join(items)}]"

    def time(self, tree):
        assert tree.data == "time"
        return tree.child(0).value

    def map(self, tree):
        items = []
        for item in tree.children:
            child = item.child(0)
            if child.data == "string":
                key = self.string(child)
            elif child.data == "number":
                key = self.number(child)
            else:
                internal_assert(child.data == "path")
                key = self.path(child)
            value = self.base_expression(item.child(1))
            items.append(f"{key}: {value}")

        sep = ", "
        return f"{{{sep.join(items)}}}"

    def regular_expression(self, tree):
        """
        Compiles a regexp object from a regular_expression tree
        """
        regexp = tree.child(0).value
        assert len(tree.children) == 1
        return regexp

    @classmethod
    def types(cls, tree):
        assert tree.data == "types"
        c = tree.first_child()
        if c.data == "map_type":
            key = cls.base_type(c.child(0))
            value = cls.types(c.child(1))
            return f"Map[{key}, {value}]"
        elif c.data == "list_type":
            inner = cls.types(c.child(0))
            return f"List[{inner}]"
        else:
            return cls.base_type(c)

    @staticmethod
    def base_type(tree):
        return tree.child(0).value

    def entity(self, tree):
        return self.values(tree.child(0))

    def values(self, tree):
        """
        Parses a values subtree
        """
        subtree = tree.child(0)
        if hasattr(subtree, "data"):
            if subtree.data == "string":
                return self.string(subtree)
            elif subtree.data == "boolean":
                return self.boolean(subtree)
            elif subtree.data == "list":
                return self.list(subtree)
            elif subtree.data == "number":
                return self.number(subtree)
            elif subtree.data == "time":
                return self.time(subtree)
            elif subtree.data == "map":
                return self.map(subtree)
            elif subtree.data == "regular_expression":
                return self.regular_expression(subtree)
            elif subtree.data == "types":
                return self.types(subtree)
            elif subtree.data == "null":
                return "null"

        return self.path(tree)

    def argument(self, tree):
        """
        Compiles an argument tree to the corresponding object.
        """
        name = tree.child(0).value
        value = self.expression(tree.child(1))
        return f"{name}:{value}"

    def arguments(self, tree):
        """
        Parses a group of arguments rules
        """
        arguments = []
        for argument in tree.find_data("arguments"):
            arguments.append(self.argument(argument))

        sep = " "
        return f"{sep.join(arguments)}"

    def typed_argument(self, tree):
        name = tree.child(0).value
        value = self.values(Tree("anon", [tree.child(1)]))
        return f"{name}:{value}"

    def function_arguments(self, tree):
        arguments = []
        for argument in tree.find_data("typed_argument"):
            arguments.append(self.typed_argument(argument))

        sep = " "
        return f"{sep.join(arguments)}"

    def output(self, tree):
        assert tree.data == "output"
        outputs = [c.value for c in tree.children]
        return ", ".join(outputs)

    def expression(self, tree):
        """
        Compiles an expression object with the given tree.
        """
        assert tree.data == "expression"
        return self.expr_visitor.expression(tree)

    def base_expression(self, tree):
        """
        Compiles an soon to be expression object with the given tree.
        """
        child = tree.child(0)
        assert child.data == "expression"
        return self.expression(child)
