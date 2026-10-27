#!/usr/bin/env python3
"""Render every current PDF page with Poppler and create compact sheets for human QA."""
from pathlib import Path
import argparse,hashlib,io,json,re,subprocess
import fitz
from PIL import Image,ImageDraw,ImageFont
from current_publication import configuration, load_scope, sha, ACCEPTED, PARTIAL
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path);p.add_argument('--map',type=Path);p.add_argument('--edition-date');p.add_argument('--baseline',type=Path,help='Previously rendered and reviewed page_qa.json for exact pixel comparison');a=p.parse_args();scope_path,edition_day=configuration(a.map,a.edition_date);out=(a.output or ROOT/('verification/publication_'+edition_day.isoformat()+'/page_qa')).resolve();out.mkdir(parents=True,exist_ok=True)
baseline=json.loads(a.baseline.read_text()) if a.baseline else None
scope,final_counts=load_scope(scope_path)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)
report={'schema':'paper-ii-current-page-qa/2','edition_date':edition_day.isoformat(),'correspondence':{'path':str(scope_path.relative_to(ROOT)),'sha256':sha(scope_path),'status':scope['status']},'all_pages_rendered':True,'visual_review':'PENDING','documents':[]}
for short,stem in [('traditional','Paper_II_Traditional_Final'),('visual','Paper_II_Visual_Guide_Final'),('lean','Paper_II_Lean_Guide_Final')]:
 pdf=ROOT/'papers'/(stem+'.pdf');doc=fitz.open(pdf);texts=[];metrics=[];sheets=[]
 for start in range(0,len(doc),6):
  sheet=Image.new('RGB',(1344,1208),'#dce7e6');draw=ImageDraw.Draw(sheet)
  for j,i in enumerate(range(start,min(start+6,len(doc)))):
   raw=subprocess.run(['pdftoppm','-f',str(i+1),'-l',str(i+1),'-r','72','-singlefile','-png',str(pdf)],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
   im=Image.open(io.BytesIO(raw.stdout)).convert('RGB');pixel_sha=hashlib.sha256(im.tobytes()).hexdigest();raster_size=list(im.size);im.thumbnail((428,554))
   x=12+(j%3)*448;y=12+(j//3)*600;sheet.paste(im,(x,y));draw.text((x,y+564),f'{short} physical page {i+1}',font=font,fill='#164c51')
   page=doc[i];text=page.get_text();texts.append(text);outside=[]
   for block in page.get_text('dict')['blocks']:
    if block['type']!=0:continue
    for line in block['lines']:
     for span in line['spans']:
      box=fitz.Rect(span['bbox'])
      if not (page.rect+(-.5,-.5,.5,.5)).contains(box):outside.append({'text':span['text'],'bbox':span['bbox']})
   metrics.append({'physical_page':i+1,'raster_rgb_sha256':pixel_sha,'raster_size_72dpi':raster_size,'text_sha256':hashlib.sha256(text.encode()).hexdigest(),'words':len(page.get_text('words')),'replacement_characters':text.count('\ufffd'),'unresolved_reference_marks':text.count('??'),'text_outside_page':outside,'images':len(page.get_images()),'drawings':len(page.get_drawings())})
  target=out/f'{short}_{start//6+1:02}.png';sheet.save(target);sheets.append(str(target))
 log=ROOT/'publication/build'/stem/(stem+'.log');logtext=log.read_text(errors='replace')
 issues={'missing_characters':re.findall(r'Missing character:.*',logtext),'overfull_boxes':re.findall(r'Overfull \\[hv]box.*',logtext),'undefined_references':re.findall(r'.*(?:undefined references|Citation .* undefined|Reference .* undefined).*',logtext),'outside_page_count':sum(len(x['text_outside_page']) for x in metrics),'replacement_characters':sum(x['replacement_characters'] for x in metrics),'unresolved_reference_marks':sum(x['unresolved_reference_marks'] for x in metrics)}
 (out/(short+'_text.txt')).write_text('\n\f\n'.join(texts))
 record={'file':str(pdf.relative_to(ROOT)),'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'pages':len(doc),'metadata':doc.metadata,'all_pages_rendered_with':'Poppler pdftoppm72dpi','contact_sheets':sheets,'contact_sheet_sha256':{str(Path(s).name):hashlib.sha256(Path(s).read_bytes()).hexdigest() for s in sheets},'page_metrics':metrics,'issues':issues,'visual_review':'PENDING'}
 if final_counts:
  joined=re.sub(r'\s+',' ',' '.join(texts));accepted=final_counts.get(ACCEPTED,0);partial=final_counts.get(PARTIAL,0);open_labels=scope.get('known_open_bridge_labels',[])
  pending=scope['proof_level_count']-accepted-partial
  zero_partial='No partial or pending proof records are listed in this correspondence.' in joined
  partial_phrase=f'{partial} records retain kernel checked partial scope' in joined
  bridge_state=(zero_partial and not open_labels) if accepted==scope['proof_level_count'] else ((partial_phrase if partial else True) and ('named open bridges remain explicit' in joined if open_labels else True))
  record['current_scope_text_check']={'accepted':accepted,'denominator':scope['proof_level_count'],'partial':partial,'pending':pending,'accepted_count_phrase_present':f'{accepted} of {scope["proof_level_count"]}' in joined,'partial_count_phrase_present':partial_phrase if partial else zero_partial,'open_bridge_state_matches':bool(bridge_state),'named_open_bridges':open_labels}
 if baseline:
  old=next((item for item in baseline['documents'] if item['file']==record['file']),None)
  if old:
   old_by_hash={}
   for metric in old['page_metrics']:old_by_hash.setdefault(metric.get('raster_rgb_sha256'),[]).append(metric['physical_page'])
   unchanged=[];changed=[]
   for metric in metrics:
    matches=old_by_hash.get(metric['raster_rgb_sha256'],[])
    (unchanged if matches else changed).append({'physical_page':metric['physical_page'],'baseline_physical_pages':matches} if matches else metric['physical_page'])
   record['pixel_comparison']={'baseline_pdf_sha256':old['pdf_sha256'],'identical_pages':unchanged,'changed_or_new_pages':changed}
 report['documents'].append(record);print(json.dumps({'document':short,'pages':len(doc),'issues':issues,'contact_sheets':len(sheets)}),flush=True)
if baseline:report['baseline']={'path':str(a.baseline.resolve()),'sha256':hashlib.sha256(a.baseline.read_bytes()).hexdigest(),'status':baseline['visual_review']}
report['total_pages']=sum(d['pages'] for d in report['documents']);(out/'page_qa.json').write_text(json.dumps(report,indent=2)+'\n')
