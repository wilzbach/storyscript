from .Method import Method
from ..version import version


class Program:

    def __init__(self, parser, story):
        parser.program = self
        self.parser = parser
        self.story = story

    def sorted_lines(self, lines):
        return sorted(lines.keys(), key=lambda x: int(x))

    def next_line(self, lines, line_number):
        sorted_lines = self.sorted_lines(lines)
        next_line_index = sorted_lines.index(line_number) + 1
        if next_line_index < len(sorted_lines):
            next_line = sorted_lines[next_line_index]
            return lines[str(next_line)]

    def children(self, dictionary, children, parent=None):
        for child in children:
            self.parse_item(dictionary, child, parent=parent)

    def parse_item(self, dictionary, item, parent=None):
        if isinstance(item, Method):
            dictionary[item.lineno] = item.json()
            if parent:
                dictionary[item.lineno]['parent'] = parent.lineno
            if item.suite:
                child_line_numbers = [
                    self.parse_item(dictionary, child, parent=item)
                    for child in item.suite
                ]
                dictionary[item.lineno]['next'] = child_line_numbers[0]
            return item.lineno
        child_line_numbers = [
            self.parse_item(dictionary, child, parent=parent)
            for child in item
        ]
        return child_line_numbers[0]

    def generate(self):
        story = {}
        for item in self.story:
            story[item.lineno] = self.parse_item(item)
        return story

    def json(self):
        return {'version': version, 'script': self.generate()}

    def __repr__(self):
        return 'Program({}, {})'.format(self.parser, self.story)
