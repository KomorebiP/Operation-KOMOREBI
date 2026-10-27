"""Check recovered package integrity. This does not run Lean."""
from pathlib import Path
import hashlib
import json

def check_manifest(root, name):
    expected={}
    for line in (root/name).read_text().splitlines():
        digest,relative=line.split('  ',1)
        path=Path(relative)
        if path.is_absolute() or '..' in path.parts or relative in expected:
            raise ValueError('Invalid manifest path: '+relative)
        expected[relative]=digest
    actual={p.relative_to(root).as_posix() for p in root.rglob('*')
            if p.is_file() and '__pycache__' not in p.parts and p!=root/name}
    if actual!=set(expected):
        raise ValueError(json.dumps({'missing':sorted(set(expected)-actual),'extra':sorted(actual-set(expected))}))
    for relative,digest in expected.items():
        path=root/relative
        if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:
            raise ValueError('Hash mismatch: '+relative)
    return len(expected)

def main():
    root=Path(__file__).resolve().parent
    total=check_manifest(root,'RECOVERY_SHA256SUMS')
    original=root/'Komorebi_Unified_Inference_Stochastic_Bayesian_CONTINUATION_v14_2026-09-12'
    inherited=check_manifest(original,'SHA256SUMS')
    print(json.dumps({'status':'PASS_RECOVERY_INTEGRITY','package_manifest_entries':total,
                      'original_manifest_entries':inherited,'new_lean_checks':0}))

if __name__=='__main__':main()
