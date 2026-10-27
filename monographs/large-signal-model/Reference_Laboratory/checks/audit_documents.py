"""Check final PDF structure using optional PyMuPDF and pdffonts.

Visual inspection of rendered pages is a separate release step, not claimed by
this script. Requires prebuilt documents. No fonts are copied or redistributed.
"""
from pathlib import Path
import json
import subprocess
ROOT=Path(__file__).resolve().parents[1]


def validate_quality(stem: str, result: dict) -> None:
    """Explicit gates remain active when Python assertion statements are disabled."""
    if not isinstance(result.get('pages'), int) or result['pages'] < 1:
        raise ValueError(stem + ': no document pages')
    if (result.get('text_outside_page') != [] or
            result.get('replacement_glyph_pages') != [] or
            result.get('font_embedding_all_yes') is not True):
        raise ValueError(stem + ': page bounds, glyph or font gate failed')
    for key in ('overfull_boxes', 'underfull_boxes', 'undefined_reference_messages',
                'duplicate_destination_messages'):
        if result.get(key) != 0:
            raise ValueError(stem + ': failed ' + key)


def main():
    import fitz
    report={}
    for stem in ['FOUNDATIONS','READING_GUIDE','PROOF_REGISTER','VISUAL_ATLAS']:
        doc=fitz.open(ROOT/'theory'/f'{stem}.pdf')
        log=(ROOT/'verification'/f'{stem}_latex_final.log').read_text()
        fonts=subprocess.run(['pdffonts',str(ROOT/'theory'/f'{stem}.pdf')],capture_output=True,text=True,check=True).stdout
        (ROOT/'verification'/f'{stem}_fonts.txt').write_text(fonts)
        bad=[];replacement=[]
        for i,page in enumerate(doc):
            if '\ufffd' in page.get_text():replacement.append(i+1)
            for block in page.get_text('blocks'):
                if len(block)>4 and isinstance(block[4],str) and block[4].strip():
                    b=fitz.Rect(block[:4]);rect=page.rect
                    if b.x0<-1 or b.y0<-1 or b.x1>rect.width+1 or b.y1>rect.height+1:
                        bad.append({'page':i+1,'box':list(b)})
        result={'pages':len(doc),'overfull_boxes':log.count('Overfull'),'underfull_boxes':log.count('Underfull'),
                'undefined_reference_messages':log.count('undefined references'),
                'duplicate_destination_messages':log.count('duplicate ignored'),'text_outside_page':bad,
                'replacement_glyph_pages':replacement,
                'font_embedding_all_yes':bool(fonts.splitlines()[2:]) and all(len(row.split()) >= 6 and row.split()[-5]=='yes' for row in fonts.splitlines()[2:] if row.strip())}
        report[stem]=result
        validate_quality(stem, result)
    (ROOT/'verification'/'pdf_quality.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
