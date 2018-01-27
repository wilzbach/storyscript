import os
import re

from ply import lex

from .exceptions import ScriptError


keywords = [
    'with', 'and',
    'has', 'to', 'as', 'into',
    'is', 'like', 'or',
    'contains', 'then',
    'if', 'else', 'elif',
    'try', 'catch',
    'while', 'from',
    'set', 'unset',
    'append', 'remove'
]


class Lexer:
    def __init__(self, optimize=True):
        self.build(optimize=optimize)

    def build(self, **kwargs):
        self.lexer = lex.lex(object=self, outputdir=os.getcwd(), **kwargs)
        self.lexer.filename = None
        self.token_stream = None

    def input(self, script):
        if not script.endswith('\n'):
            # we will insert a new line if the source has none
            script += '\n'
        self.lexer.input(script)
        self.lexer._offsets = self.get_offsets(script)
        self.token_stream = self._token_stream(self.lexer)

    def get_offsets(self, text):
        offsets = [0]
        for i in re.compile(r'\n').finditer(text):
            offsets.append(i.end())
        offsets.append(len(text))
        return offsets

    def token(self):
        try:
            x = next(self.token_stream)
            return x
        except StopIteration:
            return None

    def error(self, type, t, reason=None):
        lexer, lineno, lexpos = self.lexer, t.lineno, t.lexpos
        _lineno = lineno - 1
        start = lexer._offsets[_lineno]
        end = lexer._offsets[_lineno + 1] - 1
        text = lexer.lexdata[start:end]
        offset = lexpos - start + 1
        raise ScriptError([dict(
            message=reason,
            text=text,
            offset=offset,
            lineno=lineno
        )])

    states = (('variable', 'exclusive'),
              ('singleq1', 'exclusive'),
              ('singleq2', 'exclusive'),
              ('tripleq1', 'exclusive'),
              ('tripleq2', 'exclusive'))

    tokens = tuple(set((
        'ID',
        'PATH',
        'NI', 'INTO',
        'CONTAINER',

        'DIGITS',
        'BOOLEAN',
        'REGEX',
        'FROM',

        'ELSEIF', 'SET',

        # Operations
        'OPERATOR', 'GTLT', 'GTLTE', 'EQ', 'NE', 'ISNT',
        'LPAREN', 'RPAREN',

        # Strings
        'STRING_START_TRIPLE',
        'STRING_START_SINGLE',
        'STRING_CONTINUE',
        'STRING_END',

        # System
        'NEWLINE', 'WS', 'COMMA', 'INDENT', 'DEDENT', 'EOF',
    ) + tuple([k.upper() for k in keywords])))

    REQUIRES_INDENT = ('IF', 'ELSEIF', 'ELSE', 'SUITE')

    DIGITS = (
        r'\-?\$?(?:0[xX][0-9a-fA-F]+'
        r'|0[0-7]+'
        r'|(?:(?:0'
        r'|[1-9][0-9]*)\.[0-9]*(?:[eE][+-]?[0-9]+)?'
        r'|\.[0-9]+(?:[eE][+-]?[0-9]+)?'
        r'|(?:0|[1-9][0-9]*)(?:[eE][+-]?[0-9]+)?))\%?'
    )

    # Token
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_AND = r'\&|and|also'
    t_COMMA = r'\,'
    t_SET = r'set'

    INDEXES = (
        r'(\[(-?\d+)(((?:(-?\d+))\.{2})'
        r'|(\.{2}(?=(-?\d+))))?((?:\.{2})-?\d*)?\])?'
    )

    NAME = (
        r'((\.?_?[a-zA-Z]+(\-\w+)?\d*)'
        r'|(\[(\'[^\']+\'|"[^"]+"|\d+)\]))+'
    ) + INDEXES

    def t_CONTAINER(self, t):
        r'([\w\-\.]+/)?[\w\-\.]+/[\w\-\.]+((\:|\@)\w+)?'
        # [?HOSTNAME]/[PROJECT-ID]/[IMAGE][?:TAG|@DIGEST]
        return t

    def t_BOOLEAN(self, t):
        r'(true|false)(?=\s)'
        t.value = (t.value == 'true')
        return t

    def t_REGEX(self, t):
        r'\/[^\s]+\/i?'
        t.value = {
            '$OBJECT': 'regexp',
            'regexp': re.compile(t.value[1:-1]).pattern,
        }
        return t

    def t_EQ(self, t):
        r'((==?)|((is\s)?equals?(?=\s)(\sto)?))'
        t.value = '=='
        return t

    def t_NE(self, t):
        r'(!=|((is\s)?not\sequals?(\sto)?))'
        t.value = '!='
        return t

    def t_OPERATOR(self, t):
        r'(\+|-|\*|\/|\<=|\>=)'
        return t

    def t_GTLTE(self, t):
        r'(is\s)?(great|\<|\>|less)(er)?(\sth(e|a)n)?\sor\s(equal|={1,2})\sto'
        t.value = '<=' if 'less' in t.value or '<' in t.value else '>='
        return t

    def t_GTLT(self, t):
        r'(\<|\>|((is\s)?(great|\<|\>|less)(er)?(\sth(e|a)n)?))'
        t.value = '<' if 'less' in t.value or '<' in t.value else '>'
        return t

    def t_ISNT(self, t):
        r'((is\snot)|isnt|not)(?=\s)'
        t.value = 'isnot'
        return t

    def t_CONJ(self, t):
        r'((the)|a|(an))\s'
        pass

    def t_WS(self, t):
        r' [ \t]+ '
        if not hasattr(t.lexer, 'at_line_start') or t.lexer.at_line_start:
            return t

    def t_escaped_newline(self, t):
        r'\\\n'
        t.type = 'STRING_CONTINUE'
        t.lexer.lineno += 1

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
        t.type = 'NEWLINE'
        return t

    def t_ELSEIF(self, t):
        r'((else\s(if|unless))|elif|elseif)'
        return t

    def t_IF(self, t):
        r'(if|unless)'
        return t

    def t_FROM(self, t):
        r'(for|from)(?=\s)'
        return t

    def t_NI(self, t):
        r'(at|on|in)(?=\s)'
        return t

    @lex.TOKEN(NAME)
    def t_ID(self, t):
        if t.value.lower() in keywords:
            t.type = t.value.upper()
        else:
            t.type = 'PATH'
        return t

    @lex.TOKEN(DIGITS)
    def t_DIGITS(self, t):
        if t.value.find(','):
            if t.value.find('.') > t.value.find(','):
                # european style
                t.value = t.value.replace('.', '').replace(',', '.')
            else:
                t.value = t.value.replace(',', '')
        if t.value.endswith('%'):
            t.value = float(t.value[:-1]) / 100
        elif '.' in t.value:
            t.value = float(t.value)
        else:
            t.value = int(t.value)
        return t

    def t_error(self, t):  # pragma: no cover
        self.error('Syntax Error', t)

    def t_COMMENT(self, t):
        r'\#.*'
        pass

    t_variable_ignore = r' '

    @lex.TOKEN(NAME)
    def t_variable_PATH(self, t):
        return t

    def t_variable_error(self, t):
        self.error('Syntax Error', t)

    def t_singleq1_singleq2_tripleq1_tripleq2_escaped(self, t):
        r'\\(.|\n)'
        t.type = 'STRING_CONTINUE'
        t.lexer.lineno += t.value.count('\n')
        return t

    def t_start_triple_quoted_q1_string(self, t):
        r"'''"
        t.lexer.push_state('tripleq1')
        t.type = 'STRING_START_TRIPLE'
        t.value = t.value.split("'", 1)[0]
        return t

    def t_tripleq1_simple(self, t):
        r"((({|})?[^{}'])|('{0,2}[^'{}]+))+"
        t.type = 'STRING_CONTINUE'
        t.lexer.lineno += t.value.count('\n')
        return t

    def t_tripleq1_variable_START(self, t):
        r'{{'
        t.lexer.push_state('variable')

    def t_tripleq1_variable_end(self, t):
        r'}}'
        t.lexer.pop_state()

    def t_tripleq1_end(self, t):
        r"'''"
        t.type = 'STRING_END'
        t.lexer.pop_state()
        return t

    t_tripleq1_ignore = ''

    def t_tripleq1_error(self, t):
        self.error('Syntax Error', t)

    def t_start_triple_quoted_q2_string(self, t):
        r'"""'
        t.lexer.push_state('tripleq2')
        t.type = 'STRING_START_TRIPLE'
        t.value = t.value
        return t

    def t_tripleq2_simple(self, t):
        r'((({|})?[^{}"])|("{0,2}[^"{}]+))+'
        t.type = 'STRING_CONTINUE'
        t.lexer.lineno += t.value.count('\n')
        return t

    def t_tripleq2_variable_START(self, t):
        r'{{'
        t.lexer.push_state('variable')

    def t_tripleq2_end(self, t):
        r'"""'
        t.type = 'STRING_END'
        t.lexer.pop_state()
        return t

    t_tripleq2_ignore = ''

    def t_tripleq2_error(self, t):  # pragma: no cover
        self.error('Syntax Error', t)

    def t_start_single_quoted_q1_string(self, t):
        r"'"
        t.lexer.push_state('singleq1')
        t.type = 'STRING_START_SINGLE'
        t.value = t.value.split("'", 1)[0]
        return t

    def t_singleq1_simple(self, t):
        r"(({|})?[^{}'])+"
        t.type = 'STRING_CONTINUE'
        return t

    def t_singleq1_variable_START(self, t):
        r'{{'
        t.lexer.push_state('variable')

    def t_singleq1_end(self, t):
        r"'"
        t.type = 'STRING_END'
        t.lexer.pop_state()
        return t

    t_singleq1_ignore = ''

    def t_singleq1_error(self, t):  # pragma: no cover
        self.error(
            'Syntax Error',
            t,
            'EOL while scanning single quoted string'
        )

    def t_start_single_quoted_q2_string(self, t):
        r'"'
        t.lexer.push_state('singleq2')
        t.type = 'STRING_START_SINGLE'
        t.value = t.value.split('"', 1)[0]
        return t

    def t_singleq2_simple(self, t):
        r'(({|})?[^{}"])+'
        t.type = 'STRING_CONTINUE'
        return t

    def t_singleq2_variable_START(self, t):
        r'{{'
        t.lexer.push_state('variable')

    def t_singleq2_end(self, t):
        r'"'
        t.type = 'STRING_END'
        t.lexer.pop_state()
        return t

    t_singleq2_ignore = ''

    def t_singleq2_error(self, t):  # pragma: no cover
        self.error(
            'Syntax Error',
            t,
            'EOL while scanning single quoted string'
        )

    def TOKEN(self, type, lineno):
        tok = lex.LexToken()
        tok.type = type
        tok.value = None
        tok.lineno = lineno
        tok.lexpos = -100
        return tok

    def DEDENT(self, lineno):
        return self.TOKEN('DEDENT', lineno)

    def INDENT(self, lineno):
        return self.TOKEN('INDENT', lineno)

    def _token_stream(self, lexer):
        token_stream = iter(lexer.token, None)
        token_stream = self.annotate_indentation(lexer, token_stream)
        token_stream = self.synthesize_indentation_tokens(token_stream)
        token_stream = self._end(token_stream)
        return token_stream

    def annotate_indentation(self, lexer, token_stream):
        lexer.at_line_start = at_line_start = True
        must_indent_next_line = False
        next_real_token_must_indent = False
        for token in token_stream:
            token.at_line_start = at_line_start
            token.must_indent = False

            if token.type == 'NEWLINE':
                at_line_start = True
                if must_indent_next_line:
                    must_indent_next_line = False
                    next_real_token_must_indent = True

            elif token.type == 'WS':
                assert token.at_line_start is True
                at_line_start = True

            else:
                if token.type in self.REQUIRES_INDENT:
                    must_indent_next_line = True

                if next_real_token_must_indent:
                    token.must_indent = True
                    next_real_token_must_indent = False

                at_line_start = False

            yield token
            lexer.at_line_start = at_line_start

    def synthesize_indentation_tokens(self, token_stream):
        levels = [0]
        token = None
        depth = 0
        prev_was_ws = False
        for token in token_stream:
            if token.type == 'WS':
                # WS occurs at SOL only, skip till someobject real
                assert depth == 0
                depth = len(token.value)
                prev_was_ws = True
                continue

            if token.type == 'NEWLINE':
                depth = 0
                if prev_was_ws or token.at_line_start:
                    # ignore empty lines
                    continue
                yield token
                continue

            prev_was_ws = False

            if token.must_indent:
                # current depth must be larger than the previous depth
                if not (depth > levels[-1]):
                    self.error('Indentation Error', token)

                levels.append(depth)
                yield self.INDENT(token.lineno)

            elif token.at_line_start:
                # Must be on the same level or one of the previous levels
                if depth == levels[-1]:
                    # at the same level
                    pass
                elif depth > levels[-1]:
                    # yield token
                    yield self.INDENT(token.lineno)
                    levels.append(depth)
                else:
                    # back up; but only if it matches a previous level
                    i = levels.index(depth)
                    for _ in range(i + 1, len(levels)):
                        yield self.DEDENT(token.lineno)
                        levels.pop()

            yield token

        # dedent remaining levels
        if len(levels) > 1:
            assert token is not None
            for _ in range(1, len(levels)):
                yield self.DEDENT(token.lineno)

    def _end(self, token_stream):
        """Make the EOF for the token stream
        """
        tok = None
        for tok in token_stream:
            yield tok
        lineno = tok.lineno if tok is not None else 1
        yield self.TOKEN('EOF', lineno)
