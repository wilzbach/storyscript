# -*- coding: utf-8 -*-
from lark import Lark
from lark.common import UnexpectedToken

from pytest import fixture, raises

from storyscript.parser import CustomIndenter, Ebnf, Parser


@fixture
def ebnf(magic, parser):
    ebnf = magic()
    parser.ebnf = ebnf
    return ebnf


def test_parser_init():
    parser = Parser()
    assert parser.algo == 'lalr'


def test_parser_init_algo():
    parser = Parser(algo='algo')
    assert parser.algo == 'algo'


def test_parser_line(parser, ebnf):
    parser.line()
    defintions = (['values'], ['assignments'], ['operation'], ['statements'],
                  ['comment'], ['command'], ['block'])
    ebnf.rules.assert_called_with('line', *defintions)


def test_parser_whitespaces(parser, ebnf):
    parser.whitespaces()
    tokens = (('ws', '(" ")+'), ('nl', r'/(\r?\n[\t ]*)+/'))
    ebnf.tokens.assert_called_with(*tokens, inline=True, regexp=True)


def test_parser_indentation(parser, ebnf):
    parser.indentation()
    tokens = (('indent', '<INDENT>'), ('dedent', '<DEDENT>'))
    ebnf.tokens.assert_called_with(*tokens, inline=True)


def test_parser_spaces(patch, parser):
    patch.many(Parser, ['whitespaces', 'indentation'])
    parser.spaces()
    assert Parser.whitespaces.call_count == 1
    assert Parser.indentation.call_count == 1


def test_parser_block(parser, ebnf):
    parser.block()
    definition = 'line _NL [_INDENT block+ _DEDENT]'
    ebnf.rule.assert_called_with('block', definition, raw=True)


def test_parser_number(parser, ebnf):
    parser.number()
    ebnf.loads.assert_called_with(['int', 'float'])
    ebnf.rules.assert_called_with('number', ['int'], ['float'])


def test_parser_string(parser, ebnf):
    parser.string()
    tokens = (('single_quoted', "/'([^']*)'/"),
              ('double_quoted', '/"([^"]*)"/'))
    ebnf.tokens.assert_called_with(*tokens, regexp=True)
    definitions = (['single_quoted'], ['double_quoted'])
    ebnf.rules.assert_called_with('string', *definitions)


def test_parser_boolean(parser, ebnf):
    parser.boolean()
    ebnf.tokens.assert_called_with(('true', 'true'), ('false', 'false'))
    ebnf.rules.assert_called_with('boolean', ['true'], ['false'])


def test_parser_filepath(parser, ebnf):
    parser.filepath()
    ebnf.token.assert_called_with('filepath', '/`([^"]*)`/', regexp=True)


def test_parser_values(patch, parser, ebnf):
    patch.many(Parser, ['number', 'string', 'list', 'objects', 'filepath',
                        'boolean'])
    parser.values()
    assert Parser.number.call_count == 1
    assert Parser.string.call_count == 1
    assert Parser.boolean.call_count == 1
    assert Parser.filepath.call_count == 1
    assert Parser.list.call_count == 1
    assert Parser.objects.call_count == 1
    definitions = (['number'], ['string'], ['boolean'], ['filepath'], ['list'],
                   ['objects'])
    ebnf.rules.assert_called_with('values', *definitions)


def test_parser_operator(parser, ebnf):
    parser.operator()
    tokens = (('plus', '+'), ('minus', '-'), ('multiplier', '*'),
              ('division', '/'))
    ebnf.tokens.assert_called_with(*tokens)
    definitions = (['plus'], ['minus'], ['multiplier'], ['division'])
    ebnf.rules.assert_called_with('operator', *definitions)


def test_parser_operation(patch, parser, ebnf):
    patch.object(Parser, 'operator')
    parser.operation()
    assert Parser.operator.call_count == 1
    definitions = (('values', 'ws', 'operator', 'ws', 'values'),
                   ('values', 'operator', 'values'))
    ebnf.rules.assert_called_with('operation', *definitions)


