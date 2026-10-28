"""Keep public guides checked without admitting arbitrary source paths."""
from pathlib import Path
import tempfile
import unittest
from update_completion_status import validate_maintained_documents


class MaintainedDocumentTests(unittest.TestCase):
    def test_root_and_github_guides_are_registered(self):
        paths = ['docs/guide.md', 'CONTRIBUTING.md', 'CITATION.md',
                 '.github/pull_request_template.md', '.github/ISSUE_TEMPLATE/01-correction.md']
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for path in paths:
                (root/path).parent.mkdir(parents=True, exist_ok=True)
                (root/path).write_text('# Guide\n', encoding='utf-8')
            self.assertEqual(validate_maintained_documents(root, paths), set(paths))

    def test_sources_workflows_and_path_traversal_are_not_maintenance_guides(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for path in ['papers/original.md', '.github/workflows/check.md',
                         'docs/../original.md', '.github/ISSUE_TEMPLATE/../secret.md',
                         '/docs/guide.md', 'C:/docs/guide.md']:
                with self.subTest(path=path), self.assertRaises(AssertionError):
                    validate_maintained_documents(root, [path])

    def test_missing_and_duplicate_guides_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaisesRegex(AssertionError, 'Missing maintained document'):
                validate_maintained_documents(root, ['CITATION.md'])
            (root/'CITATION.md').write_text('# Cite\n', encoding='utf-8')
            with self.assertRaisesRegex(AssertionError, 'Duplicate maintained document'):
                validate_maintained_documents(root, ['CITATION.md', 'CITATION.md'])


if __name__ == '__main__':
    unittest.main()
