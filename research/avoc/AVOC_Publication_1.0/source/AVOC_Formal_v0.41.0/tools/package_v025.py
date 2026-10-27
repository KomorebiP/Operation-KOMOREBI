#!/usr/bin/env python3
"""Package current source/evidence, excluding binaries, caches and self-hashed reports."""
from pathlib import Path
import argparse,hashlib,json,os,zipfile
root=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
output=a.output.resolve()
if output.suffix!='.zip' or output.is_relative_to(root):raise SystemExit('use an external .zip output path')
skip={'.lake','.git','__pycache__'}
files=sorted(p for p in root.rglob('*') if p.is_file() and not any(x in skip for x in p.relative_to(root).parts)
 and p.suffix not in {'.pyc','.olean','.ilean','.ttf','.otf','.woff','.woff2'} and p.name!='SHA256SUMS.txt')
lines=[sha(p)+'  '+str(p.relative_to(root)) for p in files]
(root/'SHA256SUMS.txt').write_text('\n'.join(lines)+'\n')
files.append(root/'SHA256SUMS.txt')
temporary=output.with_name(output.name+'.building')
with zipfile.ZipFile(temporary,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for f in files:z.write(f,str(Path(root.name)/f.relative_to(root)))
with zipfile.ZipFile(temporary) as z:
 if z.testzip() is not None:raise SystemExit('ZIP CRC failure')
 for f in files:
  if z.read(str(Path(root.name)/f.relative_to(root)))!=f.read_bytes():raise SystemExit('payload mismatch: '+str(f))
os.replace(temporary,output)
digest=sha(output)
output.with_name(output.name+'.sha256').write_text(digest+'  '+output.name+'\n')
report=dict(passed=True,payload_files=len(files)-1,zip_entries=len(files),bytes=output.stat().st_size,sha256=digest)
output.with_name(output.name+'.packaging.json').write_text(json.dumps(report,indent=2)+'\n')
print(report)
