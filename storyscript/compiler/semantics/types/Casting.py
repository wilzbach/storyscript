from storyscript.compiler.semantics.ExpressionResolver import (
    SymbolExpressionVisitor,
)
from storyscript.compiler.semantics.types.Types import AnyType


def implicit_type_cast(
    arg_node, source_type, target_type, fn_type, fn_name, arg_name
):
    """
    Checks whether an implicit cast from source_type to
    target type is allowed. If it is possible the implicit cast
    is performed on AST subtree.

    Args:
        arg_node: Tree node pointing to the actual argument node
            inside the tree in question.
        target_type: instance of one of the suitable type class
            for parameter.
        fn_type: string specifying if the args are for a function,
            mutation or a service.
        fn_name: string specifying name of the function,
            or a service.
        arg_name: string specifying name of the argument.
    """
    type_cast_result = target_type.can_be_assigned(source_type)
    arg_node.expect(
        type_cast_result or source_type == AnyType.instance(),
        "param_arg_type_mismatch",
        fn_type=fn_type,
        name=fn_name,
        arg_name=arg_name,
        target=target_type,
        source=source_type,
    )
    if target_type != AnyType.instance() and type_cast_result != source_type:
        # We don't emit a type cast if:
        # * Target type is AnyType (AnyType can represent anything)
        # * Target and Source type are the same.
        arg_node.children[1] = SymbolExpressionVisitor.type_cast_expression(
            arg_node.children[1], target_type
        )
