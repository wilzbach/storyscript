# -*- coding: utf-8 -*-
from lark.lexer import Token

from pytest import fixture

from storyscript.compiler.lowering import FakeTree
from storyscript.parser import Tree


@fixture
def fake_tree(block):
    return FakeTree(block)


def test_faketree_init(block, fake_tree):
    assert fake_tree.block == block
    assert fake_tree.original_line == str(block.line())
    assert fake_tree.new_lines == {}


def test_faketree_check_existing_empty(block, fake_tree):
    """
    Checks checking for fake lines with an empty block
    """
    fake_tree._check_existing_fake_lines(block)
    assert fake_tree.new_lines == {}


def test_faketree_check_existing_one_child(block, fake_tree):
    """
    Checks checking for fake lines with an one child block
    """
    block.children = [
        Tree("path", [Token("NAME", "foo")]),
        Tree("assignment", [Tree("path", [Token("NAME", "foo")])]),
    ]
    fake_tree._check_existing_fake_lines(block)
    assert fake_tree.new_lines == {}


def test_faketree_check_existing_with_fake(block, fake_tree):
    """
    Checks checking for fake lines with a fake path
    """
    block.children = [
        Tree("assignment", [Tree("path", [Token("NAME", "foo", line="1")])]),
        Tree(
            "assignment",
            [Tree("path", [Token("NAME", "__p-bar", line="1.1")])],
        ),
    ]
    fake_tree._check_existing_fake_lines(block)
    assert fake_tree.new_lines == {"__p-bar": False}


def test_faketree_check_existing_multiple_fake(block, fake_tree):
    """
    Checks checking for fake lines with multiple fake paths
    """
    block.children = [
        Tree(
            "assignment",
            [Tree("path", [Token("NAME", "__p-bar1", line="1.1")])],
        ),
        Tree("assignment", [Tree("path", [Token("NAME", "foo", line="1")])]),
        Tree(
            "assignment",
            [Tree("path", [Token("NAME", "__p-bar2", line="2.1")])],
        ),
        Tree("assignment", [Tree("path", [Token("NAME", "foo", line="2")])]),
        Tree(
            "assignment",
            [Tree("path", [Token("NAME", "__p-bar3", line="3.1")])],
        ),
    ]
    fake_tree._check_existing_fake_lines(block)
    assert fake_tree.new_lines == {
        "__p-bar1": False,
        "__p-bar2": False,
        "__p-bar3": False,
    }


def test_faketree_line(patch, fake_tree):
    """
    Ensures FakeTree.line can create a fake line number
    """
    fake_tree.original_line = "1"
    result = fake_tree.line()
    assert fake_tree.new_lines == {"1.1": None}
    assert result == "1.1"


def test_faketree_line_successive(patch, fake_tree):
    """
    Ensures FakeTree.line takes into account FakeTree.new_lines
    """
    fake_tree.original_line = "1.1"
    fake_tree.new_lines = {"1.1": None}
    assert fake_tree.line() == "1.2"


def test_faketree_get_line(patch, tree, fake_tree):
    """
    Ensures FakeTree.get_line can get a new line
    """
    patch.object(FakeTree, "line")
    result = fake_tree.get_line(tree)
    assert result == FakeTree.line()


def test_faketree_get_line_existing(tree, fake_tree):
    """
    Ensures FakeTree.get_line gets the existing line when appropriate.
    """
    fake_tree.new_lines = {"0.1": None}
    tree.line.return_value = "0.1"
    assert fake_tree.get_line(tree) == tree.line()


def test_faketree_path(patch, fake_tree):
    patch.object(FakeTree, "line")
    FakeTree.line.return_value = "fake.line"
    result = fake_tree.path()
    name = "__p-fake.line"
    assert result == Tree("path", [Token("NAME", name, line=FakeTree.line())])


def test_faketree_path_name(patch, fake_tree):
    patch.object(FakeTree, "line")
    FakeTree.line.return_value = "fake.line"
    result = fake_tree.path(name="x")
    assert result.child(0).value == "x"


def test_faketree_path_line(fake_tree):
    assert fake_tree.path(line=1).child(0).line == 1


def test_faketree_set_line(patch, fake_tree):
    tok = Token("NAME", "foo")
    tree = Tree("path", [tok])
    patch.object(tree, "find_first_token", return_value=tok)
    fake_tree.set_line(tree, "1")
    tree.find_first_token.assert_called()
    assert tok.line == "1"

    patch.object(tree, "find_first_token", return_value=None)
    fake_tree.set_line(tree, "2")
    tree.find_first_token.assert_called()
    assert tree._line == "2"


def test_faketree_assignment(patch, tree, fake_tree):
    patch.many(FakeTree, ["path", "get_line", "set_line"])
    result = fake_tree.assignment(tree)
    FakeTree.get_line.assert_called_with(tree)
    line = FakeTree.get_line()
    FakeTree.set_line.assert_called_with(tree, line)
    FakeTree.path.assert_called_with(line=line)
    assert result.children[0] == FakeTree.path()
    tree = Tree("base_expression", [tree])
    subtree = [Token("EQUALS", "=", line=line), tree]
    expected = Tree("assignment_fragment", subtree)
    assert result.children[1] == expected


def test_faketree_add_assignment(patch, fake_tree, block):
    patch.object(FakeTree, "assignment")
    patch.object(Tree, "create_token_from_tok")
    patch.object(FakeTree, "find_insert_pos", return_value=0)
    block.children = [1]
    block.child.return_value = None
    result = fake_tree.add_assignment("value", original_line=10)
    FakeTree.assignment.assert_called_with("value")
    assert block.children == [FakeTree.assignment(), 1]
    path_tok = FakeTree.assignment().path.child(0)
    Tree.create_token_from_tok.assert_called_with(
        path_tok, "NAME", path_tok.value
    )
    name = Tree.create_token_from_tok()
    name.line = 10
    assert result.data == "path"
    assert result.children == [name]


def test_faketree_add_assignment_more_children(patch, fake_tree, block):
    patch.object(FakeTree, "assignment")
    patch.object(FakeTree, "find_insert_pos", return_value=0)
    block.children = ["c1", fake_tree.block.last_child()]
    fake_tree.add_assignment("value", original_line=42)
    expected = [FakeTree.assignment(), "c1", block.last_child()]
    assert block.children == expected


def test_faketree_add_assignment_four_children(patch, fake_tree, block):
    patch.object(FakeTree, "assignment")
    patch.object(FakeTree, "find_insert_pos", return_value=1)
    block.children = ["c1", "c2", "c3", fake_tree.block.last_child()]
    fake_tree.add_assignment("value", original_line=42)
    expected = ["c1", FakeTree.assignment(), "c2", "c3", block.last_child()]
    assert block.children == expected


def test_faketree_add_assignment_four_children_bottom(patch, fake_tree, block):
    patch.object(FakeTree, "assignment")
    patch.object(FakeTree, "find_insert_pos", return_value=-1)
    block.children = ["c1", "c2", "c3", fake_tree.block.last_child()]
    fake_tree.add_assignment("value", original_line=42)
    expected = ["c1", "c2", "c3", FakeTree.assignment(), block.last_child()]
    assert block.children == expected
