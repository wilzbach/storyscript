class Module:
    """
    Provides information, context and functionality of the current module.
    """

    def __init__(self, symbol_resolver, function_table, mutation_table,
                 root_scope, service_typing, storycontext):
        self.symbol_resolver = symbol_resolver
        self.function_table = function_table
        self.mutation_table = mutation_table
        self.features = storycontext.features
        self.root_scope = root_scope
        self.service_typing = service_typing
        self.storycontext = storycontext
