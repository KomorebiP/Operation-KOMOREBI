#!/usr/bin/env python3
"""Check this research edition's inventory and original ZIPs; no model runs.

Hashes detect changed bytes relative to the supplied manifest. They do not
independently authenticate an author, establish source truth, or certify any
scientific hypothesis. Nested archives are checked for integrity and font files.
"""
from __future__ import annotations
import argparse,hashlib,io,json,sys,zipfile
from pathlib import Path,PurePosixPath
ROOT=Path(__file__).resolve().parent
FONT_SUFFIXES={'.ttf','.otf','.woff','.woff2','.eot','.pfb','.pfa','.ttc','.otc','.dfont','.afm','.pfm','.tfm','.vf','.fon','.fnt','.otb','.bdf','.pcf','.fd'}
IGNORED_PARTS={'__pycache__','.pytest_cache','.git'}

def sha(path:Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for data in iter(lambda:f.read(1024*1024),b''):h.update(data)
    return h.hexdigest()

def archives(data:bytes,label:str,errors:list[str],depth:int=0)->int:
    if depth>12:errors.append('archive_depth:'+label);return 0
    count=1
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            names=set()
            for entry in z.infolist():
                path=PurePosixPath(entry.filename)
                if path.is_absolute() or '..' in path.parts or '\\' in entry.filename:
                    errors.append('archive_path:'+label+'!'+entry.filename)
                if entry.filename in names:errors.append('archive_duplicate:'+label+'!'+entry.filename)
                names.add(entry.filename)
                if entry.is_dir():continue
                if path.suffix.lower() in FONT_SUFFIXES:errors.append('font_file:'+label+'!'+entry.filename)
                content=z.read(entry)  # Reading the complete member validates its CRC.
                if path.suffix.lower() in {'.zip','.whl'}:count+=archives(content,label+'!'+entry.filename,errors,depth+1)
    except (OSError,ValueError,zipfile.BadZipFile,RuntimeError) as exc:errors.append('archive:'+label+':'+str(exc))
    return count

def verify(deep:bool=True)->dict:
    errors=[];manifest=json.loads((ROOT/'MANIFEST.json').read_text(encoding='utf-8'));rows=manifest['files'];seen=set()
    for row in rows:
        name=row['path'];p=PurePosixPath(name)
        if p.is_absolute() or '..' in p.parts or '\\' in name:errors.append('unsafe_path:'+name);continue
        if name in seen:errors.append('duplicate:'+name)
        seen.add(name);file=ROOT.joinpath(*p.parts)
        if file.is_symlink():errors.append('symlink:'+name);continue
        if not file.is_file():errors.append('missing:'+name);continue
        if file.stat().st_size!=row['bytes'] or sha(file)!=row['sha256']:errors.append('modified:'+name)
        if file.suffix.lower() in FONT_SUFFIXES:errors.append('font_file:'+name)
    actual={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and not any(x in IGNORED_PARTS for x in p.relative_to(ROOT).parts) and p.relative_to(ROOT).as_posix() not in {'MANIFEST.json','MANIFEST.sha256'}}
    for extra in sorted(actual-seen):errors.append('unlisted:'+extra)
    expected=(ROOT/'MANIFEST.sha256').read_text().split()[0]
    if sha(ROOT/'MANIFEST.json')!=expected:errors.append('manifest_digest')
    ledger=json.loads((ROOT/'SOURCE_LEDGER.json').read_text())['source_archives'];nested=0
    for row in ledger:
        file=ROOT/row['path']
        if not file.is_file() or sha(file)!=row['sha256']:errors.append('source_archive:'+row['id']);continue
        if deep:nested+=archives(file.read_bytes(),row['id'],errors)
        for copy in row.get('copied_evidence',[]):
            p=ROOT/copy['copy_path']
            if not p.is_file() or sha(p)!=copy['sha256']:errors.append('evidence_copy:'+copy['copy_path'])
    return {'schema':'komorebi.osl-neuralese.release-verification.v1','all_checks_pass':not errors,
            'file_count':len(rows),'source_archives':len(ledger),'nested_archives_checked':nested,
            'deep_archive_check':deep,'errors':errors,
            'scope':'Byte inventory, original source bindings, safe archive paths and CRC; no neural evaluation or universal semantics proof'}

def main()->int:
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--fast',action='store_true',help='Skip recursive ZIP inspection; still check all file and source hashes');args=parser.parse_args()
    try:report=verify(not args.fast)
    except (OSError,ValueError,KeyError,TypeError) as exc:
        print(json.dumps({'all_checks_pass':False,'error':str(exc)},indent=2));return 2
    print(json.dumps(report,indent=2));return 0 if report['all_checks_pass'] else 1
if __name__=='__main__':raise SystemExit(main())
