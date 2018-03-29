from .Method import Method
from ..version import version


class Program:

    def __init__(self, parser, story):
        parser.program = self
        self.parser = parser
        self.story = story
        self.lines = {}

    @staticmethod
    def sorted_lines(lines):
        return sorted(lines.keys(), key=lambda x: int(x))

    def last_line(self):
        """
        Returns the last line from current generated lines
        """
        if self.lines:
            return self.sorted_lines(self.lines)[-1]

    def set_as_next_line(self, line_number):
        """
        Sets the current line as the next line for the previous one
        """
        previous_line = self.last_line()
        if previous_line:
            self.lines[previous_line]['next'] = line_number

    def parse_suite(self, suite, parent_line):
        """
        Parses a set of items that are the children of another line
        """
        for item in suite:
            self.set_as_next_line(item.lineno)
            self.lines[item.lineno] = item.json()
            self.lines[item.lineno]['parent'] = parent_line

    def parse_item(self, item):
        """
        Parses a single item
        """
        self.set_as_next_line(item.lineno)
        self.lines[item.lineno] = item.json()
        if item.suite:
            self.parse_suite(item.suite, item.lineno)

    def generate(self):
        for item in self.story:
            self.set_as_next_line(item.lineno)
            self.lines[item.lineno] = item.json()
            if item.suite:
                self.parse_suite(item.suite, item.lineno)

    def json(self):
        self.generate()
        return {'version': version, 'script': self.lines}

    def __repr__(self):
        return 'Program({}, {})'.format(self.parser, self.story)
