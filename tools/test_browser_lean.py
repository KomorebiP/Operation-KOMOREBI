from pathlib import Path
import posixpath
import tempfile
from types import SimpleNamespace
import unittest

from browser_lean import PAGE, TARGET, build, verify
from home_page import home_page


class BrowserLeanRoutes(unittest.TestCase):
    def fixture(self, output):
        def write(path, text):
            dest = output / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(text, encoding='utf8')
        def page(path, title, body):
            write(path, '<html><head><link rel="canonical" href="https://example.test/' + path + '"></head>'
                '<body><main>' + body + '</main><footer><a href="https://github.com/example/project">GitHub</a></footer></body></html>')
        site = SimpleNamespace(root=Path(__file__).resolve().parents[1], revision='a' * 40,
            write=write, page=page,
            rel=lambda target, page: posixpath.relpath(target, posixpath.dirname(page)))
        return SimpleNamespace(site=site)

    def test_homepage_opens_general_local_workspace(self):
        markup = home_page()
        self.assertIn('href="' + TARGET + '"', markup)
        self.assertNotIn('lean/playground.html', markup)
        self.assertNotIn('Paper XII', markup)

    def test_old_bookmark_has_only_local_workspace_routes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build(self.fixture(root))
            self.assertEqual(verify(root, {})['target'], TARGET)
            markup = (root / PAGE).read_text(encoding='utf8')
            self.assertIn('<noscript>', markup)
            self.assertNotIn('Paper XII', markup)
            self.assertNotIn('live.lean-lang.org', markup)

    def test_external_editor_cannot_reappear_in_alias_page(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build(self.fixture(root))
            original = (root / PAGE).read_text(encoding='utf8')
            for injected in ('<iframe src="https://live.lean-lang.org/"></iframe>',
                             '<a href="https://live.lean-lang.org/">Editor</a>'):
                (root / PAGE).write_text(original.replace('</main>', injected + '</main>'), encoding='utf8')
                with self.assertRaises(AssertionError):
                    verify(root, {})


if __name__ == '__main__':
    unittest.main()
