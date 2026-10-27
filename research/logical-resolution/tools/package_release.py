"""Build a deterministic, source-only distribution and check all payload bytes."""
from __future__ import annotations
import argparse, hashlib, io, json, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXCLUDED_DIRS={'build','__pycache__','.git','.lake'}
FONT_SUFFIXES={'.ttf','.otf','.ttc','.woff','.woff2'}

def sha(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()

def scan_zip(data:bytes,label:str,depth:int=0)->int:
    if depth>24:
        raise RuntimeError('Unreviewed archive depth: '+label)
    count=0
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        if z.testzip() is not None: raise RuntimeError('CRC failure: '+label)
        for i in z.infolist():
            if i.is_dir():continue
            count+=1
            suffix=Path(i.filename).suffix.lower()
            if suffix in FONT_SUFFIXES:raise RuntimeError('Font payload refused: '+label+'::'+i.filename)
            if suffix=='.zip':count+=scan_zip(z.read(i),label+'::'+i.filename,depth+1)
    return count

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=ROOT.parent/(ROOT.name+'.zip'));a=ap.parse_args()
    files=sorted(p for p in ROOT.rglob('*') if p.is_file()
                 and not any(x in EXCLUDED_DIRS for x in p.relative_to(ROOT).parts)
                 and p.name!='FILE_MANIFEST.json' and p.suffix not in {'.pyc','.olean','.ilean','.o'})
    records=[];nested=0
    for p in files:
        data=p.read_bytes()
        if p.suffix.lower() in FONT_SUFFIXES: raise RuntimeError('Font refused: '+str(p))
        if p.suffix.lower()=='.zip': nested+=scan_zip(data,p.name)
        records.append({'path':str(p.relative_to(ROOT)),'bytes':len(data),'sha256':sha(data)})
    manifest={'schema':'komorebi-distribution-integrity-v1','files':records}
    (ROOT/'FILE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
    files.append(ROOT/'FILE_MANIFEST.json')
    output=a.output.resolve();output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(files):
            info=zipfile.ZipInfo(ROOT.name+'/'+str(p.relative_to(ROOT)),date_time=(2026,9,21,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
            z.writestr(info,p.read_bytes())
    with zipfile.ZipFile(output) as z:
        bad=z.testzip()
        if bad:raise RuntimeError('Final CRC error '+bad)
        for rec in records:
            data=z.read(ROOT.name+'/'+rec['path'])
            if len(data)!=rec['bytes'] or sha(data)!=rec['sha256']:raise RuntimeError('Changed archive payload '+rec['path'])
    digest=sha(output.read_bytes());Path(str(output)+'.sha256').write_text(digest+'  '+output.name+'\n')
    print(json.dumps({'status':'PASS','archive':str(output),'entries':len(files),'bytes':output.stat().st_size,
        'sha256':digest,'payload_files':len(records),'nested_entries_scanned':nested,'fonts_found':0},indent=2))
if __name__=='__main__':main()
