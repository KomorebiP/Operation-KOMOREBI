#!/usr/bin/env python3
"""Validate active computation records against the packaged, unchanged bytes."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--report', type=Path)
args = parser.parse_args()
validator = root / 'verification/computation/vendor/validate_manifest.py'
paths = sorted((root/'verification/computation').glob('*run/manifest.json'))
paths += [root/'audit/math/small_exact_bounded_run_v2/manifest.json',
          root/'audit/guide_review/bounded_examples/manifest.json',
          root/'editable/visual_guide/computations/exact_examples_v2/manifest.json',
          root/'editable/lean_guide/audit/static_bound_release_run/manifest.json']
assert len(paths) == 9, 'Active gate list has changed; review before updating.'
records = []
for manifest in paths:
    assert manifest.is_file(), manifest
    data = json.loads(manifest.read_text())
    local_visual_root = 'editable/visual_guide/' in str(manifest.relative_to(root))
    base = root/'editable/visual_guide' if local_visual_root else root
    aliases = {'lean_guide': root/'editable/lean_guide',
               'traditional': root/'editable/traditional',
               'visual_guide': root/'editable/visual_guide'}
    mapped = []
    with tempfile.TemporaryDirectory(prefix='paper-ix-evidence-') as temp:
        stage = Path(temp)
        artifacts = data.get('input_artifacts', []) + data.get('outputs', [])
        for entry in artifacts:
            relative = Path(entry['path'])
            assert not relative.is_absolute() and '..' not in relative.parts
            if not local_visual_root and relative.parts[0] in aliases:
                source = aliases[relative.parts[0]].joinpath(*relative.parts[1:])
            else:
                source = base/relative
            assert source.is_file(), source
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            assert digest == entry['sha256'], f'Changed artifact: {source}'
            target = stage/relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            mapped.append({'recorded_path': str(relative),
                           'packaged_path': str(source.relative_to(root)),
                           'sha256': digest})
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
        proc = subprocess.run([sys.executable, str(validator), str(manifest),
                               '--root', str(stage)], capture_output=True,
                              text=True, env=env)
        assert proc.returncode == 0, proc.stdout + proc.stderr
    records.append({'manifest': str(manifest.relative_to(root)),
                    'manifest_sha256': hashlib.sha256(manifest.read_bytes()).hexdigest(),
                    'status': 'PASS', 'validator_stdout': proc.stdout.strip(),
                    'path_mapping': mapped})
report = {'status': 'PASS', 'active_manifests': len(records), 'records': records,
          'scope': 'Validation of unchanged input/output bytes and complete records. '
                   'Editable companion folders are mapped to their original execution paths '
                   'in temporary validation roots. No command is reexecuted and no theorem '
                   'or inherited compiler outcome is established by this check.',
          'inactive_records': 'Superseded visual and static path-metadata predecessors and '
                              'the stale-input math predecessor remain archived with status notes; '
                              'they are not active evidence.'}
if args.report:
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps({'status': report['status'], 'active_manifests': len(records)}, indent=2))
