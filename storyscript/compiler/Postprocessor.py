# -*- coding: utf-8 -*-

from ..exceptions import CompilerError


class Postprocessor:
    """
    Checks the return type of functions.
    """

    @classmethod
    def has_return(cls, tree):
        if tree.rules and tree.rules.return_statement:
            return True

        if tree.block and len(tree.block.children) == 1 and \
                tree.block.rules.return_statement:
            return True

        if tree.if_block:
            # an if requires an else and all statements to have a return
            if tree.if_block.else_block:
                for block in tree.if_block.children[1:]:
                    if not cls.has_return(block):
                        return False
                return True
            return False

        nested_block = tree.nested_block or tree.child(0).nested_block
        if nested_block:
            for block in nested_block.children:
                if cls.has_return(block):
                    return True
        return False

    @classmethod
    def function_block(cls, tree):
        if tree.function_statement.function_output:
            if not cls.has_return(tree):
                t = tree.function_statement.function_output
                raise CompilerError('return_required', tree=t)

    @classmethod
    def process(cls, tree):
        for block in tree.find_data('block'):
            if block.function_block is not None:
                cls.function_block(block.function_block)
        return tree
