# -*- coding: utf-8 -*-
from pytest import fixture, mark

from storyscript.compiler import FakeTree, Preprocessor


@fixture
def fake_tree(patch):
    patch.object(Preprocessor, 'fake_tree')
    return Preprocessor.fake_tree


def test_preprocessor_fake_tree(patch):
    patch.init(FakeTree)
    result = Preprocessor.fake_tree('block')
    FakeTree.__init__.assert_called_with('block')
    assert isinstance(result, FakeTree)


def test_preprocessor_replace_expression(magic, tree):
    parent = magic()
    expression = magic()
    Preprocessor.replace_expression(tree, parent, expression)
    tree.add_assignment.assert_called_with(expression.service)
    assignment = tree.add_assignment().path.child()
    entity = parent.expression.multiplication.exponential.factor.entity
    entity.path.replace.assert_called_with(0, assignment)


def test_preprocessor_replace_expression_argument(magic, tree):
    parent = magic(expression=None)
    expression = magic()
    Preprocessor.replace_expression(tree, parent, expression)
    tree.add_assignment.assert_called_with(expression.service)
    assignment = tree.add_assignment().path.child()
    parent.entity.path.replace.assert_called_with(0, assignment)


def test_preprocessor_replace_in_entity(magic, tree, block, fake_tree):
    path_value = magic()
    Preprocessor.replace_in_entity(block, tree, path_value)
    fake_tree.assert_called_with(block)
    service = path_value.path.inline_expression.service
    fake_tree().add_assignment.assert_called_with(service)
    path_value.replace.assert_called_with(0, fake_tree().add_assignment().path)
    assert path_value.path.children[0].line == tree.line()


def test_preprocessor_service_arguments(patch, magic, tree, fake_tree):
    patch.object(Preprocessor, 'replace_expression')
    argument = magic()
    tree.find_data.return_value = [argument]
    Preprocessor.service_arguments('block', tree)
    fake_tree.assert_called_with('block')
    tree.find_data.assert_called_with('arguments')
    argument.node.assert_called_with('entity.path.inline_expression')
    args = (fake_tree(), argument, argument.node())
    Preprocessor.replace_expression.assert_called_with(*args)


def test_preprocessor_service_arguments_no_expression(patch, magic, tree):
    patch.many(Preprocessor, ['fake_tree', 'replace_expression'])
    argument = magic(inline_expression=None)
    tree.service_fragment.find_data.return_value = [argument]
    Preprocessor.service_arguments(magic(), tree)
    assert Preprocessor.replace_expression.call_count == 0


def test_preprocessor_assignment_expression(patch, magic, tree, fake_tree):
    patch.object(Preprocessor, 'replace_expression')
    block = magic()
    Preprocessor.assignment_expression(block, tree)
    fake_tree.assert_called_with(block)
    parent = block.rules.assignment.assignment_fragment
    args = (fake_tree(), parent, tree.inline_expression)
    Preprocessor.replace_expression.assert_called_with(*args)


def test_preprocessor_assignments(patch, magic, tree):
    """
    Ensures Preprocessor.assignments can process lines like
    a = alpine echo text:(random value)
    """
    patch.object(Preprocessor, 'service_arguments')
    assignment = magic()
    tree.find_data.return_value = [assignment]
    Preprocessor.assignments(tree)
    args = (tree, assignment.assignment_fragment.service)
    Preprocessor.service_arguments.assert_called_with(*args)


def test_preprocessor_assignments_to_expression(patch, magic, tree):
    """
    Ensures Preprocessor.assignments can process lines like
    a = (alpine echo message:'text')
    """
    patch.object(Preprocessor, 'assignment_expression')
    assignment = magic()
    assignment.assignment_fragment.service = None
    tree.find_data.return_value = [assignment]
    Preprocessor.assignments(tree)
    fragment = assignment.assignment_fragment
    factor = fragment.expression.multiplication.exponential.factor
    args = (tree, factor.entity.path)
    Preprocessor.assignment_expression.assert_called_with(*args)


def test_preprocessor_assignments_no_expression(patch, magic, tree):
    patch.object(Preprocessor, 'assignment_expression')
    assignment = magic()
    assignment.assignment_fragment.service = None
    fragment = assignment.assignment_fragment
    factor = fragment.expression.multiplication.exponential.factor
    factor.entity.path.inline_expression = None
    tree.find_data.return_value = [assignment]
    Preprocessor.assignments(tree)
    assert Preprocessor.assignment_expression.call_count == 0


def test_preprocessor_service(patch, magic, tree):
    patch.object(Preprocessor, 'service_arguments')
    Preprocessor.service(tree)
    tree.node.assert_called_with('service_block.service')
    Preprocessor.service_arguments.assert_called_with(tree, tree.node())


