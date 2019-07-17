# -*- coding: utf-8 -*-
from lark import Transformer as LarkTransformer
from lark.lexer import Token

from .Tree import Tree
from ..exceptions import StorySyntaxError


class Transformer(LarkTransformer):

    """
    Performs transformations on the tree before it's parsed.
    All trees are transformed to Storyscript's custom tree. In some cases,
    additional transformations or checks are performed.
    """
    reserved_keywords = ['function', 'if', 'else', 'foreach', 'return',
                         'returns', 'try', 'catch', 'finally', 'when', 'as',
                         'while', 'throw', 'null']
    future_reserved_keywords = [
        'async', 'story', 'assert', 'called', 'mock', 'class', 'extends',
        'implements', 'interface', 'type', 'public', 'private', 'protected',
        'const', 'immutable', 'let', 'var', 'auto', 'immutable', 'switch',
        'module', 'package', 'final', 'this', 'self', 'case', 'abstract',
        'static', 'none', 'await', 'service', 'in', 'has', 'not', 'is', 'inf',
        'nan', 'unknown', 'import'
    ]

    def __init__(self, allow_single_quotes=False):
        self.allow_single_quotes = allow_single_quotes

    @classmethod
    def is_keyword(cls, token):
        keyword = token.value
        if keyword is None:
            return
        if keyword in cls.reserved_keywords:
            raise StorySyntaxError('reserved_keyword',
                                   token=token,
                                   format_args={'keyword': keyword})
        if keyword in cls.future_reserved_keywords:
            raise StorySyntaxError('future_reserved_keyword',
                                   token=token,
                                   format_args={'keyword': keyword})
        if keyword.startswith('__'):
            raise StorySyntaxError('path_name_internal', token=token)

    @staticmethod
    def assignment(matches):
        """
        Transforms an assignment tree and checks for invalid characters in the
        variable name.
        """
        matches[1].expect(len(matches[0].children) > 0,
                          'object_destructoring_no_variables')
        token = matches[0].children[0]
        if isinstance(token, Tree):
            matches[0].expect(token.data != 'inline_expression',
                              'assignment_inline_expression')
        return Tree('assignment', matches)

    @classmethod
    def command(cls, matches):
        cls.is_keyword(matches[0])
        return Tree('command', matches)

    @classmethod
    def path(cls, matches):
        cls.is_keyword(matches[0])
        return Tree('path', matches)

    @classmethod
    def inline_service(cls, matches):
        """
        Transforms an inline service back into a normal service.
        """
        matches[1].data = 'service_fragment'
        return Tree('service', matches)

    @staticmethod
    def filter_nested_block(nested_block, nodes):
        for block in nested_block.children:
            assert block.data == 'block'
            el = block.follow(nodes)
            if el is not None:
                yield el

    @classmethod
    def service_block(cls, matches):
        """
        Transforms service blocks, moving indented arguments back to the first
        node.
        """
        if len(matches) == 1:
            return Tree('service_block', matches)

        if matches[1].block.rules:
            args = [*cls.filter_nested_block(
                matches[1],
                ['rules', 'block', 'arguments']
            )]
            if len(args) > 0:
                for arg in args:
                    matches[0].service_fragment.children.append(arg)
                return Tree('service_block', [matches[0]])

        return Tree('service_block', matches)

    @staticmethod
    def create_when_block(service_name, block, command=None, output=None,
                          fragment=None):
        """
        Creates a when_block node from its building blocks.
        """
        assert service_name is not None
        if fragment:
            return Transformer.create_when_block_tree(
                service_name=service_name,
                fragment=fragment,
                block=block
            )

        service_fragment = Tree('service_fragment', [])
        if command:
            assert isinstance(command, Token)
            assert command.type == 'NAME'
            service_fragment.children.append(Tree('command', [command]))

        if output:
            assert output.data == 'output'
            service_fragment.children.append(output)
        return Transformer.create_when_block_tree(
            service_name=service_name,
            fragment=service_fragment,
            block=block
        )

    @staticmethod
    def create_when_block_tree(service_name, fragment, block):
        """
        Creates a when_block tree node from its building blocks.
        """
        service = Tree('service', [
            Tree('path', [service_name]),
            fragment,
        ])
        return Tree('when_block', [service, block])

    @classmethod
    def when_block(cls, matches):
        """
        Transforms when blocks.
        """
        when = matches[0]
        if when.type == 'NAME':
            # service without commands for which the command will be inferred
            # from the parent service call, e.g. `when my_service`
            assert when.type == 'NAME'
            output = matches[1].data == 'output' and matches[1]
            return cls.create_when_block(
                service_name=when,
                output=output,
                block=matches[-1],
            )

        assert len(matches) == 2
        assert isinstance(when.children[0], Token)
        assert when.data == 'when_service'
        name_token = when.child_token(0, 'NAME')
        path_token = when.path.child_token(0, 'NAME')
        nested_block = matches[1]

        if not when.service_fragment:
            # workaround for LARK's parser limitations (no look-ahead)
            # it parses: when <service> <path> <output>?
            # but it's actually: when <service> <command> <output>?
            # Example:
            #   when my_service listen
            #     -> <when> <name=myservice> <path=listen>
            return cls.create_when_block(
                service_name=name_token,
                command=path_token,
                output=when.output,
                block=nested_block
            )

        # workaround for LARK's parser. It parses the first service_fragment
        # argument wrongly, because arguments without names are still allowed
        # and thus the parser only sees `path (name:)?expression`
        # Example:
        #   when listen method:'/get'
        #     -> <when> <name=myservice> <path=method> <:get>
        if not when.service_fragment.command:
            first_arg = when.service_fragment.arguments
            cls.argument_shorthand(first_arg)
            if first_arg and not isinstance(first_arg.first_child(), Token) \
                    and first_arg.first_child().data == 'expression':
                # the parser parsed the first argument as `:<or_expression>`
                first_arg.children = [path_token, first_arg.last_child()]
            else:
                command = Tree('command', [path_token])
                when.service_fragment.children.insert(0, command)
            return cls.create_when_block(
                service_name=name_token,
                fragment=when.service_fragment,
                block=nested_block)

        # concise when which needs to wrapped in a service block
        when.children.pop(0)
        when.data = 'service'
        return Tree('concise_when_block', [
            name_token, path_token,
            Tree('when_block', [when, nested_block]),
        ])

    @classmethod
    def absolute_expression(cls, matches):
        """
        Transform zero-argument expression into service blocks
        """
        if len(matches) == 1:
            path = matches[0].follow_node_chain([
                'expression', 'entity', 'path'
            ])
            if path is not None:
                service_fragment = Tree('service_fragment', [])
                service = Tree('service', [path, service_fragment])
                return Tree('service_block', [service])
        return Tree('absolute_expression', matches)

    @classmethod
    def function_block(cls, matches):
        """
        Transforms function blocks, moving indented arguments back to the first
        node.
        """
        if len(matches) > 1:
            if matches[1].data == 'indented_typed_arguments':
                for argument in matches.pop(1).find_data('typed_argument'):
                    matches[0].children.append(argument)
                matches[-1] = Tree('nested_block', [matches[-1]])

        return Tree('function_block', matches)

    @staticmethod
    def multi_line_string(text):
        """
        Lines are joined by a single space unless they end with a backslash.
        Indentation is ignored.
        """
        buf = ''
        has_backslash = True
        for i,  line in enumerate(text.split('\n')):
            if i == 0:
                buf += line
            elif has_backslash:
                buf = buf[:-1] + line.lstrip()
            else:
                line = line.lstrip()
                if len(line) > 0:
                    buf += f' {line.lstrip()}'

            if len(line) > 0 and line[-1] == '\\':
                has_backslash = True
            else:
                has_backslash = False

        return buf

    def string(self, matches):
        """
        Remove quotes from strings.
        """
        tree = Tree('string', matches)
        # Lark string still contain the raw quotes around them -> remove
        if matches[0].type == 'SINGLE_QUOTED' or \
                matches[0].type == 'DOUBLE_QUOTED':
            text = matches[0].value[1:-1]
            # multi-line strings
            text = self.multi_line_string(text)
            if matches[0].type == 'SINGLE_QUOTED':
                tree.expect(self.allow_single_quotes, 'single_quotes')
        else:
            text = matches[0].value[3:-3]
        matches[0].value = text
        return tree

    @staticmethod
    def argument_shorthand(tree):
        """
        Try to convert argument to shorthand syntax if possible.
        """
        assert tree.data == 'arguments'
        if len(tree.children) == 1:
            path = tree.child(0).follow_node_chain([
                'expression', 'entity', 'path'
            ])
            if path is not None:
                # shorthand syntax for arguments (:name)
                tree.children = [path.child(0), tree.children[0]]

    @classmethod
    def expression_rewrite(cls, expr, matches):
        if len(matches) == 1:
            return matches[0]
        else:
            t = Tree('expression', matches)
            t.kind = expr
            return t

    @classmethod
    def expression(cls, matches):
        return cls.expression_rewrite('expression', matches)

    @classmethod
    def or_expression(cls, matches):
        return cls.expression_rewrite('or_expression', matches)

    @classmethod
    def and_expression(cls, matches):
        return cls.expression_rewrite('and_expression', matches)

    @classmethod
    def cmp_expression(cls, matches):
        return cls.expression_rewrite('cmp_expression', matches)

    @classmethod
    def arith_expression(cls, matches):
        return cls.expression_rewrite('arith_expression', matches)

    @classmethod
    def mul_expression(cls, matches):
        return cls.expression_rewrite('mul_expression', matches)

    @classmethod
    def unary_expression(cls, matches):
        return cls.expression_rewrite('unary_expression', matches)

    @classmethod
    def as_expression(cls, matches):
        return cls.expression_rewrite('as_expression', matches)

    @classmethod
    def pow_expression(cls, matches):
        return cls.expression_rewrite('pow_expression', matches)

    @classmethod
    def dot_arguments(cls, matches):
        return Tree('mutation', [
            Tree('mutation_fragment', [
                matches[0],
                *matches[1:]
            ])
        ])

    @staticmethod
    def build_inline(node):
        """
        Build an inline_expression around `node`.
        inline_expression will be lowered into new lines by the compiler.
        """
        return Tree('expression', [
                Tree('entity', [
                    Tree('path', [
                        Tree('inline_expression', [
                            node
                        ])
                    ])
                ])
            ])

    @classmethod
    def dot_expression(cls, matches):
        if len(matches) == 1:
            return matches[0]
        elif isinstance(matches[0], Token) and matches[0].type == 'FLOAT':
            # 1. is parsed as FLOAT token
            # -> convert into a mutation
            value = matches[0].value.split('.')[0]
            matches[0] = Tree('dummy', [matches[0]]).create_token('INT', value)
            # end_column is a string, but still an int :/
            matches[0].end_column = str(int(matches[0].end_column) - 1)
            tree = Tree('mutation', [
                Tree('expression', [
                    Tree('entity', [
                        Tree('values', [
                            Tree('number', [
                                matches[0]
                            ])
                        ])
                    ])
                ]),
                Tree('mutation_fragment', [matches[1]])
            ])
            # At the moment there are no int mutations with arguments
            assert len(matches) < 3 or matches[2].data == 'mutation'

            offset = 2
            # if len(matches) >= 3 and matches[2].data != 'mutation':
            #   # append its arguments (if available)
            #   tree.children[1].append(matches[2])
            #   offset += 1
            for mutation in matches[offset:]:
                tree = Tree('mutation', [
                    cls.build_inline(tree),
                    *mutation.children,
                ])
        else:
            # normal dot_expressions like "a".mutation()
            tree = Tree('mutation', [
                    matches[0],
                    *matches[1].children
                ])
            for mutation in matches[2:]:
                expression = cls.build_inline(tree)
                tree = Tree('mutation', [
                    expression,
                    *mutation.children,
                ])
        tree = cls.build_inline(tree)
        return tree

    @classmethod
    def primary_expression(cls, matches):
        if len(matches) == 1 and matches[0].data == 'entity':
            # leave the separate expression only for leaf entities
            t = Tree('expression', matches)
            t.kind = 'primary_expression'
            return t
        return cls.expression_rewrite('primary_expression', matches)

    def __getattr__(self, attribute, *args):
        return lambda matches: Tree(attribute, matches)
