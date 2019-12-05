from storyscript.compiler.semantics.functions.HubMutations import Hub


def test_mutations_empty():
    assert len(Hub([]).mutations()) == 0
