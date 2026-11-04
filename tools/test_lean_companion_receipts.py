"""Guard the site's recorded formal coverage against stale or altered evidence."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from check_lean_companions import PROJECTS, RECORD, check_project

ROOT = Path(__file__).resolve().parents[1]


class LeanCompanionReceiptTests(unittest.TestCase):
    def test_published_companions_match_their_checked_bytes(self):
        for project in PROJECTS:
            with self.subTest(project=project):
                self.assertEqual(check_project(ROOT, project)["status"], "PASS")

    def copy_fixture(self, directory):
        root = Path(directory)
        relative = PROJECTS[0]
        shutil.copytree(ROOT / relative, root / relative,
                        ignore=shutil.ignore_patterns('.lake', '__pycache__'))
        (root / 'tools').mkdir()
        shutil.copy2(ROOT / 'tools/verify_lean_companion.py', root / 'tools/verify_lean_companion.py')
        return root, relative

    def test_changed_proof_is_not_covered_by_an_earlier_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            root, relative = self.copy_fixture(directory)
            path = root / relative / 'KomorebiReader/FactorialLanes.lean'
            path.write_text(path.read_text() + '\n-- A changed source needs a new receipt.\n')
            with self.assertRaisesRegex(ValueError, 'Source changed'):
                check_project(root, relative)

    def test_changed_compiler_log_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root, relative = self.copy_fixture(directory)
            path = root / relative / RECORD
            record = json.loads(path.read_text())
            log = path.parent / record['checks'][0]['log']
            log.write_text('Altered compiler evidence\n')
            with self.assertRaisesRegex(ValueError, 'Compiler evidence changed'):
                check_project(root, relative)


if __name__ == '__main__':
    unittest.main()
