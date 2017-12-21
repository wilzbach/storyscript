import pytest
from json import dumps
from ddt import ddt, data

import storyscript
from storyscript import exceptions


def expand_script(script):
    """ < line: line; line;
       > line\n\tline\nline
    """
    lines = script.replace(': ', ':\n').replace('; ', ';\n').split('\n')
    script = []
    indent = 0
    for line in lines:
        to = 0
        if line.endswith(':'):
            to = 1
            line = line[:-1]
        elif line.endswith(';'):
            to = -1
            line = line[:-1]
        script.append("".join(("\t"*indent, line)))
        indent = indent + to
    return "\n".join(script)


@pytest.mark.parametrize('script,expected', [
    ("foreach product: pass", {'args': [{'path': 'product'}], 'output': None, 'linenum': '1', 'method': 'foreach', 'parent': None, 'kwargs': None}),
    ("set x to _customer twitter username", {'output': None, 'args': ['x', {'path': '_customer.twitter.username'}], 'method': 'set', 'parent': None, 'kwargs': None, 'linenum': '1'}),
    ("set c to true", {'output': None, 'args': ['c', True], 'method': 'set', 'parent': None, 'kwargs': None, 'linenum': '1'}),
    ("set c to false", {'output': None, 'args': ['c', False], 'method': 'set', 'parent': None, 'kwargs': None, 'linenum': '1'}),
    ("set c to false; "*3, {'output': None, 'args': ['c', False], 'method': 'set', 'parent': None, 'kwargs': None, 'linenum': '1'}),
    ("set c to apple.orange[1]; ", {"output": None, "args": ["c", {"path": "apple.orange[1]"}], "method": "set", "parent": None, "kwargs": None, 'linenum': '1'}),
    ("set c to apple.orange['corey']; ", {"output": None, "args": ["c", {"path": "apple.orange['corey']"}], "method": "set", "parent": None, "kwargs": None, 'linenum': '1'}),
    ('set c to apple.orange["steve"]; ', {"output": None, "args": ["c", {"path": "apple.orange[\"steve\"]"}], "method": "set", "parent": None, "kwargs": None, 'linenum': '1'}),
    ('set c to apple.orange[1..2]; ', {"output": None, "args": ["c", {"path": "apple.orange[1..2]"}], "method": "set", "parent": None, "kwargs": None, 'linenum': '1'}),
    ("# hello; this", {}),
    ("set x to not_me", {"output": None, "args": ["x", {"path": "not_me"}], "method": "set", "parent": None, "kwargs": None, 'linenum': '1'}),
    ("set x to equals_it", {"output": None, "args": ["x", {"path": "equals_it"}], "method": "set", "parent": None, "kwargs": None, 'linenum': '1'}),
    ("x = equals_it", {"output": None, "args": ["x", {"path": "equals_it"}], "method": "set", "parent": None, "kwargs": None, 'linenum': '1'}),
    ("x is equals_it", {"output": None, "args": ["x", {"path": "equals_it"}], "method": "set", "parent": None, "kwargs": None, 'linenum': '1'}),
    ("set x to true_it", {"output": None, "args": ["x", {"path": "true_it"}], "method": "set", "parent": None, "kwargs": None, 'linenum': '1'}),
    ("append x into y", {'output': None, 'args': [{'path': 'x'}, {'path': 'y'}], 'method': 'append', 'parent': None, 'kwargs': None, 'linenum': '1'}),
    ("remove x from y", {'output': None, 'args': [{'path': 'x'}, {'path': 'y'}], 'method': 'remove', 'parent': None, 'kwargs': None, 'linenum': '1'}),
    ("if x is not equal to y: pass", {'output': None, 'args': [{'values': [{'path': 'x'}, {'path': 'y'}], 'expression': '{} != {}'}], 'method': 'if', 'parent': None, 'kwargs': None, 'linenum': '1'}),
    ("if name like /^Steve/: pass", {'output': None, 'args': [{'right': {'regexp': '^Steve'}, 'method': 'like', 'left': {'path': 'name'}}], 'method': 'if', 'parent': None, 'kwargs': None, 'linenum': '1'}),
    ("if name is like /^Steve/: pass", {'output': None, 'args': [{'right': {'regexp': '^Steve'}, 'method': 'like', 'left': {'path': 'name'}}], 'method': 'if', 'parent': None, 'kwargs': None, 'linenum': '1'}),
    ("if name is not like /.*joe$/: pass", {'output': None, 'args': [{'right': {'regexp': '.*joe$'}, 'method': 'notlike', 'left': {'path': 'name'}}], 'method': 'if', 'parent': None, 'kwargs': None, 'linenum': '1'}),
    ("if name like 'steve': pass", {'output': None, 'args': [{'right': {'value': 'steve'}, 'method': 'like', 'left': {'path': 'name'}}], 'method': 'if', 'parent': None, 'kwargs': None, 'linenum': '1'}),
    ("if name like 'steve with {{this}}': pass", {'output': None, 'args': [{'right': {'values': [{'path': 'this'}], 'string': 'steve with {}'}, 'method': 'like', 'left': {'path': 'name'}}], 'method': 'if', 'parent': None, 'kwargs': None, 'linenum': '1'}),
    ("if _c has name: pass", {'output': None, 'args': [{'right': {'path': 'name'}, 'method': 'has', 'left': {'path': '_c'}}], 'method': 'if', 'parent': None, 'kwargs': None, 'linenum': '1'}),
    ("if 'Hello' == 'George': pass", {'output': None, 'args': [{'values': [{'value': 'Hello'}, {'value': 'George'}], 'expression': '{} == {}'}], 'method': 'if', 'parent': None, 'kwargs': None, 'linenum': '1'}),
    ("if xyz < 10 and 50 < 30: pass", {'output': None, 'args': [{'values': [{'path': 'xyz'}], 'expression': '{} < 10.0 and 50.0 < 30.0'}], 'method': 'if', 'parent': None, 'kwargs': None, 'linenum': '1'}),
    ("if 10 == 10: pass", {'output': None, 'args': [{'values': [], 'expression': '10.0 == 10.0'}], 'method': 'if', 'parent': None, 'kwargs': None, 'linenum': '1'}),
    ("if ((15 * 2) + 10) / 3 * _c age: pass", {'output': None, 'args': [{'values': [{'path': '_c.age'}], 'expression': '( ( 15.0 * 2.0 ) + 10.0 ) / 3.0 * {}'}], 'method': 'if', 'parent': None, 'kwargs': None, 'linenum': '1'}),
    ("if (_c age > 23) and _c name like '{{_c name}} Eric': pass", {'output': None, 'args': [{'values': [{'path': '_c.age'}, {'right': {'values': [{'path': '_c.name'}], 'string': '{} Eric'}, 'method': 'like', 'left': {'path': '_c.name'}}], 'expression': '( {} > 23.0 ) and {}'}], 'method': 'if', 'parent': None, 'kwargs': None, 'linenum': '1'}),
    ("if _c points >= 10 or _c age <= 50: pass", {'output': None, 'args': [{'values': [{'path': '_c.points'}, {'path': '_c.age'}], 'expression': '{} >= 10.0 or {} <= 50.0'}], 'method': 'if', 'parent': None, 'kwargs': None, 'linenum': '1'}),
    ("if cart contains cheezy: pass", {'output': None, 'args': [{'left': {'path': 'cart'}, 'method': 'contains', 'right': {'path': 'cheezy'}}], 'method': 'if', 'parent': None, 'kwargs': None, 'linenum': '1'}),
    ("if s in 'Hello world!': pass", {'output': None, 'args': [{'right': {'value': 'Hello world!'}, 'method': 'in', 'left': {'path': 's'}}], 'method': 'if', 'parent': None, 'kwargs': None, 'linenum': '1'}),
    ("if not s: pass", {"output": None, "args": [{"right": True, "method": "isnot", "left": {"path": "s"}}], "method": "if", "parent": None, "kwargs": None, 'linenum': '1'}),
    ("if 'Hello world!' contains s: pass", {'output': None, 'args': [{'left': {'value': 'Hello world!'}, 'method': 'contains', 'right': {'path': 's'}}], 'method': 'if', 'parent': None, 'kwargs': None, 'linenum': '1'}),
    ('with _customer: pass', {'output': None, 'args': [{'path': '_customer'}], 'method': 'with', 'parent': None, 'kwargs': None, 'linenum': '1'}),
    ("method variable, 'Good morning!'", {'output': None, 'args': [{'path': 'variable'}, {'value': 'Good morning!'}], 'method': 'method', 'parent': None, 'kwargs': None, 'linenum': '1'}),
    ("if 1 < 2: pass; else: pass", {'output': None, 'args': [{'values': [], 'expression': '1.0 < 2.0'}], 'method': 'if', 'parent': None, 'kwargs': None, 'linenum': '1'}),
    ("if 1 < 2: pass; else if 1 > 2: pass; else: pass", {'output': None, 'args': [{'values': [], 'expression': '1.0 < 2.0'}], 'method': 'if', 'parent': None, 'kwargs': None, 'linenum': '1'}),
    ("if 1 < 2: pass; else if 1 > 2: pass; else if 1 > 2: pass; else: pass", {'output': None, 'args': [{'values': [], 'expression': '1.0 < 2.0'}], 'method': 'if', 'parent': None, 'kwargs': None, 'linenum': '1'}),
    ("unless 1 < 2: pass; else: pass", {'output': None, 'args': [{'values': [], 'expression': '1.0 < 2.0'}], 'method': 'unless', 'parent': None, 'kwargs': None, 'linenum': '1'}),
    ("if _p in customer.favorites and _p not in cart: pass", {'output': None, 'args': [{'values': [{'right': {'path': 'customer.favorites'}, 'method': 'in', 'left': {'path': '_p'}}, {'left': {'path': '_p'}, 'method': 'excludes', 'right': {'path': 'cart'}}], 'expression': '{} and {}'}], 'method': 'if', 'parent': None, 'kwargs': None, 'linenum': '1'}),
    ('''log "string {{v}} string": --status """: {{a}} string 'string'"string'"string\n\t string {{variable variable}} with quotes \'\'\'string \'\'\'"""''', {'output': None, 'args': [{'values': [{'path': 'v'}], 'string': 'string {} string'}], 'method': 'log', 'parent': None, 'kwargs': {'status': {'values': [{'path': 'a'}, {'path': 'variable.variable'}], 'string': '{} string \'string\'"string\'"string\n\t\t\t string {} with quotes \'\'\'string \'\'\''}}, 'linenum': '1'}),
    ("""log '''string {{v}}\\n\\n string'''""", {'output': None, 'args': [{'values': [{'path': 'v'}], 'string': 'string {}\\n\\n string'}], 'method': 'log', 'parent': None, 'kwargs': None, 'linenum': '1'}),
    ('log "...{{value}}..."', {'output': None, 'args': [{'values': [{'path': 'value'}], 'string': '...{}...'}], 'method': 'log', 'parent': None, 'kwargs': None, 'linenum': '1'}),
    ('log \\\n "...{{value}}..."', {'output': None, 'args': [{'values': [{'path': 'value'}], 'string': '...{}...'}], 'method': 'log', 'parent': None, 'kwargs': None, 'linenum': '1'}),
    ('method arg, arg as result', {'output': 'result', 'args': [{'path': 'arg'}, {'path': 'arg'}], 'method': 'method', 'parent': None, 'kwargs': None, 'linenum': '1'}),
    # testing tokens work
    ('method ontop', {"output": None, "args": [{"path": "ontop"}], "method": "method", "parent": None, "kwargs": None, 'linenum': '1'}),
    ('method inventory', {"output": None, "args": [{"path": "inventory"}], "method": "method", "parent": None, "kwargs": None, 'linenum': '1'}),
    ('method fortune', {"output": None, "args": [{"path": "fortune"}], "method": "method", "parent": None, "kwargs": None, 'linenum': '1'}),
    ('method as result: --kwarg', {'output': 'result', 'args': None, 'method': 'method', 'parent': None, 'kwargs': {'kwarg': True}, 'linenum': '1'}),
    ('method as result: --kwarg blah', {'output': 'result', 'args': None, 'method': 'method', 'parent': None, 'kwargs': {'kwarg': {'path': 'blah'}}, 'linenum': '1'}),
    ('method as result: --kwarg blah; : --kwarg again', {'output': 'result', 'args': None, 'method': 'method', 'parent': None, 'kwargs': {'kwarg': [{'path': 'blah'}, {'path': 'again'}]}, 'linenum': '1'}),
    ('while 10 > 9: pass', {"output": None, "args": [{"values": [], "expression": "10.0 > 9.0"}], "method": "while", "parent": None, "kwargs": None, 'linenum': '1'}),
    ('while x < 2: pass', {"output": None, "args": [{"values": [{"path": "x"}], "expression": "{} < 2.0"}], "method": "while", "parent": None, "kwargs": None, 'linenum': '1'}),
    ('while true as ok: pass', {"output": 'ok', "args": [True], "method": "while", "parent": None, "kwargs": None, 'linenum': '1'}),
    ('unset apples', {"output": None, "args": ["apples"], "method": "unset", "parent": None, "kwargs": None, 'linenum': '1'}),
])
def test_methods(script, expected):
    print(expand_script(script))
    result = storyscript.parse(expand_script(script+"\n")).json()
    print(dumps(result['script'].get('1', {}), indent=2))
    print(result['script'].get('1'))
    assert result['script'].get('1', {}) == expected


