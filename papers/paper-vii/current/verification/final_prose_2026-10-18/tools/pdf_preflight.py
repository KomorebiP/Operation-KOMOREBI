#!/usr/bin/env python3
"""Authoring QA: writes current preflight/font reports. Revalidate the package afterward."""
from pathlib import Path
import hashlib,json,re,subprocess
import fitz
from pypdf import PdfReader
R=Path(__file__).resolve().parents[3]
V=R/'verification/final_prose_2026-10-18'
specs=[('traditional','Paper_VII_Traditional_Final'),('visual_guide','Paper_VII_Visual_Guide_Final'),('lean_guide','Paper_VII_Lean_Guide_Final')]
records=[];failures=[]
for role,stem in specs:
 path=R/'papers'/(stem+'.pdf'); rows=[];badchars=[];outside=[];badlinks=[];linkcount=0;orphans=[]
 reader=PdfReader(path); named=reader.named_destinations; named_checked=0
 with fitz.open(path) as pdf:
  for i,page in enumerate(pdf):
   text=page.get_text();spans=[s for b in page.get_text('dict')['blocks'] for l in b.get('lines',[]) for s in l['spans'] if s['text'].strip()]
   for s in spans:
    if any(c in s['text'] for c in ('\u0357','\ufffd','\x00')):badchars.append({'page':i+1,'text':s['text'],'font':s['font']})
    x0,y0,x1,y1=s['bbox']
    if x0 < -0.1 or y0 < -0.1 or x1 > page.rect.width+0.1 or y1 > page.rect.height+0.1:outside.append({'page':i+1,'text':s['text'],'bbox':s['bbox']})
   content=[s for s in spans if 48 < s['bbox'][1] < page.rect.height-44]
   if content and content[0]['text'].strip() in ('□','∎','◻'):
    orphans.append({'page':i+1,'text':content[0]['text'],'bbox':content[0]['bbox']})
   for l in page.get_links():
    linkcount+=1
    if l['kind'] in (fitz.LINK_GOTO,fitz.LINK_NAMED):
     target=l.get('page',-1)
     if not 0<=target<len(pdf):badlinks.append({'page':i+1,'problem':'Invalid resolved target page','link':str(l)})
     rect=l['from']
     if rect.x0<0 or rect.y0<0 or rect.x1>page.rect.width or rect.y1>page.rect.height:badlinks.append({'page':i+1,'problem':'Link rectangle outside page'})
     if l.get('nameddest'):
      key=l['nameddest'];named_checked+=1
      if key not in named or reader.get_destination_page_number(named[key])!=target:badlinks.append({'page':i+1,'problem':'Named destination differs between PyMuPDF and pypdf','name':key})
   rows.append({'physical_page':i+1,'printed_page':page.get_label(),'characters':len(text),'text_spans':len(spans),'raster_images':len(page.get_images())})
  badtoc=[row for row in pdf.get_toc() if not 1<=row[2]<=len(pdf)]
  info={'path':str(path.relative_to(R)),'role':role,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'pages':len(pdf),'metadata':pdf.metadata,'toc_entries':len(pdf.get_toc())}
 log=(R/'editable'/role/(stem+'.log')).read_text(errors='replace')
 hard=[l for l in log.splitlines() if re.search(r'Overfull \\[hv]box|undefined references|undefined citations|undefined on input|Missing character:|LaTeX Error',l)]
 driver=(R/'editable'/role/'build_pdf_driver.txt').read_text(errors='replace')
 dw=[l for l in driver.splitlines() if 'warning:' in l.lower() or 'fatal:' in l.lower()]
 fr=subprocess.run(['pdffonts',str(path)],capture_output=True,text=True); (V/'build'/(role+'_pdffonts.txt')).write_text(fr.stdout+fr.stderr)
 problems=badchars+outside+badlinks+badtoc+hard+dw+orphans
 if problems:failures.append(role)
 info.update({'status':'FAIL' if problems else 'PASS_FOR_STATED_SCOPE','corrupt_or_replacement_characters':badchars,'text_outside_page_bounds':outside,'invalid_internal_links':badlinks,'links_checked':linkcount,'named_links_cross_checked_with_pypdf':named_checked,'invalid_bookmark_targets':badtoc,'final_tex_faults':hard,'pdf_driver_warnings':dw,'possible_orphan_qed_markers':orphans,'font_report':'build/'+role+'_pdffonts.txt','page_records':rows})
 records.append(info)
out={'schema':'paper_vii_pdf_preflight.v1','status':'FAIL' if failures else 'PASS_FOR_STATED_SCOPE','scope':'Mechanical checks of every current PDF page, physical text bounds, known corrupted/replacement characters, internal link destinations, bookmarks and final build diagnostics. Visual acceptance is separately recorded.','documents':records,'failures':failures}
(V/'PDF_PREFLIGHT.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'status':out['status'],'documents':[{k:r[k] for k in ['role','pages','sha256','status','possible_orphan_qed_markers','final_tex_faults','pdf_driver_warnings']} for r in records]},indent=2))
