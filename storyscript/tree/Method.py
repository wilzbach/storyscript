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

    def args_json(self, args):
        if type(args) in (bool, int, float):
            return args
        elif hasattr(args, 'json'):
            return args.json()
        elif type(args) is dict:
            items = {}
            for key, value in args.items():
                items[key] = self.args_json(value)
            return items
        elif type(args) is list:
            items = []
            for value in args:
                if hasattr(value, 'json'):
                    items.append(value.json())
                else:
                    items.append(value)
            return items

    def json(self):
        return {'method': self.method,
                'ln': self.lineno,
                'output': self.output,
                'container': self.container,
                'args': self.args_json(self.args),
                'enter': self.enter,
                'exit': self.exit
                }
