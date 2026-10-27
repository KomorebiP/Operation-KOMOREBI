#!/usr/bin/env python3
"""Optional PDF geometry, text, font and rendering preflight. Requires PyMuPDF.

This does not replace visual inspection. Contact sheets and selected full pages
were inspected during drafting; that scope is recorded in REVIEW_NOTES.md.
"""
from pathlib import Path
import argparse
import json
import re
import subprocess
import fitz
ROOT=Path(__file__).resolve().parents[1]
STEM='Self_Improving_Intelligence_v0.2.0'

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--renders',type=Path)
    args=ap.parse_args()
    doc=fitz.open(ROOT/f'{STEM}.pdf');issues=[];pages=[];figures=[]
    if args.renders:args.renders.mkdir(parents=True,exist_ok=True)
    for i,page in enumerate(doc):
        for word in page.get_text('words'):
            x0,y0,x1,y1=word[:4]
            if min(x0,y0)<-0.5 or x1>page.rect.width+.5 or y1>page.rect.height+.5:
                issues.append({'page':i+1,'word':word[4],'rect':[x0,y0,x1,y1]})
        text=page.get_text()
        if '\ufffd' in text or '??' in text:issues.append({'page':i+1,'unresolved_text':True})
        pages.append({'page':i+1,'words':len(text.split()),'width':page.rect.width,'height':page.rect.height})
        if 'Figure ' in text:figures.append(i+1)
        if args.renders:page.get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False).save(args.renders/f'page-{i+1:02d}.png')
    log=ROOT/'build'/f'{STEM}.log'
    diagnostics=[]
    if log.exists():diagnostics=[line for line in log.read_text(errors='replace').splitlines()
       if any(x in line for x in ('Warning','Overfull','Underfull','Missing character'))]
    fonts=subprocess.run(['pdffonts',str(ROOT/f'{STEM}.pdf')],capture_output=True,text=True,check=True).stdout
    (ROOT/'validation'/'pdf_fonts.txt').write_text(fonts)
    # pdffonts reports fixed columns after a line of dashes. Parse embedded=yes.
    font_lines=fonts.splitlines()[2:];unembedded=[]
    for line in font_lines:
        tokens=line.split()
        if len(tokens)>=8 and tokens[-5]!='yes':unembedded.append(line)
    result={'status':'PASS' if not issues and not diagnostics and not unembedded else 'FAIL',
       'page_count':len(doc),'page_geometry':pages,'figure_pages':figures,'text_geometry_issues':issues,
       'latex_diagnostics':diagnostics,'unembedded_font_rows':unembedded,
       'renderer':f'PyMuPDF {fitz.VersionBind}','rendered_all_pages':args.renders is not None,
       'visual_review_is_separate':True}
    (ROOT/'validation'/'pdf_preflight.json').write_text(json.dumps(result,indent=2)+'\n')
    print(f"{result['status']}: {len(doc)} pages, {len(issues)} geometry/text issues, {len(diagnostics)} LaTeX diagnostics.")
    if result['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
