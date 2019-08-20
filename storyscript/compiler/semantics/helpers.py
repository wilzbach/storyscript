from storyscript.compiler.semantics.ExpressionResolver import \
    SymbolExpressionVisitor
from storyscript.compiler.semantics.types.Types import AnyType


def do_type_cast_check(tree, source_type, target_type,
                       fn_type, fn_name, arg_name, arg_node):
    """
    Checks whether an implicit cast from source_type to
    target type is allowed. If it is possible the implicit cast
    is performed on AST subtree.

    Args:
        tree: AST subtree which holds the args
            source_type: instance of one of the suitable type class
            for argument
        target_type: instance of one of the suitable type class
            for parameter
        fn_type: string specifying if the args are for a function,
            mutation or a service
        fn_name: string specifying name of the function,
            or a service
        arg_name: string specifying name of the argument
        arg_node: Tree node pointing to the actual argument node
            inside the tree in question
    """
    type_cast_result = target_type.can_be_assigned(source_type)
    tree.expect(type_cast_result or source_type == AnyType.instance(),
                'param_arg_type_mismatch',
                fn_type=fn_type,
                name=fn_name,
                arg_name=arg_name,
                target=target_type,
                source=source_type)
    if target_type != AnyType.instance() and type_cast_result != source_type:
        # We don't emit a type cast if:
        # * Target type is AnyType (AnyType can represent anything)
        # * Target and Source type are the same.
        arg_node.children[1] = SymbolExpressionVisitor.\
            type_cast_expression(arg_node.children[1], target_type)
