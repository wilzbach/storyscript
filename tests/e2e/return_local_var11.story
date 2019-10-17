function foo returns int
    a = 1
    try
        b = 2
        try
            c = 3
            return c + b + a
        catch
            d = 4
            return d + b + a
        finally
            e = 5
            return e + b + a
    return a
