#!/usr/bin/env python3
"""Create a deterministic source/evidence release, omitting reproducible raster/build scratch."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parent
OUT=ROOT.parent/'Komorebi_Euler_Final_Paper_Traditional_Visual_Lean_2026-10-06.zip'
def selected(p):
 rel=p.relative_to(ROOT);parts=rel.parts
 if '__pycache__' in parts:return False
 if p.suffix in {'.pyc','.aux','.toc','.out','.xdv','.synctex','.fls','.fdb_latexmk'}:return False
 if parts[0]=='preserved':return True
 if p.name=='MANIFEST_SHA256.json':return False
 if 'pdf_preflight' in parts and p.name.startswith('page_') and p.suffix=='.png':return False
 if 'current_renders' in parts:return False
 if 'visual_pages' in parts:return False
 if parts[0]=='sources' and p.suffix in {'.pdf','.log'}:return False
 if 'standalone' in str(rel).lower():return False
 return True
files=sorted(p for p in ROOT.rglob('*') if p.is_file() and selected(p))
manifest={'release':'Euler final strengthened three-part paper','edition':'2026-10-06','scope':'File integrity, not mathematical truth or an authenticity signature','files':[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]}
(ROOT/'MANIFEST_SHA256.json').write_text(json.dumps(manifest,indent=2)+'\n')
files.append(ROOT/'MANIFEST_SHA256.json')
with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:
  name='Komorebi_Euler_Final_Paper_2026-10-06/'+str(p.relative_to(ROOT))
  info=zipfile.ZipInfo(name,(2026,10,6,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=(0o100644<<16)
  z.writestr(info,p.read_bytes())
with zipfile.ZipFile(OUT) as z:
 bad=z.testzip()
 if bad:raise SystemExit('Bad member '+bad)
 if len(z.namelist())!=len(files):raise SystemExit('Member count mismatch')
print(json.dumps({'status':'PASS','archive':str(OUT),'files':len(files),'bytes':OUT.stat().st_size,'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest()},indent=2))
