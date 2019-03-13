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
                         'import', 'while', 'throw']
    future_reserved_keywords = ['async', 'story', 'assert', 'called', 'mock']

    @classmethod
    def is_keyword(cls, token):
        keyword = token.value
        if keyword in cls.reserved_keywords:
            raise StorySyntaxError('reserved_keyword',
                                   token=token, format={'keyword': keyword})
        if keyword in cls.future_reserved_keywords:
            raise StorySyntaxError('future_reserved_keyword',
                                   token=token, format={'keyword': keyword})

    @staticmethod
    def implicit_output(tree):
        """
        Adds implicit output to a service.
        """
        fragment = tree.service_fragment
        if fragment and fragment.output is None:
            output = Tree('output', [fragment.command.child(0)])
            fragment.children.append(output)

    @staticmethod
    def arguments(matches):
        """
        Transforms an argument tree. If dealing with is a short-hand argument,
        expand it.
        """
        if len(matches) == 1:
            matches = [matches[0].child(0), matches[0]]
        return Tree('arguments', matches)

    @staticmethod
    def assignment(matches):
        """
        Transforms an assignment tree and checks for invalid characters in the
        variable name.
        """
        token = matches[0].children[0]
        if '/' in token.value:
            raise StorySyntaxError('variables_backslash', token=token)
        if '-' in token.value:
            raise StorySyntaxError('variables_dash', token=token)
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
    def service_block(cls, matches):
        """
        Transforms service blocks, moving indented arguments back to the first
        node.
        """
        if len(matches) > 1:
            cls.implicit_output(matches[0])
            if matches[1].block.rules:
                for argument in matches[1].find_data('arguments'):
                    matches[0].service_fragment.children.append(argument)
                return Tree('service_block', [matches[0]])
        return Tree('service_block', matches)

    @classmethod
    def when_block(cls, matches):
        """
        Transforms when blocks.
        """
        m = matches[0]
        if isinstance(m, Token):
            # manually add implicit output for service without commands for
            # which the command will be inferred from the parent service call
            # e.g. `when my_service`
            assert m.type == 'NAME'
            output = Tree('output', [m])
            path = Tree('path', [m])
            service_fragment = Tree('service_fragment', [output])
            service = Tree('service', [path, service_fragment])
            matches[0] = service
        elif m.data == 'service' and \
                m.service_fragment.command is None and \
                m.service_fragment.output is None:
            # manually add implicit output for service without commands for
            # which the command will be inferred from the parent service call
            # e.g. `when my_service argument: 2`
            output = Tree('output', [m.path.find_first_token()])
            m.service_fragment.children.append(output)
        else:
            cls.implicit_output(m)
        return Tree('when_block', matches)

    @classmethod
    def absolute_expression(cls, matches):
        """
        Transform zero-argument expression into service blocks
        """
        if len(matches) == 1:
            path = matches[0].follow_node_chain([
                'expression', 'or_expression', 'and_expression',
                'cmp_expression', 'arith_expression', 'mul_expression',
                'unary_expression', 'pow_expression', 'primary_expression',
                'entity', 'path'
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

        return Tree('function_block', matches)

    def __getattr__(self, attribute, *args):
        return lambda matches: Tree(attribute, matches)
