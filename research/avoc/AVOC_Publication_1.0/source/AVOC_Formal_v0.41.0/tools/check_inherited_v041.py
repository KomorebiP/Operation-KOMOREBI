#!/usr/bin/env python3
"""Check every inherited non-audit Lean module against the exact v0.40 release ZIP."""
import argparse, hashlib, json, zipfile
from pathlib import Path
from release_common_v041 import ROOT, RD, BASE_PREFIX, BASE_SHA256, AUDITS, sha, write_json

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('archive',type=Path);args=parser.parse_args()
    if sha(args.archive)!=BASE_SHA256:raise RuntimeError('Not the exact authorized v0.40 archive')
    records=[]
    with zipfile.ZipFile(args.archive) as archive:
        if archive.testzip() is not None:raise RuntimeError('Base archive CRC failure')
        names=archive.namelist()
        if len(names)!=len(set(names)):raise RuntimeError('Duplicate base archive entries')
        for name in sorted(names):
            if not name.startswith(BASE_PREFIX+'AVOC/') or not name.endswith('.lean'):continue
            source=name.removeprefix(BASE_PREFIX)
            if source in AUDITS:continue
            expected=hashlib.sha256(archive.read(name)).hexdigest();path=ROOT/source
            actual=sha(path) if path.is_file() else None
            records.append(dict(source=source,sha256=expected,current_sha256=actual,byte_identical=expected==actual))
    if len(records)!=191:raise RuntimeError(f'Expected 191 inherited non-audit modules; found {len(records)}')
    result=dict(base_version='0.40.0',base_archive_sha256=BASE_SHA256,total=len(records),
                byte_identical=sum(r['byte_identical'] for r in records),passed=all(r['byte_identical'] for r in records),records=records)
    write_json(RD/'inherited_source_identity.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))
    return 0 if result['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
