from storyscript.compiler.semantics.types.Types import BooleanType, IntType, \
    StringType
from storyscript.parser import Tree


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
        main_name = tree.child(0).value
        names = [(main_name, tree.child(0).value)]
        for fragment in tree.children[1:]:
            child = fragment.child(0)
            name = None
            if isinstance(child, Tree):
                if child.data == 'string':
                    value = StringType.instance()
                elif child.data == 'boolean':
                    value = BooleanType.instance()
                else:
                    assert child.data == 'path'
                    value = self.path(child)
            else:
                name = child.value
                if child.type == 'INT':
                    value = IntType.instance()
                else:
                    assert child.type == 'NAME'
                    value = StringType.instance()
            names.append((name, value))
        return names

    def path(self, tree):
        assert tree.data == 'path'
        path_names = self.names(tree)
        for name, p in path_names:
            # ignore internal variables
            if name is None or name.startswith('__p-'):
                continue
            if p != IntType.instance():
                tree.expect('-' not in name,
                            'path_name_invalid_char', path=name, token='-')
            tree.expect('/' not in name,
                        'path_name_invalid_char', path=name, token='/')
        # ["name", <types>...]
        paths = [p[1] for p in path_names]
        return self.symbol_resolver.resolve(tree, paths)
