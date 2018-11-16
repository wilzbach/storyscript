# -*- coding: utf-8 -*-
from ..exceptions import StorySyntaxError


class Lines:
    """
    Holds compiled lines and provides methods for operation on lines.
    """
    def __init__(self):
        self.lines = {}
        self.variables = []
        self.services = []
        self.functions = {}
        self.outputs = {}
        self.modules = {}

    def sort(self):
        """
        Returns ordered line numbers
        """
        return sorted(self.lines.keys(), key=lambda x: float(x))

    def first(self):
        """
        Gets the first line.
        """
        if self.lines:
            return self.sort()[0]

    def last(self):
        """
        Gets the last line
        """
        if self.lines:
            return self.sort()[-1]

    def set_name(self, name):
        """
        Sets the name of the previous line
        """
        previous_line = self.last()
        if previous_line:
            self.lines[previous_line]['name'] = name

    def set_next(self, line_number):
        """
        Finds the previous line, and set the current as its next line
        """
        previous_line = self.last()
        if previous_line:
            self.lines[previous_line]['next'] = line_number

    def set_exit(self, line):
        """
        Sets the current line as the exit line for a previous one, as needed
        in if/elif/else and try/catch/finally blocks.
        """
        methods = ['if', 'elif', 'try', 'catch']
        for line_number in self.sort()[::-1]:
            if self.lines[line_number]['method'] in methods:
                self.lines[line_number]['exit'] = line
                break

    def set_output(self, line, output):
        self.outputs[line] = output

    def is_output(self, parent_line, service):
        """
        Checks whether a service has been defined as output for this block
        """
        if parent_line in self.outputs:
            if service in self.outputs[parent_line]:
                return True
        return False

    def make(self, method, line, name=None, args=None, service=None,
             command=None, function=None, output=None, enter=None, exit=None,
             parent=None):
        """
        Creates the base dictionary for a given line.
        """
        dictionary = {
            line: {
                'method': method,
                'ln': line,
                'output': output,
                'name': name,
                'service': service,
                'command': command,
                'function': function,
                'args': args,
                'enter': enter,
                'exit': exit,
                'parent': parent
            }
        }
        self.lines = {**self.lines, **dictionary}

    def service_method(self, service, line):
        """
        Finds whether a service is a function call or a service.
        """
        if service in self.functions:
            return 'call'
        if service.split('.')[0] in self.modules:
            return 'call'
        if '.' in service:
            raise StorySyntaxError('service_name')
        return 'execute'

    def append(self, method, line, **kwargs):
        if 'service' in kwargs:
            method = self.service_method(kwargs['service'], line)

        if method == 'function':
            self.functions[kwargs['function']] = line
        elif method == 'set':
            self.variables.append(kwargs['name'])
        elif method == 'execute':
            if self.is_output(kwargs['parent'], kwargs['service']) is False:
                self.services.append(kwargs['service'])
        self.set_next(line)
        self.make(method, line, **kwargs)

    def execute(self, line, service, command, arguments, output, enter,
                parent):
        kwargs = {'service': service, 'command': command, 'args': arguments,
                  'output': output, 'enter': enter, 'parent': parent}
        self.append('execute', line, **kwargs)

    def get_services(self):
        """
        Get the services and remove duplicates.
        """
        return list(set(self.services))
