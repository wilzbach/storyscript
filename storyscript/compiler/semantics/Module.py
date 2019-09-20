class Module:
    """
    Provides information, context and functionality of the current module.
    """

    def __init__(self, symbol_resolver, function_table, mutation_table,
                 features, root_scope, service_typing, story_context):
        self.symbol_resolver = symbol_resolver
        self.function_table = function_table
        self.mutation_table = mutation_table
        self.features = features
        self.root_scope = root_scope
        self.service_typing = service_typing
        self.story_context = story_context
