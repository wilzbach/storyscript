function factorial n: int returns int
    if n == 1
        return 1
    else
        return n * factorial(n: n - 1)
