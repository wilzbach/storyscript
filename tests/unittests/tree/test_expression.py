from pytest import fixture

from storyscript.tree import Expression


@fixture
def expression():
    return Expression('expression')


def test_expression_init(expression):
    assert expression.expression == [('', 'expression')]


def test_expression_json(expression):
    expression.expression.append(('', 'two'))
    result = expression.json(evals=[], values=[])
    assert result == {
        '$OBJECT': 'expression',
        'expression': 'expression two',
        'values': []
    }


def test_expression_json_mixins(expression):
    expression.expression.append(('mixin', 'two'))
    result = expression.json(evals=[], values=[])
    assert result['expression'] == 'expression mixin two'


def test_expression_json_no_evals(expression):
    result = expression.json()
    assert result == 'expression'


def test_expression_json_no_evals_json(mocker, expression):
    item = mocker.MagicMock(json=mocker.MagicMock())
    expression.expression = [('', item)]
    result = expression.json()
    assert result == item.json()


def test_expression_json_expressions(expression):
    expression.expression = [('', Expression('one')), ('', Expression('two'))]
    result = expression.json(evals=[], values=[])
    assert result['expression'] == 'one two'


def test_expression_json_json(mocker, expression):
    item = mocker.MagicMock(json=mocker.MagicMock())
    expression.expression = [('', item)]
    result = expression.json(evals=[], values=[])
    assert result['expression'] == '{}'
    assert result['values'] == [item.json()]
