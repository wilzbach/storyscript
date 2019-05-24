from pytest import mark

from storyscript.Api import Api
from storyscript.exceptions import CompilerError


def is_boolean(op):
    """
    Tests whether an operation requires conversion to boolean.
    """
    return op in ['or', 'and', '!']


def is_cmp(op):
    """
    Tests whether an operation requires comparing two types.
    """
    return op in ['<', '<=', '==', '!=', '>', '>=']


def is_equal(op):
    """
    Tests whether an operation requires equality comparison.
    """
    return op in ['==', '!=']


def is_sum(op):
    """
    Tests whether it's the sum operation
    """
    return op == '+'


def is_sub(op):
    """
    Tests whether it's the subtraction operation
    """
    return op == '-'


def is_any(op):
    """
    Returns True.
    """
    return True


def op_builder(a, b, swapped=False):
    """
    Returns a list of all possible operations between a and b
    """
    ops = [
        '+', '-', '*', '/', '%', '^', '<', '<=', '==', '!=', '>', '>=', 'or',
        'and'
    ]
    res = []
    for op in ops:
        res.append((f'{a} {op} {b}', op))
        if swapped:
            res.append((f'{b} {op} {a}', op))

    if not swapped:
        res.append((f'! {a}', '!'))
    return res


def runner(source, op=None, allowed=None, pre=''):
    if allowed is None:
        allowed = []
    else:
        # op must be defined when allowed is used
        assert op is not None

    in_source = f'{pre}a = {source}'
    if not isinstance(allowed, list):
        allowed = [allowed]

    s = Api.loads(in_source, features={'globals': True})
    if any(allowed_fn(op) for allowed_fn in allowed):
        s.check_success()
    else:
        e = s.errors()[0]
        assert isinstance(e.error, CompilerError)


###############################################################################
# Test operations on RegExpType
###############################################################################

@mark.parametrize('source,op', op_builder('re', 're'))
def test_regex_regex_ops(source, op):
    runner(source, op, allowed=is_equal, pre='re=/foo/\n')


@mark.parametrize('source,op', op_builder('re', '1', swapped=True))
def test_regex_int_ops(source, op):
    runner(source, pre='re=/foo/\n')


@mark.parametrize('source,op', op_builder('re', 'true', swapped=True))
def test_regex_boolean_ops(source, op):
    runner(source, pre='re=/foo/\n')


@mark.parametrize('source,op', op_builder('re', '"."', swapped=True))
def test_regex_string_ops(source, op):
    runner(source, op, allowed=is_sum, pre='re=/foo/\n')


###############################################################################
# Test operations on MapType
###############################################################################

@mark.parametrize('source,op', op_builder('{"a": 1}', '{"b": 2}'))
def test_map_map_ops(source, op):
    runner(source, op, allowed=[is_equal, is_boolean])


@mark.parametrize('source,op', op_builder('{"a": 1}', '2', swapped=True))
def test_map_int_ops(source, op):
    runner(source, op, allowed=is_boolean)


@mark.parametrize('source,op', op_builder('{"a": 1}', 'true', swapped=True))
def test_map_boolean_ops(source, op):
    runner(source, op, allowed=is_boolean)


@mark.parametrize('source,op', op_builder('{"a": 1}', '"."', swapped=True))
def test_map_string_ops(source, op):
    runner(source, op, allowed=[is_sum, is_boolean])


###############################################################################
# Test operations on ListType
###############################################################################

@mark.parametrize('source,op', op_builder('[1]', '[2]'))
def test_list_list_ops(source, op):
    runner(source, op, allowed=[is_equal, is_boolean, is_sum])


@mark.parametrize('source,op', op_builder('[1]', '2', swapped=True))
def test_list_int_ops(source, op):
    runner(source, op, allowed=is_boolean)


@mark.parametrize('source,op', op_builder('[1]', 'true', swapped=True))
def test_list_boolean_ops(source, op):
    runner(source, op, allowed=is_boolean)


@mark.parametrize('source,op', op_builder('[1]', '"."', swapped=True))
def test_list_string_ops(source, op):
    runner(source, op, allowed=[is_sum, is_boolean])


###############################################################################
# Test operations on TimeType
###############################################################################

@mark.parametrize('source,op', op_builder('1m', '2m'))
def test_time_time_ops(source, op):
    runner(source, op, allowed=[is_equal, is_boolean, is_sum, is_sub, is_cmp])


@mark.parametrize('source,op', op_builder('1m', '2', swapped=True))
def test_time_int_ops(source, op):
    runner(source, op, allowed=is_boolean)


@mark.parametrize('source,op', op_builder('1m', 'true', swapped=True))
def test_time_boolean_ops(source, op):
    runner(source, op, allowed=is_boolean)


@mark.parametrize('source,op', op_builder('1m', '"."', swapped=True))
def test_time_string_ops(source, op):
    runner(source, op, allowed=[is_sum, is_boolean])

###############################################################################
# Test operations on ObjectType
###############################################################################


@mark.parametrize('source,op', op_builder('app', 'app'))
def test_object_object_ops(source, op):
    runner(source, op, allowed=[is_equal, is_boolean])


@mark.parametrize('source,op', op_builder('app', '2', swapped=True))
def test_object_int_ops(source, op):
    runner(source, op, allowed=is_boolean)


