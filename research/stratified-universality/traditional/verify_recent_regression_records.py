from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent
GEN = ROOT / 'generated'
EXPECTED = {
    'block11_nonlinear_tree_validation.json': 115_721,
    'block12_galois_tannakian_validation.json': 11_195,
    'block13_bridge_synthesis_validation.json': 154_209,
    'block13_global_invariant_validation.json': 119_453,
}
checks = 0
for name, expected in EXPECTED.items():
    path = GEN / name
    if not path.is_file():
        raise SystemExit(f'missing validation record: {path}')
    record = json.loads(path.read_text(encoding='utf-8'))
    observed = int(record.get('checks', -1))
    failures = record.get('failures', [])
    failure_count = len(failures) if isinstance(failures, list) else int(failures or 0)
    if not record.get('passed') or observed != expected or failure_count:
        raise SystemExit(f'invalid record {name}: observed={observed}, failures={failure_count}')
    checks += observed
combined = json.loads((GEN / 'block13_combined_validation.json').read_text(encoding='utf-8'))
if not combined.get('passed') or int(combined.get('cumulative_unique_block_checks', -1)) != 2_272_676:
    raise SystemExit('invalid Block 13 combined record')
print('RECENT_REGRESSION_RECORDS=PASS')
print(f'BLOCK11_TO_BLOCK13_EXECUTED_CHECKS={checks}')
print('CUMULATIVE_UNIQUE_BLOCK03_TO_BLOCK13=2272676')
