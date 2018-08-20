# -*- coding: utf-8 -*-
import random
import uuid

from lark.lexer import Token

from ..parser import Tree


class FakeTree:
    """
    Creates fake trees that are not in the original story source.
    """

    @staticmethod
    def line(line):
        """
        Creates a fake line number, using a given line as base so that
        line - 1 < fake line < line
        """
        upper_bound = int(line)
        lower_bound = upper_bound - 1
        return str(random.uniform(lower_bound, upper_bound))

    @staticmethod
    def path(line):
        """
        Creates a fake tree path.
        """
        path = '${}'.format(uuid.uuid4().hex[:8])
        return Tree('path', [Token('NAME', path, line=line)])

    @classmethod
    def assignment(cls, line, value):
        """
        Creates a fake assignment tree, equivalent to "$fake = value"
        """
        fake_line = cls.line(line)
        value.child(0).child(0).line = fake_line
        path = cls.path(fake_line)
        fragment = Tree('assignment_fragment', [Token('EQUALS', '='), value])
        return Tree('assignment', [path, fragment])
