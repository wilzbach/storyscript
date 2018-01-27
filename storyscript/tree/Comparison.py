class Comparison:

    def __init__(self, left, method, right):
        self.left = left
        self.method = method
        self.right = right

    def _handside_json(self, item, handside_name):
        handside = getattr(self, handside_name)
        if hasattr(handside, 'json'):
            item[handside_name] = handside.json()

    def json(self):
        result = {
            '$OBJECT': 'method',
            'left': self.left,
            'right': self.right,
            'method': self.method
        }

        self._handside_json(result, 'right')
        self._handside_json(result, 'left')
        return result
