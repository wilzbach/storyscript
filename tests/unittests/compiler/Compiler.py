# -*- coding: utf-8 -*-
from lark.lexer import Token

from pytest import fixture, mark, raises

from storyscript.Version import version
from storyscript.compiler import Compiler, Lines, Objects, Preprocessor
from storyscript.exceptions import CompilerError, StorySyntaxError
from storyscript.parser import Tree


@fixture
def lines(magic):
    return magic()


@fixture
def compiler(patch, lines):
    patch.init(Lines)
    compiler = Compiler()
    compiler.lines = lines
    return compiler


def get_entity(obj):
    """
    returns the entity for an expression
    """
    return obj.or_expression.and_expression.cmp_expression.arith_expression. \
        mul_expression.unary_expression.pow_expression.primary_expression. \
        entity


def test_compiler_init(patch):
    patch.init(Lines)
    compiler = Compiler()
    assert isinstance(compiler.lines, Lines)


def test_compiler_output(tree):
    tree.children = [Token('token', 'output')]
    result = Compiler.output(tree)
    assert result == ['output']


def test_compiler_output_none():
    assert Compiler.output(None) == []


def test_compiler_extract_values(patch, tree):
    patch.object(Objects, 'entity')
    tree.expression = None
    result = Compiler.extract_values(tree)
    tree.child.assert_called_with(1)
    Objects.entity.assert_called_with(tree.child())
    assert result == [Objects.entity()]


def test_compiler_extract_values_expression(patch, tree):
    patch.object(Objects, 'expression')
    tree.expression.mutation = None
    result = Compiler.extract_values(tree)
    Objects.expression.assert_called_with(tree.expression)
    assert result == [Objects.expression()]


def test_compiler_extract_values_mutation(patch, tree):
    patch.many(Objects, ['values', 'mutation'])
    result = Compiler.extract_values(tree)
    Objects.values.assert_called_with(tree.expression.values)
    Objects.mutation.assert_called_with(tree.expression.mutation)
    assert result == [Objects.values(), Objects.mutation()]


def test_compiler_chained_mutations(patch, magic, tree):
    patch.object(Objects, 'mutation')
    mutation = magic()
    tree.find_data.return_value = [mutation]
    result = Compiler.chained_mutations(tree)
    Objects.mutation.assert_called_with(mutation.mutation_fragment)
    assert result == [Objects.mutation()]


def test_compiler_function_output(patch, tree):
    patch.object(Compiler, 'output')
    result = Compiler.function_output(tree)
    tree.node.assert_called_with('function_output.types')
    assert result == Compiler.output()


def test_compiler_imports(patch, compiler, lines, tree):
    compiler.lines.modules = {}
    compiler.imports(tree, '1')
    module = tree.child(1).value
    assert lines.modules[module] == tree.string.child(0).value[1:-1]


def test_compiler_expression(patch, compiler, lines, tree):
    """
    Ensures that expressions are compiled correctly
    """
    patch.object(Objects, 'expression')
    compiler.expression(tree, '1')
    Objects.expression.assert_called_with(tree.expression)
    args = [Objects.expression()]
    lines.append.assert_called_with('expression', tree.line(), args=args,
                                    parent='1')


def test_compiler_unary_expression(patch, compiler, lines, tree):
    patch.object(Lines, 'append')
    patch.object(Objects, 'entity')
    method = 'set.method'
    parent = '.parent.'
    compiler.unary_expression(tree, parent, method)
    args = [Objects.entity(tree.expression.multiplication.exponential.
                           factor.entity)]
    lines.append.assert_called_with(method, tree.line(), args=args,
                                    parent=parent)


def test_compiler_unary_expression_name(patch, compiler, lines, tree):
    patch.object(Lines, 'append')
    patch.object(Objects, 'entity')
    method = 'set.method'
    parent = '.parent.'
    name = '.name.'
    line = '.line.'
    compiler.unary_expression(tree, parent, method, name=name, line=line)
    args = [Objects.entity(tree.expression.multiplication.exponential.
                           factor.entity)]
    lines.append.assert_called_with(method, line, args=args, parent=parent,
                                    name=name)


