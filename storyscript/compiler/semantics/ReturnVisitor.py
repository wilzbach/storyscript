# -*- coding: utf-8 -*-

from storyscript.exceptions import CompilerError

from .Visitors import SelectiveVisitor


class ReturnVisitor(SelectiveVisitor):
    """
    Checks the return type of functions.
    """

    def has_return(self, tree):
        if tree.rules and tree.rules.return_statement:
            return True

        if tree.block and len(tree.block.children) == 1 and \
                tree.block.rules.return_statement:
            return True

        if tree.if_block:
            # an if requires an else and all statements to have a return
            if tree.if_block.else_block:
                for block in tree.if_block.children[1:]:
                    if not self.has_return(block):
                        return False
                return True
            return False

        nested_block = tree.nested_block or tree.child(0).nested_block
        if nested_block:
            for block in nested_block.children:
                if self.has_return(block):
                    return True
        return False

    def function_block(self, tree):
        if tree.function_statement.function_output:
            if not self.has_return(tree):
                t = tree.function_statement.function_output
                raise CompilerError('return_required', tree=t)

    def block(self, tree):
        self.visit_children(tree)

    def start(self, tree):
        self.visit_children(tree)
