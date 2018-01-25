class Expression:

    def __init__(self, expression):
        self.expression = [('', expression)]

    def json(self, evals=None, values=None):
        if evals is None:
            if hasattr(self.expression[0][1], 'json'):
                return self.expression[0][1].json()
            return self.expression[0][1]

        for mixin, expression in self.expression:
            if mixin != '':
                evals.append(mixin)

            if isinstance(expression, Expression):
                json = expression.json(evals, values)
                evals = [json['expression']]
                values = json['values']
            elif hasattr(expression, 'json'):
                values.append(expression.json())
                evals.append('{}')
            else:
                evals.append(expression)

        return {
            '$OBJECT': 'expression',
            'expression': ' '.join(evals),
            'values': values
        }
