#!/usr/bin/env python3
"""Package the reviewed monograph, selected sources and exact reading editions."""
from pathlib import Path
import datetime,hashlib,json,shutil,subprocess,sys,zipfile
ROOT=Path(__file__).resolve().parent
STAGE=ROOT/'package_stage'/'Realization_Calculus_Publication_Package'
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')

def main():
    audit=json.loads((ROOT/'book/final_pdf_audit.json').read_text())
    if audit.get('status')!='PASS':raise SystemExit('The independent final PDF audit must pass before packaging.')
    if audit.get('pdf_sha256')!=sha(ROOT/'output/Realization_Calculus.pdf'):
        raise SystemExit('The PDF audit does not identify the current book bytes.')
    branding=json.loads((ROOT/'book/rebranding_audit.json').read_text())
    if branding.get('status')!='PASS' or branding.get('pdf_sha256')!=audit['pdf_sha256']:
        raise SystemExit('The branding preservation audit must pass for the current book bytes.')
    visual=json.loads((ROOT/'book/final_visual_review.json').read_text())
    if visual.get('status')!='PASS' or visual.get('pdf_sha256')!=audit['pdf_sha256']:
        raise SystemExit('The final visual review must identify the current book bytes.')
    preview=json.loads((ROOT/'book/preview_manifest.json').read_text())
    if preview.get('source_sha256')!=audit['pdf_sha256'] or preview.get('preview_sha256')!=sha(ROOT/'output/Realization_Calculus_Design_Preview.pdf'):
        raise SystemExit('The preview does not identify the current book and preview bytes.')
    if STAGE.exists():shutil.rmtree(STAGE)
    STAGE.mkdir(parents=True)
    trees=['source_i_iv','source_v_viii','source_ix_xii','compiled','frozen_readers',
           'publication_notices','LICENSES','book','editorial']
    excluded=[];copied=[]
    font_exts={'.otf','.ttf','.pfb','.pfa','.t1','.afm','.woff','.woff2'}
    for name in trees:
        for p in sorted((ROOT/name).rglob('*')):
            if not p.is_file():continue
            rel=p.relative_to(ROOT)
            skip=('__pycache__' in rel.parts or p.suffix=='.pyc' or
                  (name.startswith('source_') and ('fonts' in rel.parts or p.suffix.lower() in font_exts)) or
                  (name=='editorial' and 'outer_test' in rel.parts) or
                  (name=='editorial' and any(x in rel.parts for x in ('rebrand_outer_test','rebrand_component_test')) and p.suffix.lower()=='.pdf'))
            if skip:excluded.append({'path':rel.as_posix(),'reason':'external font dependency or reproducible temporary/test file'});continue
            if p.is_symlink():raise ValueError('Unexpected source symlink: '+str(rel))
            target=STAGE/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target);copied.append(rel.as_posix())
    roots=['README.txt','LICENSE.txt','requirements.txt','publisher-layout.tex',
           'prepare_book.py','render_outer.py','assemble_monograph.py','audit_monograph.py','rebrand_components.py','audit_rebranding.py',
           'make_preview.py','rebuild_monograph.py','package_publication.py',
           'component_builds.json','typeset_i_iv_results.json','typeset_v_viii_results.json',
           'typeset_ix_x_results.json','typeset_ix_xii_results.json','MONOGRAPH_LEDGER_v1.0.0.txt','REALIZATION_CALCULUS_EDITORIAL_LEDGER_v1.1.0.txt',
           'register_current.txt','register_metadata.json','reader_inventory.json']
    for name in roots:shutil.copy2(ROOT/name,STAGE/name)
    (STAGE/'output').mkdir()
    for name in ['Realization_Calculus.pdf','Realization_Calculus_Design_Preview.pdf']:
        shutil.copy2(ROOT/'output'/name,STAGE/'output'/name)
    for p in (ROOT/'scripts').iterdir():
        if p.is_file():
            target=STAGE/'scripts'/p.name;target.parent.mkdir(exist_ok=True);shutil.copy2(p,target)
    dump(STAGE/'editorial/package_selection.json',{'excluded':excluded,'policy':'No standalone font programs; all41 frozen reader PDFs and36 editable source builds retained. Scientific assets remain in the selected source trees.'})
    rows=[{'path':p.relative_to(STAGE).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(STAGE.rglob('*')) if p.is_file()]
    manifest={'schema':'komorebi.strict_manifest.v1','checkpoint':'Realization Calculus publication revision1.1.0',
              'scope':'Publication assets and exact file membership; not mathematical verification.',
              'edition':'1.1.0 /2026-10-21','generated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':rows}
    dump(STAGE/'MANIFEST_SHA256.json',manifest)
    verify=subprocess.run([sys.executable,'-B',str(STAGE/'scripts/verify_integrity.py'),'--strict'],capture_output=True,text=True)
    (ROOT/'PACKAGE_STAGE_VERIFICATION.txt').write_text(verify.stdout+verify.stderr)
    if verify.returncode:raise SystemExit('Staging integrity verification failed.')
    target=ROOT/'output/Realization_Calculus_Publication_Package.zip'
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(STAGE.rglob('*')):
            if p.is_file():z.write(p,str(Path(STAGE.name)/p.relative_to(STAGE)))
    with zipfile.ZipFile(target) as z:
        if z.testzip():raise ValueError('ZIP CRC failure')
        names=z.namelist()
        if len(names)!=len(set(names)):raise ValueError('Duplicate ZIP path')
        for row in rows:
            data=z.read(STAGE.name+'/'+row['path'])
            if len(data)!=row['bytes'] or hashlib.sha256(data).hexdigest()!=row['sha256']:raise ValueError(row['path'])
        manifest_bytes=z.read(STAGE.name+'/MANIFEST_SHA256.json')
        if hashlib.sha256(manifest_bytes).hexdigest()!=sha(STAGE/'MANIFEST_SHA256.json'):raise ValueError('Manifest stream mismatch')
    record={'status':'PASS','package_bytes':target.stat().st_size,'package_sha256':sha(target),
            'regular_members':len(rows)+1,'manifest_rows':len(rows),'zip_crc':'PASS',
            'all_member_bytes_and_hashes':'PASS','stage_strict_integrity':'PASS',
            'font_binaries_excluded':True,'source_pdf_audit_status':audit['status'],
            'branding_preservation_audit_status':branding['status']}
    dump(ROOT/'PACKAGE_DELIVERY_VERIFICATION.json',record)
    print(json.dumps(record,indent=2))
if __name__=='__main__':main()
