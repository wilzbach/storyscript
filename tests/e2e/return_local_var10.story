function foo returns int
    a = 1
    try
        b = 2
        return b + a
    catch
        c = 3
        return c + a
    finally
        d = 4
        return d + a
    return a
