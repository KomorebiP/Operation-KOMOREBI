#!/usr/bin/env python3
"""Bind completed direct visual reviews and pixel invariants to the five PDFs."""
from pathlib import Path
import datetime, hashlib, json

BASE = Path('/workspace/scratch/604befec1954')
ROOT = BASE / 'paperxi_release'
EVIDENCE = ROOT / 'evidence/release_1_1'

def read(name):
    return json.loads((EVIDENCE / name).read_text())

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

assembly = read('ASSEMBLY_RASTER_CHECK.json')
assert assembly['status'] == 'passed'
rows = {r['kind']: r for r in assembly['records']}
assert set(rows) == {'traditional', 'visual_guide', 'lean_guide'}
assert all(r['all_pages_pixel_identical'] for r in rows.values())
for r in rows.values():
    assert sha(ROOT / 'publication/pdfs' / r['file']) == r['assembled_pdf_sha256']
main = read('MAIN_VISUAL_REVIEW.json')
intro = read('MAIN_INTRO_REVISION.json')
visual = read('visual_guide_review.json')
lean = read('LEAN_VISUAL_REVIEW.json')
cover = read('COVER_MOTIF_REMOVAL.json')
assert main['review_status'] == intro['status'] == lean['status'] == 'passed'
assert intro['previous_reviewed_sha256'] == main['current_sha256']
assert intro['current_sha256'] == rows['traditional']['raw_pdf_sha256']
assert intro['changed_pages'] == [6]
assert sorted(intro['equal_pages'] + [6]) == list(range(1, 112))
assert visual['status'] == 'passed_after_two_usability_corrections'
assert visual['raw_pdf_sha256'] == rows['visual_guide']['raw_pdf_sha256']
assert lean['raw_pdf_sha256'] == rows['lean_guide']['raw_pdf_sha256']
assert lean['page_count'] == rows['lean_guide']['pages']
assert cover['visual_inspection']['status'] == 'passed_visual_inspection'

reviews = []
def add(kind, contact, detail, receipts, findings):
    row = rows[kind]
    assert all(1 <= p <= row['pages'] for p in contact + detail)
    reviews.append({'file': row['file'], 'pdf_sha256': row['assembled_pdf_sha256'],
        'page_count': row['pages'], 'contact_pages': sorted(set(contact)),
        'detailed_pages': sorted(set(detail)), 'review_receipts': receipts,
        'raw_to_final_binding': 'ASSEMBLY_RASTER_CHECK.json', 'findings': findings})

add('traditional', [p for p in main['contact_pages'] if p != 6],
    sorted(set(main['detailed_pages'] + intro['detailed_pages'])),
    ['MAIN_VISUAL_REVIEW.json', 'MAIN_INTRO_REVISION.json'], [
        'The 111-page reader has complete visual coverage through the contact-reviewed draft and direct review of its changed page 6. The other 110 pages are pixel-identical to that reviewed draft.',
        'The 57 underfull hbox diagnostics were reviewed in the page layout. No clipped, overlapping, missing or blank content was found; no overfull boxes, missing glyphs or unresolved references/citations were reported.',
        'Every raw compiled page is pixel-identical to its final companion-link-assembled page.'
    ])
add('visual_guide', [p for p in visual['method']['all_pages_contact_review'] if p != 52],
    visual['method']['full_resolution_page_review'],
    ['visual_guide_review.json', 'visual_guide_revision_comparison.json'], [
        'All 53 pages were contact-reviewed; the final command correction on page 52 received direct full-resolution review. The other 52 pages are pixel-identical to the contact-reviewed version.',
        'The reader-route bookmark and literal two-hyphen command option were corrected and verified. Targeted mathematical displays and figure labels remain legible.',
        'Every raw compiled page is pixel-identical to its final companion-link-assembled page.'
    ])
add('lean_guide', lean['contact_pages'], lean['detailed_pages'],
    ['LEAN_VISUAL_REVIEW.json'], lean['findings'] + [
        'Every raw compiled page is pixel-identical to its final companion-link-assembled page.'
    ])
for d in cover['documents']:
    assert sha(ROOT / 'publication/pdfs' / d['filename']) == d['output_sha256']
    assert d['page_count_before'] == d['page_count_after']
    reviews.append({'file': d['filename'], 'pdf_sha256': d['output_sha256'],
        'page_count': d['page_count_after'], 'contact_pages': d['cover_pages'],
        'detailed_pages': d['cover_pages'], 'review_receipts': ['COVER_MOTIF_REMOVAL.json'],
        'findings': [
            'Every changed cover was directly inspected at full-page scale and in a 288-dpi local before/after pair. The decorative branch is absent and adjacent text and cover elements are preserved.',
            'The full document retains its text, page geometry and links. All unchanged pages are pixel-identical to the preserved predecessor at 144 dpi; they are covered by invariant checks rather than a newly claimed complete contact-sheet review.'
        ]})
assert len(reviews) == 5
sources = sorted({name for r in reviews for name in r['review_receipts']} | {'ASSEMBLY_RASTER_CHECK.json'})
result = {'schema_version': 1, 'status': 'passed',
    'recorded_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'script_sha256': sha(Path(__file__)), 'reviews': reviews,
    'source_receipt_sha256': {name: sha(EVIDENCE / name) for name in sources},
    'scope': 'Final PDF hash binding of completed visual reviews and documented pixel/content invariants. This receipt does not add a proof audit or external peer review.'}
(EVIDENCE / 'VISUAL_REVIEW.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
print(json.dumps({'status': 'passed', 'pdfs': len(reviews), 'pages': sum(r['page_count'] for r in reviews)}))
