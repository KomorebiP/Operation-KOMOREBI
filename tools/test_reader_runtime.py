import json
from pathlib import Path
import tempfile
import unittest

from fetch_reader_runtime import URL, INTEGRITY
from reader_runtime import publish_mathjax, ALTERNATIVE_BUNDLES


class ReaderRuntimeTests(unittest.TestCase):
    def fixture(self, root):
        contents = {name:('alternative '+name).encode() for name in ALTERNATIVE_BUNDLES}
        contents.update({name:('retained '+name).encode() for name in (
            'tex-svg-full.js', 'startup.js', 'core.js', 'loader.js',
            'a11y/assistive-mml.js', 'a11y/semantic-enrich.js', 'a11y/explorer.js',
            'ui/menu.js', 'sre/sre_browser.js', 'output/svg.js', 'output/chtml.js',
            'output/chtml/fonts/woff-v2/MathJax_Main.woff',
            'input/tex/extensions/physics.js', 'input/tex-svg.js', 'LICENSE', 'README.md',
        )})
        for name, raw in contents.items():
            path = root/name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)
        record = dict(url=URL, sha512_base64=INTEGRITY, files=len(contents))
        (root/'SOURCE.json').write_text(json.dumps(record), encoding='utf-8')
        contents['SOURCE.json'] = (root/'SOURCE.json').read_bytes()
        return contents

    def test_only_alternative_root_bundles_are_omitted(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); source = root/'source'; source.mkdir()
            files = self.fixture(source)
            result = publish_mathjax(source, root/'published')
            for name, raw in files.items():
                output = root/'published'/name
                if name in ALTERNATIVE_BUNDLES:
                    self.assertFalse(output.exists(), name)
                else:
                    self.assertEqual(output.read_bytes(), raw, name)
                self.assertEqual((source/name).read_bytes(), raw, name)
            self.assertEqual(result['omitted_bytes'], sum(len(files[n]) for n in ALTERNATIVE_BUNDLES))
            self.assertEqual(result['published_source_files'], len(files)-len(ALTERNATIVE_BUNDLES))
            self.assertEqual(json.loads((root/'published/PUBLISHED.json').read_bytes()), result)

    def test_missing_accessibility_module_fails_before_publication(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); source = root/'source'; source.mkdir(); self.fixture(source)
            (source/'a11y/semantic-enrich.js').unlink()
            with self.assertRaisesRegex(ValueError, 'complete pinned MathJax'):
                publish_mathjax(source, root/'published')
            self.assertFalse((root/'published').exists())

    def test_wrong_source_record_and_incomplete_source_are_rejected(self):
        for change in ('record', 'missing'):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as directory:
                root = Path(directory); source = root/'source'; source.mkdir(); self.fixture(source)
                if change == 'missing':
                    (source/'input/tex/extensions/physics.js').unlink()
                else:
                    record = json.loads((source/'SOURCE.json').read_bytes()); record['sha512_base64'] = 'wrong'
                    (source/'SOURCE.json').write_text(json.dumps(record), encoding='utf-8')
                with self.assertRaisesRegex(ValueError, 'source record differs'):
                    publish_mathjax(source, root/'published')
                self.assertFalse((root/'published').exists())


if __name__ == '__main__':
    unittest.main()
