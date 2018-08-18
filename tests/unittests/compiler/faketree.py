# -*- coding: utf-8 -*-
import uuid

from storyscript.compiler import FakeTree


def test_faketree_line(patch, magic, tree):
    """
    Ensures line can create a fake line number
    """
    patch.object(uuid, 'uuid4', return_value=magic(int=123456789))
    assert FakeTree.line('1') == '0.12345678'
