from pathlib import Path
import json,hashlib,sys,subprocess,concurrent.futures
import fitz
from PIL import Image,ImageDraw,ImageFont

ROOT=Path('/workspace/scratch/fbc994080222/paper_vi_freeze/baseline/Paper_VI_Final_Release_v1.0.0')
OUT=Path(__file__).resolve().parent
MANIFEST=json.loads((ROOT/'publication/CURRENT_PUBLICATION_MANIFEST.json').read_text())
STATUS=json.loads((ROOT/'verification/closeout_2026-10-20/RELEASE_STATUS.json').read_text())
GEOMETRY=json.loads((ROOT/'verification/closeout_2026-10-20/FINAL_GEOMETRY_AND_LINKS.json').read_text())
GUIDE_QA=json.loads((ROOT/'verification/closeout_2026-10-20/visual_qa/GUIDES_REVIEW.json').read_text())
SELECTED={'traditional':[1,2,20,50,80,110,130,151,152],'visual_guide':[1,2,4,18,22,30,39,43,44],'lean_guide':[1,2,6,16,23,32,36,55,64]}
DETAILS={'traditional':[50,130],'visual_guide':[18,44],'lean_guide':[6,36,64]}
def sha(b):return hashlib.sha256(b).hexdigest()
def one(role):
 record=next(x for x in MANIFEST['documents'] if x['role']==role);p=ROOT/record['path'];raw=p.read_bytes();digest=sha(raw);doc=fitz.open(p)
 status=next(x for x in STATUS['documents'] if x['role']==role);geom=next(x for x in GEOMETRY['documents'] if x['file']==p.name)
 data={'role':role,'path':record['path'],'sha256':digest,'bytes':len(raw),'pages':len(doc),'matches_current_manifest':digest==record['sha256'] and len(doc)==record['pages'],'matches_release_status':digest==status['sha256'] and len(doc)==status['pages'],'matches_final_geometry_receipt':digest==geom['sha256'] and len(doc)==geom['pages'],'encrypted':bool(doc.is_encrypted),'out_of_page_text_blocks':[],'empty_text_pages':[],'unicode_replacement_character_pages':[],'double_question_mark_pages':[],'invalid_internal_links':[],'internal_link_count':0,'link_kind_counts':{},'bookmarks':len(doc.get_toc()),'invalid_bookmark_pages':[],'selected_rendered_pages':SELECTED[role],'detail_pages':DETAILS[role],'named_copies':[]}
 for copy in ROOT.rglob(p.name):
  rel=copy.relative_to(ROOT).as_posix();cdigest=sha(copy.read_bytes());data['named_copies'].append({'path':rel,'sha256':cdigest,'matches_current':cdigest==digest,'historical_location':rel.startswith('provenance/')})
 if role!='traditional':
  b=next(x for x in GUIDE_QA['documents'] if Path(x['pdf']).name==p.name);data['matches_final_guide_qa']=digest==b['sha256'] and len(doc)==b['pages']
 for number,page in enumerate(doc,1):
  text=page.get_text();rect=page.rect
  if not text.strip():data['empty_text_pages'].append(number)
  if '\ufffd' in text:data['unicode_replacement_character_pages'].append(number)
  if '??' in text:data['double_question_mark_pages'].append(number)
  for b in page.get_text('blocks'):
   if b[6]!=0:continue
   x0,y0,x1,y1=b[:4]
   if x0 < -0.5 or y0 < -0.5 or x1 > rect.width+0.5 or y1 > rect.height+0.5:data['out_of_page_text_blocks'].append({'page':number,'bbox':list(b[:4]),'text':b[4][:100]})
  for link in page.get_links():
   k=str(link.get('kind'));data['link_kind_counts'][k]=data['link_kind_counts'].get(k,0)+1
   if link.get('kind') in (fitz.LINK_GOTO,fitz.LINK_NAMED):
    data['internal_link_count']+=1
    if not 0<=link.get('page',-1)<len(doc):data['invalid_internal_links'].append({'page':number,'target':link.get('page',-1),'name':link.get('nameddest')})
  if number in SELECTED[role]:page.get_pixmap(matrix=fitz.Matrix(1.4,1.4),alpha=False).save(OUT/f'{role}_page_{number:03d}.png')
  if number in DETAILS[role]:page.get_pixmap(matrix=fitz.Matrix(1.8,1.8),alpha=False).save(OUT/f'{role}_detail_{number:03d}.png')
 for i,item in enumerate(doc.get_toc(simple=False),1):
  if item[3].get('kind') in (fitz.LINK_GOTO,fitz.LINK_NAMED) and not 1<=item[2]<=len(doc):data['invalid_bookmark_pages'].append({'index':i,'title':item[1],'page':item[2]})
 font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18);cols=3;w=360;h=510;rows=(len(SELECTED[role])+cols-1)//cols
 sheet=Image.new('RGB',(cols*w,rows*h),'#d8dce0');draw=ImageDraw.Draw(sheet)
 for j,n in enumerate(SELECTED[role]):
  im=Image.open(OUT/f'{role}_page_{n:03d}.png');im.thumbnail((w-16,h-44));x=(j%cols)*w+(w-im.width)//2;y=(j//cols)*h+34;sheet.paste(im,(x,y));draw.text(((j%cols)*w+10,(j//cols)*h+8),f'{role} PDF page {n}',font=font,fill='black')
 sheet.save(OUT/f'{role}_contact.png')
 (OUT/f'{role}_check.json').write_text(json.dumps(data,indent=2)+'\n')
 print(role,len(doc),digest,'out-of-page',len(data['out_of_page_text_blocks']),flush=True)

if len(sys.argv)>1:one(sys.argv[1])
else:
 roles=list(SELECTED)
 def run(role):
  p=subprocess.run([sys.executable,__file__,role],capture_output=True,text=True)
  if p.returncode:raise RuntimeError(role+' '+p.stderr)
  print(p.stdout.strip(),flush=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(run,roles))
 docs={k:json.loads((OUT/f'{k}_check.json').read_text()) for k in roles}
 result={'status':'PENDING_VISUAL_REVIEW','scope':'Read-only current PDF identity, receipt binding, current-copy reconciliation, all-page structural/link checks and representative fresh rendered review. No PDF rebuild or mathematical audit.','documents':docs,'distinct_reader_pages':sum(d['pages'] for d in docs.values()),'release_version':STATUS['version'],'inherited_compiler_evidence':'September 6; no new Lean execution in this reader QA.'}
 (OUT/'reader_check.json').write_text(json.dumps(result,indent=2)+'\n')
