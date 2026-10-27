#!/usr/bin/env python3
"""Build the current readers and bind their exact source scope without granting acceptance."""
from pathlib import Path
import argparse
import json
import shutil
import subprocess
import sys
import fitz
from current_publication import ROOT, configuration, display_date, load_scope, sha, scope_summary

PUB = ROOT / 'publication'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--map', type=Path)
parser.add_argument('--edition-date', help='ISO edition date, independent of formal evidence dates')
parser.add_argument('--metadata-only', action='store_true')
args = parser.parse_args()
map_path, day = configuration(args.map, args.edition_date)
scope, counts = load_scope(map_path)
relative_map = str(map_path.relative_to(ROOT))


def run(*arguments):
    subprocess.run([sys.executable, *map(str, arguments)], cwd=ROOT, check=True)


# Preserve the incoming root publication metadata before any current build writes it.
history = PUB / 'history' / ('pre_' + day.isoformat())
history.mkdir(parents=True, exist_ok=True)
for relative in ['EDITION.json', 'CURRENT_READING_EDITION.txt', 'SERIES_STATUS.json',
                 'README.txt', 'publication/README.txt', 'publication/CURRENT_PUBLICATION_MANIFEST.json']:
    source = ROOT / relative
    target = history / relative.replace('/', '_')
    if source.exists() and not target.exists():
        shutil.copy2(source, target)

if not args.metadata_only:
    run(PUB / 'sync_current_scope.py', '--map', map_path, '--edition-date', day.isoformat())
    for attempt in range(4):
        run(PUB / 'build_publication.py', '--edition-date', day.isoformat(), 'Paper_II_Traditional_Final.pdf')
        run(PUB / 'sync_navigation.py')
        navigation = json.loads((PUB / 'CURRENT_NAVIGATION_BUILD.json').read_text())
        if not navigation['updated_plate_sources']:
            break
    else:
        raise SystemExit('Traditional and atlas navigation did not converge')
    run(PUB / 'build_publication.py', '--edition-date', day.isoformat(), 'Paper_II_Visual_Guide_Final.pdf')
    run(PUB / 'build_publication.py', '--edition-date', day.isoformat(), 'Paper_II_Lean_Guide_Final.pdf')

scope_build = json.loads((PUB / 'CURRENT_SCOPE_BUILD.json').read_text())
if scope_build['map_sha256'] != sha(map_path) or scope_build['edition_date'] != day.isoformat():
    raise SystemExit('Generated scope/date differs from the requested current input')
for relative, expected in scope_build['generated'].items():
    if sha(ROOT / relative) != expected:
        raise SystemExit('Generated current publication source changed: ' + relative)

specifications = json.loads((PUB / 'documents.json').read_text())
documents = []
for specification in specifications:
    pdf = PUB / 'pdfs' / specification['file_name']
    stem = pdf.stem
    build = PUB / 'build' / stem
    if not pdf.is_file():
        raise SystemExit('Missing built PDF: ' + str(pdf))
    with fitz.open(pdf) as document:
        pages = len(document)
    destination = ROOT / 'papers' / pdf.name
    shutil.copy2(pdf, destination)
    inputs = {}
    recorder = build / (stem + '.fls')
    if recorder.exists():
        source_parent = ((ROOT / specification.get('source_directory', '.')) / specification['main']).parent
        for line in recorder.read_text(errors='replace').splitlines():
            if line.startswith('INPUT '):
                path = Path(line[6:])
                path = path.resolve() if path.is_absolute() else (source_parent / path).resolve()
                if path.is_file() and path.is_relative_to(ROOT) and not path.is_relative_to(PUB / 'build'):
                    inputs[str(path.relative_to(ROOT))] = sha(path)
    transcript = build / 'build_transcript.txt'
    documents.append({'role': specification['kind'], 'title': specification['title'],
        'path': str(destination.relative_to(ROOT)), 'publication_copy': str(pdf.relative_to(ROOT)),
        'pages': pages, 'bytes': pdf.stat().st_size, 'sha256': sha(pdf),
        'actual_input_sha256': inputs, 'build_log': str(transcript.relative_to(ROOT)),
        'build_log_sha256': sha(transcript)})

state = 'REVIEW_BUILD'
summary = scope_summary(scope, counts)
correspondence = {'path': relative_map, 'sha256': sha(map_path), 'status': scope['status'],
                  'proof_counts': counts, 'release_gates': scope['release_gates']}
manifest = {'schema': 'paper-ii-current-publication-manifest/3', 'edition_date': day.isoformat(),
    'state': state, 'documents': documents, 'total_pages': sum(item['pages'] for item in documents),
    'current_correspondence': correspondence, 'navigation': 'CURRENT_PUBLICATION_LOCATORS.json',
    'boundary': 'PDF compilation and navigation refresh. Formal states are copied from their exact source correspondence. Visual QA and the final publication/package decisions require separate records.'}
