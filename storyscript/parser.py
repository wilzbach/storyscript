import os
import sys

from ply import yacc

from . import ast
from .exceptions import ScriptError
from .lexer import Lexer


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
                   | WS ID ELIF"""
        p[0] = ast.Program(self, p[1])

    def p_paths(self, p):
        """paths : PATH"""
        p[0] = ast.Path(self, p.lineno(1), p[1])

    # ----------
    # Statements
    # ----------
    def p_stmts(self, p):
        """stmts : stmt
                 | stmts stmt"""
        if len(p) == 3:
            p[1].append(p[2])
            p[0] = p[1]
        else:
            p[0] = [p[1]]

    # ----------
    # Operations
    # ----------
    def p_suite(self, p):
        """suite : NEWLINE INDENT stmts DEDENT"""
        p[0] = p[3]

    # ----------------------------
    # IF ... [ELSE IF ..] ... ELSE
    # ----------------------------
    def p_if(self, p):
        """stmt : IF expressions suite
                | IF expressions suite else_if
                | IF expressions suite else_if ELSE suite
                | IF expressions suite         ELSE suite"""
        p[0] = [ast.Method(
            p[1].lower(),
            self,
            p.lineno(1),
            suite=p[3],
            args=(p[2], ),
            enter=p[3][0].lineno
        )]
        if len(p) == 5:
            p[0][0].exit = p[4][0].lineno
            p[0].extend(p[4])
        elif len(p) == 6:
            p[0][0].exit = p[5][0].lineno
            p[0].append(ast.Method('else', self, p.lineno(4), suite=p[5]))
        elif len(p) == 7:
            p[0][0].exit = p[4][0].lineno
            p[4][-1].exit = p[6][0].lineno
            p[0].extend(p[4])
            p[0].append(ast.Method('else', self, p.lineno(5), suite=p[6]))

    def p_elseif(self, p):
        """else_if :         ELSEIF expressions suite
                   | else_if ELSEIF expressions suite"""
        if len(p) == 4:
            p[0] = [ast.Method(
                'unlessif' if 'unless' in p[1] else 'elif',
                self,
                p.lineno(1),
                suite=p[3],
                args=(p[2], ),
                enter=p[3][0].lineno
            )]
        else:
            p[1][-1].exit = p.lineno(2)
            p[1].append(ast.Method(
                'unlessif' if 'unless' in p[2] else 'elif',
                self,
                p.lineno(2),
                suite=p[4],
                args=(p[3], ),
                enter=p[4][0].lineno
            ))
            p[0] = p[1]

    # ----------
    # Exceptions
    # ----------
    def p_try(self, p):
        """stmt : TRY suite
                | TRY suite CATCH suite"""
        p[0] = [ast.Method(
            'try', self, p.lineno(1),
            suite=p[2],
            enter=p[2][0].lineno
        )]
        if len(p) == 5:
            p[0][0].exit = p[4][0].lineno
            p[0].append(ast.Method(
                'catch', self, p.lineno(3),
                suite=p[4]
            ))

    # ----------
    # Containers
    # ----------
    def p_output(self, p):
        """output : AS PATH
                  |"""
        if len(p) == 3:
            p[0] = ast.Path(self, p.lineno(1), p[2]).json()

    def p_params(self, p):
        """params : args output NEWLINE"""
        p[0] = dict(args=p[1], output=p[2])

    def p_container(self, p):
        """stmt : PATH params
                | CONTAINER params"""
        p[0] = ast.Method(
            'run',
            parser=self,
            lineno=p.lineno(1),
            container=p[1],
            **p[2]
        )

    def p_story(self, p):
        """story : stmt  EOF
                 | stmts EOF"""
        p[0] = p[1]

    # -------------
    # Set/Push/With
    # -------------
    def p_set_eq(self, p):
        """SEQ : paths TO
               | paths IS
               | paths EQ
               | SET paths TO
               | SET paths IS
               | SET paths EQ"""
        p[0] = p[1] if len(p) == 3 else p[2]

    def p_stmt_set_path(self, p):
        """stmt : SEQ expressions NEWLINE"""
        p[0] = ast.Method(
            'set',
            parser=self,
            lineno=p[1].lineno,
            args=(p[1], p[2])
        )

    def p_stmt_set_path_if(self, p):
        """stmt : SEQ expressions IF expressions NEWLINE"""
        p[0] = ast.Method(
            'set',
            parser=self,
            lineno=p[1].lineno,
            args=(
                p[1],
                ast.Condition(
                    p[3].lower() == 'if',
                    p[4],
                    p[2],
                    None
                )
            )
        )

    def p_stmt_set_path_if_else(self, p):
        """stmt : SEQ expressions \
                  IF expressions \
                  ELSE expressions NEWLINE"""
        p[0] = ast.Method(
            'set',
            parser=self,
            lineno=p[1].lineno,
            args=(
                p[1],
                ast.Condition(
                    p[3].lower() == 'if',
                    p[4],
                    p[2],
                    p[6]
                )
            )
        )

    def p_stmt_set_path_if_then(self, p):
        """stmt : SEQ IF expressions \
                  THEN expressions NEWLINE"""
        p[0] = ast.Method(
            'set',
            parser=self,
            lineno=p[1].lineno,
            args=(
                p[1],
                ast.Condition(
                    p[2].lower() == 'if',
                    p[3],
                    p[5],
                    None
                )
            )
        )

    def p_stmt_set_path_if_then_else(self, p):
        """stmt : SEQ IF expressions \
                  THEN expressions \
                  ELSE expressions NEWLINE"""
        p[0] = ast.Method(
            'set',
            parser=self,
            lineno=p[1].lineno,
            args=(
                p[1],
                ast.Condition(
                    p[2].lower() == 'if',
                    p[3],
                    p[5],
                    p[7]
                )
            )
        )

    def p_stmt_unset_path(self, p):
        """stmt : UNSET paths NEWLINE"""
        p[0] = ast.Method(
            'unset',
            parser=self,
            lineno=p.lineno(1),
            args=p[2].paths
        )

    def p_stmt_append(self, p):
        """stmt : APPEND variable TO paths NEWLINE
                | APPEND variable INTO paths NEWLINE"""
        p[0] = ast.Method(
            'append',
            parser=self,
            lineno=p.lineno(1),
            args=(p[2], p[4])
        )

    def p_stmt_remove(self, p):
        """stmt : REMOVE variable FROM paths NEWLINE"""
        p[0] = ast.Method(
            'remove',
            parser=self,
            lineno=p.lineno(1),
            args=(p[2], p[4])
        )

    def p_stmt_with(self, p):
        """stmt : WITH paths suite"""
        p[0] = ast.Method(
            'with',
            parser=self,
            lineno=p.lineno(1),
            suite=p[3],
            args=(p[2], )
        )

    # -----------
    # While Loops
    # -----------
    def p_stmt_while(self, p):
        """stmt : WHILE paths output suite
                | WHILE expressions output suite"""
        p[0] = ast.Method(
            'while',
            parser=self,
            lineno=p.lineno(1),
            output=p[3],
            suite=p[4],
            args=(p[2], )
        )

    # -----------
    # Expressions
    # -----------
    def p_expressions(self, p):
        """expressions : variable
                       | expressions AND variable
                       | expressions OR  variable"""
        if len(p) == 4:
            p[0] = p[1].add(p[2], p[3])
        else:
            p[0] = p[1]

    # --------------------
    # Expressions > Method
    # --------------------
    def p_expression_has(self, p):
        """variable : paths HAS paths"""
        p[0] = ast.Expression(ast.Comparison(p[1], 'has', p[3]))

    def p_expression_is_isnt(self, p):
        """variable : ISNT variable"""
        p[0] = ast.Expression(ast.Comparison(p[2], p[1], True))

    def p_expression_not_in(self, p):
        """variable : paths ISNT NI paths"""
        p[0] = ast.Expression(ast.Comparison(p[1], 'excludes', p[4]))

    def p_expression_contains(self, p):
        """variable : variable CONTAINS variable
                      | variable    NI    variable"""
        if p[2] == 'contains':
            p[0] = ast.Expression(ast.Comparison(p[1], 'contains', p[3]))
        else:
            p[0] = ast.Expression(ast.Comparison(p[1], 'in', p[3]))

    def p_expression_like(self, p):
        """variable : paths      LIKE variable
                    | paths IS   LIKE variable
                    | paths ISNT LIKE variable
                    | paths      LIKE REGEX
                    | paths IS   LIKE REGEX
                    | paths ISNT LIKE REGEX"""
        if len(p) == 5:
            if p[2] == 'isnot':
                p[0] = ast.Expression(ast.Comparison(p[1], 'notlike', p[4]))
            else:
                p[0] = ast.Expression(ast.Comparison(p[1], 'like', p[4]))
        else:
            p[0] = ast.Expression(ast.Comparison(p[1], 'like', p[3]))

    def p_expression_is(self, p):
        """variable : paths IS   variable
                      | paths ISNT variable"""
        p[0] = ast.Expression(ast.Comparison(
            p[1],
            'is' if p[2] == 'is' else 'isnt',
            p[3]
        ))

    # ------------------
    # Expressions > Math
    # ------------------
    def p_expression_math(self, p):
        """variable : variable OPERATOR variable
                    | variable GTLT     variable
                    | variable GTLTE    variable
                    | variable EQ       variable
                    | variable NE       variable"""
        p[0] = p[1].add(p[2], p[3])

    def p_expression_group(self, p):
        """variable : LPAREN expressions RPAREN"""
        p[2].expressions.insert(0, ('', '('))
        p[2].expressions.append(('', ')'))
        p[0] = p[2]

    # -------
    # Strings
    # -------
    def p_string_content(self, p):
        """string_content : paths
                          | STRING_CONTINUE"""
        p[0] = p[1]

    def p_string_inner(self, p):
        """string_inner :              string_content
                        | string_inner string_content"""
        if len(p) == 2:
            p[0] = ast.String(data=p[1])
        else:
            p[0] = p[1].add(p[2])

    def p_string(self, p):
        """string : STRING_START_SINGLE string_inner STRING_END
                  | STRING_START_TRIPLE string_inner STRING_END"""
        p[0] = p[2]

    # --------
    # Variable
    # --------
    def p_variable(self, p):
        """variable : paths
                    | string
                    | BOOLEAN
                    | DIGITS"""
        p[0] = ast.Expression(p[1])

    # ---------
    # Arguments
    # ---------
    def p_args(self, p):
        """args : variable
                | args variable
                | args COMMA variable
                |"""
        if len(p) == 2:
            p[0] = [p[1]]
        elif len(p) == 3:
            p[1].append(p[2])
            p[0] = p[1]
        elif len(p) == 4:
            p[1].append(p[3])
            p[0] = p[1]
