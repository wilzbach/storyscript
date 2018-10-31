# -*- coding: utf-8 -*-
import re

from lark import Transformer as LarkTransformer

from .tree import Tree
from ..exceptions import StoryError


class Transformer(LarkTransformer):

    """
    Performs transformations on the tree before it's parsed.
    All trees are transformed to Storyscript's custom tree. In some cases,
    additional transformations or checks are performed.
    """
    def __init__(self, path):
        self.path = path

    def arguments(self, matches):
        """
        Transform an argument tree. If dealing with is a short-hand argument,
        expand it.
        """
        if len(matches) == 1:
            matches = [matches[0].child(0), matches[0]]
        return Tree('arguments', matches)

    def assignment(self, matches):
        token = matches[0].children[0]
        if '/' in token.value:
            raise StoryError('variables-backslash', token, path=self.path)
        if '-' in token.value:
            raise StoryError('variables-dash', token, path=self.path)
        return Tree('assignment', matches)

    def service_block(self, matches):
        """
        Transforms service blocks, moving indented arguments back to the first
        node.
        """
        if len(matches) > 1:
            if matches[1].block.rules:
                for argument in matches[1].find_data('arguments'):
                    matches[0].service_fragment.children.append(argument)
                return Tree('service_block', [matches[0]])
        return Tree('service_block', matches)

    def __getattr__(self, attribute, *args):
        return lambda matches: Tree(attribute, matches)
