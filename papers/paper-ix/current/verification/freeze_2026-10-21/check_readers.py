from pathlib import Path
import json,sys,hashlib,subprocess,concurrent.futures,zipfile,re
import fitz
from PIL import Image,ImageDraw,ImageFont

TASK=Path('/dev/shm/komorebi_paper_ix_freeze_fbc994080222')
ROOT=TASK/'baseline/Paper_IX_Final_Release_v1.0.0';OUT=TASK/'audit_readers'
RELEASE=json.loads((ROOT/'RELEASE.json').read_text())
STATUS=json.loads((ROOT/'verification/2026-10-20/RELEASE_STATUS.json').read_text())
PUBLICATION=json.loads((ROOT/'publication/CURRENT_PUBLICATION_MANIFEST.json').read_text())
REPLAY=json.loads((ROOT/'verification/2026-10-20/FINAL_PDF_REPLAY.json').read_text())
SELECTED={'traditional':[1,2,3,20,60,73,81,110,175,205,231,232],'visual':[1,2,3,6,10,15,20,24,25],'lean_evidence':[1,2,7,20,50,73,100,130,139]}
DETAILS={'traditional':[110,205,231],'visual':[2,25],'lean_evidence':[7,139]}
def sha(b):return hashlib.sha256(b).hexdigest()
def one(role):
 record=next(x for x in RELEASE['documents'] if x['role']==role);p=ROOT/record['file'];raw=p.read_bytes();digest=sha(raw);doc=fitz.open(p)
 status=next(x for x in STATUS['documents'] if x['role']==role);pub=next(x for x in PUBLICATION['files'] if x['path']==record['file']);replay=next(x for x in REPLAY['documents'] if x['file']==p.name)
 data={'role':role,'path':record['file'],'sha256':digest,'bytes':len(raw),'pages':len(doc),'matches_RELEASE':digest==record['sha256'] and len(doc)==record['pages'],'matches_current_status':digest==status['sha256'] and len(doc)==status['pages'],'matches_publication_manifest':digest==pub['sha256'] and len(raw)==pub['bytes'],'matches_accepted_replay_frozen_input':digest==replay['frozen_sha256'] and len(doc)==replay['pages'],'recorded_rebuild_raw_byte_identical':replay['byte_identical'],'recorded_rebuild_identical_except_trailer_id':replay['identical_except_trailer_id'],'recorded_rebuild_text_and_page_match':replay['extracted_text_match'] and replay['page_count_match'],'active_named_copies':[],'encrypted':bool(doc.is_encrypted),'out_of_page_text_blocks':[],'empty_text_pages':[],'unicode_replacement_character_pages':[],'double_question_mark_pages':[],'invalid_internal_links':[],'internal_link_count':0,'link_kind_counts':{},'bookmarks':len(doc.get_toc()),'invalid_bookmark_pages':[],'selected_rendered_pages':SELECTED[role],'detail_pages':DETAILS[role]}
 copies=[p,ROOT/record['mirror']]
 for copy in copies:data['active_named_copies'].append({'path':copy.relative_to(ROOT).as_posix(),'sha256':sha(copy.read_bytes()),'matches_current':sha(copy.read_bytes())==digest})
 build=ROOT/'publication/build'/p.stem/p.name
 if build.exists():
  braw=build.read_bytes();bd=fitz.open(build);pattern=re.compile(rb'/ID\s*\[\s*<[0-9a-fA-F]+>\s*<[0-9a-fA-F]+>\s*\]')
  different_text=[i+1 for i in range(min(len(doc),len(bd))) if doc[i].get_text()!=bd[i].get_text()]
  data['unselected_build_artifact']={'path':build.relative_to(ROOT).as_posix(),'sha256':sha(braw),'bytes':len(braw),'pages':len(bd),'exact_bytes_match_selected':digest==sha(braw),'matches_after_trailer_id_normalization':pattern.sub(b'/ID [<NORMALIZED><NORMALIZED>]',raw)==pattern.sub(b'/ID [<NORMALIZED><NORMALIZED>]',braw),'different_extracted_text_pages':different_text,'page_counts_equal':len(doc)==len(bd),'selection':'Unselected retained build-workspace artifact; not a current reading mirror or the accepted FINAL_PDF_REPLAY output.'}
 selected_images=[]
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
  if number in SELECTED[role]:
   pix=page.get_pixmap(matrix=fitz.Matrix(1,1),alpha=False);selected_images.append((number,Image.frombytes('RGB',[pix.width,pix.height],pix.samples)))
  if number in DETAILS[role]:page.get_pixmap(matrix=fitz.Matrix(1.65,1.65),alpha=False).save(OUT/f'{role}_detail_{number:03d}.png')
 for i,item in enumerate(doc.get_toc(simple=False),1):
  if item[3].get('kind') in (fitz.LINK_GOTO,fitz.LINK_NAMED) and not 1<=item[2]<=len(doc):data['invalid_bookmark_pages'].append({'index':i,'title':item[1],'page':item[2]})
 font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17);w=340;h=475;cols=3;rows=(len(selected_images)+cols-1)//cols
 sheet=Image.new('RGB',(w*cols,h*rows),'#d8dce0');draw=ImageDraw.Draw(sheet)
 for j,(n,im) in enumerate(selected_images):
  im.thumbnail((w-14,h-36));x=(j%cols)*w+(w-im.width)//2;y=(j//cols)*h+30;sheet.paste(im,(x,y));draw.text(((j%cols)*w+8,(j//cols)*h+7),f'{role} PDF page {n}',font=font,fill='black')
 sheet.save(OUT/f'{role}_contact.png')
 (OUT/f'{role}_check.json').write_text(json.dumps(data,indent=2)+'\n');print(role,len(doc),digest,flush=True)

