#!/usr/bin/env python3
"""Mechanical PDF preflight. Visual inspection remains a separate review step."""
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,re,subprocess
import fitz
ROOT=Path(__file__).resolve().parents[1]
NAMES=['Komorebi_Space_Monograph','Komorebi_Space_Visual_Guide','Komorebi_Space_Lean_Guide']

def main():
    outputs=[];failures=[]
    for name in NAMES:
        p=ROOT/'publication'/f'{name}.pdf'
        d=fitz.open(p);outside=[];empty=[];replacement=[]
        for i,page in enumerate(d):
            t=page.get_text()
            if len(t.strip())<60:empty.append(i+1)
            if '\ufffd' in t:replacement.append(i+1)
            for block in page.get_text('dict')['blocks']:
                for line in block.get('lines',[]):
                    for span in line['spans']:
                        x0,y0,x1,y1=span['bbox']
                        if x0 < -1 or y0 < -1 or x1>page.rect.width+1 or y1>page.rect.height+1:
                            outside.append({'page':i+1,'text':span['text'],'bbox':span['bbox']})
        logpath=ROOT/'audit'/f'{name}_final3.stdout'
        log=logpath.read_text() if logpath.exists() else ''
        bad_log=[line for line in log.splitlines() if re.search(r'Overfull|undefined|^!|Fatal error',line)]
        font_run=subprocess.run(['pdffonts',str(p)],capture_output=True,text=True,check=True)
        font_lines=font_run.stdout.splitlines()[2:]
        # Poppler columns end with embedded/subset/unicode/object/generation.
        unembedded=[s for s in font_lines if len(s.split())>=5 and s.split()[-5]!='yes']
        if outside or empty or replacement or bad_log or unembedded:
            failures.append({'file':p.name,'outside':outside,'empty':empty,'replacement':replacement,'log':bad_log,'unembedded':unembedded})
        (ROOT/'audit'/f'{name}_fonts.txt').write_text(font_run.stdout)
        outputs.append({'file':str(p.relative_to(ROOT)),'pages':len(d),'bytes':p.stat().st_size,
                        'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
                        'text_outside_page':outside,'near_empty_pages':empty,'replacement_character_pages':replacement,
                        'unembedded_fonts':unembedded,'final_build_errors':bad_log,
                        'internal_links':sum(len(page.get_links()) for page in d)})
    text='\n'.join(p.read_text() for p in (ROOT/'source/chapters').glob('*.tex'))
    ids=re.findall(r'\\source\{(KS\d{2})\}',text)
    expected={f'KS{i:02}' for i in range(1,55)}
    if set(ids)!=expected or len(ids)!=54:failures.append({'claim_markers':ids})
    result={'status':'PASS' if not failures else 'FAIL','executed_utc':datetime.now(timezone.utc).isoformat(),
            'documents':outputs,'principal_source_markers':len(ids),'figure_source_count':len(list((ROOT/'source/figures').glob('*.tex'))),
            'failures':failures,'scope':'Mechanical checks of rendered files and source markers. Visual review and mathematical judgment are separate.'}
    (ROOT/'audit/publication_preflight.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    if failures:raise SystemExit(1)

if __name__=='__main__':main()
