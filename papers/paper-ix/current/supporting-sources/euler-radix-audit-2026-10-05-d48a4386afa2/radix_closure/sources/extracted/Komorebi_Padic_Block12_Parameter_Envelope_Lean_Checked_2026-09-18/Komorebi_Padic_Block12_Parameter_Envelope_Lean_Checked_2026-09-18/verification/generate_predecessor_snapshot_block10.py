#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, re, sys
from pathlib import Path

THEOREM_START = re.compile(r"^\s*(?:@\[[^\]]+\]\s*)*(?:protected\s+)?(?:theorem|lemma)\s+([A-Za-z0-9_'.]+)\b")

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def theorem_headers(lean_root: Path) -> dict[str, dict[str, str]]:
    out = {}
    for path in sorted((lean_root / 'KomorebiPadic').glob('*.lean')):
        lines = path.read_text(encoding='utf-8').splitlines()
        i = 0
        while i < len(lines):
            m = THEOREM_START.match(lines[i])
            if not m:
                i += 1
                continue
            name = m.group(1)
            acc = [lines[i]]
            while ':=' not in acc[-1]:
                i += 1
                if i >= len(lines):
                    raise RuntimeError(f'unterminated theorem header {name} in {path}')
                acc.append(lines[i])
            joined = '\n'.join(acc).split(':=', 1)[0]
            out[name] = {
                'header': ' '.join(joined.split()),
                'file': str(path.relative_to(lean_root.parent)),
            }
            i += 1
    return out

def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit('usage: script PREDECESSOR_LEAN OUT_JSON')
    lean = Path(sys.argv[1])
    out = Path(sys.argv[2])
    headers = theorem_headers(lean)
    files = sorted(lean.rglob('*.lean'))
    payload = {
        'schema': 'komorebi-padic-block09-theorem-headers-v1',
        'theorem_count': len(headers),
        'headers': headers,
        'source_files': {str(p.relative_to(lean.parent)): sha256(p) for p in files},
    }
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(f'theorems={len(headers)} out={out}')

if __name__ == '__main__':
    main()
