import re

from . import exceptions


any_number = tuple('0123456789')


def resolve_path(data, path):
    """
    Resolves a path, recursivelly in the data
    """
    try:
        for part in path.split('.'):
            if part.startswith(any_number):
                data = data[int(part)]
            else:
                data = data[part]
        return data
    except Exception:
        print('Unable to resolve path %s' % path)
        return None


def resolve_obj(data, obj):
    """
    Resolves a Story Object to it's real value
    """
    if 'path' in obj:
        return resolve_path(data, obj['path'])
    elif 'value' in obj:
        return obj['value']
    elif 'regexp' in obj:
        return re.compile(obj['regexp'])
    elif 'expression' in obj:
        return resolve_expression(data, **obj)
    elif 'method' in obj:
        return resolve_method(data, **obj)


def resolve_method(data, left, right, method):
    """
    Resolve method to a boolean
    """
    _left = resolve_obj(data, left)
    _right = resolve_obj(data, right)
    try:
        if method == 'like':
            return _right.match(_left) is not None
        elif method in ('has', 'contains'):
            return _right in _left
        elif method == 'in':
            return _left in _right
        elif method == 'excludes':
            return _left not in _right
        elif method == 'isnt':
            return _right != _left
        elif method == 'is':
            return _right == _left

    except Exception as err:
        raise err


def resolve_expression(data, expression, values):
    """
    Resolve expression to a boolean
    """
    try:
        return eval(expression.format(
            *map(
                stringify,
                resolve_list(data, values)
            )
        ))

    except Exception as err:
        raise err


def resolve_list(data, lst):
    """
    Resolves a list of arguments [object, object, ...]
    """
    return [
        resolve_obj(data, obj)
        for obj in lst
    ]


def resolve_dict(data, dct):
    """
    Resolves a dictionary of {key:objects}
    """
    return dict(
        (key, resolve_obj(data, value))
        for key, value in dct.items()
    )


def stringify(obj):
    """
    Escapes a string for expression injection
    """
    if type(obj) is str:
        return '"""%s"""' % obj.replace('"', '\"')
    return str(obj)
