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

        for c in node.children:
            cls.visit(c, block, entity, pred, fun, parent=node)

    @staticmethod
    def is_inline_expression(n):
        return hasattr(n, 'data') and n.data == 'inline_expression'

    @staticmethod
    def add_strings(n1, *other_nodes):
        """
        Create an AST for concating two or more nodes.
        """
        # concatenation is currently defined as
        # arith_expression = arith_expression arith_operator mul_expression
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
        # if we only got one node, no concatenation is required. return
        # directly
        if len(other_nodes) == 0:
            return base_tree.children[0]

        base_tree.children.append(
            Tree('arith_operator', [Token('PLUS', '+')]),
        )
        # Technically, the grammar only supports binary expressions, but
        # the compiler and engine can handle n-ary expressions, so we can
        # directly flatten the tree and add all additional nodes as extra
        # mul_expressions
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
        # the previously seen character (n-1)
        last_char = None
        # indicates whether we're inside of a string template
        inside_interpolation = False
        buf = ''
        for c in text:
            preceding_slash = last_char == '\\'
            if preceding_slash:
                buf += c
            elif inside_interpolation:
                if c == '}':
                    # end string interpolation
                    inside_interpolation = False
                    tree.expect(len(buf) > 0, 'string_templates_empty')
                    yield {'$OBJECT': 'code', 'code': buf}
                    buf = ''
                else:
                    tree.expect(c != '{', 'string_templates_nested')
                    buf += c
            elif c == '{':
                # string interpolation might be the start of the string: "{..}"
                if len(buf) > 0:
                    yield {'$OBJECT': 'string', 'string': buf}
                    buf = ''
                inside_interpolation = True
            else:
                buf += c
            last_char = c

        # emit remaining string in the buffer
        if len(buf) > 0:
            yield {'$OBJECT': 'string', 'string': buf}

    def eval(self, orig_node, code_string, fake_tree):
        """
        Evaluates a string by parsing it to its AST representation.
        Inserts the AST expression as fake_node and returns the path
        reference to the inserted fake_node.
        """
        new_node = self.parser.parse(code_string)
        new_node = new_node.block
        orig_node.expect(new_node, 'string_templates_no_assignment')
        # go to the actual node -> jump into block.rules or block.service
        for i in range(2):
            orig_node.expect(len(new_node.children) == 1,
                             'string_templates_no_assignment')
            new_node = new_node.children[0]
        # for now only expressions or service_blocks are allowed inside string
        # templates
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
            orig_node.expect(new_node.data == 'service',
                             'string_templates_no_assignment')

        line = orig_node.line()
        return fake_tree.add_assignment(new_node, original_line=line)

    @classmethod
    def build_string_value(cls, text):
        """
        Returns the AST for a plain string AST node with 'text'
        """
        return Tree('values', [
            Tree('string', [
                Token('DOUBLE_QUOTED', text)
            ])
        ])

    def concat_string_templates(self, block, orig_node, string_objs):
        """
        Concatenes the to-be-inserted string templates.
        For example, a string template like "a{exp}b" gets flatten to:
            "a" + fake_path_to_exp + "b"

        Strings can be inserted directly, but string templates must be
        evaluated to new AST nodes and the reference to their fake_node
        assignment should be used instead.
        """
        fake_tree = self.fake_tree(block)
        ks = []
        for s in string_objs:
            if s['$OBJECT'] == 'string':
                # plain string -> insert directly
                value = f'"'+s['string']+'"'
                ks.append(self.build_string_value(value))
            else:
                assert s['$OBJECT'] == 'code'
                # string template -> eval
                # ignore newlines in string interpolation
                code = ''.join(s['code'].split('\n'))
                ks.append(self.eval(orig_node, code, fake_tree))
        return self.add_strings(*ks)

    def inline_string_templates(self, node, block, parent):
        """
        String templates generate fake_nodes in the AST before their block
        and are replaced with a reference to their fake_nodes.
        """
        string_node = node.follow_node_chain([
            'cmp_expression',
            'arith_expression', 'mul_expression', 'unary_expression',
            'pow_expression', 'primary_expression', 'entity', 'values',
            'string'])
        if string_node is None:
            return

        text = Objects.unescape_string(string_node)
        string_objs = list(self.flatten_template(string_node, text))

        # is plain string without string templates?
        if len(string_objs) == 1 and string_objs[0]['$OBJECT'] == 'string':
            return

        node.children = [self.concat_string_templates(block, string_node,
                                                      string_objs)]

    def visit_string_templates(self, node, block, parent):
        """
        Iterates the AST and evaluates string templates.
        """
        if not hasattr(node, 'children'):
            return

        if node.data == 'block':
            block = node
        elif node.data == 'cmp_expression':
            self.inline_string_templates(node, block, parent)

        for c in node.children:
            self.visit_string_templates(c, block, node)

    def process(self, tree):
        """
        Applies several preprocessing steps to the existing AST.
        """
        pred = Preprocessor.is_inline_expression
        self.visit_string_templates(tree, block=None, parent=None)
        self.visit(tree, None, None, pred,
                   self.replace_expression, parent=None)
        return tree
