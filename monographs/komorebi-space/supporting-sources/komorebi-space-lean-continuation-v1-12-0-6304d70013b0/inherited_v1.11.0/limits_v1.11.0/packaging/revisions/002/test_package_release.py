#!/usr/bin/env python3
"""Focused adverse-input checks for preservation and archive path safety."""
from pathlib import Path
import hashlib
import importlib.util
import stat
import sys
import tempfile
import unittest
import warnings
import zipfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('package_release', HERE / 'package_release.py')
pkg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pkg)


class PackageChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='test-fixture-', dir=HERE)
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def archive(self, entries):
        p = self.root / 'case.zip'
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            with zipfile.ZipFile(p, 'x') as z:
                for name, content in entries:
                    z.writestr(name, content)
        return p

    def test_good_archive_is_complete_and_hash_bound(self):
        content = b'proof source\n'
        digest = hashlib.sha256(content).hexdigest()
        manifest = f'{digest}  formal/Main.lean\n'.encode()
        p = self.archive([('release/formal/Main.lean', content), ('release/SHA256SUMS.txt', manifest)])
        data, actual_manifest = pkg.zip_tree(p, 'release')
        self.assertEqual(actual_manifest, manifest)
        self.assertEqual(data['formal/Main.lean'], digest)
        self.assertEqual(len(data), 2)

    def test_relative_path_rejects_traversal_and_aliases(self):
        for name in ('../secret', '/absolute', 'a/../b', 'a//b', './a', 'a\\b', 'a\nb', 'C:/drive'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                pkg.safe_relative(name)

    def test_zip_rejects_traversal(self):
        p = self.archive([('release/../escape', b'x')])
        with self.assertRaisesRegex(ValueError, 'Unsafe relative path'):
            pkg.zip_tree(p, 'release')

    def test_zip_rejects_symlink(self):
        item = zipfile.ZipInfo('release/link')
        item.create_system = 3
        item.external_attr = (stat.S_IFLNK | 0o777) << 16
        p = self.archive([(item, b'target')])
        with self.assertRaisesRegex(ValueError, 'ZIP symlink'):
            pkg.zip_tree(p, 'release')

    def test_zip_rejects_duplicate_members(self):
        p = self.archive([('release/a', b'one'), ('release/a', b'two')])
        with self.assertRaisesRegex(ValueError, 'Duplicate ZIP member'):
            pkg.zip_tree(p, 'release')

    def test_zip_rejects_extra_unmanifested_payload(self):
        digest = hashlib.sha256(b'a').hexdigest()
        p = self.archive([('release/a', b'a'), ('release/b', b'b'),
                          ('release/SHA256SUMS.txt', f'{digest}  a\n'.encode())])
        with self.assertRaisesRegex(ValueError, 'every payload file'):
            pkg.zip_tree(p, 'release')

    def test_zip_rejects_manifest_hash_mismatch(self):
        p = self.archive([('release/a', b'a'),
                          ('release/SHA256SUMS.txt', ('0' * 64 + '  a\n').encode())])
        with self.assertRaisesRegex(ValueError, 'every payload file'):
            pkg.zip_tree(p, 'release')

    def test_tree_rejects_included_symlink(self):
        source = self.root / 'source'
        source.mkdir()
        (source / 'target').write_text('source')
        (source / 'alias').symlink_to('target')
        with self.assertRaisesRegex(ValueError, 'nonregular'):
            pkg.tree(source, filtered=True)

    def test_tree_excludes_build_before_following_links(self):
        source = self.root / 'source'
        source.mkdir()
        (source / 'Main.lean').write_text('theorem test : True := True.intro\n')
        (source / 'Main.olean').write_text('compiled')
        (source / 'build').mkdir()
        (source / 'build/accepted').symlink_to('/does/not/exist')
        self.assertEqual(list(pkg.tree(source, filtered=True)), ['Main.lean'])

    def test_copy_preserves_bytes_and_refuses_overwrite(self):
        source = self.root / 'source'
        source.mkdir()
        (source / 'Main.lean').write_text('precise source\n')
        expected = pkg.tree(source)
        target = self.root / 'target'
        pkg.copy_checked(source, target, expected)
        self.assertEqual(pkg.tree(target), expected)
        with self.assertRaisesRegex(ValueError, 'overwrite'):
            pkg.copy_checked(source, target, expected)

    def test_copy_rejects_changed_input(self):
        source = self.root / 'source'
        source.mkdir()
        (source / 'Main.lean').write_text('original')
        expected = pkg.tree(source)
        (source / 'Main.lean').write_text('changed')
        with self.assertRaisesRegex(ValueError, 'Source changed before copy'):
            pkg.copy_checked(source, self.root / 'target', expected)

    def test_manifest_rejects_duplicate_paths(self):
        row = '0' * 64 + '  file\n'
        with self.assertRaisesRegex(ValueError, 'Duplicate checksum path'):
            pkg.parse_manifest((row + row).encode())


if __name__ == '__main__':
    unittest.main(verbosity=2)
