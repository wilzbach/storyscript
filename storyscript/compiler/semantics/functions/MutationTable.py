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

    def resolve(self, type_, name, arg_names):
        """
        Returns the mutation `name` or `None`.
        """
        if name not in self.mutations:
            return None

        arg_names = Mutation.compute_arg_names_hash(arg_names)

        t = self.type_key(type(type_))
        muts = self.mutations[name]
        overloads = muts.get(t, None)
        if overloads is None:
            return None

        match = overloads.get(arg_names, None)
        if match is not None:
            return match

        if len(overloads) == 1:
            # there is only one overload -> return
            return next(iter(overloads.values()))

        # return all overloads
        return list(sorted(overloads.values(),
                           key=lambda d: d.arg_names_hash()))

    @classmethod
    def init(cls):
        """
        Builds a list of all mutations of the Hub.
        """
        mi = cls()
        for m in hub.mutations():
            mi.insert(m)
        return mi
