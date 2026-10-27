"""Structural PDF checks. Optional dependency: PyMuPDF. Visual review remains required."""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def normalized(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def main() -> int:
    try:
        import fitz
    except ImportError:
        print('PDF review requires PyMuPDF. Install requirements-review.txt.', file=sys.stderr)
        return 2
    document = fitz.open(ROOT / 'Komorebi_Methodology.pdf')
    texts = [page.get_text() for page in document]
    normalized_pages = [normalized(text) for text in texts]
    bad_spans = []
    bad_links = []
    bookmark_mismatches = []
    for page_number, page in enumerate(document, 1):
        rect = page.rect
        for block in page.get_text('dict')['blocks']:
            for line in block.get('lines', []):
                for span in line.get('spans', []):
                    if not span.get('text', '').strip():
                        continue
                    x0, y0, x1, y1 = span['bbox']
                    if x0 < -.5 or y0 < -.5 or x1 > rect.width+.5 or y1 > rect.height+.5:
                        bad_spans.append({'page': page_number, 'text': span['text'], 'bbox': span['bbox']})
        for link in page.get_links():
            if link['kind'] == fitz.LINK_GOTO and not 0 <= link.get('page', -1) < len(document):
                bad_links.append({'page': page_number, 'link': str(link)})
    bookmarks = document.get_toc()
    for level, title, page_number in bookmarks:
        if not 1 <= page_number <= len(document) or normalized(title) not in normalized_pages[page_number-1]:
            bookmark_mismatches.append({'level': level, 'title': title, 'page': page_number})
    warnings = [i+1 for i, text in enumerate(texts) if i >= 4 and len(text.split()) < 150]
    summary = {
        'physical_pages': len(document), 'bookmark_count': len(bookmarks),
        'bookmark_mismatches': bookmark_mismatches, 'invalid_internal_links': bad_links,
        'out_of_page_text_spans': bad_spans,
        'unresolved_reference_markers': sum(t.count('??') for t in texts),
        'replacement_glyphs': sum(t.count('\ufffd') for t in texts),
        'short_body_pages_for_visual_review': warnings,
        'scope': 'Structural checks only. Bookmark titles are matched to their target pages. No semantic or visual-completeness proof.'
    }
    failures = any([bad_spans, bad_links, bookmark_mismatches,
                    summary['unresolved_reference_markers'], summary['replacement_glyphs']])
    summary['status'] = 'FAIL' if failures else 'PASS'
    (ROOT/'audit').mkdir(exist_ok=True)
    (ROOT/'audit/layout_geometry.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k != 'scope'}, indent=2))
    return int(failures)

if __name__ == '__main__':
    raise SystemExit(main())
