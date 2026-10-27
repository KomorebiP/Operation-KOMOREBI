#!/usr/bin/env python3
"""Assemble the cumulative consolidated Paper IX release and verify its contents."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
BASE = WORKSPACE / 'output/PRSC_IX_Complete_Analytic_Regularity.zip'
BASE_SHA = 'cf5b3d3e159b5f6bc38a7f1b4c20813eda40412c31469f510b512e38eb2f47a2'
PREFIX = 'PRSC_IX_Complete_Analytic_Regularity/'
RELEASE = 'PRSC_IX_Consolidated_Manuscript'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def encode(value):
    return (json.dumps(value,indent=2,ensure_ascii=False)+'\n').encode()

def main():
    assert sha(BASE.read_bytes()) == BASE_SHA
    build = json.loads((ROOT/'build/BUILD_REPORT.json').read_text())
    assert build['status'] == 'PASS' and build['sources_unchanged_during_build']
    pdf = (ROOT/'build/Paper_IX_Consolidated.pdf').read_bytes()
    assert sha(pdf) == build['pdf_sha256']
    for name, expected in build['source_hashes'].items():
        assert sha((ROOT/'manuscript'/name).read_bytes()) == expected
    review = json.loads((ROOT/'audit/MANUSCRIPT_REVIEW.json').read_text())
    visual = json.loads((ROOT/'audit/PDF_VISUAL_REVIEW.json').read_text())
    index = json.loads((ROOT/'audit/STATEMENT_INDEX.json').read_text())
    assert review['status'] == visual['status'] == index['status'] == 'PASS'
    assert visual['pdf_sha256'] == sha(pdf) and visual['pages'] == 45
    assert review['rendered_pdf_binding']['sha256'] == sha(pdf)
    for artifact in review['reviewed_artifacts']:
        assert sha(Path(artifact['workspace_path']).read_bytes()) == artifact['sha256'], artifact['path']
    files = {}
    coverage = []
    replaced = {'README.md','REMAINING_CHECKLIST.md','MANIFEST.json',
                'RELEASE_AUDIT.json','PACKAGE_COMPLETENESS.json'}
    with zipfile.ZipFile(BASE) as base:
        assert base.testzip() is None
        for item in base.infolist():
            assert not item.is_dir() and item.filename.startswith(PREFIX)
            relative = item.filename[len(PREFIX):]
            assert '..' not in Path(relative).parts
            if relative in replaced:
                dest = 'historical/analytic_regularity_release_root/'+relative
            elif relative == 'manuscript/README.md':
                dest = 'historical/analytic_regularity_release_root/manuscript_README.md'
            else:
                dest = relative
            assert dest not in files
            data = base.read(item)
            files[dest] = data
            coverage.append({'previous_path':relative,'current_path':dest,
                             'bytes':len(data),'sha256':sha(data)})
    assert len(coverage) == 2194
    for path in sorted((ROOT/'manuscript').rglob('*.tex')):
        dest = 'manuscript/consolidated/'+str(path.relative_to(ROOT/'manuscript'))
        assert dest not in files
        files[dest] = path.read_bytes()
    files['manuscript/consolidated/Paper_IX_Consolidated.pdf'] = pdf
    for folder in ['audit','tools']:
        for path in sorted((ROOT/folder).iterdir()):
            if path.is_file() and path.suffix in {'.json','.md','.csv','.py'}:
                dest = 'consolidation/'+folder+'/'+path.name
                assert dest not in files
                files[dest] = path.read_bytes()
    for name in ['BUILD_REPORT.json','Paper_IX_Consolidated.log',
                 'latex_pass_1.txt','latex_pass_2.txt','latex_pass_3.txt']:
        files['consolidation/build/'+name] = (ROOT/'build'/name).read_bytes()
    for name in ['README.md','REMAINING_CHECKLIST.md']:
        files[name] = (ROOT/'release_docs'/name).read_bytes()
    files['manuscript/README.md'] = (ROOT/'release_docs/MANUSCRIPT_README.md').read_bytes()
    files['PACKAGE_COMPLETENESS.json'] = encode({
        'status':'PASS','previous_archive':BASE.name,'previous_archive_sha256':BASE_SHA,
        'previous_files':2194,'files_preserved_by_content_hash':2194,
        'coverage':coverage,
        'scope':'Every prior archive file is retained exactly. Six replaced entry documents are relocated to the historical folder. Historical recovery limits remain explicit.'})
    files['RELEASE_AUDIT.json'] = encode({
        'status':'PASS','release':RELEASE,'author':'Komorebi P.','date':'2026-09-08',
        'kind':'Manuscript consolidation; no new Lean theorem or compiler rerun',
        'manuscript_pages':45,'manuscript_pdf_sha256':sha(pdf),
        'manuscript_source_hashes':build['source_hashes'],
        'mapped_statements':index['mapped_statements'],
        'resolved_statement_source_links':index['resolved_statement_source_links'],
        'retained_previous_files':2194,'previous_archive_sha256':BASE_SHA,
        'manuscript_review_sha256':sha((ROOT/'audit/MANUSCRIPT_REVIEW.json').read_bytes()),
        'visual_review_sha256':sha((ROOT/'audit/PDF_VISUAL_REVIEW.json').read_bytes()),
        'evidence_index_sha256':sha((ROOT/'audit/EVIDENCE_INDEX.json').read_bytes()),
        'latest_preserved_polynomial_gate':{'checks':91,'modules':55,'axiom_closures':515,'status':'PASS'},
        'remaining':'General singular persistence, Native13.2/13.3, further exact arithmetic classifications, historical formula recovery and chart-interface comparisons.',
        'limits':['Earlier compiler evidence is retained with its original scope.',
                  'Fresh official arXiv access was blocked; prior source-statement review is retained.',
                  'Original manuscript TeX, figure sources and complete experiment package remain unavailable.']})
    for item in coverage:
        assert sha(files[item['current_path']]) == item['sha256']
    manifest = {'release':RELEASE,'algorithm':'SHA-256','manifest_excludes_itself':True,
                'file_count_excluding_manifest':len(files),
                'files':[{'path':name,'bytes':len(data),'sha256':sha(data)} for name,data in sorted(files.items())]}
    files['MANIFEST.json'] = encode(manifest)
    output = WORKSPACE/'output'/f'{RELEASE}.zip'
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for name,data in sorted(files.items()):
            z.writestr(RELEASE+'/'+name,data)
    with zipfile.ZipFile(output) as z:
        assert z.testzip() is None
        assert len(z.infolist()) == len(files)
        for item in manifest['files']:
            assert sha(z.read(RELEASE+'/'+item['path'])) == item['sha256']
        for item in coverage:
            assert sha(z.read(RELEASE+'/'+item['current_path'])) == item['sha256']
    standalone = WORKSPACE/'output/Paper_IX_Consolidated.pdf'
    standalone.write_bytes(pdf)
    print(json.dumps({'status':'PASS','zip':str(output),'files':len(files),
                      'bytes':output.stat().st_size,'sha256':sha(output.read_bytes()),
                      'prior_files_preserved':2194,'pdf':str(standalone),'pdf_sha256':sha(pdf)},indent=2))

if __name__ == '__main__':
    main()
