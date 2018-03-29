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

    def parse_suite(self, suite, parent_line):
        """
        Parses a set of items that are the children of another line
        """
        lines = {}
        for item in suite:
            previous_line = self.last_line(lines)
            if previous_line:
                lines[previous_line]['next'] = item.lineno
            if lines == {}:
                parent_line['next'] = item.lineno
            lines[item.lineno] = item.json()
            lines[item.lineno]['parent'] = parent_line['ln']
        return lines

    def generate(self):
        story = {}
        for item in self.story:
            previous_line = self.last_line(story)
            story[item.lineno] = item.json()
            if previous_line:
                story[previous_line]['next'] = item.lineno
            if item.suite:
                story = {**story, **self.parse_suite(item.suite, story[item.lineno])}
        return story

    def json(self):
        return {'version': version, 'script': self.generate()}

    def __repr__(self):
        return 'Program({}, {})'.format(self.parser, self.story)
