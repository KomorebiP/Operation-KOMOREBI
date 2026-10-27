#!/usr/bin/env python3
"""Paper XII checks in isolated copies; never writes to delivered raw sources."""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import zipfile

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def parse_sha_manifest(path,root):
    errors=[];count=0
    for line in path.read_text().splitlines():
        if not line.strip():continue
        m=re.fullmatch(r'([a-fA-F0-9]{64})\s+\*?(.+)',line)
        if not m:raise ValueError('Unrecognized SHA256 manifest line: '+str(path))
        name=m[2];p=(root/name).resolve();count+=1
        if not p.is_relative_to(root.resolve()) or not p.is_file() or sha(p)!=m[1].lower():errors.append(name)
    return {'entries':count,'status':'PASS' if not errors else 'FAIL','mismatches':errors}

def archive_audit(archive,sidecar,extracted):
    expected=sidecar.read_text().split()[0]
    actual=sha(archive);errors=[]
    if actual!=expected:errors.append('Archive container SHA256 mismatch')
    with zipfile.ZipFile(archive) as z:
        files=[x for x in z.infolist() if not x.is_dir()]
        duplicate_names=[n for n,c in Counter(x.filename for x in files).items() if c>1]
        if duplicate_names:errors.append('Duplicate archive names')
        crc_bad=z.testzip()
        if crc_bad:errors.append('CRC failure: '+crc_bad)
        prefix=extracted.name+'/'
        compared=0
        for m in files:
            if not m.filename.startswith(prefix):errors.append('Unexpected member prefix: '+m.filename);continue
            rel=m.filename[len(prefix):];p=(extracted/rel).resolve()
            if not p.is_relative_to(extracted.resolve()) or not p.is_file():errors.append('Missing/unsafe extraction: '+rel);continue
            if hashlib.sha256(z.read(m)).hexdigest()!=sha(p):errors.append('Extracted member differs: '+rel)
            compared+=1
        extracted_names={p.relative_to(extracted).as_posix() for p in extracted.rglob('*') if p.is_file()}
        archive_names={x.filename[len(prefix):] for x in files if x.filename.startswith(prefix)}
        if extracted_names!=archive_names:errors.append('Extracted file inventory differs from archive')
        return {'archive':archive.name,'bytes':archive.stat().st_size,'sha256':actual,'sidecar_sha256':sha(sidecar),
                'expected_sha256':expected,'file_members':len(files),'extracted_files':len(extracted_names),
                'uncompressed_bytes':sum(x.file_size for x in files),'compared_member_hashes':compared,
                'crc_pass':crc_bad is None,'duplicate_names':duplicate_names,
                'status':'PASS' if not errors else 'FAIL','errors':errors}

