from storyscript.compiler.semantics.functions.HubMutations import hub
from storyscript.compiler.semantics.functions.Mutation import Mutation


class MutationOverloads:
    """
    Contains all overloads for a mutation of a specific name and type.
    """

    def __init__(self, obj):
        self._obj = obj

    def all(self):
        """
        Builds a sorted list of all available overloads.
        """
        # return all overloads
        return list(sorted(self._obj.values(),
                           key=lambda d: d.arg_names_hash()))

    def match(self, arg_names):
        """
        Finds the matching overload for an arg_names pair.
        Returns all overloads if no match was found.
        """
        arg_names = Mutation.compute_arg_names_hash(arg_names)
        match = self._obj.get(arg_names, None)
        if match is not None:
            return match

        if len(self._obj) == 1:
            # there is only one overload -> return
            return next(iter(self._obj.values()))

        return None


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
        arg_names = mutation.arg_names_hash()
        match = muts.get(t, None)
        if match is not None:
            assert arg_names not in match, \
                    (f'mutation {name} for {t} already exists with the '
                     'same overload')
        else:
            muts[t] = {}
        muts[t][arg_names] = mutation

    @staticmethod
    def type_key(type_):
        """
        Returns a hashable key for a type.
        """
        return type_.__name__

    def find_mutation(self, name):
        if name not in self.mutations:
            return None
        return self.mutations[name]

    def resolve_any(self, name, arg_names):
        muts = self.find_mutation(name)
        overloads = {}
        for t, overload in muts:
            overloads = {**overloads, **overload}

        return MutationOverloads(overloads)

    def resolve(self, type_, name):
        """
        Returns the mutation `name` or `None`.
        """
        muts = self.find_mutation(name)
        if muts is None:
            return None

        t = self.type_key(type(type_))
        overloads = muts.get(t, None)
        if overloads is None:
            return None

        return MutationOverloads(overloads)

    @classmethod
    def init(cls):
        """
        Builds a list of all mutations of the Hub.
        """
        mi = cls()
        for m in hub.mutations():
            mi.insert(m)
        return mi
