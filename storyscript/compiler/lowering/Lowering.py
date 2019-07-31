# -*- coding: utf-8 -*-
from enum import Enum

from lark.lexer import Token

from storyscript.compiler.lowering.Faketree import FakeTree
from storyscript.compiler.lowering.utils import service_to_mutation, \
        unicode_escape
from storyscript.parser.Transformer import Transformer
from storyscript.parser.Tree import Tree


class UnicodeNameDecodeState(Enum):
    No = 0  # no unicode decode
    Start = 1  # beginning
    Running = 2  # after '{'


class Lowering:
    """
    Performs additional transformations that can't be performed, or would be
    too complicated for the Transformer, before the tree is compiled.
    """

    def __init__(self, parser, features):
        """
        Saves the used parser as it might be used again for re-evaluation
        of new statements (e.g. for string interpolation)
        """
        self.parser = parser
        self.features = features

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
        elif node.data == 'entity' or node.data == 'key_value':
            # set the parent where the inline_expression path should be
            # inserted
            entity = node
        elif node.data == 'service' and node.child(0).data == 'path':
            entity = node

        for c in node.children:
            cls.visit(c, block, entity, pred, fun, parent=node)

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
                entity.entity = Tree('entity', [entity.path])
                service_to_mutation(entity)

    @staticmethod
    def is_inline_expression(n):
        return hasattr(n, 'data') and n.data == 'inline_expression'

    @staticmethod
    def add_strings(n1, *other_nodes):
        """
        Create an AST for concating two or more nodes.
        """
        # concatenation is currently defined as
        # expression = expression arith_operator expression
        base_tree = Tree('expression', [n1])
        base_tree.kind = 'arith_expression'

        # if we only got one node, no concatenation is required. return
        # directly
        if len(other_nodes) == 0:
            return base_tree.children[0]

        base_tree.children.append(
            Tree('arith_operator', [n1.create_token('PLUS', '+')]),
        )

        # Technically, the grammar only supports binary expressions, but
        # the compiler and engine can handle n-ary expressions, so we can
        # directly flatten the tree and add all additional nodes as extra
        # expressions
        for n2 in other_nodes:
            base_tree.children.append(n2)
        return base_tree

    @classmethod
    def flatten_template(cls, tree, text):
        """
        Flattens a string template into concatenation
        """
        # the previously seen character (n-1)
        preceding_slash = False
        # indicates whether we're inside of a string template
        inside_interpolation = False
        inside_unicode = UnicodeNameDecodeState.No
        buf = ''
        for c in text:
            if preceding_slash:
                if c == '{' or c == '}' or c == "\'" or c == '"':
                    # custom escapes
                    buf = f'{buf[:-1]}{c}'
                else:
                    # avoid deprecation messages for invalid escape sequences
                    if c == ' ':
                        buf += '\\'
                    if c == 'N':
                        # start unicode escaped name sequence
                        inside_unicode = UnicodeNameDecodeState.Start
                    buf += c
                preceding_slash = False
            else:
                if inside_unicode != UnicodeNameDecodeState.No:
                    if c == '{':
                        inside_unicode = UnicodeNameDecodeState.Running
                    tree.expect(inside_unicode ==
                                UnicodeNameDecodeState.Running,
                                'string_templates_nested')
                    if c == '}':
                        inside_unicode = UnicodeNameDecodeState.No
                    buf += c
                elif inside_interpolation:
                    if c == '}':
                        # end string interpolation
                        inside_interpolation = False
                        tree.expect(len(buf) > 0, 'string_templates_empty')
                        yield {
                            '$OBJECT': 'code',
                            'code': unicode_escape(tree, buf)
                        }
                        buf = ''
                    else:
                        tree.expect(c != '{', 'string_templates_nested')
                        buf += c
                elif c == '{':
                    # string interpolation might be the start of the string.
                    # example: "{..}"
                    if len(buf) > 0:
                        yield {
                            '$OBJECT': 'string',
                            'string': buf
                        }
                        buf = ''
                    inside_interpolation = True
                elif c == '}':
                    tree.expect(0, 'string_templates_unopened')
                else:
                    buf += c
                preceding_slash = c == '\\'

        # emit remaining string in the buffer
        tree.expect(not inside_interpolation, 'string_templates_unclosed')
        if len(buf) > 0:
            yield {
                '$OBJECT': 'string',
                'string': buf
            }

    def eval(self, orig_node, code_string, fake_tree):
        """
        Evaluates a string by parsing it to its AST representation.
        Inserts the AST expression as fake_node and returns the path
        reference to the inserted fake_node.
        """
        line = orig_node.line()
        column = int(orig_node.column()) + 1
        # add whitespace as padding to fixup the column location of the
        # resulting tokens.
        from storyscript.Story import Story
        story = Story(' ' * column + code_string, features=self.features)
        story.parse(self.parser, allow_single_quotes=True)
        new_node = story.tree

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
            name = Token('NAME', code_string.strip(), line=line, column=column)
            name.end_column = int(orig_node.end_column()) - 1
            return Tree('path', [name])
        if new_node.data == 'absolute_expression':
            new_node = new_node.children[0]
        else:
            orig_node.expect(new_node.data == 'service',
                             'string_templates_no_assignment')

        # the new assignment should be inserted at the top of the current block
        return fake_tree.add_assignment(new_node, original_line=line)

    @classmethod
    def build_string_value(cls, orig_node, text):
        """
        Returns the AST for a plain string AST node with 'text'
        Uses a `orig_node` to determine the line and column of the new Token.
        """
        return Tree('values', [
            Tree('string', [
                orig_node.create_token('DOUBLE_QUOTED', text)
            ])
        ])

    def concat_string_templates(self, fake_tree, orig_node, string_objs):
        """
        Concatenates the to-be-inserted string templates.
        For example, a string template like "a{exp}b" gets flatten to:
            "a" + fake_path_to_exp as string + "b"

        Strings can be inserted directly, but string templates must be
        evaluated to new AST nodes and the reference to their fake_node
        assignment should be used instead.
        """
        ks = []
        for s in string_objs:
            if s['$OBJECT'] == 'string':
                # plain string -> insert directly
                str_node = self.build_string_value(orig_node=orig_node,
                                                   text=s['string'])
                string_tree = Tree('expression', [
                    Tree('entity', [
                        str_node
                    ])
                ])
                string_tree.kind = 'primary_expression'
                ks.append(string_tree)
            else:
                assert s['$OBJECT'] == 'code'
                # string template -> eval
                # ignore newlines in string interpolation
                code = ''.join(s['code'].split('\n'))

                evaled_node = self.eval(orig_node, code, fake_tree)

                # cast to string (`as string`)
                base_type = orig_node.create_token('STRING_TYPE', 'string')
                as_operator = Tree('as_operator', [
                    Tree('types', [
                        Tree('base_type', [
                            base_type
                        ])
                    ])
                ])
                as_tree = Tree('expression', [
                    Tree('expression', [
                        Tree('entity', [
                            evaled_node
                        ]),
                    ]),
                    as_operator
                ])
                as_tree.kind = 'pow_expression'
                as_tree.child(0).kind = 'primary_expression'
                ks.append(as_tree)

        return ks

    def inline_string_templates(self, node, block, parent):
        """
        String templates generate fake_nodes in the AST before their block
        and are replaced with a reference to their fake_nodes.

        If the string expression is the only node in its expression, it
        will be directly inserted in the AST.
        Otherwise, the string concatenation will be inserted as a new AST node.
        """
        entity = node.entity
        string_node = entity.follow_node_chain(['entity', 'values', 'string'])
        if string_node is None:
            return

        text = string_node.child(0).value
        string_objs = list(self.flatten_template(string_node, text))

        # empty string
        if len(string_objs) == 0:
            # no AST modifications required
            return

        # is plain string without string templates?
        if len(string_objs) == 1 and string_objs[0]['$OBJECT'] == 'string':
            string_node.child(0).value = string_objs[0]['string']
            # no further AST modifications required
            return

        fake_tree = self.fake_tree(block)
        children = self.concat_string_templates(fake_tree, string_node,
                                                string_objs)
        new_node = self.add_strings(*children)

        assert len(node.children) == 1
        node.children = new_node.children
        node.kind = new_node.kind

    def visit_string_templates(self, node, block, parent):
        """
        Iterates the AST and evaluates string templates.
        """
        if not hasattr(node, 'children'):
            return

        if node.data == 'block':
            block = node

        for c in node.children:
            self.visit_string_templates(c, block, node)

        # leaf-to-to to avoid double execution
        if node.data == 'expression':
            if node.entity is not None:
                self.inline_string_templates(node, block, parent)

    def visit_concise_when(self, node):
        """
        Searches for to be processed concise_when_block.
        """
        if node.data == 'start':
            for c in node.children:
                self.visit_concise_when(c)
        # concise_when_blocks can only occur at the root-level, hence we can
        # directly iterate here:
        if node.data == 'block':
            fake_tree = self.fake_tree(node)
            for i, c in enumerate(node.children):
                if c.data == 'concise_when_block':
                    node.children[i] = self.process_concise_block(c, fake_tree)

    def process_concise_block(self, node, fake_tree):
        """
        Creates a service_block around a concise_when_block and fixes up its
        line numbers with the fake_tree.
        """
        line = fake_tree.line()
        # create token from the "new" line
        name = Token('NAME', node.child(0).value, line=line)
        path_token = Token('NAME', node.child(1).value, line=line)
        t = Tree('service_block', [
            Tree('service', [
                Tree('path', [name]),
                Tree('service_fragment', [
                    Tree('command', [path_token]),
                    Tree('output', [path_token]),
                ])
            ]),
            Tree('nested_block', [
                Tree('block', [
                    node.when_block
                ])
            ])
        ])
        return t

    @staticmethod
    def create_entity(path):
        """
        Create an entity expression
        """
        return Tree('expression', [
            Tree('entity', [
                path
            ])
        ])

    def visit_assignment(self, node, block, parent):
        """
        Visit assignments and lower destructors
        """
        if not hasattr(node, 'children') or len(node.children) == 0:
            return

        if node.data == 'block':
            # only generate a fake_block once for every line
            # node: block in which the fake assignments should be inserted
            block = self.fake_tree(node)

        if node.data == 'assignment':
            c = node.children[0]

            if c.data == 'path':
                # a path assignment -> no processing required
                pass
            else:
                assert c.data == 'assignment_destructoring'
                line = node.line()
                base_expr = node.assignment_fragment.base_expression
                orig_node = Tree('base_expression', base_expr.children)
                orig_obj = block.add_assignment(orig_node, original_line=line)
                for i, n in enumerate(c.children):
                    new_line = block.line()
                    n.expect(len(n.children) == 1,
                             'object_destructoring_invalid_path')
                    name = n.child(0)
                    name.line = new_line  # update token's line info
                    # <n> = <val>
                    val = self.create_entity(Tree('path', [
                        orig_obj.child(0),
                        Tree('path_fragment', [
                            Tree('string', [name])
                        ])
                    ]))
                    if i + 1 == len(c.children):
                        # for the last entry, we can recycle the existing node
                        node.children[0] = n
                        node.assignment_fragment.base_expression.children = \
                            [val]
                    else:
                        # insert new fake line
                        a = block.assignment_path(n, val, new_line)
                        parent.children.insert(0, a)
        else:
            for c in node.children:
                self.visit_assignment(c, block, parent=node)

    @classmethod
    def rewrite_cmp_expr(cls, node):
        cmp_op = node.cmp_operator
        cmp_tok = cmp_op.child(0)

        if cmp_tok.type == 'NOT_EQUAL':
            cmp_tok = cmp_op.create_token('EQUAL', '==')
        elif cmp_tok.type == 'GREATER_EQUAL':
            cmp_tok = cmp_op.create_token('LESSER', '<')
            cmp_op.children.reverse()
        else:
            assert cmp_tok.type == 'GREATER'
            cmp_tok = cmp_op.create_token('LESSER_EQUAL', '<=')
            cmp_op.children.reverse()

        # replace comparison token
        cmp_op.children = [cmp_tok]
        # create new comparison tree with 'NOT'
        node.kind = 'unary_expression'
        node.children = [
            Tree('unary_operator', [node.create_token('NOT', '!')]),
            Tree('expression', node.children),
        ]

    def visit_cmp_expr(self, node):
        """
        Visit assignments and lower destructors
        """
        if not hasattr(node, 'children') or len(node.children) == 0:
            return

        if node.data == 'expression' and node.kind == 'cmp_expression' and \
                len(node.children) == 3:
            cmp_op = node.child(1)
            assert cmp_op.data == 'cmp_operator'
            cmp_tok = cmp_op.child(0)
            if cmp_tok.type == 'NOT_EQUAL' or \
                    cmp_tok.type == 'GREATER_EQUAL' or \
                    cmp_tok.type == 'GREATER':
                self.rewrite_cmp_expr(node)

        for c in node.children:
            self.visit_cmp_expr(c)

    def visit_arguments(self, node):
        """
        Transforms an argument tree. Short-hand argument (:foo) will be
        expanded.
        """
        if not hasattr(node, 'children') or len(node.children) == 0:
            return

        if node.data == 'arguments':
            Transformer.argument_shorthand(node)

        for c in node.children:
            self.visit_arguments(c)

    def visit_as_expr(self, node, block):
        """
        Visit assignments and move 'as' up the tree if required
        """
        if not hasattr(node, 'children') or len(node.children) == 0:
            return

        if node.data == 'foreach_block':
            block = node.foreach_statement
            assert block is not None
        elif node.data == 'service_block' or node.data == 'when_block':
            block = node.service.service_fragment
            block = node.service.service_fragment
            assert block is not None

        if node.data == 'expression' and node.kind == 'as_expression':
            as_op = node.as_operator
            if as_op is not None and as_op.output_names is not None:
                output = Tree('output', as_op.output_names.children)
                node.expect(block is not None, 'service_no_inline_output')
                block.children.append(output)
                node.children = [node.children[0].children[0]]

        for c in node.children:
            self.visit_as_expr(c, block)

    def visit_function_dot(self, node, block):
        """
        Visit function call with more than one path and lower
        them into mutations.
        """
        if not hasattr(node, 'children') or len(node.children) == 0:
            return

        if node.data == 'call_expression':
            call_expr = node
            if len(call_expr.path.children) > 1:
                path_fragments = call_expr.path.children
                call_expr.children = [
                    Tree('expression', [
                        Tree('entity', [
                            Tree('path', call_expr.path.children[:-1])
                        ])
                    ]),
                    Tree('mutation_fragment', [
                        path_fragments[-1].children[0],
                        *call_expr.children[1:]
                    ])
                ]
                call_expr.data = 'mutation'

        for c in node.children:
            self.visit_function_dot(c, block)

    def visit_path(self, node, block):
        """
        Visit path's with expression and lower these expressions to path's.
        """
        if not hasattr(node, 'children') or len(node.children) == 0:
            return

        if node.data == 'block':
            # only generate a fake_block once for every line
            # node: block in which the fake assignments should be inserted
            block = self.fake_tree(node)

        if node.data == 'path':
            for child in node.children:
                if not (isinstance(child, Tree) and
                        child.data == 'path_fragment'):
                    continue

                path_fragment = child
                expression = path_fragment.child(0)

                if not (isinstance(expression, Tree) and
                        expression.data == 'expression'):
                    # Don't do anything if the first child of path_fragment
                    # isn't actually an expression
                    continue

                # First lower path's deep inside the expression,
                # before lowering current expression.
                self.visit_path(expression, block)

                if len(expression.children) > 1:
                    # Generate an fake path for current expression and
                    # make path fragment point to this fake path.
                    fake_path = block.add_assignment(
                        expression,
                        original_line=node.line())
                    path_fragment.children = [fake_path]
                else:
                    # Remove the expression construct and make entity a
                    # direct descendant. This saves us from adding fake
                    # lines in some common use cases.
                    path_or_values = expression.child(0).child(0)
                    if path_or_values.data == 'values':
                        path_or_values = path_or_values.child(0)
                    else:
                        assert path_or_values.data == 'path'
                    path_fragment.children = [path_or_values]
        else:
            for c in node.children:
                self.visit_path(c, block)

    def process(self, tree):
        """
        Applies several preprocessing steps to the existing AST.
        """
        pred = Lowering.is_inline_expression
        self.visit_concise_when(tree)
        self.visit_cmp_expr(tree)
        self.visit_as_expr(tree, block=None)
        self.visit_arguments(tree)
        self.visit_assignment(tree, block=None, parent=None)
        self.visit_string_templates(tree, block=None, parent=None)
        self.visit_function_dot(tree, block=None)
        self.visit(tree, None, None, pred,
                   self.replace_expression, parent=None)
        self.visit_path(tree, None)
        return tree
