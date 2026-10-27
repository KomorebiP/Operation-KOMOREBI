#!/usr/bin/env python3
"""Package audited v0.17 sources, excluding runtime/cache outputs.

The package manifest certifies bytes, not theorem truth. Run the verification
collector first. This tool checks the relevant current source/log hashes again.
"""
from __future__ import annotations
from pathlib import Path
import argparse,hashlib,json,shutil,zipfile
ROOT=Path(__file__).resolve().parents[1]

def sha(data:bytes)->str:return hashlib.sha256(data).hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,default=Path('/mnt/data'));args=ap.parse_args()
    audit=json.loads((ROOT/'AUDIT.json').read_text())
    if audit.get('status')!='PASS' or audit.get('version')!='0.18.0':raise SystemExit('Missing passed v0.17 audit')
    rd=ROOT/'results/v0.18.0'
    for rec in json.loads((rd/'final_local_build_summary.json').read_text()):
        if sha((ROOT/rec['source']).read_bytes())!=rec['source_sha256']:raise SystemExit('Stale source '+rec['source'])
    for name in ['planner_regression']:
        report=json.loads((rd/(name+'.json')).read_text())
        for rel,digest in report['source_hashes'].items():
            if sha((ROOT/rel).read_bytes())!=digest:raise SystemExit('Stale regression '+rel)
    args.output_dir.mkdir(parents=True,exist_ok=True)
    dest=args.output_dir/'AVOC_Formal_v0.18.0'
    if dest.resolve()!=ROOT.resolve():
        if dest.exists():shutil.rmtree(dest)
        shutil.copytree(ROOT,dest,ignore=shutil.ignore_patterns('.lake','.git','__pycache__','*.pyc','*.olean','*.ilean'))
    exclusions={'SHA256SUMS.txt','PACKAGING.json'}
    files=sorted(p for p in dest.rglob('*') if p.is_file() and str(p.relative_to(dest)) not in exclusions and not any(x in p.relative_to(dest).parts for x in ['.lake','.git','__pycache__']) and p.suffix not in ['.pyc','.olean','.ilean'])
    lines=[sha(p.read_bytes())+'  '+p.relative_to(dest).as_posix() for p in files]
    (dest/'SHA256SUMS.txt').write_text('\n'.join(lines)+'\n')
    for line in lines:
        digest,rel=line.split('  ',1)
        assert sha((dest/rel).read_bytes())==digest
    (dest/'PACKAGING.json').write_text(json.dumps(dict(status='PASS',payload_hashes=len(files),
        manifest_scope='All delivered regular files except SHA256SUMS.txt and this self-referential packaging note.',
        excluded='Local build, dependency/runtime caches, compiled Lean binaries and Python bytecode.',
        theorem_audit='AUDIT.json; byte integrity is not proof verification.'),indent=2)+'\n')
    archive=args.output_dir/'AVOC_Formal_v0.18.0.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in files+[dest/'SHA256SUMS.txt',dest/'PACKAGING.json']:
            z.write(p, 'AVOC_Formal_v0.18.0/'+p.relative_to(dest).as_posix())
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for n in z.namelist():assert z.read(n)==(args.output_dir/n).read_bytes(),n
    result=dict(status='PASS',archive=str(archive),archive_bytes=archive.stat().st_size,
        archive_sha256=sha(archive.read_bytes()),payload_hashes=len(files),zip_crc='PASS',zip_payload_comparison='PASS')
    (args.output_dir/'AVOC_v0.18.0_DELIVERY.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