def test_compiler_absolute_expression(patch, compiler, lines, tree):
    patch.object(Compiler, 'expression')
    tree.expression.is_unary_leaf.return_value = False
    compiler.absolute_expression(tree, '1')
    Compiler.expression.assert_called_with(tree, '1')


def test_compiler_absolute_expression_unary(patch, compiler, lines, tree):
    patch.object(Compiler, 'unary_expression')
    tree.expression.is_unary_leaf.return_value = True
    compiler.absolute_expression(tree, '1')
    Compiler.unary_expression.assert_called_with(tree.expression, '1',
                                                 method='expression')


def test_compiler_assignment(patch, compiler, lines, tree):
    """
    Ensures a line like "x = value" is compiled correctly
    """
    patch.many(Objects, ['names', 'entity'])
    tree.assignment_fragment.service = None
    tree.assignment_fragment.mutation = None
    compiler.assignment(tree, '1')
    Objects.names.assert_called_with(tree.path)
    fragment = tree.assignment_fragment
    entity = get_entity(fragment.expression)
    Objects.entity.assert_called_with(entity)
    kwargs = {'name': Objects.names(), 'args': [Objects.entity()],
              'parent': '1'}
    lines.append.assert_called_with('set', tree.line(), **kwargs)


def test_compiler_assignment_service(patch, compiler, lines, tree):
    patch.object(Objects, 'names')
    patch.object(Compiler, 'service')
    lines.is_variable_defined.return_value = False
    compiler.assignment(tree, '1')
    service = tree.assignment_fragment.service
    Compiler.service.assert_called_with(service, None, '1')
    lines.set_name.assert_called_with(Objects.names())


def test_compiler_assignment_mutation(patch, compiler, lines, tree):
    """
    Ensures that assignments to mutations are compiled correctly.
    """
    patch.object(Objects, 'names', return_value='name')
    patch.object(Compiler, 'mutation_block')
    tree.assignment_fragment.service = None
    compiler.assignment(tree, '1')
    Compiler.mutation_block.assert_called_with(tree.assignment_fragment, '1')
    lines.set_name.assert_called_with('name')


def test_compiler_assignment_expression(patch, compiler, lines, tree):
    patch.object(Objects, 'names', return_value='name')
    patch.object(Compiler, 'expression')
    tree.assignment_fragment.service = None
    tree.assignment_fragment.mutation = None
    tree.assignment_fragment.expression.is_unary_leaf.return_value = False
    compiler.assignment(tree, '1')
    fragment = tree.assignment_fragment
    Compiler.expression.assert_called_with(fragment, '1')
    lines.set_name.assert_called_with('name')


def test_compiler_arguments(patch, compiler, lines, tree):
    patch.object(Objects, 'arguments')
    lines.last.return_value = '1'
    lines.lines = {'1': {'method': 'execute', 'args': ['args']}}
    compiler.arguments(tree, '0')
    Objects.arguments.assert_called_with(tree)
    assert lines.lines['1']['args'] == ['args'] + Objects.arguments()


def test_compiler_arguments_fist_line(patch, compiler, lines, tree):
    """
    Ensures that if this is the first line, an error is raised.
    """
    patch.init(StorySyntaxError)
    lines.last.return_value = None
    with raises(StorySyntaxError):
        compiler.arguments(tree, '0')
    error = 'arguments_noservice'
    StorySyntaxError.__init__.assert_called_with(error, tree=tree)


def test_compiler_arguments_not_execute(patch, compiler, lines, tree):
    """
    Ensures that if the previous line is not an execute, an error is raised.
    """
    patch.init(StorySyntaxError)
    patch.object(Objects, 'arguments')
    lines.last.return_value = '1'
    lines.lines = {'1': {'method': 'whatever'}}
    with raises(StorySyntaxError):
        compiler.arguments(tree, '0')
    error = 'arguments_noservice'
    StorySyntaxError.__init__.assert_called_with(error, tree=tree)


