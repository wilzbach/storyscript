from storyscript.tree import Program


def test_program_init(mocker):
    parser = mocker.MagicMock()
    program = Program(parser, 'story')
    assert program.parser == parser
    assert program.parser.program == program
    assert program.story == 'story'