def test_parser_list(parser, ebnf):
    parser.list()
    tokens = (('comma', ','), ('osb', '['), ('csb', ']'))
    ebnf.tokens.assert_called_with(*tokens, inline=True)
    definition = '_OSB (values (_COMMA values)*)? _CSB'
    ebnf.rule.assert_called_with('list', definition, raw=True)


def test_parser_key_value(parser, ebnf):
    parser.key_value()
    ebnf.token.assert_called_with('colon', ':', inline=True)
    ebnf.rule.assert_called_with('key_value', ('string', 'colon', 'values'))


def test_parser_objects(patch, parser, ebnf):
    patch.object(Parser, 'key_value')
    parser.objects()
    assert Parser.key_value.call_count == 1
    ebnf.tokens.assert_called_with(('ocb', '{'), ('ccb', '}'), inline=True)
    rule = '_OCB (key_value (_COMMA key_value)*)? _CCB'
    ebnf.rule.assert_called_with('objects', rule, raw=True)


def test_parser_path_fragment(parser, ebnf):
    parser.path_fragment()
    ebnf.load.assert_called_with('word')
    ebnf.token.assert_called_with('dot', '.', inline=True)
    definitions = (('dot', 'word'), ('osb', 'int', 'csb'),
                   ('osb', 'string', 'csb'))
    ebnf.rules.assert_called_with('path_fragment', *definitions)


def test_parser_path(patch, parser, ebnf):
    patch.object(Parser, 'path_fragment')
    parser.path()
    Parser.path_fragment.call_count == 1
    ebnf.rule.assert_called_with('path', 'WORD (path_fragment)*', raw=True)


def test_parser_assignments(patch, parser, ebnf):
    patch.object(Parser, 'path')
    parser.assignments()
    assert Parser.path.call_count == 1
    ebnf.rule.assert_called_with('assignments', ('path', 'equals',
                                    'values'))
    ebnf.token.assert_called_with('equals', '=')


def test_parser_comparisons(parser, ebnf):
    parser.comparisons()
    tokens = (('greater', '>'), ('greater_equal', '>='), ('lesser', '<'),
              ('lesser_equal', '<='), ('not', '!='), ('equal', '=='))
    ebnf.tokens.assert_called_with(*tokens)
    definitions = (['greater'], ['greater_equal'], ['lesser'],
                   ['lesser_equal'], ['not'], ['equal'])
    ebnf.rules.assert_called_with('comparisons', *definitions)


def test_parser_if_statement(parser, ebnf):
    parser.if_statement()
    definitions = (('if', 'ws', 'word'),
                   ('if', 'ws', 'word', 'ws', 'comparisons', 'ws', 'word'))
    ebnf.rules.assert_called_with('if_statement', *definitions)
    ebnf.token.assert_called_with('if', 'if')


def test_parser_else_statement(parser, ebnf):
    parser.else_statement()
    ebnf.token.assert_called_with('else', 'else')
    ebnf.rule.assert_called_with('else_statement', ['else'])


def test_parser_elseif_statement(parser, ebnf):
    parser.elseif_statement()
    rule = 'ELSE _WS? IF _WS WORD [_WS comparisons _WS WORD]?'
    ebnf.rule.assert_called_with('elseif_statement', rule, raw=True)


def test_parser_for_statement(parser, ebnf):
    parser.for_statement()
    definition = ('for', 'ws', 'word', 'ws', 'in', 'ws', 'word')
    ebnf.rule.assert_called_with('for_statement', definition)
    ebnf.tokens.assert_called_with(('for', 'for'), ('in', 'in'))


def test_parser_foreach_statement(parser, ebnf):
    parser.foreach_statement()
    definition = ('foreach', 'ws', 'word', 'ws', 'as', 'ws', 'word')
    ebnf.rule.assert_called_with('foreach_statement', definition)
    ebnf.tokens.assert_called_with(('foreach', 'foreach'), ('as', 'as'))


def test_parser_wait_statement(parser, ebnf):
    parser.wait_statement()
    definitions = (('wait', 'ws', 'word'), ('wait', 'ws', 'string'))
    ebnf.rules.assert_called_with('wait_statement', *definitions)
    ebnf.token.assert_called_with('wait', 'wait')


