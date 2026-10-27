#!/usr/bin/env python3
"""Optional PDF geometry/text preflight. Requires PyMuPDF; does not replace visual review."""
from __future__ import annotations
import hashlib,json,re,subprocess
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[1]
def main():
    pdf=ROOT/'build/Machine_Societies_v1.0.0.pdf';doc=fitz.open(pdf)
    outside=[];markers=[];counts=[]
    for i,p in enumerate(doc):
        words=p.get_text('words');counts.append(len(words));text=p.get_text()
        for w in words:
            if w[0]<-0.5 or w[1]<-0.5 or w[2]>p.rect.width+0.5 or w[3]>p.rect.height+0.5:outside.append([i+1,*w[:5]])
        if '\ufffd' in text or '??' in text:markers.append(i+1)
    log=(ROOT/'build/Machine_Societies_v1.0.0.log').read_text(errors='replace')
    diagnostics=[l for l in log.splitlines() if re.search(r'Warning|Overfull|Underfull|undefined|Missing character',l)]
    font=subprocess.run(['pdffonts',str(pdf)],capture_output=True,text=True,check=True).stdout
    (ROOT/'validation/pdf_fonts.txt').write_text(font)
    # pdffonts reports embedded, subset, Unicode flags after the encoding field.
    unembedded=[l for l in font.splitlines()[2:] if re.search(r'\sno\s+(?:yes|no)\s+(?:yes|no)\s+\d+\s+\d+\s*$',l)]
    result={'status':'PASS' if not(outside or markers or diagnostics or unembedded) else 'FAIL',
            'pages':len(doc),'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),
            'out_of_page_words':outside,'unresolved_or_replacement_marker_pages':markers,
            'compiler_diagnostics':diagnostics,'unembedded_font_lines':unembedded,'page_word_counts':counts,
            'scope':'Geometry, extracted-text markers and compiler/font diagnostics. Separate rendered-page review is recorded.'}
    (ROOT/'validation/pdf_preflight.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='page_word_counts'},indent=2))
    return result['status']!='PASS'
if __name__=='__main__':raise SystemExit(main())
