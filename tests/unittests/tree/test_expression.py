from pytest import fixture

from storyscript.tree import Expression


@fixture
def expression():
    return Expression('one')


@fixture
def item(mocker):
    return mocker.MagicMock(json=mocker.MagicMock())


def test_expression_init(expression):
    assert expression.expressions == [('', 'one')]


def test_expression_representation(expression):
    assert '{}'.format(expression) == "Expression([('', 'one')])"


def test_expression_add(expression):
    expression.add('method', 'expression')
    assert expression.expressions[-1] == ('method', 'expression')


def test_expression_json(expression):
    expression.expressions.append(('', 'two'))
    result = expression.json(evals=[], values=[])
    assert result == {
        '$OBJECT': 'expression',
        'expression': 'one two',
        'values': []
    }


def test_expression_json_mixins(expression):
    expression.expressions.append(('mixin', 'two'))
    result = expression.json(evals=[], values=[])
    assert result['expression'] == 'one mixin two'


def test_expression_json_mixins_numbers(expression):
    expression.expressions.append(('mixin', 2))
    result = expression.json(evals=[], values=[])
    assert result['expression'] == 'one mixin 2'


def test_expression_json_no_evals(expression):
    assert expression.json() == 'one'


def test_expression_json_no_evals_expressions(item, expression):
    expression.expressions = [('1', item), ('2', 'two')]
    expression.json()


def test_expression_json_no_evals_json(item, expression):
    expression.expressions = [('', item)]
    result = expression.json()
    assert result == item.json()


def test_expression_json_expressions(expression):
    expression.expressions = [('', Expression('one')), ('', Expression('two'))]
    result = expression.json(evals=[], values=[])
    assert result['expression'] == 'one two'


def test_expression_json_json(item, expression):
    expression.expressions = [('', item)]
    result = expression.json(evals=[], values=[])
    assert result['expression'] == '{}'
    assert result['values'] == [item.json()]
