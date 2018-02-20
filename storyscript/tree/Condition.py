class Condition:

    def __init__(self, condition, boolean, consequence, other=None):
        self.condition = condition
        self.boolean = boolean
        self.consequence = consequence
        self.other = other

    def json(self):
        dictionary = {
            '$OBJECT': 'condition',
            'condition': self.condition.json(),
            'is': self.boolean,
            'then': self.consequence.json(),
            'else': self.other
        }
        if self.other:
            dictionary['else'] = self.other.json()
        return dictionary
