"""Build two verifiable handoffs without modifying source archives.
The full archive preserves original ZIP streams byte-for-byte.
"""
from pathlib import Path
import zipfile,hashlib,json
r=Path(__file__).resolve().parents[1]
out=r.parent
source=out/'komorebi_sources'
compact=out/'Machine_Native_Reasoning_Working_Source.zip'
full=out/'Machine_Native_Reasoning_Full_Research_Archive.zip'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

exclude_dirs={'_build','pdf_renders','__pycache__'}
local=[]
for p in sorted(r.rglob('*')):
 if not p.is_file():continue
 if any(x in exclude_dirs for x in p.relative_to(r).parts):continue
 if p.name.endswith(('.pyc','.aux','.log')) and p.name not in ('core83_run.log','core_exact_replay.log','admission_exact_replay.log','core_baseline_integrity.log'):continue
 if p.name=='contact_sheet.png':continue
 local.append(p)
with zipfile.ZipFile(compact,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=7,allowZip64=True) as z:
 for p in local:
  z.write(p,arcname='Machine_Native_Reasoning_Working_Edition/'+p.relative_to(r).as_posix())

external_names=[
 'Komorebi_Machine_Theory_Lean_Block15_v0.15.0_complete.zip',
 'Komorebi_Machine_Theory_Reviewed_Core_v0.2_complete.zip',
 'Komorebi_Machine_Theory_Compendium_v1.0.0_Collection.zip',
 'Proof_Path_Theory_Monograph_1.8.0.zip',
 'Machine_Societies_v1.0.0_complete.zip',
 'Komorebi_Space_Publication_v1.15.0.zip',
 'Komorebi_Space_Monograph_v1.15.0.pdf',
 'Realization_Calculus_Large_Signal_Model.pdf'
]
external=[source/name for name in external_names]
assert all(p.exists() for p in external)

info='''# Machine-Native Reasoning — Full Source Snapshot

This source-preservation archive contains the new working manuscript and its verifier and eight unchanged prior source packages/reading editions. The old 24-document compendium contains a selected research reader and related source materials; its existence does not mean every historical source branch is editable or fully formalized. The saved Block 15 Lean ZIP contains historical compiler evidence and all 1,442 manifest-verified files; no new Lean compiler run was performed for the working edition.

Unchanged ZIPs are stored as ZIP members without recompression and without editing their internal bytes. They can be extracted individually. The newest Large Signal Model reading PDF is included, but its separate final editable-source-package save remains unverified: a PDF is not a replacement for that missing source archive. The newer Komorebi Space publication ZIP is included alongside its reading PDF.

The short `Machine_Native_Reasoning_Working_Source.zip` contains the complete editable new manuscript, selected anchored source records, Python exact checks, and the recorded execution results. The final 30-chapter volume remains unfinished. See `PROGRESS_LEDGER.md` in that ZIP for scope and next work.

No environment-local pinned Lean binaries, proprietary model weights, font binaries, or third-party runtime installations are distributed. Hashes and claims are listed separately in `Machine_Native_Reasoning_Delivery_Manifest.json`.
'''
with zipfile.ZipFile(full,'w',compression=zipfile.ZIP_STORED,allowZip64=True) as z:
 z.writestr('START_HERE.md',info)
 z.write(compact,arcname='Publication/Machine_Native_Reasoning_Working_Source.zip')
 z.write(out/'Machine_Native_Reasoning_Working_Edition.pdf',arcname='Publication/Machine_Native_Reasoning_Working_Edition.pdf')
 for p in external:z.write(p,arcname='Original_Research_Sources/'+p.name)

manifest={'status':'CREATED; DELIVERY VERIFICATION FOLLOWS','files':{},'contents':[],'assurance':'archive integrity, not mathematical truth or new Lean verification'}
for p in [out/'Machine_Native_Reasoning_Working_Edition.pdf',compact,full]:
 manifest['files'][p.name]={'bytes':p.stat().st_size,'sha256':sha(p)}
for p in external:manifest['contents'].append({'name':p.name,'bytes':p.stat().st_size,'sha256':sha(p)})
mp=out/'Machine_Native_Reasoning_Delivery_Manifest.json'
mp.write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'compact':manifest['files'][compact.name],'full':manifest['files'][full.name],'contents':len(external)},indent=2))
