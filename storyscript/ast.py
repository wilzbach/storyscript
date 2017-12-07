from . import version


def debug(yes, *this): # pragma: no cover
    if yes:
        if len(this) > 1:
            for x in this[:-1]:
                print x,
        print this[-1]


class Program(object):
    def __init__(self, parser, story):
        self.parser = parser
        parser.program = self
        self.story = story

    def _json_next(self, dct, method, parent=None):
        if isinstance(method, Method):
            dct[str(method.lineno)] = dict(
                method=method.method,
                output=method.output,
                linenum=method.lineno,
                args=self._dump_json(method.args),
                kwargs=self._dump_json(method.kwargs),
                parent=parent.lineno if parent else None
            )
            if method.suite:
                for e in method.suite:
                    self._json_next(dct, e, method)

        else:
            for m in method:
                self._json_next(dct, m, parent)

    def _dump_json(self, obj):
        if type(obj) in (type(None), bool, int, float):
            return obj
        elif hasattr(obj, 'json'):
            return obj.json()
        elif type(obj) is dict:
            return dict([(key, self._dump_json(var)) for key, var in obj.items()])
        else:
            return [var.json() if hasattr(var, 'json') else var for var in obj]

    def json(self):
        dct = {}
        self._json_next(dct, self.story)
        return dict(
            version=version,
            script=dct
        )


class Method(object):
    def __init__(self, method, parser, lineno, suite=None, output=None, args=None, kwargs=None):
        self.method = method
        self.parser = parser
        self.lineno = str(lineno)
        self.output = output
        self.suite = suite
        self.args = args
        self.kwargs = kwargs


class Path(object):
    def __init__(self, parser, lineno, path, agg=None):
        self.parser = parser
        self.lineno = lineno
        self.path = path
        self.agg = agg

    def add(self, path):
        self.path = self.path+'.'+path
        return self

    def json(self):
        return dict(path=self.path, agg=self.agg) if self.agg else dict(path=self.path)


class String(object):
    def __init__(self, data):
        self.chunks = [data]

    def add(self, data):
        self.chunks.append(data)
        return self

    def json(self):
        is_complex = False
        for st in self.chunks:
            if isinstance(st, Path):
                is_complex = True
                break

        if is_complex:
            string = []
            values = {}
            for st in self.chunks:
                if isinstance(st, Path):
                    values[str(len(values))] = st.json()
                    string.append("{%d}" % (len(values)-1))
                else:
                    string.append(st)
            return dict(string=''.join(string).strip(), values=values)

        else:
            return dict(value=" ".join([d.strip() for d in self.chunks]).strip())


class Figure(object):
    def __init__(self, parser, paths, **kwargs):
        # ---------------------
        # Figure out the figure
        # ---------------------
        self.parser = parser
        if 1 > kwargs.get('limit', 0) > -1 and kwargs.get('limit', 0) != 0:
            kwargs['limit'] = str(kwargs['limit'] * 100) + "%"
        elif kwargs.get('limit') is not None:
            kwargs['limit'] = int(kwargs['limit'])

        # [:groupby, :figure, :path]
        if len(paths) == 3:
            kwargs['groupby'] = paths[0]
            kwargs['figure'] = paths[1]
            kwargs['path'] = paths[2]

        # [:figure, :path]
        elif len(paths) == 2:
            kwargs['figure'] = paths[0]
            if kwargs.get('limit'):
                kwargs['groupby'] = paths[0]
            kwargs['path'] = paths[1]

            # these types of aggs -> We know the sorting method
            if kwargs.get('agg') in ("largest", "newest", "lowest", "smallest", "highest", "oldest", "least", "most"):
                # lets default that value to 1
                # ex. `lowest product sold` => `lowest 1 product sold`
                kwargs.setdefault('limit', 1)
                if kwargs.get('agg') in ("largest", "newest", "highest", "most"):
                    if kwargs.setdefault('dir', 'desc') != 'desc':
                        raise SyntaxError("Contridicting sorting methods")
                elif kwargs.setdefault('dir', 'asc') != 'asc':
                    raise SyntaxError("Contridicting sorting methods")
                # dont need the agg anymore
                kwargs.pop('agg')
                # sort method must be the second path
                # ex. `lowest product sold` => `lowest 1 product sold sort by sold asc`
                if kwargs.setdefault('sortby', paths[1]) != paths[1]:
                    raise SyntaxError("Contridicting sorting methods")

            elif kwargs.get('agg') == 'count':
                # ex. `number of store orders`
                kwargs.setdefault('groupby', kwargs['path'])

        # [:figure]
        elif len(paths) == 1:
            kwargs['figure'] = paths[0]
            # one path has limited agg methods
            if kwargs.get('agg') in ('count', 'length'):
                kwargs.pop('agg')
                kwargs['path'] = 'count'
                kwargs.setdefault('limit', 1)
            elif kwargs.get('agg') in ('first', 'last', 'oldest', 'newest', 'random', 'largest', 'lowest', 'smallest', 'highest'):
                pass
            elif kwargs.get('agg') is not None:
                raise SyntaxError("Invalid agg method for one figure path provided")

        else:
            # is there a time for more then 3 paths?????
            debug(self.parser.debug, "\033[32m-=-=-=-=IMPORTANT-=-=-=-=-=-=-=-=-=-=-=\033[0m", paths)
            raise SyntaxError("To many paths presented for figure")

        # ---------------------
        # Different Agg Methods
        # ---------------------
        if str(kwargs.get('offset')) == "0":
            kwargs.pop('offset')

        # limits require sorting mehtod
        if kwargs.get('limit') and (not kwargs.get('sortby') and kwargs.get('path') != 'count'):
            raise SyntaxError("sorting method required to limit the results")

        # one (1) result when `agg` and `not(groupby)`
        if kwargs.get('agg') and kwargs.get('groupby') is None:
            if kwargs.setdefault('limit', 1) != 1:
                raise SyntaxError("must group the figure to have more then one result")

        self.kwargs = kwargs

    def json(self):
        return dict([(k,  v.json() if hasattr(v, 'json') else v) for k,v in self.kwargs.items() if v])


class Expression(object):
    def __init__(self, expression):
        self.expressions = [("", expression)]

    def add(self, method, expression):
        self.expressions.append((method, expression))
        return self

    def json(self, evals=None, values=None):
        if evals is None:
            if len(self.expressions) == 1:
                e = self.expressions[0][1]
                return e.json() if hasattr(e, 'json') else e
            evals = []
            values = {}
        for mixin, expression in self.expressions:
            evals.append(mixin)

            if isinstance(expression, Expression):
                _d = expression.json(evals, values)
                evals = [_d['expression']]
                values = _d['values']

            elif hasattr(expression, 'json'):
                d = expression.json()
                i = (max(map(int, values.keys())) + 1) if values else 0
                values[str(i)] = d
                evals.append("{%d}" % (i))
            else:
                evals.append(expression)

        return dict(expression=" ".join([ev for ev in evals if ev != ""]),
                    values=values)


class Comparison(object):
    def __init__(self, left, method, right):
        self.left = left
        self.method = method
        self.right = right

    def json(self):
        return dict(method=self.method,
                    left=self.left.json() if hasattr(self.left, 'json') else self.left,
                    right=self.right.json() if hasattr(self.right, 'json') else self.right)
