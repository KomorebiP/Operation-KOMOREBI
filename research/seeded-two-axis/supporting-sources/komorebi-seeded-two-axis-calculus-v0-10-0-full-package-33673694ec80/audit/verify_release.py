#!/usr/bin/env python3
"""Verify packaged hashes and optionally an explicitly supplied ZIP."""
from __future__ import annotations
import argparse,hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--zip',type=Path);args=ap.parse_args()
    manifest=json.loads((ROOT/'audit/release_manifest.json').read_text())
    for item in manifest['files']:
        p=ROOT/item['path'];assert p.is_file(),p
        assert p.stat().st_size==item['bytes'],p
        assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'],p
    if args.zip:
        with zipfile.ZipFile(args.zip) as z:
            assert z.testzip() is None
            for item in manifest['files']:
                payload=z.read(ROOT.name+'/'+item['path'])
                assert hashlib.sha256(payload).hexdigest()==item['sha256'],item['path']
    print(json.dumps({'status':'PASS','checked_files':len(manifest['files']),
                      'zip_integrity_checked':args.zip is not None},indent=2))
if __name__=='__main__':main()
