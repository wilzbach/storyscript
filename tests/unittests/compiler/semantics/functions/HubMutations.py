from storyscript.compiler.semantics.functions.HubMutations import Hub


def test_mutations_empty():
    assert len(Hub('').mutations()) == 0


def test_mutations_comment():
    assert len(Hub('#comment\n#another comment\n').mutations()) == 0
