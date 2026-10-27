#!/usr/bin/env python3
"""Verify the recovered B01 archive without extracting or modifying it.

Checks its original per-file manifest, CRC, safe paths, and standalone fonts
including recursively nested ZIP archives. Embedded PDF fonts are not standalone
font files. This is file integrity, not proof compilation.
"""
from __future__ import annotations
import argparse,hashlib,io,json,zipfile
from pathlib import Path,PurePosixPath
FONT_EXT={'.ttf','.otf','.ttc','.woff','.woff2','.pfa','.pfb','.afm','.bdf','.pcf','.fon','.fnt'}
def digest(p:Path)->str:
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def inspect_fonts(z:zipfile.ZipFile,label:str,result:dict,depth:int=0)->None:
 if depth>20:raise ValueError('Archive nesting exceeds20 levels')
 result['zip_archives_inspected']+=1
 for info in z.infolist():
  if info.is_dir():continue
  if PurePosixPath(info.filename).suffix.lower() in FONT_EXT:result['standalone_fonts'].append(label+'!'+info.filename)
  if info.filename.lower().endswith('.zip'):
   try:
    with zipfile.ZipFile(io.BytesIO(z.read(info))) as child:inspect_fonts(child,label+'!'+info.filename,result,depth+1)
   except (ValueError,zipfile.BadZipFile,RuntimeError) as e:result['nested_errors'].append({'file':label+'!'+info.filename,'error':str(e)})
def main()->int:
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('archive',type=Path);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
 report={'archive':a.archive.name,'sha256':digest(a.archive),'manifest_entries':0,'errors':[],'font_check':{'zip_archives_inspected':0,'standalone_fonts':[],'nested_errors':[]}}
 with zipfile.ZipFile(a.archive) as z:
  report['crc_first_bad_file']=z.testzip();names=z.namelist()
  manifests=[n for n in names if n.endswith('MANIFEST_SHA256.json')];m=min(manifests,key=len);prefix=m.rsplit('/',1)[0]+'/'
  data=json.loads(z.read(m));entries=data['files'];entries=entries if isinstance(entries,list) else [{'path':k,'sha256':v} for k,v in entries.items()]
  report['manifest_entries']=len(entries)
  for e in entries:
   path=e['path'];full=prefix+path
   if '..' in PurePosixPath(path).parts or PurePosixPath(path).is_absolute():report['errors'].append({'unsafe':path});continue
   try:
    raw=z.read(full)
    if hashlib.sha256(raw).hexdigest()!=e['sha256']:report['errors'].append({'hash_mismatch':path})
    if 'bytes' in e and len(raw)!=e['bytes']:report['errors'].append({'size_mismatch':path})
   except KeyError:report['errors'].append({'missing':path})
  expected={prefix+e['path'] for e in entries}|{m};report['extra_files']=sorted({n for n in names if not n.endswith('/')}-expected)
  inspect_fonts(z,a.archive.name,report['font_check'])
 report['status']='passed' if not (report['errors'] or report['extra_files'] or report['crc_first_bad_file'] or report['font_check']['standalone_fonts'] or report['font_check']['nested_errors']) else 'failed'
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));return int(report['status']!='passed')
if __name__=='__main__':raise SystemExit(main())
