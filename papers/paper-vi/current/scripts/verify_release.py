#!/usr/bin/env python3
"""Check the frozen Paper VI distribution and its explicitly scoped evidence.

Checks files, readers, navigation and recorded execution bindings. Does not
compile Lean, rerun scientific suites, or reprove mathematical statements.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'verification/closeout_2026-10-20'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def run_check(argv, label):
    result = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True)
    require(result.returncode == 0,
            label + ': ' + result.stdout[-2000:] + result.stderr[-1000:])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, help='Optional report outside the sealed package.')
    args = parser.parse_args()
    if args.report and args.report.resolve().is_relative_to(ROOT):
        parser.error('report must be outside the sealed package')
    report = {'schema': 'komorebi.paper-vi.release-check/1', 'status': 'FAIL',
              'checks': [], 'fresh_lean_execution': False, 'scope': __doc__}
    try:
        run_check([sys.executable, '-B', str(ROOT / 'scripts/verify_integrity.py'), '--strict'],
                  'strict integrity')
        report['checks'].append('complete file membership, paths, sizes and SHA-256')
        import fitz
        edition = read(ROOT / 'EDITION.json')
        documents = edition['documents']
        roles = {'traditional', 'visual_guide', 'lean_guide'}
        require(len(documents) == 3 and {d['role'] for d in documents} == roles,
                'three reader roles required')
        counts = {}
        for row in documents:
            path = ROOT / row['path']
            require(path.resolve().is_relative_to(ROOT), 'unsafe PDF path')
            require(path.stat().st_size == row['bytes'] and digest(path) == row['sha256'],
                    'PDF record differs: ' + row['path'])
            with fitz.open(path) as pdf:
                require(len(pdf) == row['pages'], 'PDF page count differs: ' + row['path'])
                counts[row['role']] = len(pdf)
            for folder in ['publication/pdfs', 'editable/' + row['role']]:
                require(digest(ROOT / folder / path.name) == row['sha256'],
                        'PDF copy differs: ' + folder)
        require(sum(counts.values()) == edition['total_pages'], 'reader total differs')
        for name in ['COMPANION_MAP.json', 'publication/CURRENT_PUBLICATION_MANIFEST.json',
                     'SERIES_STATUS.json']:
            require(read(ROOT / name)['documents'] == documents, 'document metadata differs: ' + name)
        report['pages'] = counts
        report['checks'].append('three readers, nine matching copies and coordinated metadata')

        trad = ROOT / 'editable/traditional'
        mapping = read(trad / 'canonical_label_to_final.json')
        locators = read(ROOT / 'CURRENT_PUBLICATION_LOCATORS.json')
        require(locators['labels'] == mapping, 'root current locators differ')
        require(locators['canonical_map_sha256'] == digest(trad / 'canonical_label_to_final.json'),
                'root locator map pin differs')
        by_role = {d['role']: d for d in documents}
        require(locators['pdf_sha256'] == by_role['traditional']['sha256'] and
                locators['pdf_pages'] == counts['traditional'], 'root locator PDF pin differs')
        with fitz.open(ROOT / by_role['traditional']['path']) as pdf:
            for label, row in mapping.items():
                page = int(row['physical_pdf_page'])
                require(1 <= page <= len(pdf) and pdf[page - 1].get_label() == str(row['printed_page']),
                        'traditional page locator differs: ' + label)
        visual = read(ROOT / 'editable/visual_guide/VISUAL_TO_TRADITIONAL_CROSSWALK.json')
        require(len(visual['pages']) == 42, 'visual page inventory differs')
        visual_targets = 0
        with fitz.open(ROOT / by_role['visual_guide']['path']) as pdf:
            for row in visual['pages']:
                page = int(row['visual_physical_pdf_page'])
                require(1 <= page <= len(pdf) and pdf[page - 1].get_label() == str(row['visual_printed_page']),
                        'visual page locator differs')
                for target in row['traditional_targets']:
                    expected = mapping[target['final_label']]
                    require(all(str(target[k]) == str(expected[k]) for k in
                                ['number', 'printed_page', 'physical_pdf_page']), 'visual target differs')
                    visual_targets += 1
        lean = read(ROOT / 'editable/lean_guide/generated/traditional_crosswalk.json')
        lean_targets = 0
        for row in walk({k: v for k, v in lean.items() if k != 'provenance'}):
            if {'final_label', 'printed_page', 'physical_pdf_page'} <= row.keys():
                expected = mapping[row['final_label']]
                require(all(str(row[k]) == str(expected[k]) for k in
                            ['printed_page', 'physical_pdf_page']), 'Lean target differs')
                lean_targets += 1
        require(len(mapping) == 500 and visual_targets == 75 and lean_targets == 58,
                'navigation inventory differs')
        for name, pin in lean['provenance'].items():
            if name.endswith(('.json', '.tex')):
                require(digest(trad / name) == pin, 'Lean navigation source pin differs: ' + name)
        require(lean['provenance']['traditional_pdf_sha256'] == by_role['traditional']['sha256'],
                'Lean navigation PDF pin differs')
        for key, expected in {
            'traditional_pdf_sha256': by_role['traditional']['sha256'],
            'visual_pdf_sha256': by_role['visual_guide']['sha256'],
            'traditional_map_sha256': digest(trad / 'canonical_label_to_final.json'),
            'traditional_source_sha256': digest(trad / 'Paper_VI_Traditional_Final.tex'),
            'traditional_source_records_sha256': digest(trad / 'SOURCE_RECORDS.json'),
        }.items():
            require(visual[key] == expected, 'visual navigation pin differs: ' + key)
        for name, value in read(ROOT / 'COMPANION_MAP.json')['crosswalks'].items():
            require(read(ROOT / 'editable' / name) == value, 'root crosswalk differs: ' + name)
        report['checks'].append('500 manuscript labels, 75 visual targets and 58 Lean guide targets')

        preservation = read(EVIDENCE / 'SOURCE_PRESERVATION.json')
        require(preservation['status'] == 'PASS' and preservation['main_source_byte_identical'] and
                preservation['numbered_records_byte_identical'] == 184 and
                preservation['proof_bodies_byte_identical'] == 140 and
                preservation['mathematical_token_changes'] == [], 'source preservation scope differs')
        for key in ['baseline', 'current']:
            row = preservation[key]
            require(digest(ROOT / row['path']) == row['sha256'], 'manuscript preservation binding differs')
        for key in ['original_source_files_unchanged', 'original_download_archives_unchanged',
                    'figures_and_exact_excerpts_unchanged']:
            for row in preservation[key]:
                require(digest(ROOT / row['path']) == row['sha256'], 'preserved file differs: ' + row['path'])
        require(len(preservation['original_source_files_unchanged']) == 739 and
                len(preservation['original_download_archives_unchanged']) == 3, 'original source inventory differs')
        static = read(EVIDENCE / 'STATIC_SOURCE_RECONCILIATION.json')
        require(static['status'] == 'PASS' and static['counts']['scoped_result_records'] == 33 and
                static['counts']['theorem_targets'] == 341 and static['counts']['proof_modules'] == 47 and
                not static['fresh_lean_kernel_run'], 'static formal reconciliation differs')
        with tempfile.TemporaryDirectory(prefix='paper-vi-static-reconciliation-') as temporary:
            current_static = Path(temporary) / 'current.json'
            run_check([sys.executable, '-B', str(ROOT / 'editable/lean_guide/reconcile_sources.py'),
                       '--output', str(current_static)], 'current static source reconciliation')
            require(read(current_static) == static, 'static receipt no longer matches current source/guide records')
        audit = read(EVIDENCE / 'INHERITED_AUDIT_RECONCILIATION.json')
        require(audit['status'].startswith('PASS'), 'inherited audit reconciliation incomplete')
        for row in walk(audit):
            if {'path', 'sha256'} <= row.keys():
                path = ROOT / row['path']
                require(path.resolve().is_relative_to(ROOT) and digest(path) == row['sha256'],
                        'inherited audit artifact pin differs: ' + row['path'])
            if {'path', 'observed_sha256'} <= row.keys():
                path = ROOT / row['path']
                require(path.resolve().is_relative_to(ROOT) and digest(path) == row['observed_sha256'],
                        'inherited monograph artifact pin differs: ' + row['path'])
        report['checks'].append('184 records, 140 proofs, 739 original sources and inherited formal scope')

        finite = read(EVIDENCE / 'finite/FINITE_REPLAY.json')
        expected_suites = {'source_integrity', 'static_pytest_verifier', 'original_sympy_exact',
            'independent_exact_rational', 'numerical_companion', 'annals_numerical',
            'strengthened_baseline', 'strengthened_expanded', 'monograph_figure_models',
            'guide_extensions_exact', 'guide_plates'}
        require(finite['status'] == 'PASS_STATED_FINITE_SCOPE' and len(finite['runs']) == 11 and
                {r['suite'] for r in finite['runs']} == expected_suites, 'finite replay suite set differs')
        require(finite['script_sha256'] == digest(ROOT / 'scripts/replay_finite.py'), 'finite runner pin differs')
        for row in finite['runs']:
            require(row['execution_exit'] == row['manifest_validation_exit'] == 0 and
                    row['run_status'] == 'completed' and row['counts']['status'] == 'PASS',
                    'finite execution not accepted: ' + row['suite'])
            result = read((ROOT / row['manifest']).parent / 'result.json')
            require(all(k == 'count_type' or (k in result and v == result[k])
                        for k, v in row['counts'].items()), 'finite summary differs from raw result: ' + row['suite'])
            run_check([sys.executable, '-B', str(ROOT / 'verification/monograph_checks/tools/validate_manifest.py'),
                       str(ROOT / row['manifest']), '--root', str(ROOT)], 'finite evidence binding ' + row['suite'])
        controls = read(EVIDENCE / 'integrity_controls/CONTROLS.json')
        require(controls['status'] == 'PASS' and controls['test_methods'] == 21 and
                controls['failures'] == controls['errors'] == controls['skips'] == 0,
                'integrity control result differs')
        for name, pin in controls['source_sha256'].items():
            require(digest(ROOT / 'scripts' / name) == pin, 'integrity control source pin differs')
        replay = read(EVIDENCE / 'ISOLATED_PDF_REPLAY.json')
        require(replay['status'] == 'PASS' and len(replay['documents']) == 3, 'PDF replay incomplete')
        require({r['document'] + '.pdf' for r in replay['documents']} ==
                {Path(d['path']).name for d in documents}, 'PDF replay reader set differs')
        for row in replay['documents']:
            name = row['document'] + '.pdf'
            expected = next(d for d in documents if Path(d['path']).name == name)
            require(row['build_returncode'] == 0 and row['page_count_match'] and row['extracted_text_match'] and
                    row['pages'] == expected['pages'] and row['shipped_pdf_sha256'] == expected['sha256'],
                    'PDF replay binding differs: ' + name)
        geometry = read(EVIDENCE / 'FINAL_GEOMETRY_AND_LINKS.json')
        require(geometry['status'] == 'PASS' and len(geometry['documents']) == 3, 'geometry QA incomplete')
        require({r['file'] for r in geometry['documents']} == {Path(d['path']).name for d in documents},
                'geometry reader set differs')
        for row in geometry['documents']:
            require(digest(ROOT / 'papers' / row['file']) == row['sha256'], 'geometry PDF binding differs')
            require(not row['out_of_page_text_spans'] and not row['replacement_character_pages'] and
                    not row['invalid_local_destinations'], 'geometry diagnostics not empty')
        visual_qa = read(EVIDENCE / 'visual_qa/ALL_REVIEW.json')
        require(visual_qa['status'].startswith('PASS') and
                visual_qa['total_pdf_pages'] == edition['total_pages'] and
                visual_qa['traditional_sha256'] == by_role['traditional']['sha256'],
                'visual review main PDF binding differs')
        guide_qa = visual_qa['guide_review']['documents']
        require(len(guide_qa) == 2 and {Path(r['pdf']).name for r in guide_qa} ==
                {Path(by_role[k]['path']).name for k in ['visual_guide', 'lean_guide']},
                'visual guide review set differs')
        for row in guide_qa:
            require(digest(ROOT / 'papers' / Path(row['pdf']).name) == row['sha256'] and
                    row['all_pages_rendered'] and row['contact_reviewed_all_pages'],
                    'visual guide review binding differs')
        captures = read(EVIDENCE / 'visual_qa/CAPTURE_INDEX.json')
        require(captures['status'] == 'PASS' and len(captures['captures']) == 49,
                'portable visual capture inventory differs')
        for row in captures['captures'] + captures['review_reports']:
            require(digest(ROOT / row['path']) == row['sha256'], 'visual capture/report pin differs')
        licenses = read(ROOT / 'LICENSE_STATUS.json')
        require(licenses['status'] == 'OPEN_LICENSES_APPLIED', 'explicit licenses absent')
        for name, pin in licenses['files'].items():
            require(digest(ROOT / name) == pin, 'license pin differs: ' + name)
        report['checks'].append('11 finite evidence manifests, 21 verifier controls, PDF replay, geometry and licenses')
        report['status'] = 'PASS'
    except Exception as exc:
        report['error'] = str(exc)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