def test_preprocessor_service_no_service(patch, magic, tree):
    patch.object(Preprocessor, 'service_arguments')
    tree.node.return_value = None
    Preprocessor.service(tree)
    assert Preprocessor.service_arguments.call_count == 0


def test_preprocessor_merge_operands(magic, tree, fake_tree):
    """
    Ensures Preprocessor.merge_operands can merge operands
    """
    rhs = magic()
    Preprocessor.merge_operands('block', tree, rhs)
    fake_tree.assert_called_with('block')
    args = (tree.values, rhs.operator, rhs.child(1))
    Preprocessor.fake_tree().expression.assert_called_with(*args)
    fake_tree().add_assignment.assert_called_with(fake_tree().expression())
    tree.replace.assert_called_with(len(tree.children) - 1,
                                    fake_tree().add_assignment().path)


def test_preprocessor_merge_operands_lhs(magic, tree, fake_tree):
    """
    Ensures Preprocessor.merge_operands can deal with lhs having no values
    branch.
    """
    rhs = magic()
    tree.values = None
    Preprocessor.merge_operands('block', tree, rhs)
    args = (tree, rhs.operator, rhs.child(1))
    Preprocessor.fake_tree().expression.assert_called_with(*args)


def test_preprocessor_merge_operands_lhs_child(magic, tree, fake_tree):
    """
    Ensures Preprocessor.merge_operands can deal with lhs having one child
    """
    rhs = magic()
    tree.children = ['one']
    Preprocessor.merge_operands('block', tree, rhs)
    fake_tree.assert_called_with('block')
    args = (tree.values, rhs.operator, rhs.child(1))
    Preprocessor.fake_tree().expression.assert_called_with(*args)
    fake_tree().add_assignment.assert_called_with(fake_tree().expression())
    tree.replace.assert_called_with(0,
                                    fake_tree().add_assignment().path.child())
    tree.rename.assert_called_with('path')


@mark.parametrize('operator', ['*', '/', '%', '^'])
def test_preprocessor_expression_stack(patch, magic, tree, operator):
    """
    Ensures expression_stack can replace the expression tree
    """
    patch.object(Preprocessor, 'merge_operands')
    child = magic()
    child.operator.child.return_value = operator
    tree.children = [magic(), child]
    Preprocessor.expression_stack('block', tree)
    args = ('block', tree.children[0], child)
    Preprocessor.merge_operands.assert_called_with(*args)
    assert tree.children == [tree.children[0]]


def test_preprocessor_expression(patch, magic, tree):
    patch.object(Preprocessor, 'expression_stack')
    expression = magic(children=[1, 2, 3])
    tree.find_data.return_value = [expression]
    Preprocessor.expression(tree)
    tree.find_data.assert_called_with('expression')
    Preprocessor.expression_stack.assert_called_with(tree, expression)


def test_preprocessor_flow_statement(patch, magic, tree):
    """
    Ensures flow_statement replaces inline expressions inside if statements
    """
    patch.object(Preprocessor, 'replace_in_entity')
    statement = magic()
    statement.child.return_value = None
    tree.find_data.return_value = [statement]
    Preprocessor.flow_statement('statement', tree)
    tree.find_data.assert_called_with('statement')
    statement.node.assert_called_with('entity.path.inline_expression')
    args = (tree, statement, statement.entity)
    Preprocessor.replace_in_entity.assert_called_with(*args)


def test_preprocessor_flow_statement_rhs(patch, magic, tree):
    """
    Ensures flow_statement replaces inline expressions on the right hand-side
    of statements
    """
    patch.object(Preprocessor, 'replace_in_entity')
    statement = magic()
    statement.node.return_value = None
    tree.find_data.return_value = [statement]
    Preprocessor.flow_statement('statement', tree)
    args = (tree, statement, statement.child())
    Preprocessor.replace_in_entity.assert_called_with(*args)


def test_preprocessor_flow_statement_no_expression(patch, magic, tree):
    """
    Ensures flow_statement ignores statements without inline expressions
    """
    patch.object(Preprocessor, 'replace_in_entity')
    statement = magic()
    statement.child.return_value = None
    statement.node.return_value = None
    tree.find_data.return_value = [statement]
    Preprocessor.flow_statement('statement', tree)
    assert Preprocessor.replace_in_entity.call_count == 0


def test_preprocessor_process(patch, magic, tree, block):
    patch.many(Preprocessor, ['assignments', 'service', 'expression',
                              'flow_statement'])
    tree.find_data.return_value = [block]
    result = Preprocessor.process(tree)
    Preprocessor.assignments.assert_called_with(block)
    Preprocessor.service.assert_called_with(block)
    Preprocessor.expression.assert_called_with(block)
    Preprocessor.flow_statement.assert_called_with('elseif_statement', block)
    assert result == tree
