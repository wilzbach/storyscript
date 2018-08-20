# -*- coding: utf-8 -*-
import random
import uuid

from lark.lexer import Token

from storyscript.compiler import FakeTree
from storyscript.parser import Tree


def test_faketree_line(patch, magic, tree):
    """
    Ensures line can create a fake line number
    """
    patch.object(random, 'uniform')
    result = FakeTree.line('1')
    random.uniform.assert_called_with(0, 1)
    assert result == str(random.uniform())


def test_faketree_path(patch):
    patch.object(uuid, 'uuid4')
    result = FakeTree.path(1)
    name = '${}'.format(uuid.uuid4().hex[:8])
    assert result == Tree('path', [Token('NAME', name, line=1)])


def test_faketree_assignment(patch, tree):
    patch.object(FakeTree, 'path')
    result = FakeTree.assignment('1', tree)
    FakeTree.path.assert_called_with('1')
    assert tree.child().child().line == '1'
    assert result.children[0] == FakeTree.path()
    expected = Tree('assignment_fragment', [Token('EQUALS', '='), tree])
    assert result.children[1] == expected
