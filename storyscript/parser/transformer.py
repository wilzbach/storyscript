# -*- coding: utf-8 -*-
from lark import Transformer as LarkTransformer


class Transformer(LarkTransformer):

    def string(self, matches):
        return matches