def test_compiler_service(patch, compiler, lines, tree):
    """
    Ensures that service trees can be compiled
    """
    patch.object(Objects, 'arguments')
    patch.object(Compiler, 'output')
    tree.node.return_value = None
    compiler.service(tree, None, 'parent')
    line = tree.line()
    service = tree.path.extract_path()
    command = tree.service_fragment.command.child()
    Objects.arguments.assert_called_with(tree.service_fragment)
    Compiler.output.assert_called_with(tree.service_fragment.output)
    lines.execute.assert_called_with(line, service, command,
                                     Objects.arguments(), Compiler.output(),
                                     None, 'parent')


def test_compiler_service_command(patch, compiler, lines, tree):
    patch.object(Objects, 'arguments')
    patch.object(Compiler, 'output')
    compiler.service(tree, None, 'parent')
    line = tree.line()
    service = tree.path.extract_path()
    command = tree.service_fragment.command.child()
    lines.set_scope.assert_called_with(line, 'parent', Compiler.output())
    lines.execute.assert_called_with(line, service, command,
                                     Objects.arguments(), Compiler.output(),
                                     None, 'parent')


def test_compiler_service_nested_block(patch, magic, compiler, lines, tree):
    patch.object(Objects, 'arguments')
    patch.object(Compiler, 'output')
    tree.node.return_value = None
    nested_block = magic()
    compiler.service(tree, nested_block, 'parent')
    line = tree.line()
    service = tree.path.extract_path()
    command = tree.service_fragment.command.child()
    lines.execute.assert_called_with(line, service, command,
                                     Objects.arguments(), Compiler.output(),
                                     nested_block.line(), 'parent')


def test_compiler_service_no_output(patch, compiler, lines, tree):
    patch.object(Objects, 'arguments')
    patch.object(Compiler, 'output')
    Compiler.output.return_value = None
    compiler.service(tree, None, 'parent')
    assert lines.set_output.call_count == 0


def test_compiler_service_expressions(patch, compiler, lines, tree):
    """
    Ensures service trees that are infact mutations on paths are compiled
    correctly
    """
    patch.object(Objects, 'names', return_value='x')
    patch.object(Compiler, 'mutation_block')
    lines.variables = ['x']
    compiler.service(tree, None, 'parent')
    Objects.names.assert_called_with(tree.path)
    Compiler.mutation_block.assert_called_with(tree, 'parent')


def test_compiler_service_syntax_error(patch, compiler, lines, tree):
    patch.object(Objects, 'arguments')
    patch.object(Compiler, 'output')
    patch.object(StorySyntaxError, 'tree_position')
    lines.execute.side_effect = StorySyntaxError('error')
    with raises(StorySyntaxError):
        compiler.service(tree, None, 'parent')
    StorySyntaxError.tree_position.assert_called_with(tree)


def test_compiler_when(patch, compiler, lines, tree):
    patch.object(Compiler, 'service')
    lines.lines = {'1': {}}
    lines.last.return_value = '1'
    compiler.when(tree, 'nested_block', '1')
    Compiler.service.assert_called_with(tree.service, 'nested_block', '1')
    assert lines.lines['1']['method'] == 'when'


def test_compiler_when_path(patch, compiler, lines, tree):
    patch.object(Objects, 'path')
    patch.object(Compiler, 'output')
    tree.service = None
    compiler.when(tree, 'nested_block', '1')
    Objects.path.assert_called_with(tree.path)
    Compiler.output.assert_called_with(tree.output)
    lines.append.assert_called_with('when', tree.line(), args=[Objects.path()],
                                    output=Compiler.output(), parent='1')


def test_compiler_return_statement(patch, compiler, lines, tree):
    """
    Ensures Compiler.return_statement can compile return statements.
    """
    tree.expression = None
    compiler.return_statement(tree, '1')
    line = tree.line()
    kwargs = {'args': None, 'parent': '1'}
    lines.append.assert_called_with('return', line, **kwargs)


