# -*- coding: utf-8 -*-


class ErrorCodes:

    unidentified_error = ('E0001', '')
    service_name = ('E0002', "A service name can't contain `.`")
    arguments_noservice = ('E0003',
                           'You have defined an argument, but not a service')
    return_outside = ('E0004', '`return` is allowed only inside functions')
    variables_backslash = ('E0005', "A variable name can't contain `/`")
    variables_dash = ('E0006', "A variable name can't contain `-`")
    incomplete_assignment = ('E0007', 'Missing value after `=`')
    misspelt_function = ('E0008', 'You have misspelt `function`')