@pytest.mark.parametrize('script,expected', [
  ('block menu: try: do this; catch: if true: retry; else: pass; ; else: goto menu', {"11": {"linenum": "11", "output": None, "args": [{"path": "menu"}], "method": "goto", "parent": "10", "kwargs": None}, "10": {"linenum": "10", "output": None, "args": None, "method": "else", "parent": "1", "kwargs": None}, "1": {"linenum": "1", "output": None, "args": [{"path": "menu"}], "method": "block", "parent": None, "kwargs": None}, "3": {"linenum": "3", "output": None, "args": [{"path": "this"}], "method": "do", "parent": "2", "kwargs": None}, "2": {"linenum": "2", "output": None, "args": None, "method": "try", "parent": "1", "kwargs": None}, "5": {"linenum": "5", "output": None, "args": [True], "method": "if", "parent": "4", "kwargs": None}, "4": {"linenum": "4", "output": None, "args": None, "method": "catch", "parent": "1", "kwargs": None}, "7": {"linenum": "7", "output": None, "args": None, "method": "else", "parent": "4", "kwargs": None}, "6": {"linenum": "6", "output": None, "args": None, "method": "retry", "parent": "5", "kwargs": None}, "8": {"linenum": "8", "output": None, "args": None, "method": "pass", "parent": "7", "kwargs": None}}),
  ('try: pass; catch: pass', {"1": {"linenum": "1", "output": None, "args": None, "method": "try", "parent": None, "kwargs": None}, "3": {"linenum": "3", "output": None, "args": None, "method": "catch", "parent": None, "kwargs": None}, "2": {"linenum": "2", "output": None, "args": None, "method": "pass", "parent": "1", "kwargs": None}, "4": {"linenum": "4", "output": None, "args": None, "method": "pass", "parent": "3", "kwargs": None}}),
  ('if true: pass; else if true: pass', {"1": {"linenum": "1", "output": None, "args": [True], "method": "if", "parent": None, "kwargs": None}, "3": {"linenum": "3", "output": None, "args": [True], "method": "elif", "parent": None, "kwargs": None}, "2": {"linenum": "2", "output": None, "args": None, "method": "pass", "parent": "1", "kwargs": None}, "4": {"linenum": "4", "output": None, "args": None, "method": "pass", "parent": "3", "kwargs": None}}),
  ('unless 1=1: pass; else unless 1=0: pass; else: pass', {"1": {"linenum": "1", "output": None, "args": [{"values": [], "expression": "1.0 == 1.0"}], "method": "unless", "parent": None, "kwargs": None}, "3": {"linenum": "3", "output": None, "args": [{"values": [], "expression": "1.0 == 0.0"}], "method": "unlessif", "parent": None, "kwargs": None}, "2": {"linenum": "2", "output": None, "args": None, "method": "pass", "parent": "1", "kwargs": None}, "5": {"linenum": "5", "output": None, "args": None, "method": "else", "parent": None, "kwargs": None}, "4": {"linenum": "4", "output": None, "args": None, "method": "pass", "parent": "3", "kwargs": None}, "6": {"linenum": "6", "output": None, "args": None, "method": "pass", "parent": "5", "kwargs": None}}),
])
def test_full(script, expected):
    print(expand_script(script))
    result = storyscript.parse(expand_script(script+"\n")).json()
    print(dumps(result['script'], indent=2))
    assert result['script'] == expected


@pytest.mark.parametrize('script,exception', [
    ("set results to first 6 unique myList prices", SyntaxError),
    ("set results to last 15 unique myList prices", SyntaxError),
    ("set x to last 10 stores where name like 'efe'", SyntaxError),
    ("set x to 'a {{b '", SyntaxError),
    ("set x to 'a", SyntaxError),
    ("if \"a < 10", SyntaxError),
    ('set x to "a {{b "', SyntaxError),
    ("set x to '''a''", SyntaxError),
    ("set x to '''a\n", SyntaxError),
    ("set x to '''{{black-n-white**'''", SyntaxError),
    ('set x to """a""', SyntaxError),
    ('if this; that', SyntaxError),
    ('set x to sum of w x y z for "1"', SyntaxError)
])
def test_errors(script, exception):
    print(expand_script(script))
    with pytest.raises(exception):
        print(storyscript.parse(expand_script(script+"\n")).json())
