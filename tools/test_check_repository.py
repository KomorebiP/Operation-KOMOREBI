"""Exercise incomplete checkouts and child-check failure reporting."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import check_repository


class RepositoryCheckTests(unittest.TestCase):
    def fixture(self, root, child=None):
        for path in ('README.md', 'CONTRIBUTIONS.md', 'CONTRIBUTING.md', 'CITATION.md',
                     'docs/START_HERE.md', 'docs/WORKFLOWS.md', 'papers/README.md',
                     'formal/README.md', 'experiments/README.md', 'packages/README.md',
                     'formal/research-preview-1/REPRODUCE.md'):
            target = root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text('# Fixture\n', encoding='utf-8')
        (root / 'manifests').mkdir()
        (root / 'manifests/contributions.json').write_text(
            json.dumps({'contributions': [{'id': 'fixture', 'disposition': 'imported',
                                          'local_path': 'formal/research-preview-1'}]}), encoding='utf-8')
        if child is not None:
            target = root / 'formal/research-preview-1/tools/check_release.py'
            target.parent.mkdir(parents=True)
            target.write_text(child, encoding='utf-8')

    def test_successful_child_and_cli_report_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture(root, 'print(\'{"status": "PASS", "sealed_files_checked": 7}\')\n')
            stream = io.StringIO()
            with patch.object(check_repository, 'ROOT', root), contextlib.redirect_stdout(stream):
                self.assertEqual(check_repository.main(), 0)
            result = json.loads(stream.getvalue())
            self.assertEqual(result['status'], 'PASS')
            self.assertEqual(result['preview']['sealed_files_checked'], 7)
            self.assertEqual(result['preview_exit_status'], 0)

    def test_absent_checkout_reports_failure_without_running_child(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(check_repository.subprocess, 'run') as run:
                result = check_repository.check(Path(tmp))
            run.assert_not_called()
            self.assertEqual(result['status'], 'FAIL')
            self.assertEqual(result['preview']['status'], 'NOT_RUN')
            self.assertIn('complete checkout', result['preview']['reason'])
            self.assertIsNone(result['preview_exit_status'])

    def test_missing_checker_in_existing_directory_reports_nonzero_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture(root)
            stream = io.StringIO()
            with patch.object(check_repository, 'ROOT', root), contextlib.redirect_stdout(stream):
                self.assertEqual(check_repository.main(), 1)
            self.assertEqual(json.loads(stream.getvalue())['preview']['status'], 'NOT_RUN')

    def test_child_start_failure_remains_structured(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture(root, '')
            with patch.object(check_repository.subprocess, 'run', side_effect=OSError('fixture launch failure')):
                result = check_repository.check(root)
            self.assertEqual(result['status'], 'FAIL')
            self.assertIn('fixture launch failure', result['preview']['reason'])

    def test_child_must_return_both_success_status_and_zero_exit(self):
        cases = [('not json', 0), ('[]', 0), ('null', 0), ('{}', 0),
                 ('{"status":"FAIL"}', 0), ('{"status":"PASS"}', 3)]
        for stdout, exit_status in cases:
            with self.subTest(stdout=stdout, exit_status=exit_status), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.fixture(root, 'import sys\nprint('+repr(stdout)+')\n'
                             'print("fixture diagnostic", file=sys.stderr)\n'
                             'raise SystemExit('+str(exit_status)+')\n')
                result = check_repository.check(root)
                self.assertEqual(result['status'], 'FAIL')
                self.assertEqual(result['preview_exit_status'], exit_status)
                self.assertIn('fixture diagnostic', result['preview_stderr'])

    def test_malformed_contribution_records_do_not_crash(self):
        for ledger in ([], {'contributions': [None]}, {'contributions': [{'id': []}]},
                       {'contributions': [{'id': 'a', 'disposition': 'imported', 'local_path': 12}]}):
            with self.subTest(ledger=ledger), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.fixture(root, 'print(\'{"status":"PASS"}\')\n')
                (root / 'manifests/contributions.json').write_text(json.dumps(ledger), encoding='utf-8')
                result = check_repository.check(root)
                self.assertEqual(result['status'], 'FAIL')
                self.assertTrue(result['errors'])


if __name__ == '__main__':
    unittest.main()
