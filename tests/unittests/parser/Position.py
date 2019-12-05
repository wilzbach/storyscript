from storyscript.parser import Position


def test_position_str():
    assert str(Position(1, 2, 3)) == "Pos(line:1, start:2, end:3)"
