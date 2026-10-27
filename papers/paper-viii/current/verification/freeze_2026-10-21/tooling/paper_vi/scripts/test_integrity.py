#!/usr/bin/env python3
"""Exercise the release verifier on isolated intact and damaged packages."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
VERIFIER = Path(__file__).with_name('verify_integrity.py')
spec = importlib.util.spec_from_file_location('paper_vi_verify_integrity', VERIFIER)
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


class IntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='paper-vi-integrity-control-')
        self.root = Path(self.temp.name) / 'package'
        (self.root / 'scripts').mkdir(parents=True)
        shutil.copyfile(VERIFIER, self.root / 'scripts' / 'verify_integrity.py')
        (self.root / 'payload.txt').write_bytes(b'exact payload\n')
        self.manifest = {'schema': verifier.SCHEMA, 'checkpoint': 'test', 'files': [
            {'path': p.relative_to(self.root).as_posix(), 'bytes': p.stat().st_size,
             'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
            for p in sorted(self.root.rglob('*')) if p.is_file()]}
        self.save()

    def tearDown(self):
        self.temp.cleanup()

    def save(self):
        (self.root / verifier.MANIFEST).write_text(json.dumps(self.manifest), encoding='utf-8')

    def check(self, passed=False):
        report = verifier.verify_tree(self.root)
        self.assertEqual(report['status'], 'PASS' if passed else 'FAIL', report)
        if not passed:
            self.assertTrue(report['failures'])
        return report

    def cli(self, *arguments):
        return subprocess.run([sys.executable, '-B', str(self.root / 'scripts' / 'verify_integrity.py'), *arguments], capture_output=True, text=True)

    def symlink(self, path, target, directory=False):
        try:
            path.symlink_to(target, target_is_directory=directory)
        except (OSError, NotImplementedError) as error:
            self.skipTest('This platform cannot create the symlink fixture: ' + str(error))

    def test_intact_and_explicit_strict(self):
        self.assertEqual(self.check(True)['files_checked'], 2)
        run = self.cli('--strict')
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(json.loads(run.stdout)['status'], 'PASS')

    def test_changed_same_size_payload(self):
        (self.root / 'payload.txt').write_bytes(b'wrong payload\n')
        self.check()

    def test_missing_payload(self):
        (self.root / 'payload.txt').unlink()
        self.check()

    def test_unlisted_payload(self):
        (self.root / 'extra.lean').write_text('axiom hidden : False\n')
        self.check()

    def test_empty_manifest(self):
        self.manifest['files'] = []
        self.save()
        self.check()

    def test_missing_manifest(self):
        (self.root / verifier.MANIFEST).unlink()
        self.check()

    def test_malformed_json_and_duplicate_keys(self):
        for text in ['{', '{"schema":"komorebi.strict_manifest.v1","files":[],"files":[]}', '{"files":NaN}', '[]']:
            with self.subTest(text=text):
                (self.root / verifier.MANIFEST).write_text(text)
                self.check()

    def test_invalid_schema_and_unknown_field(self):
        for change in [{'schema': 'unknown'}, {'files': {}}, {'files': None}, {'unexpected': True}, {'scope': 3}]:
            with self.subTest(change=change):
                original = dict(self.manifest)
                self.manifest.update(change)
                self.save()
                self.check()
                self.manifest = original

    def test_duplicate_rows(self):
        self.manifest['files'].append(dict(self.manifest['files'][0]))
        self.save()
        self.check()

    def test_unsafe_and_noncanonical_paths(self):
        row = self.manifest['files'][0]
        for path in ['/etc/passwd', '../outside', './payload.txt', 'a/../payload.txt', 'a//b', 'a/', 'C:/payload', 'a\\b', '', '.', 'a\x00b']:
            with self.subTest(path=path):
                row['path'] = path
                self.save()
                self.check()

    def test_self_manifest_row(self):
        self.manifest['files'][0]['path'] = verifier.MANIFEST
        self.save()
        self.check()

    def test_invalid_row_structure(self):
        for row in [None, 'payload.txt', {'path': 'payload.txt'}, {'path':'payload.txt','bytes':14,'sha256':'0'*64,'extra':1}]:
            with self.subTest(row=row):
                self.manifest['files'][0] = row
                self.save()
                self.check()

    def test_wrong_boolean_and_negative_sizes(self):
        for size in [0, True, -1, 14.0, '14']:
            with self.subTest(size=size):
                self.manifest['files'][0]['bytes'] = size
                self.save()
                self.check()

    def test_invalid_digests(self):
        for value in ['0'*63, 'G'*64, 'A'*64, None, 123]:
            with self.subTest(value=value):
                self.manifest['files'][0]['sha256'] = value
                self.save()
                self.check()

    def test_symlink_file(self):
        path = self.root / 'payload.txt'
        path.unlink()
        self.symlink(path, self.root / 'scripts' / 'verify_integrity.py')
        self.check()

    def test_unlisted_symlink_directory(self):
        self.symlink(self.root / 'hidden-link', self.root / 'scripts', directory=True)
        self.check()

    def test_symlink_manifest(self):
        path = self.root / verifier.MANIFEST
        outside = Path(self.temp.name) / 'manifest.json'
        path.rename(outside)
        self.symlink(path, outside)
        self.check()

    @unittest.skipUnless(hasattr(os, 'mkfifo'), 'FIFO control requires a POSIX filesystem')
    def test_special_file(self):
        os.mkfifo(self.root / 'unexpected.fifo')
        self.check()

    def test_unknown_flag_fails(self):
        run = self.cli('--strcit')
        self.assertEqual(run.returncode, 2)
        self.assertNotIn('PASS', run.stdout)

    def test_internal_report_fails_without_mutation(self):
        destination = self.root / 'new-report.json'
        run = self.cli('--report', str(destination))
        self.assertEqual(run.returncode, 2)
        self.assertFalse(destination.exists())
        self.check(True)

    def test_external_report(self):
        destination = Path(self.temp.name) / 'report.json'
        run = self.cli('--report', str(destination))
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(json.loads(destination.read_text())['status'], 'PASS')
        self.check(True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path, help='Save the bounded result outside the release tree.')
    args = parser.parse_args()
    if args.evidence and args.evidence.expanduser().resolve().is_relative_to(VERIFIER.parent.parent.resolve()):
        parser.error('--evidence must be outside the release tree')
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(IntegrityTests))
    transcript = stream.getvalue()
    print(transcript, end='')
    record = {'status': 'PASS' if result.wasSuccessful() else 'FAIL',
              'scope': 'Bounded integrity-verifier controls on isolated fixture packages; no mathematical proofs or Lean compilation.',
              'test_methods': result.testsRun, 'failures': len(result.failures),
              'errors': len(result.errors), 'skips': len(result.skipped),
              'source_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in [VERIFIER, Path(__file__)]},
              'transcript': transcript}
    if args.evidence:
        args.evidence.parent.mkdir(parents=True, exist_ok=True)
        args.evidence.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())
