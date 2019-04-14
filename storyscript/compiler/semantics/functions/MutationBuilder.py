from storyscript.compiler.semantics.functions.Mutation import Mutation
from storyscript.compiler.semantics.types.GenericTypes import \
    GenericType, ListGenericType, MapGenericType, TypeSymbol
from storyscript.compiler.semantics.types.Types import AnyType, BaseType, \
    BooleanType, FloatType, IntType, NoneType, StringType, TimeType


def parse_type_inner(text, start_tok='[', end_tok=']'):
    """
    Returns the inner type of a generic type.
    Example: List[any] => any
    :param text: type text to parse
    :param start_tok: type opening token
    :param end_tok: type end token
    :return: Inner type
    """
    level = 0
    start = None
    for i, c in enumerate(text):
        if c == start_tok:
            if level == 0:
                start = i + 1
            level = level + 1
        elif c == end_tok:
            assert level > 0, 'No start ['
            level = level - 1
            if level == 0:
                return text[start:i]
    assert 0, 'No ] found'


def parse_type(type_):
    """
    Parses a type string and returns its parsed type which can be a:
        - BaseType (e.g. `IntType`)
        - TypeSymbol (e.g. `TypeSymbol(A)`)
        - GenericType (e.g. `ListGenericType(TypeSymbol(A))`)
    """
    assert len(type_) > 0
    type_ = type_.strip()
    if type_ == 'boolean':
        return BooleanType.instance()
    if type_ == 'int':
        return IntType.instance()
    if type_ == 'float':
        return FloatType.instance()
    if type_ == 'string':
        return StringType.instance()
    if type_ == 'time':
        return TimeType.instance()
    if type_ == 'none':
        return NoneType.instance()
    if type_ == 'any':
        return AnyType.instance()

    if '[' in type_:
        types = []
        for t in parse_type_inner(type_).split(','):
            t2 = parse_type(t)
            types.append(t2)
        if type_.startswith('List['):
            return ListGenericType(types)
        else:
            assert type_.startswith('Map[')
            return MapGenericType(types)

    assert ']' not in type_
    return TypeSymbol(type_)


def split_type_arguments(text, start_tok='[', end_tok=']'):
    """
    Splits a mutation type string into its arguments.
    :return: Array of all arguments.
    """
    level = 0
    start = 0
    in_argument = False
    for i, c in enumerate(text):
        if c == start_tok:
            level = level + 1
        elif c == end_tok:
            assert level > 0, 'No start ['
            level = level - 1
        elif c == ':':
            # ignore whitespace after an argument starts
            in_argument = True
        elif c == ' ':
            if level == 0 and not in_argument:
                if start == i:
                    # skip over multiple whitespaces
                    start = i + 1
                else:
                    yield text[start:i]
                    start = i + 1
        else:
            in_argument = False
    assert level == 0
    t = text[start:]
    yield t


def get_symbols(t):
    """
    Returns the symbols of a type instance or an empty list.
    """
    if isinstance(t, GenericType):
        ts = []
        for s in t.symbols:
            if isinstance(s, TypeSymbol):
                ts.append(s)
            elif isinstance(s, GenericType):
                ts.append(*s.symbols)
            else:
                # no resolving required for base types
                assert isinstance(s, BaseType)
        return ts
    else:
        return []


def check_type_symbols(t, symbols):
    """
    Ensures that the given type only uses a set of known symbols.
    """
    t_symbols = get_symbols(t)
    for s in t_symbols:
        if not isinstance(s, BaseType):
            assert s in symbols, f'unknown symbol {s} used'


def mutation_builder(type_text):
    """
    Build a mutation from a plain mutation header typing.
    Example:
        Map[A,B] contains: A -> B
    :return: the parsed Mutation
    """
    in_types, out_types = [l.strip() for l in type_text.split('->')]
    args = [*split_type_arguments(in_types)]
    assert len(args) >= 2, f'input type and name required for {in_types}'
    main_type, name, *args = args
    # in:
    in_type = parse_type(main_type)
    symbols = get_symbols(in_type)
    # arguments:
    arguments = {}
    for arg in args:
        arg_name, arg_type = [a.strip() for a in arg.split(':')]
        t = parse_type(arg_type)
        # check that only symbols from the in_type are found
        check_type_symbols(t, symbols)
        arguments[arg_name] = t
    # out:
    out_type = parse_type(out_types)
    # check that only symbols from the in_type are found
    check_type_symbols(out_type, symbols)
    return Mutation(ti=in_type, name=name, args=arguments, output=out_type)
