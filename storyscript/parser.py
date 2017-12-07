import os
import sys
from ply import yacc

from . import ast
from .lexer import Lexer
from .exceptions import ScriptError

try:
    from . import lextab, yacctab
except ImportError:  # pragma: no cover
    lextab, yacctab = 'lextab', 'yacctab'


class Parser(object):
    def __init__(self, lex_optimize=False, lextab=lextab, yacc_optimize=False, yacctab=yacctab, yacc_debug=False):
        self.lexer = Lexer()
        self.lexer.build(optimize=lex_optimize, lextab=lextab)
        self.tokens = self.lexer.tokens
        self.parser = yacc.yacc(module=self, tabmodule=yacctab, start="program",
                                outputdir=os.path.dirname(__file__), optimize=yacc_optimize, debug=yacc_debug)

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
            sys.stdout.write("\033[91mSyntax Error:\033[0m \033[96mLine:\033[0m %s, \033[96mToken:\033[0m %s, \033[96mValue:\033[0m %s\n" % (t.lineno, t.type, t.value))

        self.parser.restart()
        return t

    def p_program(self, p):
        '''program : story
                   | WS ID ELIF'''  # Just to hide the ply warnings :)
        p[0] = ast.Program(self, p[1])

    def p_paths(self, p):
        '''paths :       PATH
                 | paths PATH'''
        if len(p) == 2:
            p[0] = ast.Path(self, p.lineno(1), p[1])
        else:
            p[0] = p[1].add(p[2])

    # ----------
    # Statements
    # ----------
    def p_stmts(self, p):
        '''stmts : stmt
                 | stmts stmt'''
        if len(p) == 3:
            p[1].append(p[2])
            p[0] = p[1]
        else:
            p[0] = [p[1]]

    # ----------
    # Operations
    # ----------
    def p_suite(self, p):
        '''suite : NEWLINE INDENT stmts DEDENT'''
        p[0] = p[3]

    # ----------------------------
    # IF ... [ELSE IF ..] ... ELSE
    # ----------------------------
    def p_if(self, p):
        '''stmt : IF expressions suite
                | IF expressions suite else_if
                | IF expressions suite else_if ELSE suite
                | IF expressions suite         ELSE suite'''
        p[0] = [ast.Method(p[1].lower(), self, p.lineno(1), suite=p[3], args=(p[2], ))]
        if len(p) == 5:
            p[0].extend(p[4])
        elif len(p) == 6:
            p[0].append(ast.Method("else", self, p.lineno(4), suite=p[5]))
        elif len(p) == 7:
            p[0].extend(p[4])
            p[0].append(ast.Method("else", self, p.lineno(5), suite=p[6]))

    def p_elseif(self, p):
        '''else_if :         ELSEIF expressions suite
                   | else_if ELSEIF expressions suite'''
        if len(p) == 4:
            p[0] = [ast.Method('unlessif' if 'unless' in p[1] else 'elif', self, p.lineno(1), suite=p[3], args=(p[2], ))]
        else:
            p[1].append(ast.Method('unlessif' if 'unless' in p[2] else 'elif', self, p.lineno(2), suite=p[4], args=(p[3], )))
            p[0] = p[1]

    # ----------
    # Exceptions
    # ----------
    def p_try(self, p):
        '''stmt : TRY suite CATCH suite
                | TRY suite CATCH suite ELSE suite'''
        p[0] = [ast.Method('try', self, p.lineno(1), suite=p[2]),
                ast.Method('catch', self, p.lineno(3), suite=p[4])]
        if len(p) == 7:
            p[0].append(ast.Method('else', self, p.lineno(5), suite=p[6]))

    # ---------------
    # Delicious Juice
    # ---------------
    def p_optional_stmts(self, p):
        '''optional_stmts : stmts
                          |'''
        if len(p) == 2:
            p[0] = p[1]

    def p_output(self, p):
        '''output : AS PATH
                  |'''
        if len(p) == 3:
            p[0] = p[2]

    def p_juice(self, p):
        '''juice : args output NEWLINE
                 | args output NEWLINE INDENT kwargs optional_stmts DEDENT
                 |      output NEWLINE INDENT kwargs optional_stmts DEDENT
                 |      output NEWLINE'''
        # [suite, args, kwargs, output]
        if len(p) == 4:
            p[0] = [None, p[1], None, p[2]]
        elif len(p) == 8:
            p[0] = [p[6], p[1], p[5], p[2]]
        elif len(p) == 7:
            p[0] = [p[5], None, p[4], p[1]]
        else:
            p[0] = [None, None, None, p[1]]

    # -------
    # Methods
    # -------
    def p_methods(self, p):
        '''stmt : PATH   juice
                | RANDOM juice'''
        p[0] = ast.Method(p[1], parser=self, lineno=p.lineno(1),
                                suite=p[2][0], output=p[2][3],
                                args=p[2][1], kwargs=p[2][2])

    def p_story(self, p):
        '''story : stmt  EOF
                 | stmts EOF'''
        p[0] = p[1]

    # ------
    # Figure
    # ------
    def p_figure_of(self, p):
        '''of : OF
              | '''
        pass

    def p_figure_agg(self, p):
        '''agg : AVERAGE  of
               | AVG      of
               | NUMBEROF
               | LENGTH   of
               | MAX      of
               | OLDEST   of
               | HIGHEST  of
               | LARGEST  of
               | MIN      of
               | NEWEST   of
               | SMALLEST of
               | LOWEST   of
               | SUM      of
               | RANDOM   of
               | '''
        if len(p) > 1:
            p[0] = dict(agg=p[1], lineno=p.lineno(1))

    def p_figure_offit(self, p):
        '''offit : FIRST  DIGITS of
                 | TOP    DIGITS of
                 | LAST   DIGITS of
                 | BOTTOM DIGITS of
                 |        DIGITS
                 | FIRST
                 | LAST
                 | '''
        # p = [offset, limit]
        if len(p) >= 3:
            if p[1] in ('first', 'top'):
                p[0] = dict(limit=float(p[2]), lineno=p.lineno(1))
            else:
                p[0] = dict(limit=float(p[2])*-1, lineno=p.lineno(1))

        elif len(p) == 2:
            if p[1] in ('first', 'top'):
                p[0] = dict(limit=1, lineno=p.lineno(1))
            elif p[1] in ('last', 'bottom'):
                p[0] = dict(limit=-1, lineno=p.lineno(1))
            else:
                p[0] = dict(limit=float(p[1]), lineno=p.lineno(1))

    def p_figure_unique(self, p):
        '''unique : UNIQUE
                  | '''
        if len(p) == 2:
            p[0] = dict(unique=True, lineno=p.lineno(1))

    def p_figexp(self, p):
        '''figexp : agg expression
                  |     expression'''
        if len(p) == 3:
            p[2].expressions[0][1].agg = p[1]['agg']
            p[0] = p[2]
        else:
            p[0] = p[1]

    def p_figure_expressions(self, p):
        '''figexps : WHERE       figexp
                   | figexps AND figexp
                   | figexps OR  figexp'''
        if len(p) == 4:
            p[0] = dict(lineno=p.lineno(2), where=p[1]['where'].add(method=p[2], expression=p[3]))
        else:
            p[0] = dict(lineno=p.lineno(1), where=p[2])

    def p_figure_sort(self, p):
        '''sort : SORTBY PATH ASCDESC
                | SORTBY PATH
                | '''
        if len(p) == 4:
            p[0] = dict(sortby=p[2], dir=p[3], lineno=p.lineno(1))
        elif len(p) == 3:
            p[0] = dict(sortby=p[2], lineno=p.lineno(1))

    def p_figure_time(self, p):
        '''time : FROM string
                | '''
        if len(p) == 3:
            p[0] = dict(time=p[2], lineno=p.lineno(1))

    def p_figure_location(self, p):
        '''location : NI PATH
                    |'''
        if len(p) == 3:
            p[0] = dict(location=p[2], lineno=p.lineno(1))

    def p_figaggone(self, p):
        '''figaggone : MOST
                     | HIGHEST
                     | LARGEST
                     | NEWEST
                     | LEAST
                     | SMALLEST
                     | LOWEST
                     | OLDEST'''
        p[0] = dict(dir='asc' if p[1] in ('least', 'oldest', 'smallest') else 'desc')

    def p_figure_aggexp(self, p):
        '''figaggexp : figaggone paths'''
        p[1]['paths'] = p[2].path.split('.')
        p[0] = p[1]

    def p_figure(self, p):
        '''figure : agg offit unique paths figexps sort time
                  | agg offit unique paths         sort time
                  | agg              paths figexps      time
                  | agg              paths figexps
                  | agg              paths              time
                  |     offit        paths figexps sort time
                  |     offit        paths         sort time
                  |                  paths figexps      time
                  |     offit unique paths              time
                  |                  paths              time'''
        _ = dict()
        [_.update(p[x]) for x in xrange(1, len(p)) if type(p[x]) is dict]
        for x in xrange(1, len(p)):
            if p[x] and isinstance(p[x], ast.Path):
                _['paths'] = p[x].path.split('.')

        _.pop('lineno', None)
        if _.keys() == ['paths']:
            p[0] = ast.Path(self, p.lineno(1), ".".join(_['paths']))
        else:
            p[0] = ast.Figure(self, _.pop('paths'), **_)

    def p_figure_with(self, p):
        '''figure : offit  PATH WITH figaggexp location figexps time
                  |        PATH WITH figaggexp location figexps time
                  | offit  PATH WITH figaggexp location               time
                  |        PATH WITH figaggexp location               time'''
        _ = dict(agg="count",  # DEFAULT
                 limit=1,  # DEFAULT
                 lineno=p.lineno(2))
        [_.update(p[x]) for x in xrange(1, len(p)) if type(p[x]) is dict]
        _['paths'].insert(0, p[1 if p[2] == 'with' else 2])
        _['sortby'] = _['paths'][-1]
        _.pop('lineno', None)
        p[0] = ast.Figure(self, _.pop('paths'), **_)

    def p_figure_expression(self, p):
        '''figure_expression : figure LT expression
                             | figure GT expression
                             | figure EQ expression
                             | figure NE expression'''
        p[0] = ast.Expression(p[1])
        p[0].add(p[2], p[3])

    # -------------
    # Set/Push/With
    # -------------
    def p_stmt_set_path_to_paths(self, p):
        '''stmt : SET PATH TO paths NEWLINE'''
        p[0] = ast.Method("set", self, p.lineno(1), args=(p[2], p[4]))

    def p_stmt_set_path_to_figure(self, p):
        '''stmt : SET PATH TO figure NEWLINE'''
        p[0] = ast.Method("set", parser=self, lineno=p.lineno(1), args=(p[2], p[4]))

    def p_stmt_set_path_to_expression(self, p):
        '''stmt : SET PATH TO expressions NEWLINE'''
        p[0] = ast.Method("set", parser=self, lineno=p.lineno(1), args=(p[2], p[4]))

    def p_stmt_unset_path(self, p):
        '''stmt : UNSET PATH NEWLINE'''
        p[0] = ast.Method("unset", parser=self, lineno=p.lineno(1), args=(p[2], ))

    def p_stmt_append(self, p):
        '''stmt : APPEND variable TO paths NEWLINE
                | APPEND variable INTO paths NEWLINE'''
        p[0] = ast.Method("append", parser=self, lineno=p.lineno(1), args=(p[2], p[4]))

    def p_stmt_remove(self, p):
        '''stmt : REMOVE variable FROM paths NEWLINE'''
        p[0] = ast.Method("remove", parser=self, lineno=p.lineno(1), args=(p[2], p[4]))

    def p_stmt_with(self, p):
        '''stmt : WITH paths suite'''
        p[0] = ast.Method("with", parser=self, lineno=p.lineno(1), suite=p[3], args=(p[2], ))

    # -----------
    # While Loops
    # -----------
    def p_stmt_while(self, p):
        '''stmt : WHILE paths               output suite
                | WHILE expressions         output suite
                | WHILE figure_expression   output suite'''
        p[0] = ast.Method("while", parser=self, lineno=p.lineno(1), output=p[3], suite=p[4], args=(p[2], ))

    # -----------
    # Expressions
    # -----------
    def p_expression_path(self, p):
        '''expression : paths'''
        p[0] = ast.Expression(p[1])

    def p_expression_num(self, p):
        '''expression : DIGITS'''
        p[0] = ast.Expression(str(float(p[1])))

    def p_expression_var(self, p):
        '''expression : variable'''
        p[0] = ast.Expression(p[1])

    def p_expressions(self, p):
        '''expressions : expression
                       | expressions AND expression
                       | expressions OR  expression'''
        if len(p) == 4:
            p[0] = p[1].add(p[2], p[3])
        else:
            p[0] = p[1]

    # --------------------
    # Expressions > Method
    # --------------------
    def p_expression_has(self, p):
        '''expression : paths HAS paths'''
        p[0] = ast.Expression(ast.Comparison(p[1], "has", p[3]))

    def p_expression_is_isnt(self, p):
        '''expression : ISNT expression'''
        p[0] = ast.Expression(ast.Comparison(p[2], p[1], True))

    def p_expression_not_in(self, p):
        '''expression : paths ISNT NI paths'''
        p[0] = ast.Expression(ast.Comparison(p[4], "excludes", p[1]))

    def p_expression_contains(self, p):
        '''expression : variable CONTAINS variable
                      | variable    NI    variable'''
        if p[2] == 'contains':
            p[0] = ast.Expression(ast.Comparison(p[3], "contains", p[1]))
        else:
            p[0] = ast.Expression(ast.Comparison(p[1], "contains", p[3]))

    def p_expression_like(self, p):
        '''expression : paths      LIKE expression
                      | paths IS   LIKE expression
                      | paths ISNT LIKE expression
                      | paths      LIKE REGEX
                      | paths IS   LIKE REGEX
                      | paths ISNT LIKE REGEX'''
        if len(p) == 5:
            if p[2] == 'isnot':
                p[0] = ast.Expression(ast.Comparison(p[1], "notlike", p[4]))
            else:
                p[0] = ast.Expression(ast.Comparison(p[1], "like", p[4]))
        else:
            p[0] = ast.Expression(ast.Comparison(p[1], "like", p[3]))

    def p_expression_is(self, p):
        '''expression : paths IS   variable
                      | paths ISNT variable'''
        p[0] = ast.Expression(ast.Comparison(p[1], "is" if p[2] == 'is' else 'isnt', p[3]))

    # ------------------
    # Expressions > Math
    # ------------------
    def p_expression_math(self, p):
        '''expression : expression OPERATOR expression
                      | expression LT       expression
                      | expression GT       expression
                      | expression EQ       expression
                      | expression NE       expression'''
        p[0] = p[1].add(p[2], p[3])

    def p_expression_group(self, p):
        '''expression : LPAREN expressions RPAREN'''
        p[2].expressions.insert(0, ("", "("))
        p[2].expressions.append(("", ")"))
        p[0] = p[2]

    # -------
    # Strings
    # -------
    def p_string_content(self, p):
        '''string_content : paths
                          | STRING_CONTINUE'''
        p[0] = p[1]

    def p_string_inner(self, p):
        '''string_inner :              string_content
                        | string_inner string_content'''
        if len(p) == 2:
            p[0] = ast.String(data=p[1])
        else:
            p[0] = p[1].add(p[2])

    def p_string(self, p):
        '''string : STRING_START_SINGLE string_inner STRING_END
                  | STRING_START_TRIPLE string_inner STRING_END'''
        p[0] = p[2]

    # --------
    # Variable
    # --------
    def p_variable(self, p):
        '''variable : paths
                    | string
                    | BOOLEAN
                    | DIGITS'''
        p[0] = p[1]

    # ---------
    # Arguments
    # ---------
    def p_args(self, p):
        '''args :            variable
                | args COMMA variable
                |'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[1].append(p[3])
            p[0] = p[1]

    def p_kwarg(self, p):
        '''kwarg : KWARG NEWLINE
                 | KWARG variable NEWLINE
                 | KWARG paths NEWLINE'''
        if len(p) == 3:
            p[0] = {p[1][2:]: True}
        else:
            p[0] = {p[1][2:]: p[2]}

    def p_kwargs(self, p):
        '''kwargs : kwarg
                  | kwargs kwarg
                  |'''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 3:
            k = p[1]['kwarg']
            p[0] = dict(kwarg=([k] if type(k) is not list else k) + [p[2]['kwarg']])
