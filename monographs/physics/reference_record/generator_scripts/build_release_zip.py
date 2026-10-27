#!/usr/bin/env python3
"""Build portable sources + combined PDF package, with internal file SHA manifest."""
from pathlib import Path
import hashlib,json,zipfile,os,shutil,csv
ROOT=Path(__file__).resolve().parent.parent
BASE=Path('/mnt/data')
OUT=BASE/'Komorebi_Physics_Collected_v0.6.0_Full_Handoff_2026-10-20.zip'
manifest=json.loads((ROOT/'book/volume_manifest.json').read_text())
file_map={}
for f in [ROOT/'README.md',ROOT/'PROGRESS_LEDGER_v0.50.0-a1.md',ROOT/'BUILD_VERIFICATION.md']:
    file_map[f.name]=f
for folder in ['manuscript','lean','figures','results','source_scripts']:
    for f in (ROOT/folder).rglob('*'):
        if not f.is_file():continue
        if f.suffix in ('.aux','.log','.out','.toc','.synctex.gz','.pyc') or f.name.startswith('__'):
            continue
        file_map[str(Path(folder)/f.relative_to(ROOT/folder))]=f
for n in ['Komorebi_Physics_Collected_Volume_0.6.0_2026-10-20.pdf','volume_manifest.json','book_validation.json','build_log.txt']:
    f=ROOT/'book'/n;file_map[f'book/{n}']=f
for e in manifest['components']:
    if e['source']=='@BLOCK50':continue
    f=Path(e['source_path']);file_map[f'originals/{f.name}']=f
for name in ['Komorebi_Physics_COMPLETE_HANDOFF_v0.49.0_2026-10-09.zip','Komorebi_Physics_Lean_v0.49.0_Checked_Block_49.zip']:
    f=BASE/'files'/name;file_map[f'predecessor/{name}']=f
with open(ROOT/'book/book_index.csv','w',newline='',encoding='utf-8') as g:
    fieldnames=['part','title','source_filename','page_start','page_end','page_count','status','source_sha256']
    w=csv.DictWriter(g,fieldnames=fieldnames);w.writeheader();w.writerows([{k:e[k] for k in fieldnames} for e in manifest['components']])
file_map['book/book_index.csv']=ROOT/'book/book_index.csv'
filesha={}
for n,p in sorted(file_map.items()):
    if not p.exists():raise FileNotFoundError(p)
    filesha[n]=hashlib.sha256(p.read_bytes()).hexdigest()
checks={'release':'0.6.0','date':'2026-10-20','scope':'complete physics reading volume plus analytic Block 50 and full verified predecessor archives',
        'files':filesha}
(ROOT/'PACKAGE_CHECKSUMS.json').write_text(json.dumps(checks,indent=2))
file_map['PACKAGE_CHECKSUMS.json']=ROOT/'PACKAGE_CHECKSUMS.json'
with zipfile.ZipFile(OUT,'w',allowZip64=True) as z:
    for n,p in sorted(file_map.items()):
        compression=zipfile.ZIP_STORED if p.suffix.lower() in ('.zip','.pdf','.png','.jpg') else zipfile.ZIP_DEFLATED
        z.write(p,arcname=f'Komorebi_Physics_Collected_v0.6.0/{n}',compress_type=compression,compresslevel=6)
print(f'Created {OUT} ({OUT.stat().st_size/1024/1024:.1f} MiB), {len(file_map)} files')
with zipfile.ZipFile(OUT) as z:
    assert z.testzip() is None
    num_pdf=sum(x.endswith('.pdf') for x in z.namelist())
    print(f'ZIP integrity PASS; {num_pdf} PDFs; {len(z.namelist())} files')
# User-facing independent book and paper copies for low-bandwidth download.
shutil.copy2(ROOT/'book'/'Komorebi_Physics_Collected_Volume_0.6.0_2026-10-20.pdf',BASE/'Komorebi_Physics_Collected_Volume_v0.6.0_2026-10-20.pdf')
shutil.copy2(ROOT/'manuscript'/'Block50_Spectral_Generator_Bridge.pdf',BASE/'Komorebi_Physics_Block50_Spectral_Bridge_2026-10-20.pdf')
shutil.copy2(ROOT/'PROGRESS_LEDGER_v0.50.0-a1.md',BASE/'Komorebi_Physics_Block50_Progress_Ledger.md')
