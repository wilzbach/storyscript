class Method:

    def __init__(self, method, parser, line_number, suite=None, output=None,
                 container=None, args=None, enter=None, exit=None):
        self.method = method
        self.parser = parser
        self.lineno = str(line_number)
        self.suite = suite
        self.output = output
        self.container = container
        self.args = args
        self.enter = enter
        self.exit = exit

        if self.enter:
            self.enter = str(self.enter)

        if self.exit:
            self.exit = str(self.exit)

    def args_json(self, args):
        if type(args) in (bool, int, float, type(None)):
            return args
        elif hasattr(args, 'json'):
            return args.json()
        elif type(args) is dict:
            return dict({
                key: self.args_json(value) for key, value in args.items()
            })
        elif type(args) in (list, tuple):
            return list(map(self.args_json, args))
        return args

    def json(self):
        dictionary = {
            'method': self.method,
            'ln': self.lineno,
            'output': self.output.json() if self.output else None,
            'container': self.container,
            'args': self.args_json(self.args),
            'enter': self.enter,
            'exit': self.exit
        }
        if self.exit:
            dictionary['exit'] = str(self.exit)
        return dictionary
