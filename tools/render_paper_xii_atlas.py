"""Check all 27 retained Paper XII plates and render their 21 original drawing views."""
import argparse
from pathlib import Path
import re
import unicodedata
from paper_xii_atlas import SPEC
from render_worked_atlases import build,digest


def validate_pdf_pages(root):
    import pypdfium2 as pdfium
    compact=lambda text:re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKC',text).lower())
    raw=(root/SPEC['pdf']).read_bytes()
    if digest(raw)!=SPEC['sha256']:raise ValueError('Changed Paper XII visual PDF')
    with pdfium.PdfDocument(raw) as document:
        if len(document)!=28:raise ValueError('Changed Paper XII PDF page inventory')
        for row in SPEC['pdf_page_checks']:
            page=document[row['number']]
            try:
                textpage=page.get_textpage()
                try:
                    if compact(row['title']) not in compact(textpage.get_text_range()):raise ValueError('Changed Paper XII PDF title')
                finally:textpage.close()
            finally:page.close()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);args=parser.parse_args();validate_pdf_pages(args.root);build(args.root,'paper-xii',SPEC)
