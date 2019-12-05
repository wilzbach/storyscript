from functools import lru_cache
from itertools import chain

from storyscript.compiler.semantics.functions.HubMutations import Hub
from storyscript.compiler.semantics.functions.Mutation import Mutation
from storyscript.compiler.semantics.types.Types import AnyType


class MutationOverloads:
    """
    Contains all overloads for a mutation of a specific name and type.
    """

    def __init__(self, name, type_):
        self._obj = {}
        self._name = name
        self._type = type_

    def add_overloads(self, overloads):
        for name, overload in overloads.items():
            self.add_overload(name, overload)

    def add_overload(self, name, overload):
        if name not in self._obj:
            self._obj[name] = []
        self._obj[name].append(overload)

    def all(self):
        """
        Builds a sorted list of all available overloads.
        """
        overloads = chain.from_iterable(self._obj.values())
        return list(sorted(overloads, key=lambda m: m.cmp_name()))

    def single(self):
        """
        If there's only one mutation overload, return this one.
        Otherwise return `None`.
        """
        if len(self._obj) != 1:
            return None

        e = next(iter(self._obj.values()))  # get the only element
        if len(e) == 1:
            # there is only one overload -> return
            return e[0]

        return None

    def match(self, arg_names):
        """
        Finds the matching overload for an arg_names pair.
        Returns `None` if no match was found.
        """
        arg_names = Mutation.compute_arg_names_hash(arg_names)
        match = self._obj.get(arg_names, None)
        if match is None:
            return None

        return match

    def type(self):
        """
        Returns the type that this mutation overload result was created for.
        """
        return self._type

    def name(self):
        """
        Returns the name that this mutation overload result was created for.
        """
        return self._name


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
            assert arg_names not in match, (
                f"mutation {name} for {t} already exists with the "
                "same overload"
            )
        else:
            muts[t] = {}
        muts[t][arg_names] = mutation

    @staticmethod
    def type_key(type_):
        """
        Returns a hashable key for a type.
        """
        return type_.__name__

    def _resolve_any(self, muts, name):
        """
        Searches for all potential type overloads on mutation.
        """
        mo = MutationOverloads(name, AnyType.instance())
        for overloads in muts.values():
            mo.add_overloads(overloads)
        return mo

    def resolve_by_type(self, type_):
        """
        Returns all mutations for a type.
        """
        t = self.type_key(type(type_))
        for name, muts in self.mutations.items():
            res = muts.get(t, None)
            if res is not None:
                for mut in res.values():
                    yield mut

    def resolve(self, type_, name):
        """
        Returns the mutation `name` or `None`.
        """
        muts = self.mutations.get(name, None)
        if muts is None:
            return None

        if type_ == AnyType.instance():
            return self._resolve_any(muts, name)

        t = self.type_key(type(type_))
        overloads = muts.get(t, None)
        if overloads is None:
            return None

        mo = MutationOverloads(name, type_)
        mo.add_overloads(overloads)
        return mo

    @classmethod
    def init(cls):
        """
        Builds a list of all mutations of the Hub.
        """
        mi = cls()
        for m in Hub.instance().mutations():
            mi.insert(m)
        return mi

    @lru_cache(maxsize=1)
    def instance():
        return MutationTable.init()
