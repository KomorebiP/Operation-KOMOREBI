"""Package source and evidence, excluding generated runtime/cache files."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def payloads():
    for p in sorted(ROOT.rglob('*')):
        rel=p.relative_to(ROOT)
        if not p.is_file() or p.is_symlink():continue
        if any(x in {'.lake','.git','__pycache__'} for x in rel.parts):continue
        if p.suffix in {'.pyc','.olean','.ilean','.ttf','.otf','.woff','.woff2'}:continue
        if str(rel) in {'SHA256SUMS.txt','PACKAGING.json'}:continue
        yield p
files=list(payloads())
manifest=''.join(sha(p)+'  '+str(p.relative_to(ROOT))+'\n' for p in files)
(ROOT/'SHA256SUMS.txt').write_text(manifest)
out=ROOT.parent/'AVOC_Formal_v0.21.0.zip'
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=7) as z:
    for p in files+[ROOT/'SHA256SUMS.txt']:
        z.write(p,'AVOC_Formal_v0.21.0/'+str(p.relative_to(ROOT)))
with zipfile.ZipFile(out) as z:
    assert z.testzip() is None
    for p in files:
        assert z.read('AVOC_Formal_v0.21.0/'+str(p.relative_to(ROOT)))==p.read_bytes()
report={'archive':str(out),'sha256':sha(out),'bytes':out.stat().st_size,'payload_hashes':len(files),
 'crc_pass':True,'byte_comparison_pass':True,'manifest_self_excluded':True,'runtime_excluded':True}
(ROOT/'PACKAGING.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
