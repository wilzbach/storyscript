# -*- coding: utf-8 -*-
from lark.lexer import Token

from pytest import fixture, mark, raises

from storyscript.compiler import Compiler, Lines, Objects, Preprocessor
from storyscript.exceptions import StoryError, StorySyntaxError
from storyscript.parser import Tree
from storyscript.version import version


@fixture
def lines(magic):
    return magic()


@fixture
def compiler(patch, lines):
    patch.init(Lines)
    compiler = Compiler()
    compiler.lines = lines
    return compiler


def test_compiler_init(patch):
    patch.init(Lines)
    compiler = Compiler()
    Lines.__init__.assert_called_with(path=None)
    assert isinstance(compiler.lines, Lines)
    assert compiler.path is None


def test_compiler_init_path(patch):
    patch.init(Lines)
    compiler = Compiler(path='path')
    Lines.__init__.assert_called_with(path='path')
    assert compiler.path == 'path'


def test_compiler_output(tree):
    tree.children = [Token('token', 'output')]
    result = Compiler.output(tree)
    assert result == ['output']


def test_compiler_output_none():
    assert Compiler.output(None) == []


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
    patch.many(Objects, ['mutation', 'path'])
    tree.expression = None
    compiler.expression(tree, '1')
    Objects.mutation.assert_called_with(tree.service_fragment)
    Objects.path.assert_called_with(tree.path)
    args = [Objects.path(), Objects.mutation()]
    lines.append.assert_called_with('expression', tree.line(), args=args,
                                    parent='1')


def test_compiler_expression_absolute(patch, compiler, lines, tree):
    """
    Ensures that absolute expressions are compiled correctly
    """
    patch.object(Objects, 'expression')
    tree.expression.mutation = None
    compiler.expression(tree, '1')
    Objects.expression.assert_called_with(tree.expression)
    args = [Objects.expression()]
    lines.append.assert_called_with('expression', tree.line(), args=args,
                                    parent='1')


def test_compiler_expression_absolute_mutation(patch, compiler, lines, tree):
    """
    Ensures that absolute expressions with mutations are compiled correctly
    """
    patch.many(Objects, ['mutation', 'values'])
    compiler.expression(tree, '1')
    Objects.mutation.assert_called_with(tree.expression.mutation)
    Objects.values.assert_called_with(tree.expression.values)
    args = [Objects.values(), Objects.mutation()]
    lines.append.assert_called_with('expression', tree.line(), args=args,
                                    parent='1')


def test_compiler_expression_assignment(patch, compiler, lines, tree):
    patch.object(Compiler, 'expression')
    compiler.expression_assignment(tree, 'name', '1')
    Compiler.expression.assert_called_with(tree, '1')
    lines.set_name.assert_called_with('name')


def test_compiler_absolute_expression(patch, compiler, lines, tree):
    patch.object(Compiler, 'expression')
    compiler.absolute_expression(tree, '1')
    Compiler.expression.assert_called_with(tree, '1')


def test_compiler_extract_values(patch, compiler, tree):
    patch.object(Objects, 'values')
    tree.expression = None
    result = compiler.extract_values(tree)
    tree.child.assert_called_with(1)
    Objects.values.assert_called_with(tree.child())
    assert result == [Objects.values()]


def test_compiler_extract_values_expression(patch, compiler, tree):
    patch.object(Objects, 'expression')
    tree.expression.mutation = None
    result = compiler.extract_values(tree)
    Objects.expression.assert_called_with(tree.expression)
    assert result == [Objects.expression()]


def test_compiler_extract_values_mutation(patch, compiler, tree):
    patch.many(Objects, ['values', 'mutation'])
    result = compiler.extract_values(tree)
    Objects.values.assert_called_with(tree.expression.values)
    Objects.mutation.assert_called_with(tree.expression.mutation)
    assert result == [Objects.values(), Objects.mutation()]


