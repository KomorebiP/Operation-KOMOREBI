"""Check final PDF structure using optional PyMuPDF and pdffonts.

Visual inspection of rendered pages is a separate release step, not claimed by
this script. Requires prebuilt documents. No fonts are copied or redistributed.
"""
from pathlib import Path
import json
import subprocess
import fitz
ROOT=Path(__file__).resolve().parents[1]


def main():
    report={}
    for stem in ['FOUNDATIONS','READING_GUIDE','PROOF_REGISTER']:
        doc=fitz.open(ROOT/'theory'/f'{stem}.pdf')
        log=(ROOT/'verification'/f'{stem}_latex_pass2.log').read_text()
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
                'font_embedding_all_yes':all(row.split()[-5]=='yes' for row in fonts.splitlines()[2:] if row.strip())}
        report[stem]=result
        assert not bad and not replacement and result['font_embedding_all_yes']
        assert result['overfull_boxes']==result['undefined_reference_messages']==result['duplicate_destination_messages']==0
    (ROOT/'verification'/'pdf_quality.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
