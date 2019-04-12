# -*- coding: utf-8 -*-

from storyscript.exceptions import CompilerError

from .ExpressionResolver import ExpressionResolver
from .SymbolResolver import SymbolResolver
from .symbols.SymbolTypes import NoneType


class ReturnVisitor:
    """
    Checks the return type of functions.
    """
    def __init__(self, return_type, function_table):
        self.return_type = return_type
        self.symbol_resolver = SymbolResolver(scope=None)
        self.resolver = ExpressionResolver(
            symbol_resolver=self.symbol_resolver,
            function_table=function_table,
        )

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

    def return_statement(self, tree, scope):
        assert tree.data == 'return_statement'
        self.symbol_resolver.update_scope(scope)
        obj = tree.base_expression
        if obj is None:
            return NoneType.instance(), tree
        return self.resolver.base_expression(tree.base_expression), obj

    def function_block(self, tree, scope):
        output = tree.function_statement.function_output
        if not output:
            return self.check_none(tree, scope)

        output = output.types.child(0).type
        if output == 'VOID_TYPE':
            return self.check_none(tree, scope)

        if not self.has_return(tree):
            t = tree.function_statement.function_output
            raise CompilerError('return_required', tree=t)
        for ret in tree.find_data('return_statement'):
            ret_type, obj = self.return_statement(ret, scope)
            obj.expect(
                self.return_type.can_be_assigned(ret_type),
                'return_type_differs',
                target=self.return_type,
                source=ret_type
            )

    def check_none(self, tree, scope):
        # function has no return output, so only `return` may be used
        for ret in tree.find_data('return_statement'):
            ret_type, obj = self.return_statement(ret, scope)
            obj.expect(
                ret_type == NoneType.instance(),
                'function_without_output_return',
            )

    @classmethod
    def check(cls, tree, scope, return_type, function_table):
        rv = ReturnVisitor(return_type, function_table)
        rv.function_block(tree, scope)