@mark.parametrize('source,op', op_builder('app', 'true', swapped=True))
def test_object_boolean_ops(source, op):
    runner(source, op, allowed=is_boolean)


@mark.parametrize('source,op', op_builder('app', '"."', swapped=True))
def test_object_string_ops(source, op):
    runner(source, op, allowed=[is_sum, is_boolean])


###############################################################################
# Test operations on NoneType
#
# No operations are allowed.
###############################################################################

NONE = 'function none_fn\n\treturn\n'


@mark.parametrize('source,op', op_builder('none_fn()', 'none_fn()'))
def test_none_none_ops(source, op):
    runner(source, op, allowed=None, pre=NONE)


@mark.parametrize('source,op', op_builder('none_fn()', '2', swapped=True))
def test_none_int_ops(source, op):
    runner(source, op, allowed=None, pre=NONE)


@mark.parametrize('source,op', op_builder('none_fn()', 'true', swapped=True))
def test_none_boolean_ops(source, op):
    runner(source, op, allowed=None, pre=NONE)


@mark.parametrize('source,op', op_builder('none_fn()', '"."', swapped=True))
def test_none_string_ops(source, op):
    runner(source, op, allowed=None, pre=NONE)


###############################################################################
# Test operations on FloatType
###############################################################################


@mark.parametrize('source,op', op_builder('1.5', '2.5'))
def test_float_float_ops(source, op):
    runner(source, op, allowed=is_any)


@mark.parametrize('source,op', op_builder('1.5', '2', swapped=True))
def test_float_int_ops(source, op):
    runner(source, op, allowed=is_any)


@mark.parametrize('source,op', op_builder('1.5', 'true', swapped=True))
def test_float_boolean_ops(source, op):
    runner(source, op, allowed=is_any)


@mark.parametrize('source,op', op_builder('1.5', '"."', swapped=True))
def test_float_string_ops(source, op):
    runner(source, op, allowed=[is_sum, is_boolean])


###############################################################################
# Test operations on BooleanType
###############################################################################

@mark.parametrize('source,op', op_builder('true', 'false'))
def test_boolean_boolean_ops(source, op):
    runner(source, op, allowed=is_any)


@mark.parametrize('source,op', op_builder('true', '2', swapped=True))
def test_boolean_int_ops(source, op):
    runner(source, op, allowed=is_any)


@mark.parametrize('source,op', op_builder('true', '"."', swapped=True))
def test_boolean_string_ops(source, op):
    runner(source, op, allowed=[is_sum, is_boolean])


###############################################################################
# Test operations on IntType
###############################################################################

@mark.parametrize('source,op', op_builder('1', '2'))
def test_int_int_ops(source, op):
    runner(source, op, allowed=is_any)


@mark.parametrize('source,op', op_builder('1', '"."', swapped=True))
def test_int_string_ops(source, op):
    runner(source, op, allowed=[is_sum, is_boolean])


###############################################################################
# Test operations on StringType
###############################################################################

@mark.parametrize('source,op', op_builder('"a"', '"b"'))
def test_string_string_ops(source, op):
    runner(source, op, allowed=[is_equal, is_boolean, is_sum, is_cmp])


###############################################################################
# Test operations on AnyType
###############################################################################

ANY = 'any_obj = {}\nany_var=any_obj[0]\n'


@mark.parametrize('source,op', op_builder('any_var', 'any_var'))
def test_any_any_ops(source, op):
    runner(source, op, allowed=is_any, pre=ANY)


@mark.parametrize('source,op', op_builder('any_var', 'true', swapped=True))
def test_any_boolean_ops(source, op):
    runner(source, op, allowed=is_any, pre=ANY)


@mark.parametrize('source,op', op_builder('any_var', '2', swapped=True))
def test_any_int_ops(source, op):
    runner(source, op, allowed=is_any, pre=ANY)


@mark.parametrize('source,op', op_builder('any_var', '2.5', swapped=True))
def test_any_float_ops(source, op):
    runner(source, op, allowed=is_any, pre=ANY)


@mark.parametrize('source,op', op_builder('any_var', '"."', swapped=True))
def test_any_string_ops(source, op):
    runner(source, op, allowed=[is_equal, is_boolean, is_sum, is_cmp], pre=ANY)


@mark.parametrize('source,op', op_builder('any_var', '[1]', swapped=True))
def test_any_list_ops(source, op):
    runner(source, op, allowed=[is_equal, is_boolean, is_sum], pre=ANY)


@mark.parametrize('source,op', op_builder('any_var', '{"a": 1}', swapped=True))
def test_any_obj_ops(source, op):
    runner(source, op, allowed=[is_equal, is_boolean], pre=ANY)


@mark.parametrize('source,op', op_builder('any_var', '1m', swapped=True))
def test_any_time_ops(source, op):
    allowed = [is_equal, is_boolean, is_sum, is_sub, is_cmp]
    runner(source, op, allowed=allowed, pre=ANY)


@mark.parametrize('source,op', op_builder('any_var', 're', swapped=True))
def test_any_regex_ops(source, op):
    runner(source, op, allowed=is_equal, pre=ANY + 're=/foo/\n')
