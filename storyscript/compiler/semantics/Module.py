from storyscript.compiler.pretty.PrettyPrinter import PrettyPrinter


class Module:
    """
    Provides information, context and functionality of the current module.
    """

    def __init__(self, symbol_resolver, function_table, mutation_table,
                 features, root_scope):
        self.symbol_resolver = symbol_resolver
        self.function_table = function_table
        self.mutation_table = mutation_table
        self.features = features
        self.root_scope = root_scope
        self.formatter = PrettyPrinter()
        self.tmp = {}

    def add_tmp_assignment(self, symbol, tree):
        self.tmp[symbol.name()] = (symbol, tree)

    def print_tmp_assignment(self, name):
        if name in self.tmp:
            symbol, tree = self.tmp[name]
            res = self.source(tree)
            buf = ''
            for s in res.split(' '):
                if s.startswith('__'):
                    buf += f'({self.print_tmp_assignment(s)})'
                else:
                    buf += s
                buf += ' '
            return buf[:-1]

        return name

    def source(self, tree):
        return self.formatter.print(tree)
