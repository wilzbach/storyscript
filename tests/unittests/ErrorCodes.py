# -*- coding: utf-8 -*-
from storyscript.ErrorCodes import ErrorCodes


def test_errorcodes():
    codes = ErrorCodes
    assert codes.unidentified_error == ('E0001', '')
    assert codes.service_name == ('E0002', "A service name can't contain `.`")

    error_3 = ('E0003', 'You have defined an argument, but not a service')
    assert codes.arguments_noservice == error_3

    error_4 = ('E0004', '`return` is allowed only inside functions')
    assert codes.return_outside == error_4

    error_5 = ('E0005', "A variable name can't contain `/`")
    assert codes.variables_backslash == error_5

    error_6 = ('E0006', "A variable name can't contain `-`")
    assert codes.variables_dash == error_6

    assert codes.incomplete_assignment == ('E0007', 'Missing value after `=`')
    assert codes.misspelt_function == ('E0008', 'You have misspelt `function`')
