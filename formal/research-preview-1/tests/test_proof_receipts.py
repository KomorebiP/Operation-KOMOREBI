"""Synthetic, adversarial receipt checks; these tests do not execute Lean."""
import copy
import hashlib
import importlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import check_proof_receipt as gate
import record_workflow_context as context

class ReceiptSafety(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.inputs = {'padic/lean/Example.lean': 'a' * 64}
        self.manifest = {'packages': [{'name': 'mathlib', 'rev': 'b' * 40}]}
        self.inventory = {'names': ['Example.a', 'Example.b']}
        specs = [('lean_version', ['lean', '--version'], 'Lean 4.34.0-rc2 commit 6a10ac8\n'),
                 ('lake_version', ['lake', '--version'], 'Lake 5.0\n'),
                 ('pin_mathlib', ['git', '-C', '/example/padic/.lake/packages/mathlib', 'rev-parse', 'HEAD'], 'b'*40+'\n')]
        texts = {'build': 'Build completed successfully (1 jobs).\n',
                 'declared_axioms': "'Example.a' does not depend on any axioms\n'Example.b' depends on axioms: [propext]\n",
                 'environment_axioms': 'PROJECT_AXIOMS|Example.a|Example|\nPROJECT_AXIOMS|Example.b|Example|propext\n'}
        specs.extend((name, argv, texts.get(name, '')) for name, argv in gate.NORMAL)
        for name in gate.NEGATIVES:
            text = ('error: declaration uses `sorry`\n' if name == 'PlaceholderControl' else
                    'error: Tactic `decide` proved that the proposition\n  1 = 2\nis false\n')
            specs.append((name, ['lake', 'env', 'lean', '-DwarningAsError=true', f'verification/{name}.lean'], text))
        commands = []
        for name, argv, text in specs:
            raw = text.encode()
            (self.root / (name + '.log')).write_bytes(raw)
            negative = name in gate.NEGATIVES
            commands.append({'name': name, 'argv': argv, 'exit_code': 1 if negative else 0,
                             'seconds': 0.01, 'timeout': False, 'launch_error': None,
                             'expected_rejection': negative, 'status': 'PASS', 'log': name + '.log',
                             'sha256': hashlib.sha256(raw).hexdigest()})
        self.report = {'status': 'PASS', 'clean_requested': True, 'fresh_project_build': True,
                       'inputs_unchanged': True, 'proof_source_hashes_before': self.inputs,
                       'proof_source_hashes_after': self.inputs,
                       'started_at_utc': '2026-09-21T00:00:00Z', 'finished_at_utc': '2026-09-21T00:01:00Z',
                       'commands': commands, 'axiom_audit': {'status': 'PASS', 'declared': 2, 'environment': 2}}
    def run_check(self):
        (self.root / 'REPLAY.json').write_text(json.dumps(self.report))
        return gate.check_receipt(self.root, expected_snapshot=self.inputs,
                                  manifest=self.manifest, inventory=self.inventory)
    def command(self, name):
        return next(c for c in self.report['commands'] if c['name'] == name)
    def rewrite_log(self, name, text):
        raw = text.encode()
        (self.root / (name + '.log')).write_bytes(raw)
        self.command(name)['sha256'] = hashlib.sha256(raw).hexdigest()
    def rejects(self, message):
        result = self.run_check()
        self.assertEqual(result['status'], 'FAIL')
        self.assertTrue(any(message in e for e in result['errors']), result)
    def test_complete_receipt(self):
        self.assertEqual(self.run_check()['status'], 'PASS')
    def test_blocked_receipt(self):
        self.report['status'] = 'BLOCKED'; self.rejects('did not finish')
    def test_incremental_build_not_fresh(self):
        self.report['fresh_project_build'] = False; self.rejects('empty project-local')
    def test_stale_source(self):
        self.report['proof_source_hashes_before'] = {'other': 'a'*64}; self.rejects('Before-run')
    def test_changed_after_run(self):
        self.report['proof_source_hashes_after'] = {}; self.rejects('After-run')
    def test_missing_control(self):
        self.report['commands'].pop(); self.rejects('Command list')
    def test_duplicate_control(self):
        self.report['commands'].append(copy.deepcopy(self.report['commands'][-1])); self.rejects('Command list')
    def test_timeout_not_pass(self):
        self.command('build')['timeout'] = True; self.rejects('Timeout')
    def test_changed_log(self):
        (self.root/'build.log').write_text('forged'); self.rejects('Log hash')
    def test_wrong_dependency_revision(self):
        self.rewrite_log('pin_mathlib', 'c'*40+'\n'); self.rejects('Dependency pin')
    def test_control_import_failure_not_contradiction(self):
        self.rewrite_log('FalseControl', 'error: unknown module prefix\n'); self.rejects('expected contradiction')
    def test_control_zero_exit_not_rejection(self):
        self.command('FalseControl')['exit_code'] = 0; self.rejects('Incorrect exit')
    def test_unsafe_log_path(self):
        self.command('build')['log'] = '../outside.log'; self.rejects('Unsafe')
    def test_symlinked_log(self):
        target = self.root/'copied.log'; target.write_bytes((self.root/'build.log').read_bytes())
        (self.root/'build.log').unlink()
        try:
            (self.root/'build.log').symlink_to(target)
        except OSError:
            self.skipTest('Host does not allow unprivileged symlinks')
        self.rejects('symlinked log')
    def test_axiom_inventory_omission(self):
        self.rewrite_log('environment_axioms', 'PROJECT_AXIOMS|Example.a|Example|\n')
        self.rejects('omits declared')
    def test_extra_axiom(self):
        self.rewrite_log('environment_axioms', 'PROJECT_AXIOMS|Example.a|Example|\nPROJECT_AXIOMS|Example.b|Example|sorryAx\n')
        self.rejects('Unexpected theorem axioms')
    def test_changed_build_command(self):
        self.command('build')['argv'] = ['echo', 'PASS']; self.rejects('Changed command')
    def test_claimed_totals_do_not_override_logs(self):
        self.report['axiom_audit']['declared'] = 500; self.rejects('Recorded axiom totals')
    def test_false_boolean_exit(self):
        self.command('build')['exit_code'] = False; self.rejects('Incorrect exit')
    def test_not_a_replay_file(self):
        (self.root/'REPLAY.json').write_text('{bad json')
        self.assertEqual(gate.check_receipt(self.root)['status'], 'FAIL')

class WorkflowContextSafety(unittest.TestCase):
    def test_context_never_infers_proof_success(self):
        result = context.workflow_record({'BOOTSTRAP_OUTCOME':'success', 'REPLAY_OUTCOME':'success'})
        self.assertFalse(result['proof_verified'])
        self.assertNotIn('status', result)
    def test_only_allowlisted_environment(self):
        result = context.workflow_record({'GITHUB_TOKEN':'secret', 'SOME_PRIVATE_VALUE':'secret', 'GITHUB_SHA':'abc'})
        self.assertNotIn('secret', json.dumps(result))
        self.assertEqual(result['context']['GITHUB_SHA'], 'abc')
    def test_missing_bootstrap_is_explicit(self):
        result = context.workflow_record({})
        self.assertEqual(result['context']['BOOTSTRAP_OUTCOME'], 'unavailable')

if __name__ == '__main__':
    unittest.main()
