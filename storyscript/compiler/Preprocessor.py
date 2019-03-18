# -*- coding: utf-8 -*-
from lark.lexer import Token

from .Faketree import FakeTree
from .Objects import Objects
from ..parser.Tree import Tree


class Preprocessor:
    """
    Performs additional transformations that can't be performed, or would be
    too complicated for the Transformer, before the tree is compiled.
    """

    def __init__(self, parser):
        """
        Saves the used parser as it might be used again for re-evaluation
        of new statements (e.g. for string interpolation)
        """
        self.parser = parser

    @staticmethod
    def fake_tree(block):
        """
        Get a fake tree
        """
        return FakeTree(block)

    @classmethod
    def replace_expression(cls, node, fake_tree, insert_point):
        """
        Inserts `node` as a new like with a fake path reference.
        Then, replaces the first child of the insert_point
        with this path reference.
        """
        line = insert_point.line()
        # generate a new assignment line
        # insert it above this statement in the current block
        # return a path reference
        child_node = None
        if node.service is not None:
            child_node = node.service
        elif node.call_expression is not None:
            assert node.call_expression is not None
            child_node = node.call_expression
        else:
            assert node.mutation is not None
            child_node = node.mutation

        fake_path = fake_tree.add_assignment(child_node, original_line=line)

        # Replace the inline expression with a fake_path reference
        insert_point.replace(0, fake_path.child(0))

    @classmethod
    def visit(cls, node, block, entity, pred, fun, parent):
        if not hasattr(node, 'children') or len(node.children) == 0:
            return

        if node.data == 'block':
            # only generate a fake_block once for every line
            # node: block in which the fake assignments should be inserted
            block = cls.fake_tree(node)
        elif node.data == 'entity':
            # set the parent where the inline_expression path should be
            # inserted
            entity = node
        elif node.data == 'service' and node.child(0).data == 'path':
            entity = node

        # create fake lines for base_expressions too, but only when required:
        # 1) `expressions` are already allowed to be nested
        # 2) `assignment_fragments` are ignored to avoid two lines for simple
        #    service/mutation assignments (`a = my_service command`)
        if node.data == 'base_expression' and \
                node.child(0).data != 'expression' and \
                parent.data != 'assignment_fragment':
            # replace base_expression too
            fun(node, block, node)
            node.children = [Tree('path', node.children)]

        for c in node.children:
            cls.visit(c, block, entity, pred, fun, parent=node)

        if pred(node):
            assert entity is not None
            assert block is not None
            fake_tree = block
            if not isinstance(fake_tree, FakeTree):
                fake_tree = cls.fake_tree(block)

            # Evaluate from leaf to the top
            fun(node, fake_tree, entity.path)

            # split services into service calls and mutations
            if entity.data == 'service':
                entity.data = 'mutation'
                entity.entity = Tree('entity', [entity.path])
                entity.service_fragment.data = 'mutation_fragment'

    @staticmethod
    def is_inline_expression(n):
        return hasattr(n, 'data') and n.data == 'inline_expression'

    @staticmethod
    def add_strings(n1, *other_nodes):
        base_tree = Tree('arith_expression', [
            Tree('arith_expression', [
                Tree('mul_expression', [
                    Tree('unary_expression', [
                        Tree('pow_expression', [
                            Tree('primary_expression', [
                                Tree('entity', [
                                    n1
                                ])
                            ])
                        ])
                    ])
                ]),
            ]),
        ])
        if len(other_nodes) == 0:
            return base_tree.children[0]

        base_tree.children.append(
            Tree('arith_operator', [Token('PLUS', '+')]),
        )
        for n2 in other_nodes:
            base_tree.children.append(Tree('mul_expression', [
                Tree('unary_expression', [
                    Tree('pow_expression', [
                        Tree('primary_expression', [
                            Tree('entity', [
                                n2
                            ])
                        ])
                    ])
                ])
            ]))
        return base_tree

    @classmethod
    def flatten_template(cls, tree, text):
        """
        Flattens a string template into concatenation
        """
        preceding_slash = False
        in_var = False
        buf = ''
        for c in text:
            if in_var:
                if not preceding_slash and c == '}':
                    in_var = False
                    tree.expect(len(buf) > 0, 'template_string_empty')
                    # yield Objects.path(Objects.name_to_path(buf))
                    yield {'$OBJECT': 'path', 'paths': buf}
                    buf = ''
                else:
                    buf += c
            elif not preceding_slash and c == '{':
                if len(buf) > 0:
                    yield {'$OBJECT': 'string', 'string': buf}
                buf = ''
                in_var = True
            else:
                buf += c
            preceding_slash = c == '\\'

        if len(buf) > 0:
            yield {'$OBJECT': 'string', 'string': buf}

    def eval(self, node, code_string, fake_tree):
        new_node = self.parser.parse(code_string)
        string_error = 'string_interpolation_no_assignment'
        new_node = new_node.block
        node.expect(new_node, string_error)
        node.expect(len(new_node.children) == 1, string_error)
        new_node = new_node.children[0]
        new_node = new_node.children[0]
        # print(new_node.pretty())
        if new_node.data == 'service_block' and \
                new_node.service_fragment is None:
            # it was a plain-old path initially
            base_tree = Tree('path', [
                Token('NAME', code_string)
            ])
            return base_tree
        if new_node.data == 'absolute_expression':
            new_node = new_node.children[0]
        else:
            node.expect(new_node.data == 'service', string_error)

        return fake_tree.add_assignment(new_node, original_line=node.line())

    @classmethod
    def build_string_value(cls, text):
        return Tree('values', [
            Tree('string', [
                Token('DOUBLE_QUOTED', text)
            ])
        ])

    def inline_string_templates(self, node, block, parent):
        if not hasattr(node, 'children'):
            return
        if node.data == 'block':
            block = node
        elif node.data == 'cmp_expression':
            string = node.follow_node_chain([
                'cmp_expression',
                'arith_expression', 'mul_expression', 'unary_expression',
                'pow_expression', 'primary_expression', 'entity', 'values',
                'string'])
            fake_tree = self.fake_tree(block)
            if string:
                text = Objects.unescape_string(string)
                strings = list(self.flatten_template(string, text))
                is_plain_string = len(strings) == 1 and \
                    strings[0]['$OBJECT'] == 'string'
                if not is_plain_string:
                    ks = []
                    for s in strings:
                        if s['$OBJECT'] == 'string':
                            value = f'"'+s['string']+'"'
                            ks.append(self.build_string_value(value))
                        else:
                            ks.append(self.eval(string, s['paths'], fake_tree))
                        node.children = [Preprocessor.add_strings(*ks)]
        for c in node.children:
            self.inline_string_templates(c, block, node)

    def process(self, tree):
        pred = Preprocessor.is_inline_expression
        self.inline_string_templates(tree, block=None, parent=None)
        self.visit(tree, None, None, pred,
                   self.replace_expression, parent=None)
        return tree
