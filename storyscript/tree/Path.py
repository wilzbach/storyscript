import re


class Path:
    def __init__(self, parser, line_number, path):
        self.parser = parser
        self.lineno = line_number
        self.paths = path

    def split(self, path):
        """
        Transforms a.b['c'] into [a, b, c]
        """
        brackets = re.compile(r"""(\[(\'|\")*.+?(\'|\")*\])""")
        matches = []
        for match in brackets.findall(path):
            path = path.replace(match[0], '.@', 1)
            matches.append(match[0].replace('[', '')
                           .replace(']', '')
                           .replace('"', '')
                           .replace("'", ''))

        shards = path.split('.')
        mapping = map(lambda x: matches.pop() if x == '@' else x, shards)
        return list(mapping)

    def json(self):
        return {
            '$OBJECT': 'path',
            'paths': self.paths
        }