def test_compiler_return_statement_entity(patch, compiler, lines, tree):
    """
    Ensures Compiler.return_statement can compile return statements that return
    entities.
    """
    patch.object(Objects, 'expression')
    compiler.return_statement(tree, '1')
    line = tree.line()
    Objects.expression.assert_called_with(tree.expression)
    kwargs = {'args': [Objects.expression()], 'parent': '1'}
    lines.append.assert_called_with('return', line, **kwargs)


def test_compiler_return_statement_error(patch, compiler, tree):
    """
    Ensures Compiler.return_statement raises CompilerError when the return
    is outside a function.
    """
    patch.init(CompilerError)
    with raises(CompilerError):
        compiler.return_statement(tree, None)
    CompilerError.__init__.assert_called_with('return_outside', tree=tree)


def test_compiler_if_block(patch, compiler, lines, tree):
    patch.object(Objects, 'assertion')
    patch.object(Compiler, 'subtree')
    tree.elseif_block = None
    tree.else_block = None
    compiler.if_block(tree, '1')
    Objects.assertion.assert_called_with(tree.if_statement)
    nested_block = tree.nested_block
    args = Objects.assertion()
    lines.set_scope.assert_called_with(tree.line(), '1')
    lines.append.assert_called_with('if', tree.line(), args=args,
                                    enter=nested_block.line(), parent='1')
    compiler.subtree.assert_called_with(nested_block, parent=tree.line())


def test_compiler_if_block_with_elseif(patch, compiler, tree):
    patch.object(Objects, 'assertion')
    patch.many(Compiler, ['subtree', 'subtrees'])
    tree.else_block = None
    tree.extract.return_value = ['one']
    compiler.if_block(tree, '1')
    tree.extract.assert_called_with('elseif_block')
    compiler.subtrees.assert_called_with('one', parent='1')


def test_compiler_if_block_with_else(patch, compiler, tree):
    patch.object(Objects, 'assertion')
    patch.many(Compiler, ['subtree', 'subtrees'])
    tree.extract.return_value = []
    compiler.if_block(tree, '1')
    compiler.subtrees.assert_called_with(tree.else_block, parent='1')


def test_compiler_elseif_block(patch, compiler, lines, tree):
    patch.object(Objects, 'assertion')
    patch.object(Compiler, 'subtree')
    compiler.elseif_block(tree, '1')
    lines.set_exit.assert_called_with(tree.line())
    Objects.assertion.assert_called_with(tree.elseif_statement)
    args = Objects.assertion()
    lines.set_scope.assert_called_with(tree.line(), '1')
    lines.append.assert_called_with('elif', tree.line(), args=args,
                                    enter=tree.nested_block.line(),
                                    parent='1')
    compiler.subtree.assert_called_with(tree.nested_block, parent=tree.line())


def test_compiler_else_block(patch, compiler, lines, tree):
    patch.object(Compiler, 'subtree')
    compiler.else_block(tree, '1')
    lines.set_exit.assert_called_with(tree.line())
    lines.set_scope.assert_called_with(tree.line(), '1')
    lines.append.assert_called_with('else', tree.line(), parent='1',
                                    enter=tree.nested_block.line())
    compiler.subtree.assert_called_with(tree.nested_block, parent=tree.line())


def test_compiler_foreach_block(patch, compiler, lines, tree):
    patch.init(Tree)
    patch.object(Objects, 'entity')
    patch.many(Compiler, ['subtree', 'output'])
    compiler.foreach_block(tree, '1')
    assert Objects.entity.call_count == 1
    compiler.output.assert_called_with(tree.foreach_statement.output)
    args = [Objects.entity()]
    lines.set_scope.assert_called_with(tree.line(), '1', Compiler.output())
    lines.append.assert_called_with('for', tree.line(), args=args,
                                    enter=tree.nested_block.line(),
                                    output=Compiler.output(), parent='1')
    compiler.subtree.assert_called_with(tree.nested_block, parent=tree.line())


