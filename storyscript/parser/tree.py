# -*- coding: utf-8 -*-
from lark.tree import Tree as LarkTree


class Tree(LarkTree):

    def json(self):
        return 'json'
