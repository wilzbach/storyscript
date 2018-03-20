from .Method import Method
from ..version import version


class Program:

    def __init__(self, parser, story):
        parser.program = self
        self.parser = parser
        self.story = story

    def parse_item(self, dictionary, item, parent=None):
        if isinstance(item, Method):
            dictionary[item.lineno] = item.json()
            if parent:
                dictionary[item.lineno]['prev'] = parent.lineno

            if item.suite:
                child_line_numbers = [
                    self.parse_item(dictionary, child, parent=item)
                    for child in item.suite
                ]
                dictionary[item.lineno]['next'] = child_line_numbers[0]

            return item.lineno

        else:
            child_line_numbers = [
                self.parse_item(dictionary, child, parent=parent)
                for child in item
            ]
            return child_line_numbers[0]

    def json(self):
        script_dictionary = {}
        self.parse_item(script_dictionary, self.story)
        return {'version': version, 'script': script_dictionary}

    def __repr__(self):
        return 'Program({}, {})'.format(self.parser, self.story)
