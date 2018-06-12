# -*- coding: utf-8 -*-
from lark.lexer import Token

from pytest import fixture, mark, raises

from storyscript.compiler import Compiler, Objects
from storyscript.exceptions import StoryscriptSyntaxError
from storyscript.parser import Tree
from storyscript.version import version


@fixture
def compiler():
    return Compiler()


def test_compiler_init(compiler):
    assert compiler.lines == {}
    assert compiler.services == []
    assert compiler.functions == {}


def test_compiler_sorted_lines(compiler):
    compiler.lines = {'1': '1', '2': '2'}
    assert compiler.sorted_lines() == ['1', '2']


def test_compiler_last_line(patch, compiler):
    patch.object(Compiler, 'sorted_lines')
    compiler.lines = {'1': '1'}
    assert compiler.last_line() == compiler.sorted_lines()[-1]


def test_compiler_last_line_no_lines(compiler):
    assert compiler.last_line() is None


def test_compiler_set_next_line(patch, compiler):
    patch.object(Compiler, 'last_line', return_value='1')
    compiler.lines['1'] = {}
    compiler.set_next_line('2')
    assert compiler.lines['1']['next'] == '2'


def test_compiler_set_exit_line(patch, compiler):
    patch.object(Compiler, 'sorted_lines', return_value=['1', '2'])
    compiler.lines = {'1': {}, '2': {'method': 'if'}}
    compiler.set_exit_line('3')
    assert compiler.sorted_lines.call_count == 1
    assert compiler.lines['2']['exit'] == '3'


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


def test_compiler_make_line(compiler):
    expected = {'1': {'method': 'method', 'ln': '1', 'output': None,
                      'function': None, 'service': None, 'command': None,
                      'enter': None, 'exit': None, 'args': None,
                      'parent': None}}
    compiler.make_line('method', '1')
    assert compiler.lines == expected


@mark.parametrize('keywords', ['service', 'command', 'function', 'output',
                               'args', 'enter', 'exit', 'parent'])
def test_compiler_make_line_keywords(compiler, keywords):
    compiler.make_line('method', '1', **{keywords: keywords})
    assert compiler.lines['1'][keywords] == keywords


def test_compiler_add_line(patch, compiler):
    patch.many(Compiler, ['make_line', 'set_next_line'])
    compiler.add_line('method', 'line', extras='whatever')
    compiler.set_next_line.assert_called_with('line')
    compiler.make_line.assert_called_with('method', 'line', extras='whatever')


def test_compiler_add_line_function(patch, compiler):
    """
    Ensures that a line is registered properly.
    """
    patch.many(Compiler, ['make_line', 'set_next_line'])
    compiler.add_line('function', 'line', function='function')
    assert compiler.functions['function'] == 'line'


def test_compiler_add_line_service(patch, compiler):
    """
    Ensures that a service is registered properly.
    """
    patch.many(Compiler, ['make_line', 'set_next_line'])
    compiler.add_line('execute', 'line', service='service')
    assert compiler.services[0] == 'service'


def test_compiler_add_line_function_call(patch, compiler):
    """
    Ensures that a function call is registered properly.
    """
    patch.many(Compiler, ['make_line', 'set_next_line'])
    compiler.functions['function'] = 1
    compiler.add_line('execute', 'line', service='function')
    compiler.make_line.assert_called_with('call', 'line', service='function')


def test_compiler_assignment(patch, compiler, tree):
    patch.many(Objects, ['path', 'values'])
    patch.object(Compiler, 'add_line')
    compiler.assignment(tree)
    assert tree.node.call_count == 2
    Objects.path.assert_called_with(tree.node())
    Objects.values.assert_called_with(tree.node())
    args = [Objects.path(), Objects.values()]
    compiler.add_line.assert_called_with('set', tree.line(), args=args,
                                         parent=None)


def test_compiler_assignment_parent(patch, compiler, tree):
    patch.many(Objects, ['path', 'values'])
    patch.object(Compiler, 'add_line')
    compiler.assignment(tree, parent='1')
    args = [Objects.path(), Objects.values()]
    compiler.add_line.assert_called_with('set', tree.line(), args=args,
                                         parent='1')


