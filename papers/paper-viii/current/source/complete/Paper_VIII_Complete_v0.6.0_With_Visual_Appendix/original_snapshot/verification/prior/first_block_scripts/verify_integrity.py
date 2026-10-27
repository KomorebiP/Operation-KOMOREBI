#!/usr/bin/env python3
"""Verify distributed file sizes and SHA-256 hashes. Author: Komorebi P.

Extra files created by a later verification run are allowed. This detects changes
against the packaged manifest; it does not provide an external authenticity signature.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    manifest = json.loads((root/'MANIFEST_SHA256.json').read_text())
    failures = []
    for name, expected in manifest['files'].items():
        rel = Path(name)
        if rel.is_absolute() or '..' in rel.parts:
            failures.append(name+': invalid path')
            continue
        target = root/rel
        if not target.is_file():
            failures.append(name+': missing')
            continue
        data = target.read_bytes()
        if len(data) != expected['bytes']:
            failures.append(name+': wrong size')
        if hashlib.sha256(data).hexdigest() != expected['sha256']:
            failures.append(name+': wrong SHA-256')
    print(json.dumps({'pass':not failures,'files_checked':len(manifest['files']),'failures':failures},indent=2))
    return 0 if not failures else 1

if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError,ValueError,KeyError) as exc:
        print(f'Integrity check failed: {exc}',file=sys.stderr)
        raise SystemExit(1)
