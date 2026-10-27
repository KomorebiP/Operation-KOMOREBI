#!/usr/bin/env python3
"""Package verified cumulative sources/evidence; exclude runtime, caches and self-hashed manifest."""
from __future__ import annotations
import argparse,hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SKIP={'.lake','.git','__pycache__','.pytest_cache'}
SUFFIX={'.pyc','.pyo','.olean','.ilean'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def included():
    for p in sorted(ROOT.rglob('*')):
        rel=p.relative_to(ROOT)
        if any(x in SKIP for x in rel.parts) or p.suffix in SUFFIX:continue
        if p.is_symlink():raise RuntimeError('Unexpected packaged symlink: '+str(rel))
        if p.is_file() and rel.as_posix()!='SHA256SUMS.txt':yield p

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    out=a.output.resolve()
    if out==ROOT or ROOT in out.parents:raise ValueError('Archive must be outside source tree')
    audit=json.loads((ROOT/'AUDIT.json').read_text())
    if not audit.get('passed') or audit.get('version')!='0.27.0':raise RuntimeError('Current evidence collector must pass before packaging')
    payload=list(included())
    manifest={p.relative_to(ROOT).as_posix():sha(p) for p in payload}
    mf=ROOT/'SHA256SUMS.txt';mf.write_text(''.join(f'{h}  {n}\n' for n,h in manifest.items()))
    out.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in payload+[mf]:z.write(p,ROOT.name+'/'+p.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(out) as z:
        if z.testzip() is not None:raise RuntimeError('ZIP CRC failure')
        expected={ROOT.name+'/'+name for name in manifest}|{ROOT.name+'/SHA256SUMS.txt'}
        if set(z.namelist())!=expected:raise RuntimeError('ZIP payload set mismatch')
        for name,digest in manifest.items():
            if sha(ROOT/name)!=digest:raise RuntimeError('Source changed during packaging: '+name)
            if hashlib.sha256(z.read(ROOT.name+'/'+name)).hexdigest()!=digest:raise RuntimeError('ZIP payload mismatch: '+name)
    digest=sha(out)
    out.with_suffix(out.suffix+'.sha256').write_text(digest+'  '+out.name+'\n')
    verification={'passed':True,'version':'0.27.0','archive':out.name,'archive_sha256':digest,
      'archive_bytes':out.stat().st_size,'hashed_payload_files':len(manifest),'zip_members':len(manifest)+1,
      'zip_crc':'PASS','source_and_archive_payload_hashes':'ALL_MATCH',
      'excluded':'Runtime, .lake/.git, Python cache, compiled Lean outputs; manifest excludes itself.',
      'scope':'Packaging integrity only; proof and runtime evidence are in versioned results and AUDIT.json.'}
    dest=out.with_name(out.stem+'_Packaging_Verification.json');dest.write_text(json.dumps(verification,indent=2)+'\n')
    print(json.dumps(verification,indent=2))
if __name__=='__main__':main()
