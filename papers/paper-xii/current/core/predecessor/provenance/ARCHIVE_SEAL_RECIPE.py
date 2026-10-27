#!/usr/bin/env python3
"""Seal the reviewed Paper XII release and verify the archive against its manifest."""
from pathlib import Path
import hashlib, json, shutil, subprocess, sys, zipfile

W = Path(__file__).resolve().parent
R = W.parent/'output/Komorebi_Paper_XII_Final_Edition_2026-10-06'
Z = R.parent/'Komorebi_Paper_XII_Final_Traditional_Visual_Lean_2026-10-06.zip'
shutil.copy2(W/'seal_release.py',R/'provenance/ARCHIVE_SEAL_RECIPE.py')
files = []
for p in sorted(R.rglob('*')):
    if p.is_file() and p != R/'MANIFEST_SHA256.json':
        files.append({'path':str(p.relative_to(R)),'bytes':p.stat().st_size,
                      'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(R/'MANIFEST_SHA256.json').write_text(json.dumps({'algorithm':'SHA256','files':files},indent=2)+'\n')
proc = subprocess.run([sys.executable,str(R/'scripts/verify_integrity.py')],capture_output=True,text=True)
if proc.returncode:
    raise SystemExit(proc.stdout+proc.stderr)
with zipfile.ZipFile(Z,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(R.rglob('*')):
        if p.is_file():
            info=zipfile.ZipInfo(str(Path(R.name)/p.relative_to(R)),date_time=(2026,10,6,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=(0o644&0xFFFF)<<16
            z.writestr(info,p.read_bytes())
with zipfile.ZipFile(Z) as z:
    bad=z.testzip()
    assert bad is None,bad
    names=z.namelist()
    assert len(names)==len(files)+1
    for row in files:
        payload=z.read(str(Path(R.name)/row['path']))
        assert len(payload)==row['bytes'] and hashlib.sha256(payload).hexdigest()==row['sha256'],row['path']
digest=hashlib.sha256(Z.read_bytes()).hexdigest()
Z.with_suffix('.zip.sha256').write_text(digest+'  '+Z.name+'\n')
report={'status':'PASS','archive':str(Z),'bytes':Z.stat().st_size,'sha256':digest,
        'archive_members':len(names),'manifest_files':len(files),'crc':'PASS','every_payload_hash':'PASS',
        'scope':'Sealed package consistency and payload preservation; not a mathematical proof or new Lean certificate.'}
(W/'verification/release/ARCHIVE_SEAL.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
