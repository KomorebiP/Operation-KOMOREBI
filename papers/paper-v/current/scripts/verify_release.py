#!/usr/bin/env python3
"""Verify frozen Paper V distribution, current readers and recorded evidence.

Does not execute Lean, the finite suites, or a PDF compiler. Use the separate
documented commands for those executions.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/'verification/closeout_2026-10-20'
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text())
def require(condition,message):
    if not condition:raise ValueError(message)
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--report',type=Path)
    args=p.parse_args()
    if args.report and args.report.resolve().is_relative_to(ROOT):p.error('report must be outside the sealed package')
    report={'schema':'komorebi.paper-v.release-check/1','status':'FAIL','checks':[],'fresh_lean_execution':False,'scope':__doc__}
    try:
        integrity=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/verify_integrity.py'),'--strict'],capture_output=True,text=True)
        require(integrity.returncode==0,'strict integrity failed: '+integrity.stdout[-2000:]+integrity.stderr[-1000:])
        report['checks'].append('strict complete-file integrity')
        import fitz
        edition=read(ROOT/'EDITION.json')
        documents=edition['documents'];require(len(documents)==3,'expected three readers')
        roles={'traditional':'traditional','visual_guide':'visual_guide','lean_guide':'lean_guide'}
        counts={}
        for row in documents:
            path=ROOT/row['path'];require(path.resolve().is_relative_to(ROOT),'unsafe PDF path')
            require(path.stat().st_size==row['bytes'] and digest(path)==row['sha256'],'PDF record differs: '+row['path'])
            with fitz.open(path) as doc:
                require(len(doc)==row['pages'],'PDF page count differs')
                counts[row['role']]=len(doc)
            for copy in [ROOT/'publication/pdfs'/path.name,ROOT/'editable'/roles[row['role']]/path.name]:
                require(copy.is_file() and digest(copy)==row['sha256'],'reader copies differ: '+str(copy))
        require(set(counts)==set(roles) and sum(counts.values())==edition['total_pages'],'document census differs')
        report['pages']=counts;report['checks'].append('three coordinated reader copies and page counts')
        mapping=read(ROOT/'editable/traditional/canonical_label_to_final.json')
        locators=read(ROOT/'CURRENT_PUBLICATION_LOCATORS.json')
        require(locators['labels']==mapping,'current locator map differs')
        require(locators['canonical_map_sha256']==digest(ROOT/'editable/traditional/canonical_label_to_final.json'),'locator map hash differs')
        require(locators['pdf_sha256']==documents[0]['sha256'],'locator PDF hash differs')
        nav=read(ROOT/'editable/lean_guide/generated/traditional_crosswalk.json')
        require(nav==mapping,'Lean guide traditional map differs')
        visual=read(ROOT/'editable/visual_guide/VISUAL_CROSSWALK.json')
        require(len(visual['worked_pages'])==40,'visual page inventory differs')
        for row in visual['worked_pages']:
            for anchor in row['anchors']:
                require(anchor['final']==mapping[anchor['canonical_label']],'visual anchor differs')
        header=r'^\\vpage\{\d+\}\{.*?\}\{.*?\}\{.*?\}$'
        atlas=(ROOT/'editable/traditional/atlas-pages.tex').read_text()
        guide=(ROOT/'editable/visual_guide/source/pages_final.tex').read_text()
        require(len(re.findall(header,atlas,re.M))==40,'expected forty integrated atlas headers')
        require(re.findall(header,atlas,re.M)==re.findall(header,guide,re.M),'integrated atlas headers differ')
        report['checks'].append('traditional, visual, integrated atlas and Lean navigation')
        preservation=read(EVIDENCE/'SOURCE_PRESERVATION.json')
        require(preservation['status']=='PASS','source preservation not accepted')
        for key in ['baseline','current']:
            x=preservation[key];require(digest(ROOT/x['path'])==x['sha256'],'source preservation binding differs')
        for row in preservation['formal_files_unchanged']:
            require(digest(ROOT/row['path'])==row['sha256'],'formal source differs: '+row['path'])
        require(preservation['all83_proof_bodies_byte_identical'] and preservation['byte_identical_numbered_records']==118,'proof/record scope differs')
        report['checks'].append('current source preservation and unchanged formal source bindings')
        finite=read(EVIDENCE/'finite/REPLAY_SUMMARY.json')
        expected={'readiness','verifier','exact_models','second_block','numeric_pytest','annals','visual_symbolic','visual_extension'}
        require(finite['status']=='PASS' and not finite['errors'] and len(finite['suites'])==8,'finite replay not accepted')
        require({x['name'] for x in finite['suites']}==expected and all(x['status']=='PASS' and x['returncode']==0 for x in finite['suites']),'finite suite set/outcomes differ')
        require(finite['runner_sha256']==digest(ROOT/'scripts/replay_finite.py'),'finite runner changed since execution')
        replay=read(EVIDENCE/'ISOLATED_PDF_REPLAY.json')
        require(replay['status']=='PASS' and len(replay['documents'])==3,'PDF replay not accepted')
        require(all(x['page_count_match'] and x['extracted_text_match'] for x in replay['documents']),'PDF replay comparison incomplete')
        for x in replay['documents']:
            require(x['pages']==counts[next(d['role'] for d in documents if Path(d['path']).stem==x['document'])],'replay page census differs')
        geom=read(EVIDENCE/'FINAL_GEOMETRY_AND_LINKS.json')
        require(geom['status']=='PASS','publication geometry not accepted')
        for x in geom['documents']:
            require(digest(ROOT/'papers'/x['file'])==x['sha256'],'QA PDF binding differs')
        require(read(ROOT/'LICENSE_STATUS.json')['status']=='OPEN_LICENSES_APPLIED','explicit licenses absent')
        report['checks'].append('recorded finite execution, isolated PDF replay, final geometry and license status')
        report['status']='PASS'
    except Exception as exc:report['error']=str(exc)
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    return 0 if report['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
