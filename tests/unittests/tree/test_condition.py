from pytest import mark

from storyscript.tree import Condition


@mark.parametrize('_else',
                  [0, 1]
                  )
def test_condition(mocker, _else):
    _if = mocker.MagicMock(json=mocker.MagicMock())
    _then = mocker.MagicMock(json=mocker.MagicMock())
    _else = mocker.MagicMock(json=mocker.MagicMock()) if _else else None
    path = Condition(_if, True, _then, _else)
    assert path.json() == {
        '$OBJECT': 'condition',
        'condition': _if.json(),
        'is': True,
        'then': _then.json(),
        'else': _else.json() if _else else None
    }
