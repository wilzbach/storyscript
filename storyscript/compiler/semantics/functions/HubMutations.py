from storyhub.engine.Builtins import builtins

from storyscript.compiler.semantics.functions.MutationBuilder import \
    mutation_builder


class Hub:
    """
    A representation of a Storyscript Engine and Hub.
    Assumed to be Asyncy Engine for now.
    """
    def __init__(self, mutations):
        self._mutations = []
        for m in mutations:
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
