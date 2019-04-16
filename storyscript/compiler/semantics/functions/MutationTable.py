from storyscript.compiler.semantics.functions.HubMutations import hub
from storyscript.compiler.semantics.functions.Mutation import Mutation


class MutationTable:
    """
    A table of all available mutation inside a story.
    """
    def __init__(self):
        self.mutations = {}

    def insert(self, mutation):
        """
        Insert a new mutation into the mutation table.
        """
        assert isinstance(mutation, Mutation)
        name = mutation.name()
        if mutation.name() not in self.mutations:
            self.mutations[name] = {}
        muts = self.mutations[name]
        t = self.type_key(mutation.base_type())
        assert t not in muts, f'mutation {name} for {t} already exists'
        muts[t] = mutation

    @staticmethod
    def type_key(type_):
        """
        Returns a hashable key for a type.
        """
        return type_.__name__

    def resolve(self, type_, name):
        """
        Returns the mutation `name` or `None`.
        """
        if name not in self.mutations:
            return None

        t = self.type_key(type(type_))
        muts = self.mutations[name]
        if t not in muts:
            return None

        return muts[t]

    @classmethod
    def init(cls):
        """
        Builds a list of all mutations of the Hub.
        """
        mi = cls()
        for m in hub.mutations():
            mi.insert(m)
        return mi