def test_compiler_assignment(patch, compiler, lines, tree):
    """
    Ensures a line like "x = value" is compiled correctly
    """
    patch.object(Objects, 'names')
    patch.object(Compiler, 'extract_values')
    tree.assignment_fragment.service = None
    tree.assignment_fragment.expression = None
    compiler.assignment(tree, '1')
    Objects.names.assert_called_with(tree.path)
    Compiler.extract_values.assert_called_with(tree.assignment_fragment)
    kwargs = {'name': Objects.names(), 'args': Compiler.extract_values(),
              'parent': '1'}
    lines.append.assert_called_with('set', tree.line(), **kwargs)


def test_compiler_assignment_service(patch, compiler, lines, tree):
    patch.object(Objects, 'names')
    patch.object(Compiler, 'service')
    compiler.assignment(tree, '1')
    service = tree.assignment_fragment.service
    Compiler.service.assert_called_with(service, None, '1')
    lines.set_name.assert_called_with(Objects.names())


def test_compiler_assignment_expression_service(patch, compiler, lines, tree):
    """
    Ensures that assignments like 'x = a mutation' are compiled correctly.
    This works by checking that 'a' was infact previously assigned, thus
    it's not a service but a variable.
    """
    patch.object(Objects, 'names', return_value='name')
    patch.object(Compiler, 'expression_assignment')
    lines.variables = ['name']
    compiler.assignment(tree, '1')
    service = tree.assignment_fragment.service
    Compiler.expression_assignment.assert_called_with(service, 'name', '1')


def test_compiler_assignment_expression(patch, compiler, lines, tree):
    patch.object(Objects, 'names', return_value='name')
    patch.object(Compiler, 'expression_assignment')
    tree.assignment_fragment.service = None
    compiler.assignment(tree, '1')
    fragment = tree.assignment_fragment
    Compiler.expression_assignment.assert_called_with(fragment, 'name', '1')


def test_compiler_arguments(patch, compiler, lines, tree):
    patch.object(Objects, 'arguments')
    lines.last.return_value = '1'
    lines.lines = {'1': {'method': 'execute', 'args': ['args']}}
    compiler.arguments(tree, '0')
    Objects.arguments.assert_called_with(tree)
    assert lines.lines['1']['args'] == ['args'] + Objects.arguments()


def test_compiler_arguments_not_execute(patch, compiler, lines, tree):
    """
    Ensures that if the previous line is an execute line, an error is raised.
    """
    patch.init(StoryError)
    patch.object(Objects, 'arguments')
    lines.last.return_value = '1'
    lines.lines = {'1': {'method': 'whatever'}}
    with raises(StoryError):
        compiler.arguments(tree, '0')
    args = ('arguments-noservice', tree)
    StoryError.__init__.assert_called_with(*args, path=compiler.path)


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
    lines.set_output.assert_called_with(line, Compiler.output())
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
    patch.object(Compiler, 'expression')
    lines.variables = ['x']
    compiler.service(tree, None, 'parent')
    Objects.names.assert_called_with(tree.path)
    Compiler.expression.assert_called_with(tree, 'parent')


def test_compiler_service_syntax_error(patch, compiler, lines, tree):
    patch.object(Objects, 'arguments')
    patch.object(Compiler, 'output')
    patch.object(StorySyntaxError, 'set_position')
    lines.execute.side_effect = StorySyntaxError('error')
    with raises(StorySyntaxError):
        compiler.service(tree, None, 'parent')
    line = tree.line()
    StorySyntaxError.set_position.assert_called_with(line, tree.column())


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


def test_compiler_return_statement(patch, compiler, tree):
    patch.init(StoryError)
    with raises(StoryError):
        compiler.return_statement(tree, None)
    args = ('return-outside', tree)
    StoryError.__init__.assert_called_with(*args, path=compiler.path)


def test_compiler_return_statement_parent(patch, compiler, lines, tree):
    patch.object(Objects, 'values')
    compiler.return_statement(tree, '1')
    line = tree.line()
    Objects.values.assert_called_with(tree.child())
    lines.append.assert_called_with('return', line, args=[Objects.values()],
                                    parent='1')


def test_compiler_if_block(patch, compiler, lines, tree):
    patch.object(Objects, 'assertion')
    patch.object(Compiler, 'subtree')
    tree.elseif_block = None
    tree.else_block = None
    compiler.if_block(tree, '1')
    Objects.assertion.assert_called_with(tree.if_statement)
    nested_block = tree.nested_block
    args = Objects.assertion()
    lines.append.assert_called_with('if', tree.line(), args=args,
                                    enter=nested_block.line(), parent='1')
    compiler.subtree.assert_called_with(nested_block, parent=tree.line())


