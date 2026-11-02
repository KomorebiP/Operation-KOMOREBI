"""Reproduce Paper VIII's 30 original PDF drawings with pypdfium2."""
import argparse
import re
import unicodedata
from pathlib import Path
from paper_viii_atlas_sources import SPEC
from render_worked_atlases import build


def validate_pdf_pages(root):
    import pypdfium2 as pdfium
    from render_worked_atlases import digest
    raw=(root/SPEC['pdf']).read_bytes()
    if digest(raw)!=SPEC['sha256']:raise ValueError('Changed retained Paper VIII visual PDF')
    compact=lambda text:re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKC',text).lower())
    with pdfium.PdfDocument(raw) as document:
        if len(document)!=SPEC['plates']+SPEC['offset']:raise ValueError('Paper VIII PDF page inventory changed')
        for record in SPEC['pdf_page_checks']:
            page=document[record['pdf_page']-1]
            try:
                textpage=page.get_textpage()
                try:
                    text=compact(textpage.get_text_range());footer=textpage.get_text_bounded(0,0,page.get_width(),80)
                    if any(compact(record[key]) not in text for key in ('title','locator')) or str(record['plate']) not in footer.split():
                        raise ValueError('Paper VIII PDF title, locator or page label changed: '+str(record['plate']))
                finally:textpage.close()
            finally:page.close()
    return len(SPEC['pdf_page_checks'])

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    args=parser.parse_args();validate_pdf_pages(args.root);build(args.root,'paper-viii',SPEC)