def test_compiler_while_block(patch, compiler, lines, tree):
    patch.init(Tree)
    patch.object(Objects, 'expression')
    patch.many(Compiler, ['subtree'])
    compiler.while_block(tree, '1')
    args = [Objects.expression()]
    lines.set_scope.assert_called_with(tree.line(), '1')
    lines.append.assert_called_with('while', tree.line(), args=args,
                                    enter=tree.nested_block.line(),
                                    parent='1')
    compiler.subtree.assert_called_with(tree.nested_block, parent=tree.line())


def test_compiler_function_block(patch, compiler, lines, tree):
    patch.object(Objects, 'function_arguments')
    patch.many(Compiler, ['subtree', 'function_output'])
    compiler.function_block(tree, '1')
    statement = tree.function_statement
    Objects.function_arguments.assert_called_with(statement)
    compiler.function_output.assert_called_with(statement)
    lines.append.assert_called_with('function', tree.line(),
                                    function=statement.child().value,
                                    args=Objects.function_arguments(),
                                    output=compiler.function_output(),
                                    enter=tree.nested_block.line(),
                                    parent='1')
    compiler.subtree.assert_called_with(tree.nested_block, parent=tree.line())


def test_compiler_function_block_redeclared(patch, compiler, lines, tree):
    patch.object(Objects, 'function_arguments')
    patch.many(Compiler, ['subtree', 'function_output'])
    compiler.lines.functions = {'.function.': '0'}
    statement = tree.function_statement
    statement.child(1).value = '.function.'
    with raises(CompilerError) as e:
        compiler.function_block(tree, '1')

    e.value.extra.function_name = '.function.'
    e.value.extra.previous_line = '0'
    e.value.extra.error = 'function_already_declared'


def test_compiler_raise_statement(patch, compiler, lines, tree):
    tree.children = [Token('RAISE', 'raise')]
    compiler.raise_statement(tree, '1')
    lines.append.assert_called_with('raise', tree.line(), args=[],
                                    parent='1')


def test_compiler_raise_name_statement(patch, compiler, lines, tree):
    patch.object(Objects, 'entity')
    tree.children = [Token('RAISE', 'raise'), Token('NAME', 'error')]
    compiler.raise_statement(tree, '1')
    args = [Objects.entity()]
    lines.append.assert_called_with('raise', tree.line(), args=args,
                                    parent='1')


def test_compiler_mutation_block(patch, compiler, lines, tree):
    patch.many(Objects, ['entity', 'mutation'])
    patch.object(Compiler, 'chained_mutations', return_value=['chained'])
    tree.path = None
    tree.nested_block = None
    compiler.mutation_block(tree, None)
    Objects.entity.assert_called_with(tree.mutation.entity)
    Objects.mutation.assert_called_with(tree.mutation.mutation_fragment)
    Compiler.chained_mutations.assert_called_with(tree.mutation)
    args = [Objects.entity(), Objects.mutation(), 'chained']
    kwargs = {'args': args, 'parent': None}
    lines.append.assert_called_with('mutation', tree.line(), **kwargs)


def test_compiler_mutation_block_nested(patch, compiler, lines, tree):
    patch.many(Objects, ['entity', 'mutation'])
    patch.object(Compiler, 'chained_mutations', return_value=['chained'])
    tree.path = None
    compiler.mutation_block(tree, None)
    Compiler.chained_mutations.assert_called_with(tree.nested_block)
    args = [Objects.entity(), Objects.mutation(), 'chained', 'chained']
    kwargs = {'args': args, 'parent': None}
    lines.append.assert_called_with('mutation', tree.line(), **kwargs)


def test_compiler_mutation_block_from_service(patch, compiler, lines, tree):
    patch.many(Objects, ['path', 'mutation'])
    patch.object(Compiler, 'chained_mutations', return_value=['chained'])
    tree.nested_block = None
    compiler.mutation_block(tree, None)
    Objects.path.assert_called_with(tree.path)
    Objects.mutation.assert_called_with(tree.service_fragment)
    Compiler.chained_mutations.assert_called_with(tree)
    args = [Objects.path(), Objects.mutation(), 'chained']
    kwargs = {'args': args, 'parent': None}
    lines.append.assert_called_with('mutation', tree.line(), **kwargs)


