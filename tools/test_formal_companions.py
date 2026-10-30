"""Reject stale source, placeholder axioms and broken formal-evidence bindings."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from formal_companions import validate_formal_companions


class FormalCompanionTests(unittest.TestCase):
    def fixture(self, root):
        tracked = {}

        def put(path, raw):
            if isinstance(raw, str):
                raw = raw.encode()
            target = root/path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            tracked[path] = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
            return hashlib.sha256(raw).hexdigest()

        source = 'formal/test'
        inputs = {'Main.lean': put(source+'/Main.lean', 'theorem checked : True := True.intro\n'),
                  'lean-toolchain': put(source+'/lean-toolchain', 'leanprover/lean4:v4.24.0\n')}
        parent = 'verification/test/run'
        receipt_path = parent+'/receipt.json'
        steps = []
        for name in ['version', 'compiler-prefix', 'compile-Main',
                     'reject-false-symmetry', 'reject-false-additivity', 'reject-sorry']:
            positive = not name.startswith('reject-')
            diagnostic = None if positive else 'EXPECTED REJECTION'
            step = {'name': name, 'accepted': True, 'exit_code': 0 if positive else 1,
                    'expected_zero': positive, 'required_diagnostic': diagnostic}
            for stream in ('stdout', 'stderr'):
                step[stream] = name+'.'+stream+'.txt'
                step[stream+'_sha256'] = put(parent+'/'+step[stream],
                                             diagnostic if diagnostic and stream == 'stdout' else '')
            steps.append(step)
        receipt = {'kind':'bounded-lean-replay', 'component':'test', 'status':'PASS',
                   'inputs':inputs, 'lean_pin':'leanprover/lean4:v4.24.0',
                   'theorem_count':1, 'theorem_axioms':{'checked':[]},
                   'steps':steps, 'negative_controls':3}
        binding = {'path':receipt_path, 'source_root':source, 'main_theorems':['checked']}
        data = {'components':[{'id':'test', 'formal_verification':binding}],
                'assessment_records':[receipt_path]}

        def seal():
            binding['sha256'] = put(receipt_path, json.dumps(receipt))

        seal()
        return data, tracked, receipt, seal, put

    def test_accepts_exact_committed_sources_and_logs(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            data, tracked, _, _, _ = self.fixture(root)
            validate_formal_companions(root, data, tracked)

    def test_rejects_source_or_diagnostic_edits_after_a_pass(self):
        for target in ['formal/test/Main.lean', 'verification/test/run/reject-sorry.stdout.txt']:
            with self.subTest(target=target), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                data, tracked, _, _, put = self.fixture(root)
                put(target, 'changed after replay')
                with self.assertRaisesRegex(AssertionError, 'digest differs'):
                    validate_formal_companions(root, data, tracked)

    def test_rejects_placeholder_axioms_missing_builds_and_failed_controls(self):
        for variant in ['sorry', 'missing-build', 'failed-control', 'missing-theorem']:
            with self.subTest(variant=variant), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                data, tracked, receipt, seal, _ = self.fixture(root)
                if variant == 'sorry':
                    receipt['theorem_axioms']['checked'] = ['sorryAx']
                elif variant == 'missing-build':
                    receipt['steps'] = [s for s in receipt['steps'] if s['name'] != 'compile-Main']
                elif variant == 'failed-control':
                    receipt['steps'][-1]['exit_code'] = 0
                else:
                    data['components'][0]['formal_verification']['main_theorems'] = ['missing']
                seal()
                with self.assertRaises(AssertionError):
                    validate_formal_companions(root, data, tracked)

    def test_rejects_uncommitted_or_escaping_source(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            data, tracked, _, _, _ = self.fixture(root)
            missing = copy.deepcopy(tracked)
            missing.pop('formal/test/Main.lean')
            with self.assertRaisesRegex(AssertionError, 'committed source'):
                validate_formal_companions(root, data, missing)
            data['components'][0]['formal_verification']['source_root'] = 'formal/../test'
            with self.assertRaises(AssertionError):
                validate_formal_companions(root, data, tracked)


if __name__ == '__main__':
    unittest.main()
