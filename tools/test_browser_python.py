"""Check that browser presets retain the published program and expected output."""
import contextlib
import io
from pathlib import Path
import re
import unittest
import importlib.util
import json

from browser_python import EXAMPLES, teaching_source

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('browser_helper', ROOT/'website/python/komorebi_browser.py')
HELPER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HELPER)


class BrowserPythonTests(unittest.TestCase):
    def setUp(self):
        HELPER._reset()
        self.messages = []
        HELPER._sink = self.messages.append

    def test_surface_payload_keeps_all_coordinates(self):
        HELPER.show_plot([dict(type='surface', x=[0, 1], y=[0, 2], z=[[0, 1], [-4, -3]])], description='Saddle samples')
        payload = json.loads(self.messages[0])
        self.assertEqual(payload['data'][0]['z'], [[0, 1], [-4, -3]])
        self.assertEqual(payload['description'], 'Saddle samples')

    def test_plot_rejects_mismatched_grids_and_nonfinite_values(self):
        with self.assertRaisesRegex(ValueError, 'grid dimensions'):
            HELPER.show_plot([dict(type='surface', x=[0], y=[0], z=[[1, 2]])], description='Invalid')
        with self.assertRaises(ValueError):
            HELPER.show_plot([dict(x=[0], y=[float('nan')])], description='Invalid')
        self.assertEqual(self.messages, [])

    def test_plot_limits_are_enforced_before_display(self):
        with self.assertRaisesRegex(ValueError, '50,000'):
            HELPER.show_plot([dict(y=[0]*50001)], description='Too large')
        self.assertEqual(self.messages, [])

    def test_exports_keep_text_and_reject_paths(self):
        HELPER.export_file('sample.csv', 'x,y\n1,2\n')
        self.assertEqual(json.loads(self.messages[0])['content'], 'x,y\n1,2\n')
        for name in ('../sample.csv', 'C:\\sample.csv', 'script.html'):
            with self.assertRaises(ValueError): HELPER.export_file(name, 'data')

    def test_new_presets_have_valid_python_and_supported_dependencies(self):
        from playground_presets import PRESETS
        for name, spec in PRESETS.items():
            with self.subTest(preset=name):
                compile(spec['code'], name+'.py', 'exec')
                self.assertTrue(set(spec['packages']) <= {'numpy', 'matplotlib', 'scipy', 'sympy'})
                self.assertTrue(spec['expected'].endswith('\n'))

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
