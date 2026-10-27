#!/usr/bin/env python3
"""Package the frozen, reviewed 1.1 reading editions and full editable evidence."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent
NAME = 'Komorebi_Special_Function_Discovery_v1.1'
GUIDE = 'Komorebi_Special_Functions_Resolution_and_Coupled_Visual_Guide_v1.1'

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    qa = json.loads((ROOT/'evidence/v11/final_qa.json').read_text())
    assert qa['status'] == 'passed'
    for p, h in qa['frozen_files'].items():
        assert digest(ROOT/p) == h, f'Review is stale: {p}'
    visual = json.loads((ROOT/'evidence/v11/final_visual_review.json').read_text())
    assert visual['verdict'] == 'pass'
    for d in visual['documents']:
        assert digest(ROOT/d['path']) == d['sha256'], d['path']
    paths = sorted(p for p in ROOT.rglob('*') if p.is_file()
                   and '__pycache__' not in p.parts and p.suffix != '.pyc'
                   and not (p.parent == ROOT and (p.name in {'package_manifest.json','SHA256SUMS'}
                            or p.suffix in {'.aux','.log','.out','.toc'})))
    assert all(not p.is_symlink() for p in paths)
    manifest = {
        'checkpoint':'SF-DISCOVERY-110','author':'Komorebi P.','date':'2026-10-09',
        'monograph_pages':118,'visual_guide_pages':19,'unique_figures':32,
        'new_figures':14,'technical_appendices':10,
        'new_checks':{'exact':5272,'numerical':26,'separate_operational_guards':13},
        'inherited_1_0_checks':{'exact':19871,'numerical':5576,'rerun_in_1_1':False},
        'sequence_catalog_rows':{'inherited':18,'new_coupled':7},
        'current_target':'research_v11/TARGET_CONTRACT.json',
        'current_computation_manifest':'evidence/v11/release-run-002/manifest.json',
        'current_reading_entry_point':'README.md',
        'historical_base_archive':'historical/release_1.0/Komorebi_Special_Function_Discovery_v1.0_Source.zip',
        'proof_review':'evidence/v11/independent_math_audit.md',
        'review_addendum':'evidence/v11/independent_math_audit_import_addendum.json',
        'hash_scope':'Every packaged file except this manifest and SHA256SUMS. SHA256SUMS additionally covers this manifest.',
        'excluded':['top-level LaTeX intermediates','Python caches','temporary page renders','downloaded execution helpers','external dependencies and third-party papers'],
        'historical_evidence':'Dated reports and runs retain original claims, paths, and hashes. Run001 is superseded by run002 for the import-only portability correction. The complete 1.0 archive retains the original historical layout.',
        'novelty':'Historical priority unresolved. Theorems are independently audited under their explicit hypotheses.',
        'files':{str(p.relative_to(ROOT)):digest(p) for p in paths},
    }
    manifest_path=ROOT/'package_manifest.json'
    manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
    paths.append(manifest_path)
    sums=ROOT/'SHA256SUMS'
    sums.write_text(''.join(f'{digest(p)}  {p.relative_to(ROOT)}\n' for p in sorted(paths)))
    paths.append(sums)
    deliverables=[]
    for src,dest in [('main.pdf',NAME+'.pdf'),('visual_guide.pdf',GUIDE+'.pdf')]:
        p=OUT/dest;shutil.copyfile(ROOT/src,p)
        assert digest(p)==digest(ROOT/src)
        deliverables.append({'path':str(p),'sha256':digest(p),'bytes':p.stat().st_size})
    archive=OUT/(NAME+'_Source.zip')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(paths):
            info=zipfile.ZipInfo(f'{ROOT.name}/{p.relative_to(ROOT)}',date_time=(2026,10,9,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
            z.writestr(info,p.read_bytes())
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert len(z.namelist())==len(paths)
        for p in paths:
            assert hashlib.sha256(z.read(f'{ROOT.name}/{p.relative_to(ROOT)}')).hexdigest()==digest(p),p
    deliverables.append({'path':str(archive),'sha256':digest(archive),'bytes':archive.stat().st_size})
    result={'status':'verified','packaged_files':len(paths),'deliverables':deliverables}
    (OUT/(NAME+'_delivery_verification.json')).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))

if __name__=='__main__':
    main()
