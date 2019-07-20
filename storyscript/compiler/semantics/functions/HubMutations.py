from storyscript.compiler.semantics.functions.MutationBuilder import \
    mutation_builder
from storyscript.hub.engine.Builtins import builtins


class Hub:
    """
    A representation of a Storyscript Engine and Hub.
    Assumed to be Asyncy Engine for now.
    """
    def __init__(self, mutations):
        self._mutations = []
        for m in mutations.split('\n'):
            if len(m.strip()) == 0 or m.startswith('#'):
                continue
            self._mutations.append(mutation_builder(m))

    def mutations(self):
        """
        Return all mutations supported by this hub.
        """
        return self._mutations

    def instance():
        """
        Return the current Hub instance
        """
        return hub


hub = Hub(builtins)
