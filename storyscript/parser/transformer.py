# -*- coding: utf-8 -*-
import re

from lark import Transformer as LarkTransformer

from .tree import Tree


class Transformer(LarkTransformer):

    def __getattr__(self, attribute, *args):
        return lambda matches: Tree(attribute, matches)
