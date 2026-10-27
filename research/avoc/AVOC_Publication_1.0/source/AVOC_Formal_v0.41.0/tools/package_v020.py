#!/usr/bin/env python3
"""Package current audited v0.20 source/evidence, excluding runtime/build caches.

This checks source/evidence fingerprints before publication. Hash/ZIP checks
certify delivered bytes, not mathematical truth or physical-host correctness.
Existing output directories are never deleted.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
RD=ROOT/'results/v0.20.0'
VERSION='0.20.0'

def sha(path:Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

def require(ok:bool,message:str)->None:
    if not ok:raise RuntimeError(message)

def include(path:Path,root:Path)->bool:
    rel=path.relative_to(root)
    return (path.is_file() and not any(x in rel.parts for x in ['.lake','.git','__pycache__'])
            and path.suffix not in ['.pyc','.olean','.ilean']
            and rel.as_posix() not in ['SHA256SUMS.txt','PACKAGING.json'])

def main()->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-dir',type=Path,default=Path('/mnt/data'));args=p.parse_args()
    audit=json.loads((ROOT/'AUDIT.json').read_text())
    require(audit['status']=='PASS' and audit['version']==VERSION,'missing current release audit')
    for rec in json.loads((RD/'final_local_build_summary.json').read_text()):
        require(sha(ROOT/rec['source'])==rec['source_sha256'],'changed proof source '+rec['source'])
        require(sha(ROOT/rec['log'])==rec['log_sha256'],'changed proof log '+rec['source'])
    inv=json.loads((RD/'declaration_inventory.json').read_text())
    ax=json.loads((RD/'axiom_audit_summary.json').read_text())
    require(ax['passed'] and ax['audited']==len(inv)==1020,'wrong axiom census')
    axrun=json.loads((RD/'full_axiom_audit.json').read_text())
    require(sha(ROOT/'AVOC/FullAudit.lean')==axrun['source_sha256'],'changed full axiom source')
    require(sha(ROOT/axrun['log'])==axrun['log_sha256'],'changed full axiom log')
    for rec in json.loads((RD/'final_negative_summary.json').read_text()):
        require(sha(ROOT/rec['source'])==rec['source_sha256'],'changed negative source')
        require(sha(ROOT/rec['log'])==rec['log_sha256'],'changed negative log')
    tests=json.loads((RD/'recovery_test_summary.json').read_text())
    require(tests['passed'] and tests['count']==22,'missing current live suite')
    for case in tests['cases']:
        record=ROOT/case['record'];require(sha(record)==case['record_sha256'],'changed case record')
        row=json.loads(record.read_text())
        require(sha(ROOT/'checks/test_recovery.py')==row['script_sha256'],'changed test program')
        for path,digest in row['source_pins'].items():
            require(sha(ROOT/path)==digest,'changed live runtime source '+path)
    # Complete v1 evidence outputs are checked independently by the included adapter.
    sys.path.insert(0,str(ROOT/'tools/audit'))
    from validate_computation_manifest import validate
    mp=RD/'computation_manifest.json'
    require(not validate(json.loads(mp.read_text()),ROOT,mp),'invalid collector computation manifest')
    args.output_dir.mkdir(parents=True,exist_ok=True)
    dest=args.output_dir/f'AVOC_Formal_v{VERSION}'
    if dest.resolve()!=ROOT.resolve():
        require(not dest.exists(),'refusing to replace an existing output directory')
        shutil.copytree(ROOT,dest,ignore=shutil.ignore_patterns('.lake','.git','__pycache__','*.pyc','*.olean','*.ilean'))
    files=sorted(p for p in dest.rglob('*') if include(p,dest))
    require(not any(p.is_symlink() for p in files),'unexpected payload symlink')
    rows=[(sha(p),p.relative_to(dest).as_posix()) for p in files]
    (dest/'SHA256SUMS.txt').write_text(''.join(d+'  '+name+'\n' for d,name in rows))
    for d,name in rows:require(sha(dest/name)==d,'payload changed during hashing '+name)
    (dest/'PACKAGING.json').write_text(json.dumps({'version':VERSION,'status':'PASS','payload_hashes':len(files),
        'manifest_scope':'All delivered regular files except SHA256SUMS.txt and this packaging note.',
        'exclusions':['.lake','.git','__pycache__','*.pyc','*.olean','*.ilean'],
        'theorem_status':'AUDIT.json; byte integrity is not theorem proof or physical correctness.'},indent=2)+'\n')
    archive=args.output_dir/f'AVOC_Formal_v{VERSION}.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for path in files+[dest/'SHA256SUMS.txt',dest/'PACKAGING.json']:
            z.write(path,f'AVOC_Formal_v{VERSION}/'+path.relative_to(dest).as_posix())
    with zipfile.ZipFile(archive) as z:
        require(z.testzip() is None,'ZIP CRC failure')
        for member in z.namelist():
            require(z.read(member)==(args.output_dir/member).read_bytes(),'ZIP payload differs '+member)
    result={'version':VERSION,'status':'PASS','archive':str(archive),'archive_bytes':archive.stat().st_size,
      'archive_sha256':sha(archive),'payload_hashes':len(files),'zip_entries':len(files)+2,
      'zip_crc':'PASS','zip_payload_comparison':'PASS'}
    (args.output_dir/f'AVOC_v{VERSION}_DELIVERY.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2));return 0

if __name__=='__main__':
    try:raise SystemExit(main())
    except (OSError,ValueError,RuntimeError,KeyError) as e:print(str(e),file=sys.stderr);raise SystemExit(2)
