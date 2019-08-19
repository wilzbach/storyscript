# -*- coding: utf-8 -*-
from pytest import mark

from storyscript.Story import Story


def story_format(source):
    return Story(source, features={}).parse(parser=None).format()


@mark.parametrize('source,expected', [
    ('a=1', 'a = 1'),
    ('a=+1', 'a = 1'),
    ('a=-1', 'a = -1'),
    ('a="f"', 'a = "f"'),
    ('a=1.5', 'a = 1.5'),
    ('a=+1.5', 'a = 1.5'),
    ('a=-1.5', 'a = -1.5'),
    ('a=true', 'a = true'),
    ('a=false', 'a = false'),
    ('a=not true', 'a = not true'),
    ('a=1+2', 'a = 1 + 2'),
    ('a=1-2', 'a = 1 - 2'),
    ('a=1*2', 'a = 1 * 2'),
    ('a=1/2', 'a = 1 / 2'),
    ('a=1%2', 'a = 1 % 2'),
    ('a=1==2', 'a = 1 == 2'),
    ('a=1!=2', 'a = 1 != 2'),
    ('a=1 and  2', 'a = 1 and 2'),
    ('a=1 or  2', 'a = 1 or 2'),
    ('a=1 < 2', 'a = 1 < 2'),
    ('a=1 <= 2', 'a = 1 <= 2'),
    ('a=1 >= 2', 'a = 1 >= 2'),
    ('a=1 > 2', 'a = 1 > 2'),
    ('f=[1,2]', 'f = [1, 2]'),
    ('a=1+2-3', 'a = 1 + 2 - 3'),
    ('a=(1+2)-3', 'a = (1 + 2) - 3'),
    ('a=5+7*(2-3) and 4 + (2 or 3)', 'a = 5 + 7 * (2 - 3) and 4 + (2 or 3)'),
    ('a={"a":"b"}', 'a = {"a": "b"}'),
    ('a={"a":"b"+"c"}', 'a = {"a": "b" + "c"}'),
    ('a={1:2}', 'a = {1: 2}'),
    ('a={1:2*3}', 'a = {1: 2 * 3}'),
    ('a={a:b}', 'a = {a: b}'),
    ('a=5s', 'a = 5s'),
    ('a=5ms', 'a = 5ms'),
    ('a=5m', 'a = 5m'),
    ('a=5d', 'a = 5d'),
    ('a=1m5s', 'a = 1m5s'),
    ('a=3h1m5s', 'a = 3h1m5s'),
    ('a=4d3h1m5s', 'a = 4d3h1m5s'),
    ('r=/foo/', 'r = /foo/'),
    ('r2=/foo/g', 'r2 = /foo/g'),
    ('k=a.b', 'k = a.b'),
    ('k=a[0]', 'k = a[0]'),
    ('k=a["b"]', 'k = a["b"]'),
    ('k=a[b]', 'k = a[b]'),
    ('f=a[0:]', 'f = a[0:]'),
    ('f=a[0 : 2]', 'f = a[0:2]'),
    ('f=a[ : 2]', 'f = a[:2]'),
    ('f=a[a:]', 'f = a[a:]'),
    ('f=a[a : b]', 'f = a[a:b]'),
    ('f=a[ : b]', 'f = a[:b]'),
    ('a= null', 'a = null'),
    ('my_service call arg1 :1 arg2: 2',
     'my_service call arg1:1 arg2:2'),
    ('foo=my_service call arg1 :1 arg2: 2',
     'foo = my_service call arg1:1 arg2:2'),
    ('foo=(my_service call arg1 :1 arg2: 2)',
     'foo = (my_service call arg1:1 arg2:2)'),
    ('foo=(my_service call arg1 :1 arg2: 2) + (my_service call arg1:3 arg2:4)',
     'foo = (my_service call arg1:1 arg2:2) + '
     '(my_service call arg1:3 arg2:4)'),
    ('return  ', 'return'),
    ('return  foo', 'return foo'),
    ('break ', 'break'),
    ('throw  foo', 'throw foo'),
    ('throw  "foo"', 'throw "foo"'),
    ('throw', 'throw'),
    ('a=b.mutation()', 'a = b.mutation()'),
    ('a=1 .mutation()', 'a = 1.mutation()'),
    ('a=fun()', 'a = fun()'),
    ('a=b.mutation(a:1)', 'a = b.mutation(a:1)'),
    ('a=b.mutation(a:1  b:2)', 'a = b.mutation(a:1 b:2)'),
    ('a=1.mutation(a:1)', 'a = 1.mutation(a:1)'),
    ('a=1.mutation(a:1  b:2)', 'a = 1.mutation(a:1 b:2)'),
    ('a=1.mutation(a:1  b:2  c: 3)', 'a = 1.mutation(a:1 b:2 c:3)'),
    ('a=b.mutation().mutation()', 'a = b.mutation().mutation()'),
    ('a=1.mutation().mutation()', 'a = 1.mutation().mutation()'),
    ('a=1.mutation(a:1 b: 2 c:3).mutation(a:4 b:5 c:6)',
     'a = 1.mutation(a:1 b:2 c:3).mutation(a:4 b:5 c:6)'),
    ('a=1.mut(a:1 b: 2 c:3).mut(a:4 b:5 c:6).mut(c:9 d:10)',
     'a = 1.mut(a:1 b:2 c:3).mut(a:4 b:5 c:6).mut(c:9 d:10)'),
    ('a=a.mutation(a:1 b: 2 c:3).mutation(a:4 b:5 c:6)',
     'a = a.mutation(a:1 b:2 c:3).mutation(a:4 b:5 c:6)'),
    ('a=a.mut(a:1 b: 2 c:3).mut(a:4 b:5 c:6).mut(c:9 d:10)',
     'a = a.mut(a:1 b:2 c:3).mut(a:4 b:5 c:6).mut(c:9 d:10)'),
    ('a=fun(a:"1")', 'a = fun(a:"1")'),
    ('a=fun(a:1  b:"b")', 'a = fun(a:1 b:"b")'),
    ('a="5" as  boolean', 'a = "5" as boolean'),
    ('a="5" as  int', 'a = "5" as int'),
    ('a="5" as  float', 'a = "5" as float'),
    ('a="5" as  time', 'a = "5" as time'),
    ('a="5" as  regex', 'a = "5" as regex'),
    ('a="5" as  any', 'a = "5" as any'),
    ('a="5" as  List[int]', 'a = "5" as List[int]'),
    ('a="5" as  List[List[float]]', 'a = "5" as List[List[float]]'),
    ('a="5" as  Map[string, boolean]', 'a = "5" as Map[string, boolean]'),
])
def test_compiler_pretty_print_format(source, expected):
    """
    Ensures that AST nodes are properly pretty printed.
    """
    assert story_format(source) == expected


