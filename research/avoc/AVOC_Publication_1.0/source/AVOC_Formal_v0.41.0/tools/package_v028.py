#!/usr/bin/env python3
"""Create a cumulative source/evidence ZIP, excluding runtime and compiled outputs."""
from pathlib import Path
import argparse,hashlib,json,zipfile
root=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('--output',type=Path,default=root.parent/'AVOC_Formal_v0.28.0.zip');ns=a.parse_args()
skip={'.lake','.git','__pycache__'}
files=[p for p in sorted(root.rglob('*')) if p.is_file() and not any(x in skip for x in p.relative_to(root).parts)
       and p.suffix not in {'.pyc','.olean','.ilean'} and p!=root/'SHA256SUMS.txt']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(root/'SHA256SUMS.txt').write_text(''.join(f'{sha(p)}  {p.relative_to(root).as_posix()}\n' for p in files))
files.append(root/'SHA256SUMS.txt')
with zipfile.ZipFile(ns.output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in files:z.write(p,root.name+'/'+p.relative_to(root).as_posix())
with zipfile.ZipFile(ns.output) as z:
    assert z.testzip() is None
    assert set(z.namelist())=={root.name+'/'+p.relative_to(root).as_posix() for p in files}
    for p in files:assert hashlib.sha256(z.read(root.name+'/'+p.relative_to(root).as_posix())).hexdigest()==sha(p)
h=sha(ns.output)
Path(str(ns.output)+'.sha256').write_text(h+'  '+ns.output.name+'\n')
summary=dict(archive=str(ns.output),bytes=ns.output.stat().st_size,sha256=h,payload_files=len(files),manifest_entries=len(files)-1,zip_integrity=True,exact_payload_comparison=True)
(root.parent/'AVOC_v0.28.0_Packaging_Verification.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
