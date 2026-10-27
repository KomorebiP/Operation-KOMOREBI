"""Compare frozen Block 17 file content, inventory, size and mtime to snapshot."""
import argparse
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--root', type=Path, required=True)
parser.add_argument('--snapshot', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
root = args.root.resolve()
before = json.loads(args.snapshot.read_text())
after = {}
for p in sorted(root.rglob('*')):
    if p.is_file():
        with p.open('rb') as f:
            digest = hashlib.file_digest(f, 'sha256').hexdigest()
        after[str(p.relative_to(root))] = {'size': p.stat().st_size,
            'mtime_ns': p.stat().st_mtime_ns, 'sha256': digest}
changed = [name for name in sorted(set(before) | set(after)) if before.get(name) != after.get(name)]
report = {'source_root': str(root), 'files_before': len(before), 'files_after': len(after),
    'unchanged': not changed, 'changed_paths': changed}
args.output.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
raise SystemExit(0 if not changed else 1)
