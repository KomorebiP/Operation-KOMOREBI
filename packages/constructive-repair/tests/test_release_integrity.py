"""Artifact binding regression tests. Synthetic receipts are fixtures, not proofs."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
import warnings
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from verify_lineage import safe_file, verify_lineage
from release_gate import check_bindings, wheel_check, proof_check


def write(root, name, data):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data, encoding='utf-8')
    return path


def dump(root, name, obj):
    return write(root, name, json.dumps(obj))


class PathsAndBindings(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.file = write(self.root, 'a/file.txt', 'fixed bytes')
        self.hash = hashlib.sha256(self.file.read_bytes()).hexdigest()

    def test_valid_file(self): self.assertEqual(safe_file(self.root, 'a/file.txt'), self.file)
    def test_parent_escape(self):
        with self.assertRaises(ValueError): safe_file(self.root, '../file.txt')
    def test_absolute_path(self):
        with self.assertRaises(ValueError): safe_file(self.root, str(self.file))
    def test_backslash_path(self):
        with self.assertRaises(ValueError): safe_file(self.root, 'a\\file.txt')
    def test_noncanonical_path(self):
        with self.assertRaises(ValueError): safe_file(self.root, 'a//file.txt')
    def test_directory_rejected(self):
        with self.assertRaises(ValueError): safe_file(self.root, 'a')
    def test_missing_file(self):
        with self.assertRaises(ValueError): safe_file(self.root, 'absent')
    def test_symlink_rejected(self):
        (self.root / 'link').symlink_to(self.file)
        with self.assertRaises(ValueError): safe_file(self.root, 'link')
    def test_binding_accepts(self):
        self.assertEqual(check_bindings(self.root, {'a/file.txt': self.hash}, 'test'), 1)
    def test_empty_binding_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Empty'): check_bindings(self.root, {}, 'test')
    def test_changed_file_rejected(self):
        self.file.write_text('changed', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Stale'): check_bindings(self.root, {'a/file.txt': self.hash}, 'test')
    def test_wrong_hash_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Stale'): check_bindings(self.root, {'a/file.txt': '0'*64}, 'test')


class WheelBinding(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        write(self.root, 'VERSION', '1.0.0rc3\n')
        self.py = ['repair_certificates.py', 'rational_menu.py', 'branch_menu.py', 'komorebi_repair/__init__.py']
        for name in self.py: write(self.root, 'python/' + name, '# synthetic wheel fixture\n')
        (self.root / 'dist').mkdir()
        self.wheel = self.root / 'dist/candidate.whl'
        self.make()

    def make(self, version='1.0.0rc3', project='komorebi-constructive-repair', omit=None, extra=False, duplicate=False):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            with zipfile.ZipFile(self.wheel, 'w') as z:
                for name in self.py:
                    if name != omit: z.write(self.root / 'python' / name, name)
                if extra: z.writestr('unexpected.py', '# extra')
                if duplicate: z.writestr(self.py[0], '# duplicate')
                z.writestr('package.dist-info/METADATA', 'Metadata-Version: 2.4\nName: ' + project + '\nVersion: ' + version + '\n\n')

    def test_matching_wheel(self): self.assertEqual(wheel_check(self.root)['files'], len(self.py))
    def test_stale_version(self):
        self.make(version='1.0.0rc2')
        with self.assertRaisesRegex(ValueError, 'version'): wheel_check(self.root)
    def test_wrong_name(self):
        self.make(project='other-project')
        with self.assertRaisesRegex(ValueError, 'project'): wheel_check(self.root)
    def test_stale_source(self):
        write(self.root, 'python/branch_menu.py', '# modified')
        with self.assertRaisesRegex(ValueError, 'mismatch'): wheel_check(self.root)
    def test_missing_python_member(self):
        self.make(omit=self.py[0])
        with self.assertRaisesRegex(ValueError, 'inventory'): wheel_check(self.root)
    def test_extra_python_member(self):
        self.make(extra=True)
        with self.assertRaisesRegex(ValueError, 'inventory'): wheel_check(self.root)
    def test_duplicate_member(self):
        self.make(duplicate=True)
        with self.assertRaisesRegex(ValueError, 'Duplicate'): wheel_check(self.root)
    def test_multiple_wheels(self):
        (self.root/'dist/second.whl').write_bytes(self.wheel.read_bytes())
        with self.assertRaisesRegex(ValueError, 'exactly one'): wheel_check(self.root)
    def test_symlink_wheel(self):
        target = self.root / 'stored.whl'; self.wheel.rename(target); self.wheel.symlink_to(target)
        with self.assertRaisesRegex(ValueError, 'symlink'): wheel_check(self.root)


class EvidenceBinding(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        # Purely synthetic data exercise the release checker; no kernel claim.
        self.mods = ['M'+str(i) for i in range(51)]
        dump(self.root, 'evidence/modules.json', self.mods)
        names = ['Synthetic.t'+str(i) for i in range(526)]
        dump(self.root, 'docs/theorem_registry.json', {'theorems':[{'name':n} for n in names]})
        mapping = {}
        for m in self.mods:
            name='lean/KomorebiRepair/'+m+'.lean';p=write(self.root,name,'-- synthetic source only\n')
            mapping[name]=hashlib.sha256(p.read_bytes()).hexdigest()
        self.v = {'status':'PASS','proof_modules':51,'theorem_declarations':526,
                  'checks':{'synthetic':{'pass':True}},'source_sha256':mapping,
                  'axioms':{n:['propext'] for n in names},
                  'commands':[{'label':prefix+m} for m in self.mods for prefix in ('compile_KomorebiRepair_','replay_')]}
        self.save()
    def save(self): dump(self.root,'evidence/verification/current/verification.json',self.v)
    def test_structural_fixture(self): self.assertEqual(proof_check(self.root)['declarations'],526)
    def test_failed_run(self):
        self.v['status']='FAIL';self.save()
        with self.assertRaisesRegex(ValueError,'did not pass'):proof_check(self.root)
    def test_failed_check(self):
        self.v['checks']['synthetic']['pass']=False;self.save()
        with self.assertRaisesRegex(ValueError,'failed'):proof_check(self.root)
    def test_missing_axiom_row(self):
        self.v['axioms'].pop(next(iter(self.v['axioms'])));self.save()
        with self.assertRaisesRegex(ValueError,'axiom inventory'):proof_check(self.root)
    def test_forbidden_axiom(self):
        self.v['axioms']['Synthetic.t0']=['sorryAx'];self.save()
        with self.assertRaisesRegex(ValueError,'Disallowed'):proof_check(self.root)
    def test_missing_proof_binding(self):
        self.v['source_sha256'].pop(next(iter(self.v['source_sha256'])));self.save()
        with self.assertRaisesRegex(ValueError,'missing'):proof_check(self.root)
    def test_stale_proof_bytes(self):
        write(self.root,'lean/KomorebiRepair/M0.lean','-- changed')
        with self.assertRaisesRegex(ValueError,'Stale formal'):proof_check(self.root)
    def test_missing_replay(self):
        self.v['commands']=self.v['commands'][:-1];self.save()
        with self.assertRaisesRegex(ValueError,'replay command'):proof_check(self.root)
    def test_duplicate_label(self):
        self.v['commands'].append(self.v['commands'][0]);self.save()
        with self.assertRaisesRegex(ValueError,'Duplicate'):proof_check(self.root)
    def test_wrong_count(self):
        self.v['proof_modules']=50;self.save()
        with self.assertRaisesRegex(ValueError,'count'):proof_check(self.root)


class HistoricalSnapshots(unittest.TestCase):
    def test_actual_lineage(self):
        self.assertEqual([r['files'] for r in verify_lineage(ROOT)['releases']], [10,23,37,51])

if __name__ == '__main__': unittest.main()
