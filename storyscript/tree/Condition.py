class Condition:

    def __init__(self, *args):
        self.args = args

    def json(self):
        return {
            '$OBJECT': 'condition',
            'condition': self.args[0].json(),
            'is': self.args[1],
            'then': self.args[2].json(),
            'else': self.args[3].json() if self.args[3] else None
        }
