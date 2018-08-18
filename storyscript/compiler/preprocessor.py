# -*- coding: utf-8 -*-
import uuid

from lark.lexer import Token

from ..parser import Tree


class Preprocessor:
    """
    Performs additional transformations that can't be performed, or would be
    too complicated for the Transformer, before the tree is compiled.
    """

    @staticmethod
    def magic_line(line):
        """
        Creates a virtual line number, using a given line as base so that
        line - 1 < magic line < line
        """
        base = int(line) - 1
        extension = str(uuid.uuid4().int)[:8]
        return '{}.{}'.format(base, extension)

    @staticmethod
    def magic_path(line):
        """
        Creates a virtual path tree.
        """
        path = '${}'.format(uuid.uuid4().hex[:8])
        return Tree('path', [Token('NAME', path, line=line)])

    @classmethod
    def magic_assignment(cls, line, value):
        """
        Creates a magic assignment tree, equivalent to: "$magic = value"
        """
        value.child(0).child(0).line = line
        path = cls.magic_path(line)
        fragment = Tree('assignment_fragment', [Token('EQUALS', '='), value])
        return Tree('assignment', [path, fragment])

    @classmethod
    def inline_arguments(cls, block, service):
        """
        Processes an inline expression in a service call, for example:
        alpine echo text:(random value)
        """
        for argument in service.service_fragment.find_data('arguments'):
            if argument.inline_expression:
                line = cls.magic_line(block)
                value = argument.inline_expression.service
                assignment = cls.magic_assignment(line, value)
                block.insert(assignment)
                argument.replace(1, assignment.path)

    @classmethod
    def process_assignments(cls, block):
        """
        Process assignments, looking for inline expressions to replace,
        for example: a = alpine echo text:(random value)
        """
        for assignment in block.find_data('assignment'):
            service = assignment.node('assignment_fragment.service')
            if service:
                cls.inline_arguments(block, service)

    @classmethod
    def process_blocks(cls, tree):
        """
        Processes blocks, looking for trees that must be preprocessed.
        """
        for block in tree.find_data('block'):
            cls.process_assignments(block)
            service = block.node('service_block.service')
            if service:
                cls.inline_arguments(block, service)

    @classmethod
    def process(cls, tree):
        cls.process_blocks(tree)
        return tree
