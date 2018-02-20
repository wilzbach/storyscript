from pytest import fixture

from storyscript.tree import Condition


@fixture
def condition(mocker):
    return Condition(mocker.MagicMock(), 'bool', mocker.MagicMock())


def test_condition_init():
    assert Condition('one', 'two').args == ('one', 'two')


def test_condition(condition):
    assert condition.json() == {
        '$OBJECT': 'condition',
        'condition': condition.args[0].json(),
        'is': 'bool',
        'then': condition.args[2].json(),
        'else': None
    }


def test_condition_json_else(mocker, condition):
    condition.args = tuple(list(condition.args) + [mocker.MagicMock()])
    assert condition.json()['else'] == condition.args[3].json()
