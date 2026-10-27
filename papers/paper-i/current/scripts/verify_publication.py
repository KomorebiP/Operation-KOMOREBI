#!/usr/bin/env python3
"""Check current PDF structure and record completed visual review separately.

Without --record-reviewed, only automated checks are recorded under build/.
Use --record-reviewed only after inspecting the rendered current PDF pages.
"""
from pathlib import Path
import argparse, hashlib, json, re
from datetime import datetime, timezone
import fitz
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--record-reviewed',action='store_true')
p.add_argument('--render-dir',type=Path)
a=p.parse_args()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
coverage_path=ROOT/'formal/coverage/COVERAGE_108.json'
coverage=json.loads(coverage_path.read_text());ids=[r['stable_id'] for r in coverage['records']]
assert len(ids)==108 and len(set(ids))==108
catalog=ROOT/'editable/machine/generated/release_catalog.tex'
ct=catalog.read_text()
assert re.findall(r'\\label\{rec:([^}]+)\}',ct)==ids
assert ct.count(r'\begin{proof}')==69
result={'status':'PASS' if a.record_reviewed else 'AUTOMATED_PASS_VISUAL_REVIEW_REQUIRED','checked_at_utc':datetime.now(timezone.utc).isoformat(),'scope':'Current PDF builds, exact record inventory, destinations, text bounds and rendered layout. Formal acceptance remains a separate receipt.','review_method':'All pages in rendered contact sheets, with detailed renders for changed text, dense listings and maps.' if a.record_reviewed else None,'inventory_sha256':sha(coverage_path),'catalog_sha256':sha(catalog),'catalog_records':108,'catalog_source_proofs':69,'all_pages_visually_reviewed':a.record_reviewed,'documents':{}}
for component,stem in [('traditional','Paper_I_Traditional_Final'),('lean_guide','Paper_I_Lean_Guide_Final'),('machine','Paper_I_Machine_Native_Final')]:
    pdf=ROOT/'papers'/(stem+'.pdf')
    assert sha(pdf)==sha(ROOT/'publication/pdfs'/pdf.name)
    assert sha(pdf)==sha(ROOT/'editable'/component/pdf.name)
    build=ROOT/'build'/component
    log=(build/(stem+'.log')).read_text()
    warnings=[l for l in log.splitlines() if re.search(r'Overfull|Missing character|undefined|multiply defined',l)]
    assert not warnings,(component,warnings)
    d=fitz.open(pdf);bounds=[]
    for n,page in enumerate(d,1):
        for b in page.get_text('blocks'):
            if b[0]<0 or b[1]<0 or b[2]>page.rect.width+1 or b[3]>page.rect.height+1:
                bounds.append({'page':n,'bbox':b[:4]})
    assert not bounds,(component,bounds)
    reader=PdfReader(pdf);dests=reader.named_destinations
    aux=(build/(stem+'.aux')).read_text()
    labels={label:dest for label,dest in re.findall(r'\\newlabel\{([^}]+)\}\{\{[^}]*\}\{[^}]*\}\{[^}]*\}\{([^}]+)\}',aux)}
    if component=='machine':
        assert all('rec:'+rid in labels and labels['rec:'+rid] in dests for rid in ids)
    if component=='traditional':
        for r in coverage['records']:
            label=re.search(r'\\label\{([^}]+)\}',r['statement']).group(1)
            assert label in labels and labels[label] in dests,label
    info={'path':str(pdf.relative_to(ROOT)),'sha256':sha(pdf),'pages':len(d),'critical_tex_warnings':warnings,'out_of_page_text_blocks':bounds,'public_copies_identical':True,'editable_copy_identical':True,'all_delivered_copies_identical':True,'all_pages_visually_reviewed':a.record_reviewed}
    if a.render_dir:
        from PIL import Image,ImageDraw
        a.render_dir.mkdir(parents=True,exist_ok=True)
        sheets=[]
        for start in range(0,len(d),12):
            sheet=Image.new('RGB',(1200,2192),(235,235,235));draw=ImageDraw.Draw(sheet)
            for idx in range(start,min(start+12,len(d))):
                pix=d[idx].get_pixmap(matrix=fitz.Matrix(.63,.63),alpha=False)
                im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
                x=(idx-start)%3*400+(400-im.width)//2;y=(idx-start)//3*548+22
                sheet.paste(im,(x,y));draw.text((x,y-18),str(idx+1),fill=(0,0,0))
            path=a.render_dir/f'{component}_{start+1:03d}.jpg';sheet.save(path,quality=90);sheets.append(str(path))
        info['rendered_contact_sheets']=sheets
    result['documents'][component]=info
out=ROOT/('verification/PUBLICATION_QA.json' if a.record_reviewed else 'build/PUBLICATION_AUTOMATED_CHECKS.json')
out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':result['status'],'documents':{k:{'pages':v['pages'],'sha256':v['sha256']} for k,v in result['documents'].items()},'record':str(out)},indent=2))
