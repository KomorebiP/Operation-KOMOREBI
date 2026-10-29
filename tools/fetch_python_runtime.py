"""Fetch and verify the small, pinned browser Python distribution."""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request

MANIFEST = Path(__file__).resolve().parents[1]/'website/python-runtime.json'


def verify(root):
    record = json.loads(MANIFEST.read_bytes())
    for name, entry in record['files'].items():
        if Path(name).name != name or ':' in name or '\\' in name:
            raise ValueError('Unsafe Python runtime name')
        raw = (root/name).read_bytes()
        if len(raw) != entry['size'] or hashlib.sha256(raw).hexdigest() != entry['sha256']:
            raise ValueError('Python runtime integrity mismatch: '+name)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    record = json.loads(MANIFEST.read_bytes())
    args.output.mkdir(parents=True, exist_ok=True)
    for name, entry in record['files'].items():
        target = args.output/name
        if target.is_file() and hashlib.sha256(target.read_bytes()).hexdigest() == entry['sha256']:
            continue
        raw = urllib.request.urlopen(entry['url'], timeout=90).read()
        if hashlib.sha256(raw).hexdigest() != entry['sha256']:
            raise ValueError('Downloaded Python runtime integrity mismatch: '+name)
        target.write_bytes(raw)
    verify(args.output)
    print('PASS: pinned Python runtime and NumPy')


if __name__ == '__main__':
    main()
