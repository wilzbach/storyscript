# -*- coding: utf-8 -*-
from lark import Transformer as LarkTransformer

from .tree import Tree


class Transformer(LarkTransformer):

    def start(self, matches):
        return Tree('line', matches)

    def string(self, matches):
        return matches