def test_compiler_service(patch, compiler, tree):
    """
    Ensures that service trees can be compiled
    """
    patch.object(Objects, 'arguments')
    patch.many(Compiler, ['add_line', 'output'])
    tree.node.return_value = None
    compiler.service(tree)
    line = tree.line()
    service = tree.child().child().value
    Objects.arguments.assert_called_with(tree.node())
    Compiler.output.assert_called_with(tree.node())
    compiler.add_line.assert_called_with('execute', line, service=service,
                                         command=tree.node(), parent=None,
                                         args=Objects.arguments(),
                                         output=Compiler.output())


def test_compiler_service_command(patch, compiler, tree):
    patch.object(Objects, 'arguments')
    patch.many(Compiler, ['add_line', 'output'])
    compiler.service(tree)
    line = tree.line()
    service = tree.child().child().value
    compiler.add_line.assert_called_with('execute', line, service=service,
                                         command=tree.node().child(),
                                         parent=None, output=Compiler.output(),
                                         args=Objects.arguments())


def test_compiler_service_parent(patch, compiler, tree):
    patch.object(Objects, 'arguments')
    patch.many(Compiler, ['add_line', 'output'])
    tree.node.return_value = None
    compiler.service(tree, parent='1')
    line = tree.line()
    service = tree.child().child().value
    compiler.add_line.assert_called_with('execute', line, service=service,
                                         command=tree.node(),
                                         args=Objects.arguments(),
                                         output=Compiler.output(), parent='1')


def test_compiler_return_statement(compiler, tree):
    with raises(StoryscriptSyntaxError):
        compiler.return_statement(tree)


def test_compiler_return_statement_parent(patch, compiler, tree):
    patch.object(Objects, 'values')
    patch.object(Compiler, 'add_line')
    compiler.return_statement(tree, parent='1')
    line = tree.line()
    Objects.values.assert_called_with(tree.child())
    compiler.add_line.assert_called_with('return', line,
                                         args=[Objects.values()], parent='1')


def test_compiler_if_block(patch, compiler):
    patch.object(Objects, 'expression')
    patch.many(Compiler, ['add_line', 'subtree'])
    tree = Tree('if_block', [Tree('if_statement', []),
                             Tree('nested_block', [])])
    compiler.if_block(tree)
    Objects.expression.assert_called_with(tree.node('if_statement'))
    nested_block = tree.node('nested_block')
    args = Objects.expression()
    compiler.add_line.assert_called_with('if', tree.line(), args=args,
                                         enter=nested_block.line(),
                                         parent=None)
    compiler.subtree.assert_called_with(nested_block, parent=tree.line())


def test_compiler_if_block_parent(patch, compiler):
    patch.object(Objects, 'expression')
    patch.many(Compiler, ['add_line', 'subtree'])
    tree = Tree('if_block', [Tree('if_statement', []),
                             Tree('nested_block', [])])
    compiler.if_block(tree, parent='1')
    nested_block = tree.node('nested_block')
    args = Objects.expression()
    compiler.add_line.assert_called_with('if', tree.line(), args=args,
                                         enter=nested_block.line(),
                                         parent='1')


def test_compiler_if_block_with_elseif(patch, compiler):
    patch.object(Objects, 'expression')
    patch.many(Compiler, ['add_line', 'subtree', 'subtrees'])
    tree = Tree('if_block', [Tree('nested_block', []),
                             Tree('elseif_block', [])])
    compiler.if_block(tree)
    compiler.subtrees.assert_called_with(tree.node('elseif_block'))


def test_compiler_if_block_with_else(patch, compiler):
    patch.object(Objects, 'expression')
    patch.many(Compiler, ['add_line', 'subtree', 'subtrees'])
    tree = Tree('if_block', [Tree('nested_block', []),
                             Tree('else_block', [])])
    compiler.if_block(tree)
    compiler.subtrees.assert_called_with(tree.node('else_block'))


def test_compiler_elseif_block(patch, compiler, tree):
    patch.object(Objects, 'expression')
    patch.many(Compiler, ['add_line', 'subtree', 'set_exit_line'])
    compiler.elseif_block(tree)
    compiler.set_exit_line.assert_called_with(tree.line())
    assert tree.node.call_count == 2
    Objects.expression.assert_called_with(tree.node())
    args = Objects.expression()
    compiler.add_line.assert_called_with('elif', tree.line(), args=args,
                                         enter=tree.node().line(), parent=None)
    compiler.subtree.assert_called_with(tree.node(), parent=tree.line())