(PUB / 'CURRENT_PUBLICATION_MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n')
edition = {'schema': 'komorebi.paper_ii.current_edition.v3', 'author': 'Komorebi P.',
    'edition_date': day.isoformat(), 'title': 'Projector Resolved Seed Calculus II: Refinement Towers, Weighted Transfer, and Integral Separation of Operator Packets',
    'edition_kind': 'Modern Monograph', 'state': state,
    'documents': [{key: value for key, value in item.items() if key in ['role', 'title', 'path', 'pages', 'bytes', 'sha256']} for item in documents],
    'total_pages': manifest['total_pages'], 'current_formal_evidence': correspondence,
    'historical_edition': 'publication/history/2026-10-08/EDITION.json',
    'boundaries': ['Formal states are copied from the current correspondence without promotion.',
                   'Historical 25-row and 160-name counts retain their original source scope.', summary]}
(ROOT / 'EDITION.json').write_text(json.dumps(edition, indent=2) + '\n')

readme = ['KOMOREBI PAPER II', 'Modern Monograph, ' + display_date(day),
          'Current publication state: ' + state, '', 'READING FILES']
for item in documents:
    readme.append('  ' + item['path'] + '    ' + str(item['pages']) + ' pages')
readme += ['', 'Start with the traditional paper for definitions and written proofs. Its',
    'twenty-four worked plates also appear in the standalone visual guide. The',
    'Lean guide begins with the current source and evidence correspondence, then',
    'preserves the inherited 25-row declaration walkthrough.', '', 'CURRENT PROOF SCOPE',
    summary, 'Exact source scope: ' + relative_map, 'Recorded correspondence status: ' + scope['status'] + '.',
    'The publication builder copies the recorded states and gates. It does not',
    'compile Lean, perform semantic acceptance or close a package release.',
    'READ_FIRST.txt and RELEASE_STATUS.json record the package entry points and',
    'the separately accepted release decision. Historical reports retain their',
    'original dates and scope. Current source evidence remains under formal/.',
    '', 'PUBLICATION EVIDENCE', 'The three PDFs build from the current editable sources. Navigation is derived',
    'from the actual traditional PDF and AUX, including named destinations and',
    'printed page references. The publication manifest binds PDF hashes, build',
    'logs, exact local TeX inputs and the selected correspondence. Page QA and',
    'formal replay remain separate records.', '', 'REBUILD',
    '  python3 publication/build_current.py --map ' + relative_map + ' --edition-date ' + day.isoformat(),
    'The correspondence must match the current chapter hashes. XeLaTeX, BibTeX,',
    'bundled fonts and PyMuPDF are required. The older guide data generator',
    'continues to describe its historical canonical input. The deterministic',
    'TeX timestamp is selected from the current edition date.', '', 'SOURCE POLICY',
    'Current editable sources and historical scientific sources remain separate.',
    'The initial edition metadata is retained in publication/history/.',
    'The cover contains no decorative mark in its top right corner.',
    'Project licenses are recorded in LICENSE.md and are not altered by this build.',
    'Other paper releases are untouched.']
(ROOT / 'README.txt').write_text('\n'.join(readme) + '\n')

series_path = ROOT / 'SERIES_STATUS.json'
series = json.loads(series_path.read_text())
series['edition_date'] = day.isoformat()
for row in series['papers']:
    if row.get('paper') == 'II':
        row.update(traditional='review_build', visual_guide='review_build', lean_guide='review_build',
            edition_date=day.isoformat(), documents=edition['documents'], total_pages=edition['total_pages'],
            source_scope=summary, current_formal_evidence=correspondence,
            notes='Current readers and source-bound navigation. Mathematical acceptance and final publication QA are distinct records.')
for key in ['finalized_papers', 'finalized_companion_documents']:
    series.pop(key, None)
series.update(run_state='Paper_II_release_review', active_authoring_papers=['II'],
    freeze_instruction='Current work is limited to Paper II. Other rows retain their historical series scope.',
    notice='Only the Paper II row is current to ' + display_date(day) + '. Consult each other paper current release for its status.')
series_path.write_text(json.dumps(series, indent=2) + '\n')
(ROOT / 'CURRENT_READING_EDITION.txt').write_text('CURRENT READING EDITION\nPaper II Modern Monograph, ' + display_date(day) + '.\nReview build with correspondence status: ' + scope['status'] + '.\nRead the PDFs in papers/. Exact scope and recorded release gates are in\n' + relative_map + '.\nHistorical sources and reports retain their original dates and scope.\n')
(PUB / 'README.txt').write_text('PAPER II CURRENT PUBLICATION\n' + display_date(day) + '\n\nBuild the readers and synchronize page references with:\n  python3 publication/build_current.py --map ' + relative_map + ' --edition-date ' + day.isoformat() + '\n\nThe selected correspondence is read without modification. Its exact source\nhashes, counts, statuses and gates are copied without formal acceptance by\npublication. The generated build remains REVIEW_BUILD until separate visual\nQA and publication review are accepted. Root RELEASE_STATUS.json records the\nseparate package decision.\n\nXeLaTeX, BibTeX, bundled fonts and PyMuPDF are required. Build directories are\nisolated in publication/build/. Readers are copied to papers/ and\npublication/pdfs/. CURRENT_PUBLICATION_MANIFEST.json binds the exact inputs.\n\nHistorical guide generators, sources and reports retain their own dated\ninputs. sync_current_scope.py generates current scope text, while\nsync_navigation.py derives current page references from the built PDF.\n')
print(json.dumps({'state': state, 'edition_date': day.isoformat(),
    'documents': [{key: item[key] for key in ['path', 'pages', 'sha256']} for item in documents],
    'total_pages': manifest['total_pages']}, indent=2))
