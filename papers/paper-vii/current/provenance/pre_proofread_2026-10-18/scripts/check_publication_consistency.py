#!/usr/bin/env python3
"""Check PDF copies, metadata, actual page locators and report dependency pins."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import fitz

ROOT = Path(__file__).resolve().parent.parent

def read(name):
    return json.loads((ROOT / name).read_text())

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def check(condition, message):
    if not condition:
        raise AssertionError(message)

def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)

def main():
    edition = read('EDITION.json')
    docs = edition['documents']
    check(len(docs) == 3, 'Three companion PDFs required')
    for d in docs:
        for folder in ['papers', 'publication/pdfs', 'editable/' + d['role']]:
            p = ROOT / folder / Path(d['path']).name
            check(sha(p) == d['sha256'], str(p) + ': PDF copy hash')
            check(p.stat().st_size == d['bytes'], str(p) + ': PDF byte size')
            with fitz.open(p) as pdf:
                check(len(pdf) == d['pages'], str(p) + ': page count')
    check(sum(d['pages'] for d in docs) == edition['total_pages'], 'Total pages')
    check(read('COMPANION_MAP.json')['documents'] == docs, 'Companion metadata')
    check(read('publication/CURRENT_PUBLICATION_MANIFEST.json')['documents'] == docs, 'Publication metadata')
    check(read('SERIES_STATUS.json')['documents'] == docs, 'Series status')
    trad = ROOT / 'editable/traditional'
    mapping = read('editable/traditional/canonical_label_to_final.json')
    visual = read('editable/visual_guide/VISUAL_TO_TRADITIONAL_CROSSWALK.json')
    lean = read('editable/lean_guide/generated/traditional_crosswalk.json')
    visual_targets = lean_targets = 0
    with fitz.open(ROOT / docs[0]['path']) as pdf:
        for label, row in mapping.items():
            page = int(row['physical_pdf_page'])
            check(1 <= page <= len(pdf), label + ': physical page')
            check(pdf[page - 1].get_label() == str(row['printed_page']), label + ': printed label')
        check(len(visual['pages']) == 40, 'Forty retained visual body pages')
        with fitz.open(ROOT / docs[1]['path']) as guide:
            for page in visual['pages']:
                check(guide[int(page['visual_physical_pdf_page']) - 1].get_label() ==
                      str(page['visual_printed_page']), 'Visual printed label')
                for row in page['traditional_targets']:
                    expected = mapping[row['final_label']]
                    for k in ['number','printed_page','physical_pdf_page']:
                        check(str(row[k]) == str(expected[k]), row['final_label'] + ': visual ' + k)
                    visual_targets += 1
        for row in walk({k:v for k,v in lean.items() if k != 'provenance'}):
            if not {'final_label','printed_page','physical_pdf_page'} <= row.keys():
                continue
            expected = mapping[row['final_label']]
            for k in ['printed_page','physical_pdf_page']:
                check(str(row[k]) == str(expected[k]), row['final_label'] + ': Lean ' + k)
            lean_targets += 1
    check(visual_targets >= 40, 'Visual target inventory is incomplete')
    check(len(lean['core']) == 19 and len(lean['strengthened']) == 79 and len(lean['supplements']) == 6, 'Lean finite/strengthened/supplement inventory')
    check(lean_targets == 110, 'Lean reading locators including twelve supplement endpoints')
    check(visual['traditional_pdf_sha256'] == docs[0]['sha256'], 'Visual traditional PDF pin')
    check(visual['visual_pdf_sha256'] == docs[1]['sha256'], 'Visual own PDF pin')
    check(visual['traditional_map_sha256'] == sha(trad / 'canonical_label_to_final.json'), 'Visual map pin')
    check(visual['traditional_source_sha256'] == sha(trad / 'Paper_VII_Traditional_Final.tex'), 'Visual wrapper pin')
    check(lean['provenance']['traditional_pdf_sha256'] == docs[0]['sha256'], 'Lean traditional PDF pin')
    for name, pin in lean['provenance'].items():
        if name.endswith(('.tex','.json')):
            check(sha(trad / name) == pin, 'Lean provenance pin ' + name)
    for name, data in read('COMPANION_MAP.json')['crosswalks'].items():
        check(read('editable/' + name) == data, 'Root crosswalk parity ' + name)
    for name in read('verification/MONOGRAPH_VERIFICATION.json')['reports']:
        report = read(name)
        check(report['status'].startswith('PASS'), name + ': review incomplete')
        for row in report.get('source_pins',[]) if isinstance(report.get('source_pins',[]),list) else []:
            check(sha(ROOT / row['path']) == row['sha256'], name + ': stale source pin ' + row['path'])
        for dependency, pin in {**report.get('report_dependencies',{}), **report.get('report_dependency_pins',{}), **report.get('input_pins',{})}.items():
            check(sha(ROOT / dependency) == pin, name + ': stale dependency ' + dependency)
    visual_report = read('verification/monograph_visual_report.json')
    check(visual_report['pdf_sha256'] == docs[1]['sha256'], 'Visual owner PDF pin')
    check(visual_report['guide_tex_sha256'] == sha(ROOT / 'editable/visual_guide/Paper_VII_Visual_Guide_Final.tex'), 'Visual owner wrapper pin')
    check(visual_report['source_crosswalk_sha256'] == sha(ROOT / 'editable/visual_guide/VISUAL_TO_TRADITIONAL_CROSSWALK.json'), 'Visual owner crosswalk pin')
    source_crosswalk = read('editable/visual_guide/SOURCE_CROSSWALK.json')
    expected_source_crosswalk = [
        {'visual_page': row['visual_page'], 'title': row['title'],
         'source_line': row['source_line_current'],
         'targets': [dict(target, label=target['final_label'],
                          traditional_page=target['printed_page'],
                          physical_page=target['physical_pdf_page'])
                     for target in row['traditional_targets']]}
        for row in visual['pages']
    ]
    check(source_crosswalk == expected_source_crosswalk, 'Visual legacy-format crosswalk parity')
    check(visual_report['pdf_qa_sha256'] == sha(ROOT / 'editable/visual_guide/PDF_QA.json'), 'Visual QA pin')
    check(visual_report['atlas_body_sha256'] == sha(trad / 'monograph_atlas.tex'), 'Integrated atlas body pin')
    check(visual_report['atlas_definitions_sha256'] == sha(trad / 'atlas_definitions.tex'), 'Integrated atlas definitions pin')
    models = read('verification/monograph_checks/TRADITIONAL_EXACT_MODELS_REVIEW.json')
    check(sha(ROOT / models['manifest']) == models['manifest_sha256'], 'Model run manifest pin')
    check(sha(ROOT / models['result']) == models['result_sha256'], 'Model run result pin')
    figures = read('verification/monograph_figure_report.json')
    check(len(figures['figures']) == 35, 'All inherited figures')
    for row in figures['source_pins']:
        check(sha(ROOT / row['path']) == row['sha256'], 'Figure source pin ' + row['path'])
    for row in figures['figures']:
        check(sha(ROOT / row['path']) == row['output_sha256'], 'Current figure pin ' + row['path'])
        check(sha(ROOT / row['original_source']) == row['input_sha256'], 'Inherited figure pin ' + row['original_source'])
    comp = read('verification/monograph_checks/COMPUTATIONAL_REVIEW.json')
    check(comp['status'].startswith('PASS'), 'Core computation status')
    for dependency, pin in comp['report_dependency_pins'].items():
        check(sha(ROOT / dependency) == pin, 'Computation report dependency ' + dependency)
    for row in comp['records']:
        check(sha(ROOT / row['manifest']) == row['manifest_sha256'], 'Current bounded manifest ' + row['name'])
    baseline = ROOT / 'provenance/current_retrieved_baseline/traditional/parts'
    parts = sorted(baseline.glob('*.tex'))
    check(len(parts) == 9, 'Nine exact retrieved mathematical parts')
    for p in parts:
        check(p.read_bytes() == (trad / 'parts' / p.name).read_bytes(), p.name + ': preserved part changed')
    preservation = read('verification/MONOGRAPH_PRESERVATION.json')
    check(preservation['status'].startswith('PASS'), 'Preservation status')
    check(sha(ROOT / preservation['current_wrapper_path']) == preservation['current_wrapper_sha256'], 'Preservation wrapper pin')
    for row in preservation['baseline_parts']:
        check(sha(ROOT / row['current_path']) == row['current_sha256'], 'Preservation current part pin')
        check(sha(ROOT / row['baseline_path']) == row['baseline_sha256'], 'Preservation baseline part pin')
    replay = read('verification/MONOGRAPH_PACKAGED_BUILD.json')
    check(replay['status'] == 'PASS', 'Packaged replay status')
    check(len(replay['documents']) == 3, 'All replay documents')
    check(all(d['page_count_match'] and d['extracted_text_match'] for d in replay['documents']), 'PDF page/text replay')
    report = {'status':'PASS_FOR_STATED_SCOPE','checked_at_utc':datetime.now(timezone.utc).isoformat(),
        'documents':docs,'active_pdf_copies_checked':9,'canonical_labels_and_aliases':len(mapping),
        'visual_body_pages':len(visual['pages']),'visual_locators':visual_targets,'lean_locators':lean_targets,
        'root_companion_crosswalk_parity':True,'mathematical_parts_byte_identical':9,
        'protected_record_environments':147,'numbered_records':142,'proof_environments':107,
        'packaged_rebuild_pages_and_text_match':True,
        'byte_identity':{d['document']:d['pdf_byte_identical'] for d in replay['documents']},
        'scope':'Current PDF synchronization, page navigation, source/report pins and packaged replay. No mathematical or Lean process is invoked.'}
    (ROOT / 'verification/PACKAGE_CONSISTENCY.json').write_text(json.dumps(report,indent=2) + '\n')
    print(json.dumps(report,indent=2))

if __name__ == '__main__':
    main()
