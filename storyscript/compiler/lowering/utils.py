def unicode_escape(tree, text):
    """
    Evaluates unicode escape codes like \n or \x12
    """
    try:
        return bytes(text, 'utf-8').decode('unicode_escape')
    except UnicodeError as e:
        tree.expect(0, 'unicode_decode_error', reason=e.reason)
