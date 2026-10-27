#!/usr/bin/env python3
"""Package source and evidence, never runtime caches or font files."""
from pathlib import Path
import os,json,hashlib,zipfile
ROOT=Path(__file__).resolve().parents[1]

def included():
    for base,dirs,files in os.walk(ROOT,followlinks=False):
        dirs[:]=[d for d in dirs if not d.endswith('.egg-info') and d not in {'.lake','__pycache__','render_before','render_after','build'}]
        for name in sorted(files):
            p=Path(base)/name;rel=p.relative_to(ROOT)
            if p.is_symlink() or name in {'MANIFEST.json','SHA256SUMS.txt','verification_pid.json'}:continue
            if p.suffix.lower() in {'.pyc','.olean','.ilean','.ttf','.otf','.woff','.woff2'}:continue
            if 'evidence' in rel.parts and p.suffix in {'.pdf','.aux','.toc','.out','.fls','.fdb_latexmk'}:continue
            yield p

def main():
    files=sorted(included());records=[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
    manifest={'version':'1.0.0rc3','files':records,'scope':'Source, final monograph and evidence. Compiler and dependencies omitted.'}
    (ROOT/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n', encoding="utf-8")
    hashfiles=files+[ROOT/'MANIFEST.json']
    (ROOT/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(ROOT))+'\n' for p in hashfiles), encoding="utf-8")
    dest=ROOT.parent/'Komorebi_Constructive_Repair_v1.0.0-rc3.zip'
    with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in files+[ROOT/'MANIFEST.json',ROOT/'SHA256SUMS.txt']:z.write(p,ROOT.name+'/'+str(p.relative_to(ROOT)))
    with zipfile.ZipFile(dest) as z:
        if z.testzip() is not None:raise RuntimeError('ZIP integrity failure')
    print(json.dumps({'zip':str(dest),'bytes':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'files':len(records)+2},indent=2))
if __name__=='__main__':main()
