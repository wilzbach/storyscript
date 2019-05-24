from storyscript.Features import Features


def test_features_str():
    assert str(Features(None)).startswith('Features(')
