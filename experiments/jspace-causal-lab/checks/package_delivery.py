"""Deterministic source ZIP. The destination must be outside the source directory."""
from pathlib import Path
import argparse,hashlib,zipfile,json
ROOT=Path(__file__).resolve().parents[1]
def build(destination:Path):
 destination=destination.resolve()
 if destination.is_relative_to(ROOT):raise ValueError('Place the archive outside the source tree')
 manifest=json.loads((ROOT/'MANIFEST.json').read_text());names=sorted([*manifest['files'],'MANIFEST.json'])
 with zipfile.ZipFile(destination,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for name in names:
   p=ROOT/name
   if Path(name).is_absolute() or '..' in Path(name).parts:raise ValueError('Unsafe member path')
   if name!='MANIFEST.json' and hashlib.sha256(p.read_bytes()).hexdigest()!=manifest['files'][name]:raise ValueError('Changed source: '+name)
   info=zipfile.ZipInfo(ROOT.name+'/'+name,date_time=(2026,9,27,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
   z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
 print(json.dumps({'archive':str(destination),'bytes':destination.stat().st_size,'sha256':hashlib.sha256(destination.read_bytes()).hexdigest()}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('destination',type=Path);build(p.parse_args().destination)
