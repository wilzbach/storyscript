from storyscript.parser import Tree

from .symbols.SymbolTypes import StringType


class PathResolver:
    """
    Resolves a path to a symbol
    """
    def __init__(self, symbol_resolver):
        # how to resolve existing symbols
        self.symbol_resolver = symbol_resolver

    def names(self, tree):
        """
        Extracts names from a path tree
        """
        assert tree.data == 'path'
        names = [tree.child(0).value]
        for fragment in tree.children[1:]:
            child = fragment.child(0)
            value = child.value
            if isinstance(child, Tree):
                if child.data == 'string':
                    value = self.string(child)
                else:
                    assert child.data == 'path'
                    value = self.path(child)
            names.append(value)
        return names

    def path(self, tree):
        assert tree.data == 'path'
        paths = self.names(tree)
        for p in paths:
            # ignore internal variables
            if not isinstance(p, str) or p.startswith('__p-'):
                break
            tree.expect('-' not in p,
                        'path_name_invalid_char', path=p, token='-')
            tree.expect('/' not in p,
                        'path_name_invalid_char', path=p, token='/')
        return self.symbol_resolver.resolve(tree, paths)

    def string(self, tree):
        """
        Compiles a string tree.
        """
        assert tree.data == 'string'
        return StringType.instance()
