from .Method import Method
from ..version import version


class Program:

    def __init__(self, parser, story):
        parser.program = self
        self.parser = parser
        self.story = story

    def sorted_lines(self, lines):
        return sorted(lines.keys(), key=lambda x: int(x))

    def last_line(self, lines):
        sorted_lines = self.sorted_lines(lines)
        if sorted_lines:
            return sorted_lines[-1]

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

    def parse_suite(self, suite, parent_linenumber):
        """
        Parses a set of items that are the children of another line
        """
        lines = {}
        for item in suite:
            previous_line = self.last_line(lines)
            lines[item.lineno] = item.json()
            lines[item.lineno]['parent'] = parent_linenumber
            if previous_line:
                lines[previous_line]['next'] = item.lineno
        return lines

    def generate(self):
        story = {}
        for item in self.story:
            previous_line = self.last_line(story)
            story[item.lineno] = item.json()
            if previous_line:
                story[previous_line]['next'] = item.lineno
            if item.suite:
                story = {**story, **self.parse_suite(item.suite, item.lineno)}
        return story

    def json(self):
        return {'version': version, 'script': self.generate()}

    def __repr__(self):
        return 'Program({}, {})'.format(self.parser, self.story)
