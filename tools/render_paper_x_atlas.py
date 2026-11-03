"""Check the full Paper X PDF and render its 29 original drawing views."""
import argparse
from pathlib import Path
import re
import unicodedata
from paper_x_atlas import SPEC
from render_worked_atlases import build,digest


def validate_pdf_pages(root):
    import pypdfium2 as pdfium
    compact=lambda text:re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKC',text).lower())
    raw=(root/SPEC['pdf']).read_bytes()
    if digest(raw)!=SPEC['sha256']:raise ValueError('Changed retained Paper X visual PDF')
    with pdfium.PdfDocument(raw) as document:
        if len(document)!=33:raise ValueError('Changed Paper X PDF page inventory')
        checks=[*SPEC['opening_pdf_pages'],*[dict(pdf_page=r['number']+3,title=r['title']) for r in SPEC['pdf_page_checks']]]
        for record in checks:
            page=document[record['pdf_page']-1]
            try:
                textpage=page.get_textpage()
                try:
                    if compact(record['title']) not in compact(textpage.get_text_range()):raise ValueError('Changed Paper X PDF section title')
                finally:textpage.close()
            finally:page.close()
    return len(checks)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    args=parser.parse_args();validate_pdf_pages(args.root);build(args.root,'paper-x',SPEC)
