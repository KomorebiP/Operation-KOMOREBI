#!/usr/bin/env python3
"""Freeze a checksum inventory and ZIP of this selected compilation."""
from __future__ import annotations
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    files={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name!='SHA256SUMS.json' and '__pycache__' not in p.parts}
    (ROOT/'SHA256SUMS.json').write_text(json.dumps({'scope':'Frozen selected collection; checksum equality does not establish truth or origin.','files':files},indent=2),encoding='utf-8')
    out=ROOT.parent/'Komorebi_Machine_Theory_Compendium_v1.0.0_Collection.zip'
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(ROOT.rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts:z.write(p,Path(ROOT.name)/p.relative_to(ROOT))
    with zipfile.ZipFile(out) as z:
        assert z.testzip() is None
        for name,h in files.items():assert hashlib.sha256(z.read(ROOT.name+'/'+name)).hexdigest()==h,name
    print(json.dumps({'zip':str(out),'bytes':out.stat().st_size,'payload_files':len(files),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'CRC_and_all_payload_hashes':'PASS'},indent=2))
if __name__=='__main__':main()
