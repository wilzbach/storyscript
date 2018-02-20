from pytest import fixture

from storyscript.tree import Condition


@fixture
def condition(mocker):
    return Condition(mocker.MagicMock(), 'bool', mocker.MagicMock())


def test_condition_init():
    condition = Condition('one', 'two', 'three')
    assert condition.condition == 'one'
    assert condition.boolean == 'two'
    assert condition.consequence == 'three'


def test_condition(condition):
    assert condition.json() == {
        '$OBJECT': 'condition',
        'condition': condition.condition.json(),
        'is': condition.boolean,
        'then': condition.consequence.json(),
        'else': None
    }


def test_condition_json_else(mocker, condition):
    condition.other = mocker.MagicMock()
    assert condition.json()['else'] == condition.other.json()