def test_parser_next_statement(parser, ebnf):
    parser.next_statement()
    ebnf.token.assert_called_with('next', 'next')
    definitions = (('next', 'ws', 'word'), ('next', 'ws', 'filepath'))
    ebnf.rules.assert_called_with('next_statement', *definitions)


def test_parser_statements(patch, parser, ebnf):
    patch.many(Parser, ['if_statement', 'for_statement', 'foreach_statement',
                        'wait_statement', 'next_statement', 'else_statement',
                        'elseif_statement'])
    parser.statements()
    assert Parser.if_statement.call_count == 1
    assert Parser.for_statement.call_count == 1
    assert Parser.foreach_statement.call_count == 1
    assert Parser.wait_statement.call_count == 1
    assert Parser.next_statement.call_count == 1
    assert Parser.else_statement.call_count == 1
    assert Parser.elseif_statement.call_count == 1
    child_rules = (['if_statement'], ['for_statement'], ['foreach_statement'],
                   ['wait_statement'], ['next_statement'], ['else_statement'],
                   ['elseif_statement'])
    ebnf.rules.assert_called_with('statements', *child_rules)


def test_parser_options(parser, ebnf):
    parser.options()
    definitions = (('dash', 'dash', 'word', 'ws', 'word'),
                   ('dash', 'dash', 'word', 'ws', 'values'))
    ebnf.rules.assert_called_with('options', *definitions)


def test_parser_arguments(patch, parser, ebnf):
    patch.object(Parser, 'options')
    parser.arguments()
    assert Parser.options.call_count == 1
    definitions = (['ws', 'values'], ['ws', 'word'], ['ws', 'options'])
    ebnf.rules.assert_called_with('arguments', *definitions)


def test_parser_command(patch, parser, ebnf):
    patch.object(Parser, 'arguments')
    parser.command()
    assert Parser.arguments.call_count == 1
    rule = 'RUN _WS WORD arguments*|WORD arguments*'
    ebnf.rule.assert_called_with('command', rule, raw=True)


def test_parser_comment(parser, ebnf):
    parser.comment()
    ebnf.rule.assert_called_with('comment', ['comment'])
    ebnf.token.assert_called_with('comment', '/#(.*)/', regexp=True)


def test_parser_get_ebnf(patch, parser):
    patch.init(Ebnf)
    assert isinstance(parser.get_ebnf(), Ebnf)


def test_parser_indenter(patch, parser):
    patch.init(CustomIndenter)
    assert isinstance(parser.indenter(), CustomIndenter)


def test_parser_build_grammar(patch, parser):
    patch.many(Parser, ['line', 'spaces', 'values', 'assignments', 'operation',
                        'statements', 'comment', 'block', 'comparisons',
                        'command', 'get_ebnf'])
    result = parser.build_grammar()
    assert parser.ebnf == parser.get_ebnf()
    parser.ebnf.start.assert_called_with('_NL? block')
    assert Parser.line.call_count == 1
    assert Parser.spaces.call_count == 1
    assert Parser.values.call_count == 1
    assert Parser.assignments.call_count == 1
    assert Parser.operation.call_count == 1
    assert Parser.statements.call_count == 1
    assert Parser.comment.call_count == 1
    assert Parser.block.call_count == 1
    assert Parser.comparisons.call_count == 1
    assert Parser.command.call_count == 1
    assert result == parser.ebnf.build()


def test_parser_parse(patch, parser):
    """
    Ensures the build method can build the grammar
    """
    patch.init(Lark)
    patch.object(Lark, 'parse')
    patch.many(Parser, ['build_grammar', 'indenter'])
    result = parser.parse('source')
    Lark.__init__.assert_called_with(Parser.build_grammar(),
                                     parser=parser.algo,
                                     postlex=Parser.indenter())
    Lark.parse.assert_called_with('source')
    assert result == Lark.parse()


def test_parser_parse_unexpected_token(patch, parser):
    patch.init(Lark)
    patch.object(Lark, 'parse', side_effect=UnexpectedToken('', '', '', ''))
    patch.many(Parser, ['build_grammar', 'indenter'])
    assert parser.parse('source') is None
