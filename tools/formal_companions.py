"""Bind separately checked Lean companions without rewriting imported evidence."""
import hashlib
import json
import re


def validate_formal_companions(root, data, current):
    def artifact(path, digest=None):
        assert isinstance(path, str) and not path.startswith('/') and '\\' not in path
        assert not any(p in ('', '.', '..') for p in path.split('/')), path
        raw = (root/path).read_bytes()
        assert current.get(path) == hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(), 'Formal artifact is not the committed source: '+path
        if digest:
            assert hashlib.sha256(raw).hexdigest() == digest, 'Formal artifact digest differs: '+path
        return raw

    for row in data['components']:
        binding = row.get('formal_verification')
        if not binding:
            continue
        path = binding['path']
        assert path.startswith('verification/') and path in data['assessment_records'], path
        receipt = json.loads(artifact(path, binding['sha256']))
        assert receipt['kind'] == 'bounded-lean-replay' and receipt['component'] == row['id'], path
        assert receipt['status'] == 'PASS', 'Formal replay did not pass: '+path
        source = binding['source_root']
        assert source.startswith('formal/') and not source.endswith('/'), source
        for name, digest in receipt['inputs'].items():
            assert '/' not in name and '\\' not in name and name not in ('.', '..'), name
            artifact(source+'/'+name, digest)
        assert artifact(source+'/lean-toolchain').decode().strip() == receipt['lean_pin'], path
        axioms = receipt['theorem_axioms']
        assert receipt['theorem_count'] == len(axioms), path
        for dependencies in axioms.values():
            assert set(dependencies) <= {'propext', 'Quot.sound', 'Classical.choice'}, 'Unaccepted formal axiom: '+path
        assert binding['main_theorems'], path
        for name in binding['main_theorems']:
            assert name in axioms and not axioms[name], 'Main formal theorem is missing or has axioms: '+name
        for name, expected in binding.get('checked_theorems', {}).items():
            assert isinstance(expected, list) and len(expected) == len(set(expected)), name
            assert name in axioms, 'Required formal theorem is missing: '+name
            assert set(axioms[name]) == set(expected), 'Formal theorem axioms differ: '+name
        controls = set()
        step_names = [s['name'] for s in receipt['steps']]
        assert len(step_names) == len(set(step_names)), path
        compilations = {'compile-'+name[:-5] for name in receipt['inputs'] if name.endswith('.lean')}
        assert compilations | {'version', 'compiler-prefix'} <= set(step_names), 'Incomplete formal build: '+path
        positive = set(binding.get('required_positive_steps', []))
        assert positive <= set(step_names), 'Missing formal execution: '+path
        assert all(s['expected_zero'] for s in receipt['steps'] if s['name'] in positive), 'Required formal execution is negative: '+path
        for step in receipt['steps']:
            assert step['accepted'] and ((step['exit_code'] == 0) == step['expected_zero']), path
            parent = path.rsplit('/', 1)[0]
            logs = []
            for stream in ('stdout', 'stderr'):
                name = step[stream]
                assert re.fullmatch(r'[a-zA-Z0-9_-]+\.(?:stdout|stderr)\.txt', name), name
                logs.append(artifact(parent+'/'+name, step[stream+'_sha256']).decode('utf-8'))
            if not step['expected_zero']:
                assert step['required_diagnostic'] and step['required_diagnostic'] in ''.join(logs), path
                controls.add(step['name'])
        required = {'reject-false-symmetry', 'reject-false-additivity', 'reject-sorry'}
        required.update(binding.get('required_controls', []))
        assert required <= controls and receipt['negative_controls'] == len(controls), path
