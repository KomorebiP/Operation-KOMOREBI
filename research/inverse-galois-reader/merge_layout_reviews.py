"""Combine actual page-review records with current immutable render checks."""
from pathlib import Path
import hashlib
import json
import fitz

ROOT = Path(__file__).resolve().parent
QA = ROOT.parent / 'tmp/pdfs/galois_qa'
REVIEW = ROOT / 'evidence/layout'
checks = json.loads((QA / 'layout_checks.json').read_text())
names = {'paper': 'Komorebi_Inverse_Galois_Conjecture_Piece_v1.0.pdf',
         'visual': 'Komorebi_Inverse_Galois_Visual_Guide_v1.0.pdf'}
documents = {}
for project, name in names.items():
    path = ROOT / 'output/pdf' / name
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    current = checks[project]
    count = len(fitz.open(path))
    assert current['pdf_sha256'] == digest
    assert current['rendered_pages'] == count
    assert current['original_unchanged_during_render']
    assert not current['outside_page_words']
    assert not current['tex_warnings_to_resolve']
    assert not current['replacement_characters']
    assert not current['unresolved_placeholders']
    coverage = []
    for record_path in sorted(REVIEW.glob('manual_*.json')):
        record = json.loads(record_path.read_text())
        if record['project'] != project:
            continue
        assert record['pdf_sha256'] == digest, record_path
        assert record['status'] == 'passed', record_path
        pages = record['pages']
        assert pages and all(type(p) is int and 1 <= p <= count for p in pages)
        declared = record.get('image_sha256', record.get('png_sha256', record.get('page_png_sha256')))
        if declared is None:
            declared = {str(row['page']): row['final_png_sha256']
                        for row in record.get('page_hashes', [])}
        for page in pages:
            png = QA / project / f'page-{page:02d}.png'
            assert png.is_file(), (record_path, page)
            assert declared.get(str(page)) == hashlib.sha256(png.read_bytes()).hexdigest(), (record_path, page)
        coverage.append({'reviewer': record['reviewer'], 'pages': pages,
                         'record': str(record_path.relative_to(ROOT)),
                         'method': record['method']})
    seen = {p for c in coverage for p in c['pages']}
    assert seen == set(range(1, count + 1)), (project, sorted(set(range(1, count + 1)) - seen))
    documents[name] = dict(current, manual_visual_review='passed',
                           manual_coverage=coverage)
out = {'date': '2026-10-09', 'status': 'passed', 'documents': documents,
       'scope': 'Every page of both final readers has an actual visual review record. Scientific data, proof and external source audits are separate records.'}
(ROOT / 'evidence/FULL_LAYOUT_VALIDATION.json').write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps({'status': 'passed', 'documents': {n:d['pages'] for n,d in documents.items()}}, indent=2))
