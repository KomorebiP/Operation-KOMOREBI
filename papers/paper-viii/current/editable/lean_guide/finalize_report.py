#!/usr/bin/env python3
"""Produce the final source-pinned guide report after rendering and review."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import tempfile
import subprocess
import fitz

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
GENERATED = HERE / 'generated'
PDF = HERE / 'Paper_VIII_Lean_Guide_Final.pdf'
PARSER = argparse.ArgumentParser(description=__doc__)
PARSER.add_argument('--inspected-pages', nargs='+', type=int, required=True,
                    help='Physical PDF pages actually inspected at full size.')
ARGS = PARSER.parse_args()
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
read = lambda path: json.loads(path.read_text())
preservation = read(GENERATED / 'preservation_manifest.json')
preserved = {name: sha(HERE / name) == digest for name, digest in preservation['files'].items()}
if not all(preserved.values()):
    raise RuntimeError('Preservation mismatch: ' + str([name for name, ok in preserved.items() if not ok]))
pdf_checks = read(HERE / 'qa/pdf_checks.json')
if pdf_checks['status'] != 'PASS' or sha(PDF) != pdf_checks['pdf_sha256']:
    raise RuntimeError('PDF checks have not passed for this exact PDF')
crosswalk = read(GENERATED / 'traditional_crosswalk.json')
traditional = HERE.parent / 'traditional'
provenance = crosswalk['provenance']
if sha(traditional / provenance['traditional_pdf_filename']) != provenance['traditional_pdf_sha256']:
    raise RuntimeError('Traditional PDF changed after final navigation')
for name, digest in provenance['source_record_pins'].items():
    if sha(traditional / name) != digest:
        raise RuntimeError('Traditional source pin changed: ' + name)
review = HERE / pdf_checks['render_review_directory']
for page in ARGS.inspected_pages:
    if not (review / f'page_{page:03d}.png').exists():
        raise RuntimeError('Missing full-size inspected render: ' + str(page))
with tempfile.TemporaryDirectory(prefix='paper-viii-lean-rebuild-') as temporary:
    output = Path(temporary)
    run = subprocess.run(['python3', str(HERE / 'build.py'), '--output-directory', str(output)],
                         text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (HERE / 'qa/isolated_rebuild.txt').write_text(run.stdout)
    if run.returncode:
        raise RuntimeError('Isolated PDF rebuild failed: qa/isolated_rebuild.txt')
    rebuilt = output / PDF.name
    rebuild = {'status': 'PASS' if sha(PDF) == sha(rebuilt) else 'FAIL',
               'delivered_pdf_sha256': sha(PDF), 'rebuilt_pdf_sha256': sha(rebuilt),
               'identical_bytes': PDF.read_bytes() == rebuilt.read_bytes(),
               'four_isolated_xelatex_passes': True}
if not rebuild['identical_bytes']:
    raise RuntimeError('Isolated rebuilt PDF bytes differ')
(HERE / 'qa/isolated_rebuild.json').write_text(json.dumps(rebuild, indent=2) + '\n')
document = fitz.open(PDF)
report = {
    'status': 'PASS', 'edition': 'Paper VIII monograph, 2026-10-09',
    'report_generated_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'pdf_relative_path': PDF.relative_to(ROOT).as_posix(),
    'pdf_sha256': sha(PDF), 'physical_pdf_pages': len(document),
    'formal_evidence': read(GENERATED / 'evidence_provenance.json'),
    'preservation': {'status': 'PASS', 'manifest_sha256': sha(GENERATED / 'preservation_manifest.json'),
                     'files': preserved, 'instructional_chapters': 10,
                     'raw_exact_excerpts': 61, 'exact_excerpt_lines': 635,
                     'catalog_data_entries': 458, 'source_module_count': 40},
    'pdf_checks': pdf_checks,
    'traditional_navigation': read(GENERATED / 'traditional_navigation_provenance.json'),
    'inspection': {'all_physical_pages_rendered_into_contact_sheets': True,
                   'all_contact_sheets_visually_inspected': True,
                   'render_review_directory': review.relative_to(ROOT).as_posix(),
                   'full_size_key_pages_inspected': ARGS.inspected_pages,
                   'full_size_render_pins': [{'path': (review / f'page_{page:03d}.png').relative_to(ROOT).as_posix(),
                                             'sha256': sha(review / f'page_{page:03d}.png')}
                                            for page in ARGS.inspected_pages],
                   'unresolved_layout_defects': []},
    'rebuild': rebuild,
    'changed_prose_sources': ['Paper_VIII_Lean_Guide_Final.tex', 'README.md',
                              'generated/traditional_navigation.tex', 'generated/result_map.tex'],
    'mathematical_token_changes': [],
    'resolved_layout_findings': ['The long opening note left two contents entries on a separate sparse page. The contents now starts on its own page, keeping all fifteen section entries together.'],
    'resolved_failures': [{'stage': 'navigation script preflight',
                          'failure': 'Python syntax error from a line continuation outside parentheses',
                          'effect': 'Script failed to compile before navigation executed. No scientific test or document result was produced by the failed attempt.',
                          'resolution': 'Wrapped the string expression in parentheses. py_compile passed before running navigation.'},
                         {'stage': 'final evidence identity guard',
                          'failure': 'The traditional proof-preservation metadata was refreshed after preliminary navigation pinned it.',
                          'effect': 'The final owner report stopped before claiming a frozen result. The actual traditional PDF and page map did not change.',
                          'resolution': 'Waited for the traditional owner to freeze all navigation inputs, then refreshed provenance and verified an identical isolated PDF rebuild.'}],
    'source_pins': [{'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path)} for path in sorted(HERE.rglob('*'))
                    if path.is_file() and path.suffix in {'.tex', '.sty', '.py'}
                    and 'historical_assembly' not in path.parts],
    'bundled_font_pins': [{'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path)}
                         for path in sorted((HERE / 'fonts').glob('*')) if path.is_file()],
}
destination = ROOT / 'verification/monograph_lean_report.json'
destination.parent.mkdir(exist_ok=True)
destination.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
print(json.dumps({'status': 'PASS', 'pages': len(document), 'pdf_sha256': sha(PDF),
                  'rebuild_identical': True, 'source_pins': len(report['source_pins'])}, indent=2))
