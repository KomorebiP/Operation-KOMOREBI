#!/usr/bin/env python3
"""Package the accepted release only after proof and executable evidence pass."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, io, json, os, shutil, subprocess, sys, zipfile
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT.parent/(ROOT.name+'.zip')
FORBIDDEN={'.ttf','.otf','.woff','.woff2','.ttc','.dfont'}
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def main():
    for fn in ['results_v07/LEAN_AUDIT.json','results_v07/PYTHON_AUDIT.json']:
        assert json.loads((ROOT/fn).read_text())['status']=='PASS',fn
    for fn in ['LEAN_MANIFEST_v07.json','COMPUTATION_MANIFEST_v07.json']:
        subprocess.run([sys.executable,str(ROOT/'tools/validate_manifest.py'),str(ROOT/fn),'--root',str(ROOT)],check=True)
    # No original project sources are removed. These are local Python run caches only.
    for p in list(ROOT.rglob('__pycache__')):
        if p.is_dir():shutil.rmtree(p)
    assert not any(p.is_file() and p.suffix.lower() in FORBIDDEN for p in ROOT.rglob('*'))
    seen=set(); archives=0; nested_entries=0
    def scan(z):
        nonlocal archives,nested_entries
        archives+=1
        for i in z.infolist():
            if i.is_dir():continue
            nested_entries+=1
            assert Path(i.filename).suffix.lower() not in FORBIDDEN,i.filename
            if i.filename.lower().endswith('.zip'):
                b=z.read(i);h=hashlib.sha256(b).hexdigest()
                if h not in seen:
                    seen.add(h)
                    with zipfile.ZipFile(io.BytesIO(b)) as nz:scan(nz)
    for p in ROOT.rglob('*.zip'):
        h=sha(p)
        if h not in seen:
            seen.add(h)
            with zipfile.ZipFile(p) as z:scan(z)
    files=[]
    for p in sorted(ROOT.rglob('*')):
        if p.is_file() and p!=ROOT/'FILE_MANIFEST.json':
            assert not p.is_symlink()
            files.append({'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
    (ROOT/'FILE_MANIFEST.json').write_text(json.dumps({'schema':'komorebi-file-manifest','version':'0.7','scope':'All release payloads except this manifest; history is immutable. Check before rerunning audits.','files':files},indent=2)+'\n')
    with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
        for p in sorted(ROOT.rglob('*')):
            if p.is_file():z.write(p,ROOT.name+'/'+p.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(OUT) as z:
        assert z.testzip() is None
        for f in files:
            b=z.read(ROOT.name+'/'+f['path'])
            assert len(b)==f['bytes'] and hashlib.sha256(b).hexdigest()==f['sha256'],f['path']
        count=len(z.namelist())
    digest=sha(OUT)
    OUT.with_suffix('.zip.sha256').write_text(digest+'  '+OUT.name+'\n')
    report={'status':'PASS','checked_at':datetime.now(timezone.utc).isoformat(),'archive':str(OUT),'bytes':OUT.stat().st_size,'entries':count,'sha256':digest,'all_payloads_match':True,'zip_crc_passed':True,'font_scan_unique_archives':archives,'font_scan_nested_entries':nested_entries,'font_files':0,'parent_preserved':json.loads((ROOT/'v07_evidence/PARENT_PRESERVATION.json').read_text())['count'],'scope':'Preservation of bytes and completed proof/executable records. Fresh-extraction replay is recorded separately.'}
    (ROOT.parent/(ROOT.name+'_PACKAGING_REPORT.json')).write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
