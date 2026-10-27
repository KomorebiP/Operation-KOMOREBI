"""Validate exported Catalan_Constant reader files and current layout/font records."""
from pathlib import Path
import hashlib
import json
import re
import fitz

ROOT = Path(__file__).resolve().parent
for folder in ('paper', 'visual'):
    for source in (ROOT / folder).glob('*.tex'):
        raw = source.read_bytes()
        assert not any(c < 32 and c not in (9, 10, 13) for c in raw), source
        content = raw.decode('utf-8')
        assert not re.search(r'(?<![\\A-Za-z])qquad\b', content), source
docs = {}
for project, name in [('paper', 'Komorebi_Catalan_Constant_Conjecture_Piece_v1.0.pdf'),
                      ('visual', 'Komorebi_Catalan_Constant_Visual_Guide_v1.0.pdf')]:
    path = ROOT / 'output' / 'pdf' / name
    document = fitz.open(path)
    text = '\n'.join(page.get_text() for page in document)
    assert len(document) > 0, (project, len(document))
    assert '\ufffd' not in text
    assert not re.search(r'\bTODO\b|Figure pending|PLACEHOLDER', text)
    assert 'Komorebi P.' in text
    for page in document:
        for link in page.get_links():
            uri = link.get('uri', '')
            assert not uri.startswith('file:'), (project, uri)
            assert '/api/library/' not in uri, (project, 'nonportable Library download link')
            assert link.get('kind') not in (fitz.LINK_LAUNCH, fitz.LINK_GOTOR), (project, 'external file action')
    log = (ROOT / project / 'main.log').read_text(errors='replace')
    issues = [line for line in log.splitlines() if re.search(
        r'Overfull|undefined|LaTeX Error|Missing character|destination with the same identifier', line)]
    assert not issues, (project, issues)
    docs[name] = {'pages': len(document), 'words_extracted': len(text.split()),
                  'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
fonts = json.loads((ROOT / 'evidence/FONT_VALIDATION.json').read_text())
assert fonts['status'] == 'passed'
for name, record in docs.items():
    assert fonts['documents'][name]['sha256'] == record['sha256']
layout = json.loads((ROOT / 'evidence/FULL_LAYOUT_VALIDATION.json').read_text())
assert layout['status'] == 'passed'
for name, record in docs.items():
    checked = layout['documents'][name]
    assert checked['pdf_sha256'] == record['sha256']
    assert checked['manual_visual_review'] == 'passed'
    assert checked['rendered_pages'] == record['pages']
    reviewed = {page for item in checked['manual_coverage'] for page in item['pages']}
    assert reviewed == set(range(1, record['pages'] + 1))
report = {'status': 'passed', 'documents': docs,
          'scope': 'Export existence, text extraction, author, page counts, resolved TeX output, and current font evidence. Mathematical validity and visual page inspection have separate reports.'}
(ROOT / 'evidence/SOURCE_VALIDATION.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
