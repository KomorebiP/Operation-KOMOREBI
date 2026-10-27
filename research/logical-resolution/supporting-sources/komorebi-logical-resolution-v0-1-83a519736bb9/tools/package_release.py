"""Create a source/evidence ZIP. Toolchains, build outputs, and fonts are excluded."""
import hashlib, io, json, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FONT_EXT={'.ttf','.otf','.woff','.woff2','.ttc'}
def sha(b):return hashlib.sha256(b).hexdigest()
def scan_archive(data,level=0):
    if level>20:raise RuntimeError('Archive nesting exceeds scan bound')
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for info in z.infolist():
            if Path(info.filename).suffix.lower() in FONT_EXT:
                raise RuntimeError('Font payload: '+info.filename)
            if info.filename.lower().endswith('.zip'):
                scan_archive(z.read(info),level+1)
files=[]
for p in sorted(ROOT.rglob('*')):
    if not p.is_file():continue
    rel=p.relative_to(ROOT)
    if rel.parts[0]=='build' or '__pycache__' in rel.parts or rel.name=='FILE_MANIFEST.json':continue
    if p.suffix.lower() in FONT_EXT:raise RuntimeError('Font file in payload')
    if p.suffix=='.zip':scan_archive(p.read_bytes())
    files.append(p)
manifest={'schema':'komorebi-payload-sha256-v1','scope':'Logical Resolution v0.1 source and evidence',
          'files':[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in files]}
(ROOT/'FILE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
files.append(ROOT/'FILE_MANIFEST.json')
out=ROOT.parent/(ROOT.name+'.zip')
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in files:
        info=zipfile.ZipInfo(str(Path(ROOT.name)/p.relative_to(ROOT)),(2026,9,21,0,0,0))
        info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
        z.writestr(info,p.read_bytes())
with zipfile.ZipFile(out) as z:
    if z.testzip() is not None:raise RuntimeError('CRC failure')
    for p in files:
        if z.read(str(Path(ROOT.name)/p.relative_to(ROOT)))!=p.read_bytes():raise RuntimeError('Payload mismatch')
checksum=sha(out.read_bytes())
out.with_suffix(out.suffix+'.sha256').write_text(checksum+'  '+out.name+'\n')
report={'status':'PASS','archive':str(out),'sha256':checksum,'bytes':out.stat().st_size,
        'entries':len(files),'payload_files':len(manifest['files']),'crc_passed':True,
        'byte_comparisons_passed':True,'recursive_font_scan_passed':True,
        'excluded':['Lean runtime','build outputs','Python bytecode']}
(ROOT.parent/(ROOT.name+'_PACKAGING.json')).write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
