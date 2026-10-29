"""Check that browser presets retain the published program and expected output."""
import contextlib
import io
from pathlib import Path
import re
import unittest

from browser_python import EXAMPLES, teaching_source

ROOT = Path(__file__).resolve().parents[1]


class BrowserPythonTests(unittest.TestCase):
    def test_teaching_presets_match_documented_output(self):
        original = (ROOT/'examples/komorebi_demonstrations.py').read_text(encoding='utf-8')
        for name, (_, doc, _) in EXAMPLES.items():
            if doc is None:
                continue
            with self.subTest(example=name):
                source = teaching_source(original, name)
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    exec(compile(source, name+'.py', 'exec'), {'__name__': '__main__'})
                document = (ROOT/('docs/demonstrations/'+doc+'.md')).read_text(encoding='utf-8')
                expected = re.search(r'<!-- expected-output -->\s*```text\n(.*?)\n```', document, re.S)[1]+'\n'
                self.assertEqual(output.getvalue(), expected)

    def test_preset_assertions_remain_active(self):
        original = (ROOT/'examples/komorebi_demonstrations.py').read_text(encoding='utf-8')
        broken = teaching_source(original, 'packets').replace('x = (2, 3)', 'x = (0, 0)')
        with self.assertRaisesRegex(AssertionError, 'Unexpected reconstructed result'):
            exec(compile(broken, 'packets.py', 'exec', optimize=2), {})


if __name__ == '__main__':
    unittest.main()
