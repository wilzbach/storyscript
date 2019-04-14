def service_to_mutation(tree):
    """
    Convert a service block into a mutation block.
    """
    tree.data = 'mutation'
    tree.service_fragment.data = 'mutation_fragment'
    # convert command into a name
    tree.mutation_fragment.children[0] = \
        tree.mutation_fragment.child(0).child(0)
    return tree