@mark.parametrize('source,expected', [
    ('when foo bar\n  x=0', 'when foo bar\n  x = 0'),
    # ('http server\n  x=0', 'http server\n  x = 0'),
    ('foreach items as i\n  x=0', 'foreach items as i\n  x = 0'),
    ('foreach items as a,b\n  x=0', 'foreach items as a, b\n  x = 0'),
    ('while true\n  x=0', 'while true\n  x = 0'),
])
def test_compiler_pretty_print_format_block(source, expected):
    """
    Ensures that AST nodes are properly pretty printed.
    """
    assert story_format(source) == expected


def test_compiler_pretty_print_format_if_elseif_else_block():
    result = """if a
    c = 0
else if b
    c = 0
else
    c = 0
"""
    story_format("""if a
    c=0
else if b
    c=0
else
    c=0
""") == result


def test_compiler_pretty_print_format_if_elseif_block():
    result = """if a
    c = 0
else if b
    c = 0
"""
    story_format("""if a
    c=0
else if b
    c=0
""") == result


def test_compiler_pretty_print_format_if_else_block():
    result = """if a
    c = 0
else
    c = 0
"""
    story_format("""if a
    c=0
else
    c=0
""") == result


def test_compiler_pretty_print_format_if_block():
    result = """if a
    c = 0
"""
    story_format("""if a
    c=0
""") == result


def test_compiler_pretty_print_format_try_catch_finally():
    result = """try
    x = 0
catch
    x = 1
finally
    x = 2
"""
    story_format("""try
    x = 0
catch
    x = 1
finally
    x = 2
""") == result


def test_compiler_pretty_print_format_try_catch():
    result = """try
    x = 0
catch
    x = 1
"""
    story_format("""try
    x = 0
catch
    x = 1
""") == result


def test_compiler_pretty_print_format_try():
    result = """try
    x = 0
"""
    story_format("""try
    x = 0
""") == result


def test_compiler_pretty_print_format_function():
    result = """function my_fun foo:int returns string
  x = 0
"""
    story_format("""function my_fun foo:int returns string
    x = 0
""") == result


def test_compiler_pretty_print_format_function_no_args():
    result = """function my_fun  returns string
  x = 0
"""
    story_format("""function my_fun returns string
    x = 0
""") == result


def test_compiler_pretty_print_format_function_no_args_no_return():
    result = """function my_fun
  x = 0
"""
    story_format("""function my_fun
    x = 0
""") == result


def test_compiler_pretty_print_format_function_return():
    result = """function my_fun foo:int returns string
  return a+2
"""
    story_format("""function my_fun foo:int returns string
    return a + 2
""") == result


def test_compiler_pretty_print_format_service_block():
    result = """http server
    c = 0
"""
    story_format("""http server
    c=0
""") == result


def test_compiler_pretty_print_format_service_block_output():
    result = """http server as x
    c = 0
"""
    story_format("""http server as x
    c=0
""") == result


def test_compiler_pretty_print_format_when_block():
    result = """when server listen
    c = 0
"""
    story_format("""when server_listen
    c=0
""") == result


def test_compiler_pretty_print_format_when_block_output():
    result = """when server listen as x
    c = 0
"""
    story_format("""when server_listen as x
    c=0
""") == result