def integrity(project,bundle,out):
    report={'scope':'Read-only integrity and preservation audit; no fresh Lean proof replay.'}
    report['complete_archive']=archive_audit(project/'downloads/Paper_XII_Complete_v0.17.1_With_Visual_Appendix.zip',
        project/'downloads/Paper_XII_Complete_v0.17.1_With_Visual_Appendix.sha256',bundle)
    old=project/'source/original_package/PSC_Paper_XII_Strengthened_Annals_Edition_Package'
    report['original_container']=archive_audit(project/'downloads/PSC_Paper_XII_Strengthened_Annals_Edition_Package.zip',
        bundle/'provenance/ORIGINAL_MANUSCRIPT_ARCHIVE.sha256',old)
    report['original_manifest']=parse_sha_manifest(bundle/'history/original_manuscript/MANIFEST.sha256',bundle/'history/original_manuscript')
    report['formal_manifest']=parse_sha_manifest(bundle/'formal_release/SHA256SUMS.txt',bundle/'formal_release')
    run=subprocess.run([sys.executable,str(bundle/'Run-PaperXII.py'),'verify'],capture_output=True,text=True)
    print(run.stdout,end='');print(run.stderr,end='',file=sys.stderr)
    report['bundle_wrapper_exit_code']=run.returncode
    report['bundle_verification']=json.loads(run.stdout[run.stdout.index('{'):])
    formal=bundle/'formal_release';v=json.loads((formal/'verification.json').read_text());rv=json.loads((formal/'REVERIFICATION.json').read_text())
    fc=json.loads((formal/'final_claims_check.json').read_text());errors=[]
    source_pairs=[]
    for m in v['modules']:
        source=formal/'lean'/Path(m['module'].replace('.','/')+'.lean');obj=formal/m['olean_path']
        sh=sha(source);oh=sha(obj)
        expected_source=v['source_hashes_before'].get(str(source.relative_to(formal/'lean')))
        expected_after=v['source_hashes_after'].get(str(source.relative_to(formal/'lean')))
        okay=sh==m['source_sha256']==expected_source==expected_after and oh==m['olean_sha256']
        if not okay:errors.append('Inherited source/object mismatch: '+m['module'])
        source_pairs.append({'module':m['module'],'source_sha256':sh,'object_sha256':oh,'pass':okay})
    logs=[]
    def logcheck(item):
        p=formal/item['log'];digest=sha(p);okay=digest==item['log_sha256']
        logs.append({'path':item['log'],'sha256':digest,'matches':okay})
        if not okay:errors.append('Inherited log changed: '+item['log'])
    for m in v['modules']:logcheck(m);logcheck(m['axiom_audit'])
    for c in v['controls']:logcheck(c)
    logcheck(fc)
    checks={'cumulative_report':sha(formal/'verification.json')==rv['cumulative_verification_sha256']==fc['cumulative_report_sha256'],
       'consumer_report':sha(formal/'final_claims_check.json')==rv['final_claims_check_sha256'],
       'consumer_source':sha(formal/'checks/FinalClaimsConsumer.lean')==fc['source_sha256'],
       'consumer_object':sha(formal/'checks/FinalClaimsConsumer.olean')==fc['object_sha256'],
       'module_manifest':sha(formal/'checks/modules.json')==v['module_manifest_sha256'],
       'three_statuses_pass':v['status']==rv['status']==fc['status']=='PASS',
       'axiom_target_names_match':{d['name'] for d in v['declarations']}=={d['name'] for d in v['axioms']},
       'allowed_axioms_only':all(set(d['axioms'])<={'propext','Classical.choice','Quot.sound'} for d in v['axioms']+fc['axioms']),
       'negative_controls_pass':len(v['controls'])==3 and all(c['passed'] and c['exit_code']!=0 and not c['timed_out'] for c in v['controls'])}
    errors.extend(k for k,b in checks.items() if not b)
    report['inherited_evidence_preservation']={'status':'PASS' if not errors else 'FAIL','errors':errors,'checks':checks,
       'source_object_pairs_verified':len(source_pairs),'source_object_pairs':source_pairs,'logs_verified':len(logs),'logs':logs,
       'recorded_started_utc':v['started_utc'],'recorded_finished_utc':v['finished_utc'],
       'production_modules':len(v['modules']),'production_named_declarations_audited':len(v['axioms']),
       'own_theorems':v['own_theorem_count'],'reused_paper_x_theorems':v['reused_theorem_count'],
       'supplementary_consumers':fc['theorem_count'],'negative_controls':len(v['controls']),
       'revised_coverage':rv['revised_coverage'],'original_wording_coverage':rv['original_wording_coverage'],
       'fresh_lean_replay':False,'interpretation':'Recorded compiler evidence is inherited; current hash checks authenticate preserved artifacts only.'}
    okay=run.returncode==0 and all(report[k]['status']=='PASS' for k in ('complete_archive','original_container','original_manifest','formal_manifest','inherited_evidence_preservation'))
    report['status']='PASS' if okay else 'FAIL'
    (out/'result.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Integrity/preservation:',report['status'])
    return 0 if okay else 1

def examples(bundle,out):
    # Exercise the documented wrapper from a byte-preserving disposable full copy.
    isolated=out/'isolated_bundle';shutil.copytree(bundle,isolated)
    run=subprocess.run([sys.executable,str(isolated/'Run-PaperXII.py'),'examples'])
    result=isolated/'build/examples/checks/EXACT_CHECKS.json'
    if result.exists():shutil.copy2(result,out/'result.json')
    return run.returncode

def original(bundle,out):
    isolated=out/'isolated_original';shutil.copytree(bundle/'history/original_manuscript',isolated)
    for name in ('verification_results.json','verification_summary.txt'):
        (isolated/'verification'/name).unlink(missing_ok=True)
    run=subprocess.run([sys.executable,str(isolated/'verification/verify_paper_xii.py')])
    result=isolated/'verification/verification_results.json'
    if result.exists():shutil.copy2(result,out/'result.json')
    summary=isolated/'verification/verification_summary.txt'
    if summary.exists():shutil.copy2(summary,out/'summary.txt')
    return run.returncode

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('task',choices=['integrity','original-finite','appendix-exact'])
    ap.add_argument('--project',type=Path,required=True);ap.add_argument('--bundle',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    return integrity(a.project,a.bundle,a.output) if a.task=='integrity' else original(a.bundle,a.output) if a.task=='original-finite' else examples(a.bundle,a.output)
if __name__=='__main__':sys.exit(main())
