import json
import unittest

try:
    import subprocess32 as subprocess
except ImportError:
    import subprocess


class Tests(unittest.TestCase):
    def test_json_output(self):
        output = subprocess.check_output(
            'python -m storyscript.__init__ -f tests/test.story', shell=True
        )
        print(output)
        out = json.loads(output)
        self.assertIn('script', out)
        self.assertIn('version', out)

    def test_silent(self):
        output = subprocess.check_output(
            'python -m storyscript.__init__ -sf tests/test.story', shell=True
        )
        print(output)
        self.assertEquals("", output)

    def test_tokens(self):
        output = subprocess.check_output(
            'python -m storyscript.__init__ -slf tests/test.story', shell=True
        )
        print(output)
        o = output.split('\n')
        assert len(o) == 6
        assert "LexToken(PATH,'run',1,0)" in o[0]
        assert "LexToken(NEWLINE,'\\n',1,3)" in o[1]
        assert "LexToken(WS,'    ',2,4)" in o[2]
        assert "LexToken(PATH,'pass',2,8)" in o[3]
        assert "LexToken(NEWLINE,'\\n',2,12)" in o[4]

    def test_error(self):
        try:
            subprocess.check_output(
                'python -m storyscript.__init__ "begin\n\tred -- flba"', shell=True
            )
        except subprocess.CalledProcessError as e:
            self.assertEqual(
                e.output.strip(),
                (
                    '\x1b[91mSyntax Error:\x1b[0m '
                    '\x1b[96mLine:\x1b[0m 2, '
                    '\x1b[96mToken:\x1b[0m OPERATOR, '
                    '\x1b[96mValue:\x1b[0m -'
                )
            )
        except:
            raise Exception('CalledProcessError not raised')
