from pytest import fixture, mark

from storyscript.tree import Comparison


@fixture
def comparison():
    return Comparison('left', 'method', 'right')


def test_comparison(comparison):
    assert comparison.left == 'left'
    assert comparison.method == 'method'
    assert comparison.right == 'right'


def test_comparison_json(comparison):
    result = comparison.json()
    assert result == {'$OBJECT': 'method', 'method': 'method', 'left': 'left',
                      'right': 'right'}


@mark.parametrize('handside', ['right', 'left'])
def test_comparison_json_handside(mocker, comparison, handside):
    mock = mocker.MagicMock(json=mocker.MagicMock())
    setattr(comparison, handside, mock)
    assert comparison.json()[handside] == mock.json()