def test_compiler_indented_chain(patch, compiler, lines, tree):
    patch.object(Compiler, 'chained_mutations')
    lines.last.return_value = '1'
    lines.lines = {'1': {'method': 'mutation', 'args': ['args']}}
    compiler.indented_chain(tree, '0')
    Compiler.chained_mutations.assert_called_with(tree)
    assert lines.lines['1']['args'] == ['args'] + Compiler.chained_mutations()


def test_compiler_indented_chain_first_line(patch, compiler, lines, tree):
    """
    Ensures that if this is the first line, an error is raised.
    """
    patch.init(StorySyntaxError)
    lines.last.return_value = None
    with raises(StorySyntaxError):
        compiler.indented_chain(tree, '0')
    error = 'arguments_nomutation'
    StorySyntaxError.__init__.assert_called_with(error, tree=tree)


def test_compiler_indented_chain_not_mutation(patch, compiler, lines, tree):
    """
    Ensures that if the previous line is not a mutation, an error is raised.
    """
    patch.init(StorySyntaxError)
    patch.object(Compiler, 'chained_mutations')
    lines.last.return_value = '1'
    lines.lines = {'1': {'method': 'whatever'}}
    with raises(StorySyntaxError):
        compiler.indented_chain(tree, '0')
    error = 'arguments_nomutation'
    StorySyntaxError.__init__.assert_called_with(error, tree=tree)


def test_compiler_service_block(patch, compiler, tree):
    patch.object(Compiler, 'service')
    tree.node.return_value = None
    compiler.service_block(tree, '1')
    Compiler.service.assert_called_with(tree.service, tree.nested_block, '1')


def test_compiler_service_block_nested_block(patch, compiler, tree):
    patch.many(Compiler, ['subtree', 'service'])
    compiler.service_block(tree, '1')
    Compiler.subtree.assert_called_with(tree.nested_block, parent=tree.line())


def test_compiler_when_block(patch, compiler, tree):
    patch.many(Compiler, ['subtree', 'when'])
    compiler.when_block(tree, '1')
    Compiler.when.assert_called_with(tree, tree.nested_block, '1')


def test_compiler_when_block_nested_block(patch, compiler, tree):
    patch.many(Compiler, ['subtree', 'when'])
    compiler.when_block(tree, '1')
    Compiler.subtree.assert_called_with(tree.nested_block, parent=tree.line())


def test_compiler_try_block(patch, compiler, lines, tree):
    """
    Ensures that try blocks are compiled correctly.
    """
    patch.object(Compiler, 'subtree')
    tree.catch_block = None
    tree.finally_block = None
    compiler.try_block(tree, '1')
    kwargs = {'enter': tree.nested_block.line(), 'parent': '1'}
    lines.set_scope.assert_called_with(tree.line(), '1')
    lines.append.assert_called_with('try', tree.line(), **kwargs)
    Compiler.subtree.assert_called_with(tree.nested_block, parent=tree.line())


def test_compiler_try_block_catch(patch, compiler, lines, tree):
    patch.many(Compiler, ['subtree', 'catch_block'])
    tree.finally_block = None
    compiler.try_block(tree, '1')
    Compiler.catch_block.assert_called_with(tree.catch_block, parent='1')


def test_compiler_try_block_finally(patch, compiler, lines, tree):
    patch.many(Compiler, ['subtree', 'finally_block'])
    tree.catch_block = None
    compiler.try_block(tree, '1')
    Compiler.finally_block.assert_called_with(tree.finally_block, parent='1')


def test_compiler_catch_block(patch, compiler, lines, tree):
    """
    Ensures that catch blocks are compiled correctly.
    """
    patch.object(Objects, 'names')
    patch.object(Compiler, 'subtree')
    compiler.catch_block(tree, '1')
    lines.set_exit.assert_called_with(tree.line())
    Objects.names.assert_called_with(tree.catch_statement)
    lines.set_scope.assert_called_with(tree.line(), '1', Objects.names())
    kwargs = {'enter': tree.nested_block.line(), 'output': Objects.names(),
              'parent': '1'}
    lines.append.assert_called_with('catch', tree.line(), **kwargs)
    Compiler.subtree.assert_called_with(tree.nested_block, parent=tree.line())


