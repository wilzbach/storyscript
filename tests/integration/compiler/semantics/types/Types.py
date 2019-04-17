from pytest import mark, raises

from storyscript.Api import Api
from storyscript.exceptions import CompilerError, StoryError


def succeed(source):
    """
    Expect the source code to pass.
    """
    Api.loads(source)


def fail(source):
    """
    Expect the source code to error.
    """
    with raises(StoryError) as e:
        Api.loads(source)
    assert isinstance(e.value.error, CompilerError)


def run(source, should_fail):
    """
    If fail is set, expect the source code to error.
    Otherwise, expect it to pass.
    """
    if 'ANY' in source:
        pre = 'ANY = {}\n'
    elif 'fn_none' in source:
        pre = 'function fn_none\n\treturn\n'
    else:
        pre = ''
    source = pre + source
    if should_fail:
        fail(source)
    else:
        succeed(source)


all_types = {
    'boolean': 'true',
    'int': '1',
    'float': '1.5',
    'time': '1s',
    'Map[string,boolean]': '{"a": true}',
    'Map[string,int]': '{"a": 1}',
    'Map[string,float]': '{"a": 1.5}',
    'Map[boolean,string]': '{true: "a"}',
    'Map[int,string]': '{1: "a"}',
    'Map[float,string]': '{1.5: "a"}',
    'Map[string,string]': '{"a": "b"}',
    'regexp': '/foo/',
    'string': '"."',
    'List[boolean]': '[true]',
    'List[int]': '[0]',
    'List[float]': '[1.5]',
    'List[string]': '["."]',
    'List[time]': '[1s]',
    'any': 'ANY[0]',
    'none': 'fn_none()',
}


def build_type_permutations(types):
    """
    Builds test combinations from a allowed type dict.
    """
    tests = []
    for k, v in types.items():
        for r_k, r_v in all_types.items():
            left = (k, all_types[k])
            right = (r_k, r_v)
            tests.append((left, right, r_k not in v))
    return tests


###############################################################################
# Hashable types (for object keys)
###############################################################################


@mark.parametrize('el,should_pass', [
    ('regexp', False),
    ('List[int]', False),
    ('Map[string,int]', False),
    ('Map[int,string]', False),
    ('none', False),
    ('time', True),
    ('any', True),
    ('boolean', True),
])
def test_index_hashable(el, should_pass):
    el = all_types[el]
    run(f'a = {el}\nb = {{a: 0}}', should_fail=not should_pass)

###############################################################################
# Index (Lists + Objects)
###############################################################################


index_types = {
    'boolean': [],
    'int': [],
    'float': [],
    'time': [],
    'regexp': [],
    'string': ['boolean', 'int', 'any'],
    'List[boolean]': ['boolean', 'int', 'any'],
    'List[int]': ['boolean', 'int', 'any'],
    'List[float]': ['boolean', 'int', 'any'],
    'List[time]': ['boolean', 'int', 'any'],
    'List[string]': ['boolean', 'int', 'any'],
    'Map[string,int]': ['string', 'any'],
    'Map[int,string]': ['boolean', 'int', 'any'],
    'none': [],
    'any': ['boolean', 'int', 'float', 'time', 'string', 'any'],
}


@mark.parametrize('left,right,should_fail',
                  build_type_permutations(index_types))
def test_index(right, left, should_fail):
    run(f'a={left[1]}\nb={right[1]}\nc=a[b]', should_fail=should_fail)

###############################################################################
# Implicit assigns
###############################################################################


implicit_assigns = {
    'boolean': ['boolean'],
    'int': ['boolean', 'int'],
    'float': ['boolean', 'int', 'float'],
    'time': ['time'],
    'regexp': ['regexp'],
    'string': ['string'],
    'List[boolean]': ['List[boolean]'],
    'List[int]': ['List[boolean]', 'List[int]'],
    'List[float]': ['List[boolean]', 'List[int]', 'List[float]'],
    'List[time]': ['List[time]'],
    'List[string]': ['List[string]'],
    'Map[int,string]': ['Map[boolean,string]', 'Map[int,string]'],
    'Map[string,int]': ['Map[string,boolean]', 'Map[string,int]'],
    'Map[string,string]': ['Map[string,string]'],
    'none': [],
    'any': [k for k in all_types.keys() if k != 'none'],
}


@mark.parametrize('left,right,should_fail',
                  build_type_permutations(implicit_assigns))
def test_implicit_assign(right, left, should_fail):
    run(f'a = {left[1]}\na = {right[1]}', should_fail=should_fail)

###############################################################################
# ConvertibleToString
###############################################################################


@mark.parametrize('el', all_types.items())
def test_string_convertible(el):
    should_fail = el[0] == 'none'
    run(f'a="." + {el[1]}', should_fail=should_fail)
