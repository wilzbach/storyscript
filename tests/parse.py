from storyscript import parser


def parse(script):
    _parser = parser.Parser(False, True)
    return _parser.parse(script, debug=True)
