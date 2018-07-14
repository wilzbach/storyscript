# -*- coding: utf-8 -*-
from lark.lexer import Token

from pytest import fixture, mark, raises

from storyscript.compiler import Compiler, Lines, Objects, Preprocessor
from storyscript.exceptions import StoryError
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


def test_compiler_init():
    compiler = Compiler()
    assert isinstance(compiler.lines, Lines)


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
    assert lines.modules[tree.child(1)] == tree.string.child(0).value[1:-1]


def test_compiler_assignment(patch, compiler, lines, tree):
    patch.many(Objects, ['path', 'values'])
    compiler.assignment(tree, '1')
    Objects.path.assert_called_with(tree.path)
    tree.assignment_fragment.child.assert_called_with(1)
    Objects.values.assert_called_with(tree.assignment_fragment.child())
    args = [Objects.path(), Objects.values()]
    lines.append.assert_called_with('set', tree.line(), args=args, parent='1')


def test_compiler_arguments(patch, compiler, lines, tree):
    patch.object(Objects, 'arguments')
    lines.last.return_value = '1'
    lines.lines = {'1': {'method': 'execute', 'args': ['args']}}
    compiler.arguments(tree, '0')
    Objects.arguments.assert_called_with(tree)
    assert lines.lines['1']['args'] == ['args'] + Objects.arguments()


def test_compiler_arguments_not_execute(patch, compiler, lines, tree):
    """
    Ensures that the previous line was an execute method.
    """
    patch.object(Objects, 'arguments')
    lines.last.return_value = '1'
    lines.lines = {'1': {'method': 'whatever'}}
    with raises(StoryError):
        compiler.arguments(tree, '0')


def test_compiler_service(patch, compiler, lines, tree):
    """
    Ensures that service trees can be compiled
    """
    patch.object(Objects, 'arguments')
    patch.object(Compiler, 'output')
    tree.node.return_value = None
    compiler.service(tree, None, 'parent')
    line = tree.line()
    service = tree.child().child().value
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
    service = tree.child().child().value
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
    service = tree.child().child().value
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


def test_compiler_return_statement(compiler, tree):
    with raises(StoryError):
        compiler.return_statement(tree, None)


def test_compiler_return_statement_parent(patch, compiler, lines, tree):
    patch.object(Objects, 'values')
    compiler.return_statement(tree, '1')
    line = tree.line()
    Objects.values.assert_called_with(tree.child())
    lines.append.assert_called_with('return', line, args=[Objects.values()],
                                    parent='1')


def test_compiler_if_block(patch, compiler, lines, tree):
    patch.object(Objects, 'expression')
    patch.object(Compiler, 'subtree')
    tree.elseif_block = None
    tree.else_block = None
    compiler.if_block(tree, '1')
    Objects.expression.assert_called_with(tree.if_statement)
    nested_block = tree.nested_block
    args = Objects.expression()
    lines.append.assert_called_with('if', tree.line(), args=args,
                                    enter=nested_block.line(), parent='1')
    compiler.subtree.assert_called_with(nested_block, parent=tree.line())


def test_compiler_if_block_with_elseif(patch, compiler, tree):
    patch.object(Objects, 'expression')
    patch.many(Compiler, ['subtree', 'subtrees'])
    tree.else_block = None
    compiler.if_block(tree, '1')
    compiler.subtrees.assert_called_with(tree.elseif_block)


def test_compiler_if_block_with_else(patch, compiler, tree):
    patch.object(Objects, 'expression')
    patch.many(Compiler, ['subtree', 'subtrees'])
    tree.elseif_block = None
    compiler.if_block(tree, '1')
    compiler.subtrees.assert_called_with(tree.else_block)


def test_compiler_elseif_block(patch, compiler, lines, tree):
    patch.object(Objects, 'expression')
    patch.object(Compiler, 'subtree')
    compiler.elseif_block(tree, '1')
    lines.set_exit.assert_called_with(tree.line())
    Objects.expression.assert_called_with(tree.elseif_statement)
    args = Objects.expression()
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
    patch.object(Objects, 'path')
    patch.many(Compiler, ['subtree', 'output'])
    compiler.foreach_block(tree, '1')
    Objects.path.assert_called_with(tree.foreach_statement)
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


@mark.parametrize('method_name', [
    'service_block', 'assignment', 'if_block', 'elseif_block', 'else_block',
    'foreach_block', 'function_block', 'return_statement', 'arguments',
    'imports'
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


def test_compiler_compiler():
    assert isinstance(Compiler.compiler(), Compiler)


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


def test_compiler_compile_debug(patch):
    patch.object(Preprocessor, 'process')
    patch.many(Compiler, ['parse_tree', 'compiler'])
    Compiler.compile('tree', debug='debug')
