from pathlib import Path
import json, hashlib, sys, subprocess, concurrent.futures
import fitz
from PIL import Image, ImageDraw, ImageFont

TASK=Path('/dev/shm/komorebi_paper_x_freeze_fbc994080222')
ROOT=TASK/'baseline/Paper_X_Final_Release_v1.0.0'
OUT=TASK/'audit_readers'
RELEASE=json.loads((ROOT/'RELEASE.json').read_text())
LOCATORS=json.loads((ROOT/'CURRENT_PUBLICATION_LOCATORS.json').read_text())
VALIDATION=json.loads((ROOT/'verification/2026-10-20/PUBLICATION_VALIDATION.json').read_text())
BUILD=json.loads((ROOT/'publication/build_results.json').read_text())
STRICT=json.loads((ROOT/'MANIFEST_SHA256.json').read_text())
REPLAY=json.loads((TASK/'ACCEPTED_CLEAN_EXTRACTION_RECEIPT.json').read_text())
FILES={'traditional':'Paper_X_Traditional_Final.pdf','visual':'Paper_X_Visual_Guide_Final.pdf','lean_evidence':'Paper_X_Lean_Guide_Final.pdf'}
SELECTED={'traditional':[1,2,3,9,27,31,38,59,62,63,85,92],'visual':[1,2,3,4,10,20,24,28,33],'lean_evidence':[1,4,6,7,12,14,15,18,37]}
DETAILS={'traditional':[2,38,60,62,63],'visual':[2,28],'lean_evidence':[6,15,37]}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def one(role):
 name=FILES[role];p=ROOT/'publication/pdfs'/name;raw=p.read_bytes();digest=sha(raw);doc=fitz.open(p);names=doc.resolve_names()
 release=next(x for x in RELEASE['pdfs'] if Path(x['file']).name==name)
 locator=next(x for x in LOCATORS['documents'] if x['name']==name)
 validation=next(x for x in VALIDATION['documents'] if x['name']==name)
 build=next(x for x in BUILD['documents'] if x['file_name']==name)
 strict=next(x for x in STRICT['files'] if x['path']==release['file'])
 replay=next(x for x in REPLAY['readers'] if Path(x['file']).name==name)
 comparison=next(x for x in REPLAY['isolated_reader_rebuild']['pdf_comparison'] if x['file']==name)
 d={'role':role,'path':p.relative_to(ROOT).as_posix(),'sha256':digest,'bytes':len(raw),'pages':len(doc),'receipt_binding':{
  'RELEASE':digest==release['sha256'] and len(doc)==release['pages'] and len(raw)==release['bytes'],
  'CURRENT_PUBLICATION_LOCATORS':digest==locator['sha256'] and len(doc)==locator['pages'],
  'current_PUBLICATION_VALIDATION':digest==validation['sha256'] and len(doc)==validation['pages'],
  'current_build_results':digest==build['sha256'] and len(doc)==build['pages'],
  'strict_manifest':digest==strict['sha256'] and len(raw)==strict['bytes'],
  'accepted_external_clean_extraction':digest==replay['sha256'] and len(doc)==replay['pages'],
  'accepted_rebuild_archive_input':digest==comparison['archive_pdf_sha256'] and len(doc)==comparison['pages']},
  'recorded_clean_rebuild_comparison':comparison,'active_named_copies':[], 'historical_same_name_copies':[],
  'encrypted':bool(doc.is_encrypted),'empty_text_pages':[],'out_of_page_text_blocks':[],'unicode_replacement_character_pages':[],'double_question_mark_pages':[],
  'internal_links':0,'relative_companion_links':[],'invalid_internal_links':[],'invalid_companion_links':[],'other_link_kinds':{},
  'named_destinations':len(names),'bookmarks':len(doc.get_toc()),'invalid_bookmark_pages':[],'selected_rendered_pages':SELECTED[role],'detail_pages':DETAILS[role]}
 for copy in ROOT.rglob(name):
  relative=copy.relative_to(ROOT).as_posix();row={'path':relative,'sha256':sha(copy.read_bytes()),'matches_current':sha(copy.read_bytes())==digest}
  if relative.startswith('publication/pdfs/'):d['active_named_copies'].append(row)
  else:d['historical_same_name_copies'].append(row)
 images=[]
 for n,page in enumerate(doc,1):
  txt=page.get_text();rect=page.rect
  if not txt.strip():d['empty_text_pages'].append(n)
  if '\ufffd' in txt:d['unicode_replacement_character_pages'].append(n)
  if '??' in txt:d['double_question_mark_pages'].append(n)
  for b in page.get_text('blocks'):
   if b[6]!=0 or not b[4].strip():continue
   if b[0]<-.5 or b[1]<-.5 or b[2]>rect.width+.5 or b[3]>rect.height+.5:d['out_of_page_text_blocks'].append({'page':n,'bbox':list(b[:4]),'text':b[4][:80]})
  for link in page.get_links():
   kind=link['kind']
   if kind in (fitz.LINK_GOTO,fitz.LINK_NAMED):
    target=link.get('page',-1)
    if 'nameddest' in link:target=names.get(link['nameddest'],{}).get('page',-1)
    d['internal_links']+=1
    if not 0<=target<len(doc):d['invalid_internal_links'].append({'page':n,'target':target,'name':link.get('nameddest')})
   elif kind in (fitz.LINK_GOTOR,fitz.LINK_LAUNCH):
    filename=doc.xref_get_key(link['xref'],'A/F')[1];dest=doc.xref_get_key(link['xref'],'A/D')[1];targetpath=p.parent/filename
    exists=targetpath.is_file();resolved=False;targetpage=None
    if exists:
     other=fitz.open(targetpath);nd=other.resolve_names().get(dest);resolved=bool(nd and 0<=nd.get('page',-1)<len(other));targetpage=nd.get('page',-1)+1 if nd else None;other.close()
    row={'from':name,'page':n,'file':filename,'destination':dest,'target_file_present':exists,'named_target_resolved':resolved,'target_pdf_page':targetpage}
    d['relative_companion_links'].append(row)
    if not exists or not resolved:d['invalid_companion_links'].append(row)
   else:d['other_link_kinds'][str(kind)]=d['other_link_kinds'].get(str(kind),0)+1
  if n in SELECTED[role]:
   pix=page.get_pixmap(matrix=fitz.Matrix(1,1),alpha=False);images.append((n,Image.frombytes('RGB',[pix.width,pix.height],pix.samples)))
  if n in DETAILS[role]:page.get_pixmap(matrix=fitz.Matrix(1.65,1.65),alpha=False).save(OUT/f'{role}_detail_{n:03d}.png')
 for i,item in enumerate(doc.get_toc(simple=False),1):
  if item[3].get('kind') in (fitz.LINK_GOTO,fitz.LINK_NAMED) and not 1<=item[2]<=len(doc):d['invalid_bookmark_pages'].append({'index':i,'title':item[1],'page':item[2]})
 d['fresh_navigation_matches_locator']=(d['bookmarks']==locator['bookmarks'] and d['named_destinations']==locator['named_destinations'] and d['internal_links']==locator['internal_links'] and len(d['relative_companion_links'])==locator['companion_links'])
 w,h=340,475;sheet=Image.new('RGB',(3*w,((len(images)+2)//3)*h),'#d8dce0');draw=ImageDraw.Draw(sheet);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
 for i,(n,im) in enumerate(images):
  im.thumbnail((w-14,h-36));x=(i%3)*w+(w-im.width)//2;y=(i//3)*h+30;sheet.paste(im,(x,y));draw.text(((i%3)*w+8,(i//3)*h+7),f'{role} PDF page {n}',fill='black',font=font)
 sheet.save(OUT/f'{role}_contact.png');(OUT/f'{role}_check.json').write_text(json.dumps(d,indent=2)+'\n');print(role,len(doc),digest,flush=True)

if len(sys.argv)>1:one(sys.argv[1])
else:
 OUT.mkdir(exist_ok=True,parents=True)
 def run(role):
  r=subprocess.run([sys.executable,'-B',__file__,role],capture_output=True,text=True)
  if r.returncode:raise RuntimeError(role+' '+r.stderr)
  print(r.stdout.strip(),flush=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(run,FILES))
 docs={role:json.loads((OUT/f'{role}_check.json').read_text()) for role in FILES}
 main=fitz.open(ROOT/'publication/pdfs'/FILES['traditional']);visual=fitz.open(ROOT/'publication/pdfs'/FILES['visual']);atlas=[]
 for row in LOCATORS['atlas']:
  a=main[row['monograph_pdf_page']-1];b=visual[row['visual_pdf_page']-1];pa=a.get_pixmap(matrix=fitz.Matrix(.5,.5),alpha=False);pb=b.get_pixmap(matrix=fitz.Matrix(.5,.5),alpha=False)
  atlas.append({**row,'exact_page_text_equal':a.get_text()==b.get_text(),'36dpi_pixels_equal':pa.width==pb.width and pa.height==pb.height and pa.samples==pb.samples})
 claims=[];names=main.resolve_names();remote=[row for d in docs.values() for row in d['relative_companion_links']]
 for row in LOCATORS['claims']:
  dest=names.get(row['pdf_destination']);claims.append({'number':row['number'],'destination':row['pdf_destination'],'locator_page':row['monograph_pdf_page'],'resolved_page':dest['page']+1 if dest else None,'matches_current_locator':bool(dest and dest['page']+1==row['monograph_pdf_page']),'companion_link_present':any(x['destination']==row['pdf_destination'] for x in remote)})
 recovery=json.loads((ROOT/'verification/2026-10-20/ORIGINAL_SOURCE_RECOVERY.json').read_text());old=next(x for x in recovery['files'] if x['path'].endswith('/PSC_Paper_X_Strengthened_Annals_Edition.pdf'));p=ROOT/old['path'];original=fitz.open(p)
 result={'status':'PENDING_VISUAL_REVIEW','scope':'Read-only selected reader receipt/copy identity, all-page structure and navigation, exact atlas duplication, historical original identity and fresh representative rendered review. No PDF/source edits or builds.','documents':docs,'delivered_selected_reader_pages':sum(x['pages'] for x in docs.values()),'intentional_duplicate_atlas_pages':30,'unique_pages_after_atlas_deduplication':132,'atlas_pair_checks':atlas,'statement_destination_checks':claims,'historical_original_reader':{'path':old['path'],'pages':len(original),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes()),'matches_recovery_receipt':sha(p.read_bytes())==old['sha256'] and len(original)==recovery['original_historical_pdf_pages'],'excluded_from_selected_page_total':True},'external_accepted_receipt':{'path':'ACCEPTED_CLEAN_EXTRACTION_RECEIPT.json','sha256':sha((TASK/'ACCEPTED_CLEAN_EXTRACTION_RECEIPT.json').read_bytes()),'status':REPLAY['status'],'isolated_reader_rebuild_status':REPLAY['isolated_reader_rebuild']['status'],'rebuild_rerun_for_freeze':False}}
 (OUT/'reader_check.json').write_text(json.dumps(result,indent=2)+'\n')