if len(sys.argv)>1:one(sys.argv[1])
else:
 def run(role):
  r=subprocess.run([sys.executable,'-B',__file__,role],capture_output=True,text=True)
  if r.returncode:raise RuntimeError(role+' '+r.stderr)
  print(r.stdout.strip(),flush=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(run,SELECTED))
 docs={k:json.loads((OUT/f'{k}_check.json').read_text()) for k in SELECTED}
 recovery=json.loads((ROOT/'recovered_history/HISTORICAL_RECOVERY_REPORT.json').read_text());archive=ROOT/'recovered_history'/recovery['source_archive']['name'];original=recovery['main_reader']
 with zipfile.ZipFile(archive) as z:
  names=[x for x in z.namelist() if x.endswith('/'+original['path']) or x==original['path']]
  if len(names)!=1:raise RuntimeError('Historical original reader member is ambiguous')
  raw=z.read(names[0]);d=fitz.open(stream=raw,filetype='pdf')
  historical={'archive_path':archive.relative_to(ROOT).as_posix(),'archive_sha256':sha(archive.read_bytes()),'archive_hash_matches_recovery':sha(archive.read_bytes())==recovery['source_archive']['sha256'],'member':names[0],'pages':len(d),'sha256':sha(raw),'member_hash_matches_recovery':sha(raw)==original['sha256'],'member_pages_match_recovery':len(d)==original['pages'],'role':'52-page historical original retained inside recovered archive; not a selected current reader and excluded from396-page current total.'}
 result={'status':'PENDING_VISUAL_REVIEW','scope':'Read-only selected PDF receipt binding, active-copy identity, all-page structural/link/bookmark checks, exact historical-reader identity and representative fresh render QA. No PDF/source edits, build or science execution.','documents':docs,'distinct_selected_reader_pages':sum(x['pages'] for x in docs.values()),'historical_original_reader':historical,'accepted_rebuild_boundary':'Recorded exact page text/page count, with byte equality only after normalization of generated trailer IDs. No raw byte-identity claim and no build rerun here.'}
 (OUT/'reader_check.json').write_text(json.dumps(result,indent=2)+'\n')