def test_compiler_if_block_with_elseif(patch, compiler, tree):
    patch.object(Objects, 'assertion')
    patch.many(Compiler, ['subtree', 'subtrees'])
    tree.else_block = None
    compiler.if_block(tree, '1')
    compiler.subtrees.assert_called_with(tree.elseif_block)


def test_compiler_if_block_with_else(patch, compiler, tree):
    patch.object(Objects, 'assertion')
    patch.many(Compiler, ['subtree', 'subtrees'])
    tree.elseif_block = None
    compiler.if_block(tree, '1')
    compiler.subtrees.assert_called_with(tree.else_block)


def test_compiler_elseif_block(patch, compiler, lines, tree):
    patch.object(Objects, 'assertion')
    patch.object(Compiler, 'subtree')
    compiler.elseif_block(tree, '1')
    lines.set_exit.assert_called_with(tree.line())
    Objects.assertion.assert_called_with(tree.elseif_statement)
    args = Objects.assertion()
    lines.append.assert_called_with('elif', tree.line(), args=args,
                                    enter=tree.nested_block.line(),
                                    parent='1')
    compiler.subtree.assert_called_with(tree.nested_block, parent=tree.line())


def test_compiler_else_block(patch, compiler, lines, tree):
    patch.object(Compiler, 'subtree')
    compiler.else_block(tree, '1')
    lines.set_exit.assert_called_with(tree.line())
    lines.append.assert_called_with('else', tree.line(), parent='1',
                                    enter=tree.nested_block.line())
    compiler.subtree.assert_called_with(tree.nested_block, parent=tree.line())


def test_compiler_foreach_block(patch, compiler, lines, tree):
    patch.init(Tree)
    patch.object(Objects, 'path')
    patch.many(Compiler, ['subtree', 'output'])
    compiler.foreach_block(tree, '1')
    Tree.__init__.assert_called_with('path', [tree.foreach_statement.child()])
    assert Objects.path.call_count == 1
    compiler.output.assert_called_with(tree.foreach_statement.output)
    args = [Objects.path()]
    lines.append.assert_called_with('for', tree.line(), args=args,
                                    enter=tree.nested_block.line(),
                                    output=Compiler.output(), parent='1')
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
    kwargs = {'enter': tree.nested_block.line(), 'parent': '1'}
    lines.append.assert_called_with('finally', tree.line(), **kwargs)
    Compiler.subtree.assert_called_with(tree.nested_block, parent=tree.line())


@mark.parametrize('method_name', [
    'service_block', 'absolute_expression', 'assignment', 'if_block',
    'elseif_block', 'else_block', 'foreach_block', 'function_block',
    'when_block', 'try_block', 'return_statement', 'arguments', 'imports'
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
    compiler.subtree.assert_called_with(tree)


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
    result = Compiler.compiler('path')
    assert isinstance(result, Compiler)
    Compiler.__init__.assert_called_with(path='path')


def test_compiler_compile(patch):
    patch.object(Preprocessor, 'process')
    patch.many(Compiler, ['parse_tree', 'compiler'])
    result = Compiler.compile('tree')
    Preprocessor.process.assert_called_with('tree')
    Compiler.compiler.assert_called_with(None)
    Compiler.compiler().parse_tree.assert_called_with(Preprocessor.process())
    lines = Compiler.compiler().lines
    expected = {'tree': lines.lines, 'version': version,
                'services': lines.get_services(), 'functions': lines.functions,
                'entrypoint': lines.first(), 'modules': lines.modules}
    assert result == expected


def test_compiler_compile_path(patch):
    patch.object(Preprocessor, 'process')
    patch.many(Compiler, ['parse_tree', 'compiler'])
    Compiler.compile('tree', path='path')
    Compiler.compiler.assert_called_with('path')


def test_compiler_compile_debug(patch):
    patch.object(Preprocessor, 'process')
    patch.many(Compiler, ['parse_tree', 'compiler'])
    Compiler.compile('tree', debug='debug')
