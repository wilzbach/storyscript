# -*- coding: utf-8 -*-
import uuid

from lark.lexer import Token

from storyscript.compiler import FakeTree
from storyscript.parser import Tree


def test_faketree_line(patch, magic, tree):
    """
    Ensures line can create a fake line number
    """
    patch.object(uuid, 'uuid4', return_value=magic(int=123456789))
    assert FakeTree.line('1') == '0.12345678'


def test_faketree_path(patch):
    patch.object(uuid, 'uuid4')
    result = FakeTree.path(1)
    name = '${}'.format(uuid.uuid4().hex[:8])
    assert result == Tree('path', [Token('NAME', name, line=1)])
