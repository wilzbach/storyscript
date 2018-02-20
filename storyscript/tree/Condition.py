class Condition:

    def __init__(self, *args):
        self.args = args

    def json(self):
        dictionary = {
            '$OBJECT': 'condition',
            'condition': self.args[0].json(),
            'is': self.args[1],
            'then': self.args[2].json(),
            'else': None
        }
        if len(self.args) > 3:
            dictionary['else'] = self.args[3].json()
        return dictionary
