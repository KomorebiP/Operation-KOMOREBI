"""Freeze canonical release archives and an initially pending delivery receipt."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import shutil
import zipfile

ROOT=Path(__file__).resolve().parents[1]
PUB=ROOT/'publication'
TECH=ROOT/'technical_record'
OUT=ROOT.parent/'publication_v115_output'
OUT.mkdir(exist_ok=True)
SKIP={'.lake','.git','__pycache__'}
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def files(root):
    for base,dirs,names in os.walk(root):
        dirs[:]=sorted(d for d in dirs if d not in SKIP and not (Path(base)/d).is_symlink())
        for n in sorted(names):
            p=Path(base)/n
            if p.is_symlink():raise ValueError(f'Unexpected symlink: {p}')
            if not n.endswith('.pyc'):yield p
def copy(src,dst):dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
def archive(root,name):
    manifest=root/'SHA256SUMS'
    paths=[p for p in files(root) if p!=manifest]
    manifest.write_text(''.join(f'{sha(p)}  {p.relative_to(root)}\n' for p in paths))
    dst=OUT/(name+'.zip')
    assert not dst.exists(),dst
    with zipfile.ZipFile(dst,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in files(root):z.write(p,name+'/'+str(p.relative_to(root)))
    with zipfile.ZipFile(dst) as z:
        assert z.testzip() is None
        names=z.namelist();assert len(names)==len(set(names))==len(paths)+1
        assert all(not n.startswith('/') and '..' not in Path(n).parts and not set(Path(n).parts)&SKIP for n in names)
        for line in z.read(name+'/SHA256SUMS').decode().splitlines():
            digest,rel=line.split('  ',1)
            assert hashlib.sha256(z.read(name+'/'+rel)).hexdigest()==digest,rel
    return {'file':dst.name,'bytes':dst.stat().st_size,'sha256':sha(dst),'zip_crc_verified':True,'manifest_entries_verified':len(paths),'duplicate_paths':0,'unsafe_paths':0}

edition=json.loads((PUB/'verification/EDITION_VERIFICATION.json').read_text())
audit=json.loads((ROOT/'reviews/final_metadata_audit.json').read_text())
assert audit['status']=='PASS'
for rel,digest in edition['source_identity'].items():assert sha(PUB/rel)==digest,rel
for rel,digest in edition['current_reviews'].items():assert sha(PUB/'verification'/rel)==digest,rel
for b in edition['books'].values():
    assert sha(PUB/b['file'])==b['sha256']
    copy(PUB/b['file'],OUT/Path(b['file']).name)
copy(ROOT/'reviews/final_metadata_audit.json',PUB/'verification/FINAL_METADATA_AUDIT.json')
copy(ROOT/'reviews/final_metadata_audit.md',PUB/'verification/FINAL_METADATA_AUDIT.md')
public=archive(PUB,'Komorebi_Space_Publication_v1.15.0')

assert not TECH.exists()
TECH.mkdir()
parent=ROOT.parent/'publication_v114_output/Komorebi_Space_Technical_Record_v1.14.0.zip'
assert sha(parent)=='6801ddfd3dbf60fe24fe3e882c46ac2d719be8f17d432bd7643a44c9cf384193'
copy(parent,TECH/'history'/parent.name)
copy(OUT/public['file'],TECH/'publication'/public['file'])
for folder in ['records','reviews','logs','drafts','scripts']:
    for p in files(ROOT/folder):copy(p,TECH/'current'/folder/p.relative_to(ROOT/folder))
for p in files(ROOT/'runs'):
    rel=p.relative_to(ROOT/'runs')
    if 'build' not in rel.parts:copy(p,TECH/'current/runs'/rel)
for p in files(ROOT/'build'):
    rel=p.relative_to(ROOT/'build')
    # All book attempts and text/check records; final rendered images are reproducible.
    if p.suffix!='.png':copy(p,TECH/'current/build'/rel)
for name in ['lean_env.sh','proc_self_exe_compat.c']:
    copy(ROOT.parent/'komorebi_diagonal_formalization/scripts'/name,TECH/'host_environment'/name)
copy(ROOT.parent/'.lean_runtime/proc_self_exe_compat.so',TECH/'host_environment/proc_self_exe_compat.so')
(TECH/'README.md').write_text('''# Komorebi Space technical record, publication edition 1.15.0

The canonical publication ZIP is in `publication/`. The complete, byte-preserved
v1.14.0 technical record is in `history/`; it retains the earlier evidence chain.
`current/` contains this edition's source snapshots, proof attempts and compiler
logs, independent reviews, complete fresh replay receipt and declaration
inventory, compiler/cache identity inventory, book-build attempts, and editorial
records. Failed attempts are retained with their causes. Static checks and
development-cache builds are not represented as fresh integrated verification.

Fresh project object bytes are hashed in the receipt but omitted from this
archive, as are external compiler/dependency caches and reproducible page PNGs.
The public portable runner recreates project objects in an empty output directory.
Book PDFs, logs, text extractions, structural checks, and visual-review records
are retained. The final delivery receipt is separate because its saved-file
identities become available only after these archives have been created.

`host_environment/` discloses the external wrapper and narrow proc-self-exe
compatibility shim used on this host. Official Lean compiler files were not
patched. The portable runner itself does not require or install this adapter.
The full compiler, dependency-cache, and preload byte inventories are in the
fresh replay record. These are trusted runtime inputs, not independently
authenticated dependency rebuilds.

Technical work is complete. The owner has not chosen public reuse licenses.
`current/records/PROPOSED_REUSE_TERMS.json` is a concrete MIT-code / CC BY 4.0-text
proposal, not a license grant. The public `REUSE.md` states the current boundary.
''')
technical=archive(TECH,'Komorebi_Space_Technical_Record_v1.15.0')
delivery={'schema':'komorebi-delivery-verification-v1','edition':'1.15.0','author':'Komorebi P.',
    'technical_status':'COMPLETE','reuse_license_status':'OWNER_CHOICE_PENDING_NO_NEW_GRANT',
    'canonical_checks_status':'PASS','distribution_status':'PENDING_ACTUAL_DOWNLOAD_VERIFICATION',
    'counts':edition['counts'],'formal_replay':edition['fresh_integrated_replay'],
    'canonical_archives':[public,technical],
    'canonical_books':[{'file':Path(b['file']).name,'bytes':(PUB/b['file']).stat().st_size,'sha256':b['sha256'],'pages':b['pages'],'identical_to_public_archive_book':True} for b in edition['books'].values()],
    'trust_boundary':edition['trust_boundary'],'limitations':edition['limitations'],
    'distribution_verification':None,'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
target=OUT/'Komorebi_Space_Delivery_Verification_v1.15.0.json'
target.write_text(json.dumps(delivery,indent=2)+'\n')
print(json.dumps({'deliverables':[{'file':p.name,'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(OUT.iterdir()) if p.is_file()]},indent=2))