def test_compiler_finally_block(patch, compiler, lines, tree):
    """
    Ensures that finally blocks are compiled correctly.
    """
    patch.object(Compiler, 'subtree')
    compiler.finally_block(tree, '1')
    lines.set_exit.assert_called_with(tree.line())
    lines.set_scope.assert_called_with(tree.line(), '1')
    kwargs = {'enter': tree.nested_block.line(), 'parent': '1'}
    lines.append.assert_called_with('finally', tree.line(), **kwargs)
    Compiler.subtree.assert_called_with(tree.nested_block, parent=tree.line())


def test_compiler_break_statement(compiler, lines, tree):
    compiler.break_statement(tree, '1')
    lines.append.assert_called_with('break', tree.line(), parent='1')


def test_compiler_break_statement_outside(patch, compiler, lines, tree):
    patch.init(CompilerError)
    with raises(CompilerError):
        compiler.break_statement(tree, None)
    CompilerError.__init__.assert_called_with('break_outside', tree=tree)


@mark.parametrize('method_name', [
    'service_block', 'absolute_expression', 'assignment', 'if_block',
    'elseif_block', 'else_block', 'foreach_block', 'function_block',
    'when_block', 'try_block', 'return_statement', 'arguments', 'imports',
    'mutation_block', 'indented_chain', 'break_statement'
])
def test_compiler_subtree(patch, compiler, method_name):
    patch.object(Compiler, method_name)
    tree = Tree(method_name, [])
    compiler.subtree(tree)
    method = getattr(compiler, method_name)
    method.assert_called_with(tree, None)


def test_compiler_subtree_parent(patch, compiler):
    patch.object(Compiler, 'assignment')
    tree = Tree('assignment', [])
    compiler.subtree(tree, parent='1')
    compiler.assignment.assert_called_with(tree, '1')


def test_compiler_subtrees(patch, compiler, tree):
    patch.object(Compiler, 'subtree', return_value={'tree': 'sub'})
    compiler.subtrees(tree, tree)
    compiler.subtree.assert_called_with(tree, parent=None)


def test_compiler_subtrees_parent(patch, compiler, tree):
    patch.object(Compiler, 'subtree', return_value={'tree': 'sub'})
    compiler.subtrees(tree, tree, parent='1')
    compiler.subtree.assert_called_with(tree, parent='1')


def test_compiler_parse_tree(compiler, patch):
    """
    Ensures that the parse_tree method can parse a complete tree
    """
    patch.object(Compiler, 'subtree')
    tree = Tree('start', [Tree('command', ['token'])])
    compiler.parse_tree(tree)
    compiler.subtree.assert_called_with(Tree('command', ['token']),
                                        parent=None)


def test_compiler_parse_tree_parent(compiler, patch):
    patch.object(Compiler, 'subtree')
    tree = Tree('start', [Tree('command', ['token'])])
    compiler.parse_tree(tree, parent='1')
    compiler.subtree.assert_called_with(Tree('command', ['token']), parent='1')


def test_compiler_compiler(patch):
    patch.init(Compiler)
    result = Compiler.compiler()
    assert isinstance(result, Compiler)


def test_compiler_compile(patch):
    patch.object(Preprocessor, 'process')
    patch.many(Compiler, ['parse_tree', 'compiler'])
    result = Compiler.compile('tree')
    Preprocessor.process.assert_called_with('tree')
    Compiler.compiler().parse_tree.assert_called_with(Preprocessor.process())
    lines = Compiler.compiler().lines
    expected = {'tree': lines.lines, 'version': version,
                'services': lines.get_services(), 'functions': lines.functions,
                'entrypoint': lines.first(), 'modules': lines.modules}
    assert result == expected
