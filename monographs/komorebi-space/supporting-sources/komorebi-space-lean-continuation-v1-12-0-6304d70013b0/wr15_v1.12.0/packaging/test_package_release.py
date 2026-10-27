#!/usr/bin/env python3
"""Bounded adverse-input checks for the release builder; never builds a release."""
import hashlib
import importlib.util
from pathlib import Path
import stat
import tempfile
import unittest
import warnings
import zipfile

SCRIPT = Path(__file__).with_name('package_release.py')
spec = importlib.util.spec_from_file_location('package_release', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class PackageChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def make_zip(self, members, name='fixture.zip'):
        path = self.root / name
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            with zipfile.ZipFile(path, 'x') as z:
                for key, value in members:
                    z.writestr(key, value)
        return path

    def test_complete_valid_manifest(self):
        body = b'preserved predecessor payload\n'
        manifest = f'{hashlib.sha256(body).hexdigest()}  proof.txt\n'.encode()
        path = self.make_zip([('Release/proof.txt', body), ('Release/SHA256SUMS.txt', manifest)])
        result, found = module.zip_tree(path, 'Release')
        self.assertEqual(found, manifest)
        self.assertEqual(len(result), 2)

    def test_traversal_and_noncanonical_paths(self):
        for path in ('../escape', '/absolute', 'a//b', 'a/./b', 'a/../b', 'C:drive', 'a\\b', 'a\x00b'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                module.safe_relative(path)

    def test_duplicate_zip_member(self):
        p = self.make_zip([('Release/a', b'a'), ('Release/a', b'a')])
        with self.assertRaisesRegex(ValueError, 'Duplicate ZIP'):
            module.zip_tree(p, 'Release')

    def test_zip_symlink(self):
        symlink = zipfile.ZipInfo('Release/a')
        symlink.create_system = 3
        symlink.external_attr = (stat.S_IFLNK | 0o777) << 16
        p = self.make_zip([(symlink, b'outside')])
        with self.assertRaisesRegex(ValueError, 'ZIP symlink'):
            module.zip_tree(p, 'Release')

    def test_file_directory_collision(self):
        p = self.make_zip([('Release/a', b'file'), ('Release/a/', b'')])
        with self.assertRaisesRegex(ValueError, 'collision'):
            module.zip_tree(p, 'Release')

    def test_file_ancestor_collision(self):
        p = self.make_zip([('Release/a', b'file'), ('Release/a/b', b'child')])
        with self.assertRaisesRegex(ValueError, 'collision'):
            module.zip_tree(p, 'Release')

    def test_unmanifested_payload(self):
        m = f'{hashlib.sha256(b"a").hexdigest()}  a\n'.encode()
        p = self.make_zip([('Release/a', b'a'), ('Release/b', b'b'), ('Release/SHA256SUMS.txt', m)])
        with self.assertRaisesRegex(ValueError, 'enumerate and match'):
            module.zip_tree(p, 'Release')

    def test_payload_digest_mismatch(self):
        m = f'{hashlib.sha256(b"original").hexdigest()}  a\n'.encode()
        p = self.make_zip([('Release/a', b'changed'), ('Release/SHA256SUMS.txt', m)])
        with self.assertRaisesRegex(ValueError, 'enumerate and match'):
            module.zip_tree(p, 'Release')

    def test_duplicate_manifest_path(self):
        line = '0' * 64 + '  proof.lean\n'
        with self.assertRaisesRegex(ValueError, 'Duplicate checksum'):
            module.parse_manifest((line + line).encode())

    def test_symlink_argument_ancestor(self):
        target = self.root / 'target'
        target.mkdir()
        (self.root / 'alias').symlink_to(target, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'symlink path component'):
            module.ordinary_path(self.root / 'alias' / 'missing-child')

    def test_copy_refuses_overwrite(self):
        src = self.root / 'source'; src.mkdir()
        (src / 'proof.lean').write_text('theorem t : True := True.intro\n')
        dst = self.root / 'destination'; dst.mkdir()
        (dst / 'sentinel').write_bytes(b'keep')
        with self.assertRaisesRegex(ValueError, 'overwrite'):
            module.copy_checked(src, dst, module.tree(src))
        self.assertEqual((dst / 'sentinel').read_bytes(), b'keep')

    def test_filtered_evidence_keeps_attempts_but_omits_runtime_objects(self):
        for name in ('attempt_001/source.lean', 'attempt_001/compile.log', 'reviews/final.md',
                     'recovery/runtime_recovery.json', 'build/module.olean', 'runtime/lean',
                     '__pycache__/module.pyc', 'attempt_001/object.olean.private'):
            p = self.root / name; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(name)
        self.assertEqual(set(module.tree(self.root, filtered=True)),
                         {'attempt_001/source.lean','attempt_001/compile.log','reviews/final.md',
                          'recovery/runtime_recovery.json'})

if __name__ == '__main__':
    unittest.main(verbosity=2)
