# -*- coding: utf-8 -*-


class ErrorCodes:

    unidentified_error = ('E0001', '')
    service_name = ('E0002', "A service name can't contain `.`")
    arguments_noservice = ('E0003',
                           'You have defined an argument, but not a service')
    return_outside = ('E0004', '`return` is allowed only inside functions')
    variables_backslash = ('E0005', "A variable name can't contain `/`")
    variables_dash = ('E0006', "A variable name can't contain `-`")
    assignment_incomplete = ('E0007', 'Missing value after `=`')
    function_misspell = ('E0008', 'You have misspelt `function`')
    import_misspell = ('E0009', 'You have misspelt `import`')
    import_misspell_as = ('E0010',
                          'You have misspelt `as` in an import statement')
    import_unquoted_file = ('E0011', 'The imported filename must be in quotes')
    string_opening_quote = ('E0012', 'Missing opening quote for string')
    string_closing_quote = ('E0013', 'Missing closing quote for string')
    list_trailing_comma = ('E0014', 'Trailing comma in list')
    list_opening_bracket = ('E0015', 'Missing opening bracket for list')
    list_closing_bracket = ('E0016', 'Missing closing bracket for list')
    object_opening_bracket = ('E0017', 'Missing opening bracket for object')
    object_closing_bracket = ('E0018', 'Missing closing bracket for object')
    service_argument_colon = ('E0019', 'Missing colon in service argument')
    reserved_keyword = ('E0020', '`{keyword}` is a reserved keyword')
    future_reserved_keyword = ('E0030',
                               '`{keyword}` is reserved for future use')
    arguments_nomutation = (
        'E0039',
        'You have defined a chained mutation, but not a mutation')
    compiler_error_no_operator = (
        'E0040', 'Invalid operator `{operator}` provided.')
    invalid_character = ('E0041', '`{character}` is not allowed here')
    function_already_declared = (
        'E0042',
        '`{function_name}` has already been declared at line {line}')
    unexpected_token = ('E0043',
                        '`{token}` is not allowed here. Allowed: {allowed}')
    break_outside = ('E0044', '`break` is allowed only inside loops')
    unnecessary_colon = (
        'E0045',
        'There is an unnecessary colon at the end of the line')
    block_expected_after = ('E0045',
                            'An indented block is required to follow here')
    block_expected_before = ('E0046',
                             'An indented block is required to be before here')
    file_not_found = ('E0047',
                      'File `{path}` not found at `{abspath}`')
    function_call_no_function = ('E0048',
                                 'Function {name} has not been defined yet')
    function_call_invalid_path = ('E0049',
                                  'Function {name} is not a valid path')
    function_call_no_inline_expression = (
        'E0050', 'Service output can not be called as a function')
    when_no_output_parent = (
        'E0051', 'No service parent has been found.')
    service_without_command = (
        'E0052', 'Service calls require a command.')
    unexpected_end_of_line = (
        'E0053', 'Unexpected end of line. Expected: {allowed}.')
    arguments_expected = (
        'E0054', 'Arguments need to be declared with `key:value`')
    first_option_more_stories = (
        'E0055',
        'The option `--first`/-`f` can only be used if one story is complied.')
    expected_end_of_line = (
        'E0056', 'Expected end of line instead of `{token}`.')
    string_templates_no_assignment = (
        'E0057', 'Only expressions are allowed inside string templates')
    path_name_internal = (
        'E0058', 'Path names can\'t start with double underscore')
    string_templates_nested = (
        'E0059', 'String templates can\'t be nested')
    string_templates_empty = (
        'E0060', 'String templates can\'t be empty')
    path_name_invalid_char = (
        'E0061', 'Invalid path name: `{path}`. '
        'Path names can\'t contain `{token}`')
    return_required = ('E0062', 'All paths of a function need to return')
    assignment_inline_expression = (
        'E0063', 'Can\'t assign to inline expressions.')
    foreach_output_required = (
        'E0064', 'Foreach blocks require an output (e.g. `as item`)')
    nested_service_block = ('E0065', 'Nested service blocks are not allowed')
    nested_when_block = ('E0066', 'Nested when blocks are not allowed')
    time_value_inconsistent_week = (
        'E0067', 'Time value inconsistent: `w` must be the first time unit')
    time_value_inconsistent = (
        'E0068',
        'Time value inconsistent: `{current}` must to be before `{prior}`')
    type_assignment_different = (
        'E0100', 'Can\'t assign `{source}` to `{target}`')
    var_not_defined = (
        'E0101', 'Variable `{name}` has not been defined.')
    return_type_differs = (
        'E0102',
        '`{source}` can\'t be implicitly converted to expected '
        'return type `{target}`.')
    type_operation_incompatible = (
        'E0103',
        '`{left}` is not compatible with `{right}`'
    )
    type_index_incompatible = (
        'E0104',
        '`{left}` can\'t be indexed with `{right}`'
    )
    foreach_output_children = (
        'E0105',
        '`foreach` can only have one or two outputs'
    )
    foreach_iterable_required = (
        'E0106',
        '`foreach` requires an iterable type, but `{target}` is not'
    )
    output_type_only_one = (
        'E0107',
        'Only one output is allowed for `{target}` blocks.'
    )
    output_unique = (
        'E0108', 'Service output `{name}` must be unique. Use `as outputName`')
    service_no_inline_output = (
        'E0109', 'Inline service calls can\'t define an output')

    @staticmethod
    def is_error(error_name):
        """
        Checks whether a given error name is a valid error.
        """
        if isinstance(error_name, str):
            if hasattr(ErrorCodes, error_name):
                return True

    @staticmethod
    def get_error(error_name):
        """
        Retrieve the error object for a valid error name.
        """
        return getattr(ErrorCodes, error_name)
