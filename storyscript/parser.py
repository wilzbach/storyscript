import os
import sys

from ply import yacc

from .exceptions import ScriptError
from .lexer import Lexer
from .tree import Comparison, Condition, \
    Expression, Method, Path, Program, String


class Parser:
    def __init__(self, optimize=True, debug=False):
        self.lexer = Lexer(optimize)
        self.tokens = self.lexer.tokens

        self.parser = yacc.yacc(
            module=self,
            start='program',
            outputdir=os.getcwd(),
            optimize=optimize,
            debug=debug
        )

    def parse(self, source, debug=False, using_cli=False):
        self.debug = debug
        self.errors = []
        self.using_cli = using_cli
        story = self.parser.parse(source, lexer=self.lexer, debug=debug)
        if story is None or self.errors:
            raise ScriptError(self.errors)
        else:
            return story

    def p_error(self, t):
        self.errors.append(dict(lineno=t.lineno, token=t.type, value=t.value))
        if self.using_cli:
            sys.stdout.write(
                (
                    '\033[91mSyntax Error:\033[0m '
                    '\033[96mLine:\033[0m {}, '
                    '\033[96mToken:\033[0m {}, '
                    '\033[96mValue:\033[0m {}\n'
                ).format(t.lineno, t.type, t.value)
            )

        self.parser.restart()
        return t

    def p_program(self, p):
        """program : story
                   | WS"""
        p[0] = Program(self, p[1])

    def p_paths(self, p):
        """paths : PATH"""
        p[0] = Path(self, p.lineno(1), p[1])

    def p_stmts(self, p):
        """stmts : stmt
                 | stmts stmt"""
        if len(p) == 3:
            p[1].append(p[2])
            p[0] = p[1]
        else:
            p[0] = [p[1]]

    def p_suite(self, p):
        """suite : NEWLINE INDENT stmts DEDENT"""
        p[0] = p[3]

    def p_if(self, p):
        """stmt : IF expressions suite
                | IF expressions suite else_if
                | IF expressions suite else_if ELSE suite
                | IF expressions suite ELSE suite"""
        p[0] = [Method(
            p[1].lower(),
            self,
            p.lineno(1),
            args=(p[2], ),
            suite=p[3],
            enter=p[3][0].lineno
        )]
        if len(p) == 5:
            p[0][0].exit = p[4][0].lineno
            p[0].extend(p[4])
        elif len(p) == 6:
            p[0][0].exit = p[5][0].lineno
            p[0].append(Method('else', self, p.lineno(4), suite=p[5]))
        elif len(p) == 7:
            p[0][0].exit = p[4][0].lineno
            p[4][-1].exit = p[6][0].lineno
            p[0].extend(p[4])
            p[0].append(Method('else', self, p.lineno(5), suite=p[6]))

    def p_elseif(self, p):
        """else_if : ELSEIF expressions suite
                   | else_if ELSEIF expressions suite"""
        if len(p) == 4:
            p[0] = [Method(
                'unlessif' if 'unless' in p[1] else 'elif',
                self,
                p.lineno(1),
                args=(p[2], ),
                suite=p[3],
                enter=p[3][0].lineno
            )]
        else:
            p[1][-1].exit = p.lineno(2)
            p[1].append(Method(
                'unlessif' if 'unless' in p[2] else 'elif',
                self, p.lineno(2),
                args=(p[3], ),
                suite=p[4],
                enter=p[4][0].lineno
            ))
            p[0] = p[1]

    def p_try(self, p):
        """stmt : TRY suite
                | TRY suite CATCH suite"""
        p[0] = [Method(
            'try', self, p.lineno(1),
            suite=p[2],
            enter=p[2][0].lineno
        )]
        if len(p) == 5:
            p[0][0].exit = p[4][0].lineno
            p[0].append(Method(
                'catch', self, p.lineno(3),
                suite=p[4]
            ))

    def p_output(self, p):
        """output : AS PATH
                  |"""
        if len(p) == 3:
            p[0] = Path(self, p.lineno(1), p[2])

    def p_next_story(self, p):
        """stmt : NEXT variable NEWLINE"""
        p[0] = Method(
            'next', self, p.lineno(1),
            args=(p[2], )
        )

    def p_keyword(self, p):
        """stmt : CONTINUE args NEWLINE
                | BREAK args NEWLINE
                | EXIT NEWLINE
                | PASS NEWLINE
                | END NEWLINE"""
        p[0] = Method(
            p[1].lower(), self, p.lineno(1),
            args=(p[2], ) if len(p) == 4 else None
        )

    def p_wait(self, p):
        """stmt : WAIT arg suite
                | WAIT arg NEWLINE"""
        args = ('wait', self, p.lineno(1))
        kwargs = {'args': (p[2], ), 'enter': None, 'exit': None, 'suite': None}
        if type(p[3]) is list:
            kwargs['suite'] = p[3]
            kwargs['enter'] = p[3][0].lineno
            kwargs['exit'] = p[3][-1].lineno
        p[0] = Method(*args, **kwargs)

    def p_container(self, p):
        """stmt : PATH args NEWLINE
                | CONTAINER args NEWLINE"""
        p[0] = Method(
            'run', self, p.lineno(1),
            container=p[1],
            args=p[2]
        )

    def p_container_suite(self, p):
        """stmt : PATH args suite
                | CONTAINER args suite"""
        p[0] = Method(
            'run', self, p.lineno(1),
            container=p[1],
            args=p[2],
            suite=p[3]
        )

    def p_story(self, p):
        """story : stmt  EOF
                 | stmts EOF"""
        p[0] = p[1]

    def p_set_eq(self, p):
        """SEQ : paths TO
               | paths IS
               | paths EQ
               | SET paths TO
               | SET paths IS
               | SET paths EQ"""
        p[0] = p[1] if len(p) == 3 else p[2]

    def p_stmt_set_path_container(self, p):
        """stmt : SEQ PATH args NEWLINE
                | SEQ CONTAINER args NEWLINE"""
        p[0] = Method(
            'run', self, p[1].lineno,
            output=p[1],
            container=p[2],
            args=p[3]
        )

    def p_stmt_set_path(self, p):
        """stmt : SEQ expressions NEWLINE"""
        p[0] = Method(
            'set', self, p[1].lineno,
            args=(p[1], p[2])
        )

    def p_stmt_set_path_if(self, p):
        """stmt : SEQ expressions \
                  IF expressions NEWLINE"""
        p[0] = Method(
            'set', self, p[1].lineno,
            args=(
                p[1],
                Condition(
                    p[4], p[3].lower() == 'if', p[2], None
                )
            )
        )

    def p_stmt_set_path_if_else(self, p):
        """stmt : SEQ expressions \
                  IF expressions \
                  ELSE expressions NEWLINE"""
        p[0] = Method(
            'set', self, p[1].lineno,
            args=(
                p[1],
                Condition(
                    p[4], p[3].lower() == 'if', p[2], p[6]
                )
            )
        )

    def p_stmt_set_path_if_then(self, p):
        """stmt : SEQ IF expressions \
                  THEN expressions NEWLINE"""
        p[0] = Method(
            'set', self, p[1].lineno,
            args=(
                p[1],
                Condition(
                    p[3], p[2].lower() == 'if', p[5], None
                )
            )
        )

    def p_stmt_set_path_if_then_else(self, p):
        """stmt : SEQ IF expressions \
                  THEN expressions \
                  ELSE expressions NEWLINE"""
        p[0] = Method(
            'set', self, p[1].lineno,
            args=(
                p[1],
                Condition(
                    p[3], p[2].lower() == 'if', p[5], p[7]
                )
            )
        )

    def p_stmt_with(self, p):
        """stmt : WITH paths output suite"""
        p[0] = Method(
            'with', self, p.lineno(1),
            args=(p[2], ),
            output=p[3],
            suite=p[4]
        )

    def p_stmt_while_expression(self, p):
        """stmt : WHILE expressions output suite"""
        p[0] = Method(
            'while', self, p.lineno(1),
            args=(p[2], ),
            output=p[3],
            suite=p[4]
        )

    def p_stmt_while_container(self, p):
        """stmt : WHILE PATH PATH args output suite
                | WHILE CONTAINER PATH args output suite"""
        p[0] = Method(
            'while', self, p.lineno(1),
            container=p[2],
            args=[p[3]] + (p[4] or []),
            output=p[5],
            suite=p[6]
        )

    def p_stmt_for_item_in_list(self, p):
        """stmt : FOR PATH IN variable suite"""
        p[0] = Method('for', self, p.lineno(1), args=[p[2], p[4]], suite=p[5])

    def p_expressions(self, p):
        """expressions : expression
                       | expressions AND expression
                       | expressions OR expression"""
        if len(p) == 4:
            p[1].add(p[2], p[3])
            p[0] = p[1]
        else:
            p[0] = p[1]

    def p_expression_variable(self, p):
        """expression : variable"""
        p[0] = Expression(p[1])

    def p_expression_has(self, p):
        """expression : variable HAS variable"""
        p[0] = Expression(Comparison(p[1], 'has', p[3]))

    def p_expression_is_isnt(self, p):
        """expression : NOT variable"""
        p[0] = Expression(Comparison(p[2], 'is not', True))

    def p_expression_not_in(self, p):
        """expression : variable ISNT IN variable"""
        p[0] = Expression(Comparison(p[1], 'not in', p[4]))

    def p_expression_contains(self, p):
        """expression : variable CONTAINS variable
                      | variable IN variable"""
        p[0] = Expression(Comparison(p[1], p[2], p[3]))

    def p_expression_like(self, p):
        """expression : variable LIKE variable
                      | variable IS LIKE variable
                      | variable ISNT LIKE variable
                      | variable LIKE REGEX
                      | variable IS LIKE REGEX
                      | variable ISNT LIKE REGEX"""
        if len(p) == 5:
            if p[2] == 'is not':
                p[0] = Expression(Comparison(p[1], 'not like', p[4]))
            else:
                p[0] = Expression(Comparison(p[1], 'like', p[4]))
        else:
            p[0] = Expression(Comparison(p[1], 'like', p[3]))

    def p_expression_is(self, p):
        """expression : variable IS variable
                      | variable ISNT variable"""
        p[0] = Expression(Comparison(p[1], p[2], p[3]))

    def p_expression_math(self, p):
        """expression : variable OPERATOR variable
                      | variable GTLT variable
                      | variable GTLTE variable
                      | variable EQ variable
                      | variable NE variable"""
        p[1].add(p[2], p[3])
        p[0] = p[1]

    def p_expression_group(self, p):
        """expression : LPAREN expressions RPAREN"""
        p[2].expressions.insert(0, ('', '('))
        p[2].expressions.append(('', ')'))
        p[0] = p[2]

    def p_list(self, p):
        """list : LBRACKET list_items RBRACKET"""
        p[0] = {
            '$OBJECT': 'list',
            'items': p[2]
        }

    def p_listitems(self, p):
        """list_items : variable
                      | list_items COMMA variable"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[1].append(p[3])
            p[0] = p[1]

    def p_object(self, p):
        """object : LBRACE object_keys RBRACE"""
        p[0] = p[2]

    def p_object_keys(self, p):
        """object_keys : object_key
                       | object_keys COMMA object_key"""
        if len(p) == 4:
            p[1]['items'].insert(0, p[3]['items'][0])
        p[0] = p[1]

    def p_object_key(self, p):
        """object_key : PATH COLON object
                      | PATH COLON variable
                      | string COLON object
                      | string COLON variable"""
        p[0] = {
            '$OBJECT': 'dict',
            'items': [
                (p[1], p[3])
            ]
        }

    def p_string_content(self, p):
        """string_content : paths
                          | STRING_CONTINUE"""
        p[0] = p[1]

    def p_string_inner(self, p):
        """string_inner : string_content
                        | string_inner string_content"""
        if len(p) == 2:
            p[0] = String(data=p[1])
        else:
            p[1].add(p[2])
            p[0] = p[1]

    def p_string(self, p):
        """string : STRING_START_SINGLE string_inner STRING_END
                  | STRING_START_TRIPLE string_inner STRING_END"""
        p[0] = p[2]

    def p_variable(self, p):
        """variable : paths
                    | string
                    | list
                    | object
                    | BOOLEAN
                    | DIGITS"""
        p[0] = Expression(p[1])

    def p_container_arg(self, p):
        """arg : expression
               | FLAG"""
        p[0] = p[1]

    def p_args(self, p):
        """args : arg
                | args arg
                | args COMMA arg
                |"""
        if len(p) == 2:
            p[0] = [p[1]]
        elif len(p) == 3:
            p[1].append(p[2])
            p[0] = p[1]
        elif len(p) == 4:
            if p[1]:
                p[1].append(p[3])
            else:
                p[1] = [p[3]]
            p[0] = p[1]