def test_compiler_elseif_block_parent(patch, compiler, tree):
    patch.object(Objects, 'expression')
    patch.many(Compiler, ['add_line', 'subtree'])
    compiler.elseif_block(tree, parent='1')
    args = Objects.expression()
    compiler.add_line.assert_called_with('elif', tree.line(), args=args,
                                         enter=tree.node().line(), parent='1')


def test_compiler_else_block(patch, compiler, tree):
    patch.many(Compiler, ['add_line', 'subtree', 'set_exit_line'])
    compiler.else_block(tree)
    compiler.set_exit_line.assert_called_with(tree.line())
    compiler.add_line.assert_called_with('else', tree.line(),
                                         enter=tree.node().line(), parent=None)
    compiler.subtree.assert_called_with(tree.node(), parent=tree.line())


def test_compiler_else_block_parent(patch, compiler, tree):
    patch.many(Compiler, ['add_line', 'subtree'])
    compiler.else_block(tree, parent='1')
    compiler.add_line.assert_called_with('else', tree.line(),
                                         enter=tree.node().line(), parent='1')


def test_compiler_foreach_block(patch, compiler, tree):
    patch.object(Objects, 'path')
    patch.many(Compiler, ['add_line', 'subtree', 'output'])
    compiler.foreach_block(tree)
    Objects.path.assert_called_with(tree.node())
    compiler.output.assert_called_with(tree.node())
    args = [Objects.path()]
    compiler.add_line.assert_called_with('for', tree.line(), args=args,
                                         enter=tree.node().line(),
                                         output=Compiler.output(), parent=None)
    compiler.subtree.assert_called_with(tree.node(), parent=tree.line())


def test_compiler_foreach_block_parent(patch, compiler, tree):
    patch.object(Objects, 'path')
    patch.many(Compiler, ['add_line', 'subtree', 'output'])
    compiler.foreach_block(tree, parent='1')
    args = [Objects.path()]
    compiler.add_line.assert_called_with('for', tree.line(), args=args,
                                         enter=tree.node().line(),
                                         output=Compiler.output(), parent='1')


def test_compiler_function_block(patch, compiler, tree):
    patch.object(Objects, 'function_arguments')
    patch.many(Compiler, ['add_line', 'subtree', 'function_output'])
    compiler.function_block(tree)
    Objects.function_arguments.assert_called_with(tree.node())
    compiler.function_output.assert_called_with(tree.node())
    compiler.add_line.assert_called_with('function', tree.line(),
                                         function=tree.node().child().value,
                                         args=Objects.function_arguments(),
                                         output=compiler.function_output(),
                                         enter=tree.node().line(),
                                         parent=None)
    compiler.subtree.assert_called_with(tree.node(), parent=tree.line())


def test_compiler_function_block_parent(patch, compiler, tree):
    patch.object(Objects, 'function_arguments')
    patch.many(Compiler, ['set_next_line', 'add_line', 'subtree',
                          'function_output'])
    compiler.function_block(tree, parent='1')
    compiler.add_line.assert_called_with('function', tree.line(),
                                         function=tree.node().child().value,
                                         args=Objects.function_arguments(),
                                         output=compiler.function_output(),
                                         enter=tree.node().line(), parent='1')


@mark.parametrize('method_name', [
    'service', 'assignment', 'if_block', 'elseif_block', 'else_block',
    'foreach_block', 'function_block', 'return_statement'
])
def test_compiler_subtree(patch, compiler, method_name):
    patch.object(Compiler, method_name)
    tree = Tree(method_name, [])
    compiler.subtree(tree)
    method = getattr(compiler, method_name)
    method.assert_called_with(tree, parent=None)


def test_compiler_subtree_parent(patch, compiler):
    patch.object(Compiler, 'service')
    tree = Tree('service', [])
    compiler.subtree(tree, parent='1')
    compiler.service.assert_called_with(tree, parent='1')


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


def test_compiler_compiler():
    assert isinstance(Compiler.compiler(), Compiler)


def test_compiler_compile(patch):
    patch.many(Compiler, ['parse_tree', 'compiler'])
    result = Compiler.compile('tree')
    Compiler.compiler().parse_tree.assert_called_with('tree')
    expected = {'tree': Compiler.compiler().lines, 'version': version,
                'services': Compiler.compiler().services,
                'functions': Compiler.compiler().functions}
    assert result == expected
