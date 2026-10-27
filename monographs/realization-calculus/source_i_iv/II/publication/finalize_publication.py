#!/usr/bin/env python3
"""Bind separately accepted scope and complete visual QA to the exact current PDFs."""
from pathlib import Path
import argparse
import json
from current_publication import ROOT, configuration, load_scope, sha, scope_summary

PUB = ROOT / 'publication'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--qa', type=Path, required=True)
parser.add_argument('--map', type=Path)
parser.add_argument('--edition-date')
parser.add_argument('--accepted-map-status', required=True,
                    help='Exact status already granted by the separate formal acceptance process')
args = parser.parse_args()
map_path, day = configuration(args.map, args.edition_date)
scope, counts = load_scope(map_path)
if scope['status'] != args.accepted_map_status:
    raise SystemExit('Correspondence does not have the separately accepted status requested')


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


qa_path = args.qa.resolve()
if not qa_path.is_relative_to(ROOT):
    raise SystemExit('Place the final QA receipt inside the package')
qa = read(qa_path)
if qa['visual_review'] != 'PASS' or not qa['all_pages_rendered']:
    raise SystemExit('Complete rendering and visual review are required')
manifest_path = PUB / 'CURRENT_PUBLICATION_MANIFEST.json'
manifest = read(manifest_path)
if manifest['current_correspondence']['sha256'] != sha(map_path):
    raise SystemExit('Publication metadata uses a different correspondence')
if manifest['edition_date'] != day.isoformat():
    raise SystemExit('Publication metadata uses a different edition date')
qa_documents = {item['file']: item for item in qa['documents']}
if set(qa_documents) != {item['path'] for item in manifest['documents']}:
    raise SystemExit('Visual QA does not cover exactly the current reader set')
for document in manifest['documents']:
    pdf = ROOT / document['path']
    review = qa_documents[document['path']]
    if review['visual_review'] != 'PASS' or any(bool(value) for value in review['issues'].values()):
        raise SystemExit('Document visual review is incomplete: ' + document['path'])
    if document['sha256'] != sha(pdf) or review['pdf_sha256'] != sha(pdf):
        raise SystemExit('PDF differs from its build or visual review: ' + document['path'])
    scope_check = review.get('current_scope_text_check', {})
    if not all(scope_check.get(key) for key in ['accepted_count_phrase_present', 'open_bridge_state_matches']):
        raise SystemExit('PDF scope text has not been checked against the selected correspondence: ' + document['path'])
    if document['pages'] != review['pages']:
        raise SystemExit('PDF page count differs from its review')
    for relative, expected in document['actual_input_sha256'].items():
        if sha(ROOT / relative) != expected:
            raise SystemExit('PDF source changed after build: ' + relative)
if sum(item['pages'] for item in manifest['documents']) != qa['total_pages']:
    raise SystemExit('Visual QA total page count differs from the current reader set')
navigation = read(PUB / 'CURRENT_NAVIGATION_BUILD.json')
traditional = next(item for item in manifest['documents'] if item['role'] == 'traditional')
if navigation['destination_page_mismatches'] or navigation['updated_plate_sources']:
    raise SystemExit('Navigation has unresolved changes')
if navigation['traditional_pdf_sha256'] != traditional['sha256']:
    raise SystemExit('Navigation is not bound to the exact traditional PDF')

state = 'PUBLICATION_READY_FOR_RECORDED_SCOPE'
summary = scope_summary(scope, counts)
qa_record = {'path': str(qa_path.relative_to(ROOT)), 'sha256': sha(qa_path),
             'total_pages': qa['total_pages'], 'visual_review': 'PASS'}
manifest.update(state=state, page_qa=qa_record)
manifest['boundary'] = ('The exact PDFs passed compilation, navigation and complete visual review. '
                        + summary + ' The separate package release decision remains in RELEASE_STATUS.json.')
write(manifest_path, manifest)
edition_path = ROOT / 'EDITION.json'
edition = read(edition_path)
edition.update(state=state, page_qa=qa_record)
write(edition_path, edition)
series_path = ROOT / 'SERIES_STATUS.json'
series = read(series_path)
for row in series['papers']:
    if row.get('paper') == 'II':
        row.update(traditional='publication_ready', visual_guide='publication_ready',
                   lean_guide='publication_ready', publication_state=state, page_qa=qa_record,
                   source_scope=summary + ' Historical 25-row and 160-target contracts remain separate.')
series.update(run_state='Paper_II_publication_ready_for_recorded_scope', active_authoring_papers=[])
write(series_path, series)
for relative in ['README.txt', 'CURRENT_READING_EDITION.txt', 'publication/README.txt']:
    path = ROOT / relative
    text = path.read_text().split('\nFINAL PUBLICATION REVIEW\n', 1)[0]
    text = text.replace('Current publication state: REVIEW_BUILD', 'Current publication state: ' + state)
    text = text.replace('Review build with correspondence status:', 'Reviewed reading edition with correspondence status:')
    text = text.replace('The generated build remains REVIEW_BUILD until separate visual\nQA and publication review are accepted.',
                        'The current exact PDFs have passed complete visual QA and publication review.')
    text += ('\nFINAL PUBLICATION REVIEW\n'
             f'All {qa["total_pages"]} pages passed rendering and visual review. Navigation\n'
             'is bound to the exact PDFs. Evidence: ' + qa_record['path'] + '\n'
             + summary + '\n'
             'The correspondence status is copied from the separate accepted map.\n'
             'Publication does not make or extend a mathematical acceptance decision.\n'
             'Root RELEASE_STATUS.json records the separate package release decision.\n')
    path.write_text(text)
report = {'schema': 'paper-ii-final-publication-review/2', 'state': state,
          'edition_date': day.isoformat(), 'current_correspondence': str(map_path.relative_to(ROOT)),
          'current_correspondence_sha256': sha(map_path), 'recorded_status': scope['status'],
          'proof_counts': counts, 'page_qa': qa_record, 'total_pages': qa['total_pages'],
          'pdfs': [{key: item[key] for key in ['path', 'pages', 'sha256']} for item in manifest['documents']],
          'boundary': 'Publication readiness only. Formal correspondence, root release status and package checksum manifest are not modified.'}
write(PUB / 'FINAL_PUBLICATION_REVIEW.json', report)
print(json.dumps(report, indent=2))
