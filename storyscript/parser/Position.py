class Position:
    """
    A position object consists of a `line`, (start) `column` and `end_column`.
    """

    def __init__(self, line, column, end_column):
        self.line = line
        self.column = column
        self.end_column = end_column

    def __str__(self):
        return (
            f"Pos(line:{self.line}, start:{self.column}, "
            f"end:{self.end_column})"
        )
