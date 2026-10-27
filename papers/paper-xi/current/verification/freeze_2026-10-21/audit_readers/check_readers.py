#!/usr/bin/env python3
"""Read-only Paper XI freeze reader QA; requires PyMuPDF, Pillow for render contacts.
No TeX, Lean, axiom auditor or scientific suite is invoked. Output must be outside root.
"""
from pathlib import Path
from collections import Counter
import argparse,hashlib,importlib.util,json,sys,datetime
sys.dont_write_bytecode=True
import fitz
from PIL import Image,ImageDraw

EXPECTED={
 'traditional':('Paper_XI_Traditional_v1.1.0.pdf',111,'a15f5ba78334f3b9ea5969b9de53c72b17af55c16151f4c2b619b014052b0210'),
 'visual':('Paper_XI_Visual_Guide_v1.1.0.pdf',53,'feebaffc77ca8da24572a4b67b3ba5550feedf476995526ea5119fab345cd03e'),
 'lean':('Paper_XI_Lean_Guide_v1.1.0.pdf',239,'7df5d6a03c93431f2dc802df6d3209cdc0bc87026ff32f0dd56b576a2165249a'),
 'research':('Paper_XI_Conjecture66_Progress_v0.4.0.pdf',77,'608bf94c6f41fc2ed1bc6d0898375d3295b6d7b84f8f79bbe2bb15177062669a'),
 'atlas':('Paper_XI_Conjecture66_Visual_Atlas_v0.5.0.pdf',36,'f5f7b093defb5b1ef12de9284474120585f8edb43b5625ab5a8d661976867214')}
CONTACTS={'traditional':[1,2,6,12,20,28,38,45,52,62,76,92,105,111],
 'visual':[1,2,5,11,18,26,34,42,49,53],
 'lean':[1,2,3,5,8,12,17,28,50,80,120,160,200,239],
 'research':[1,2,7,15,24,33,34,44,54,65,72,77],
 'atlas':[1,2,4,8,13,18,23,28,32,36]}
DETAILS={'traditional':[2,45,52,105], 'visual':[18,42], 'lean':[3,8,239], 'research':[33,54,77], 'atlas':[4,28,36]}

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()

def dump(p,d):p.write_text(json.dumps(d,indent=2)+'\n')

def render(doc,page,dpi):
 p=doc[page-1].get_pixmap(dpi=dpi,alpha=False,colorspace=fitz.csRGB)
 return Image.frombytes('RGB',(p.width,p.height),p.samples)

def main():
 a=argparse.ArgumentParser();a.add_argument('--root',type=Path,required=True);a.add_argument('--output',type=Path,required=True);a.add_argument('--receipt',type=Path);a.add_argument('--render',action='store_true');args=a.parse_args()
 root=args.root.resolve();out=args.output.resolve();assert not out.is_relative_to(root);out.mkdir(parents=True,exist_ok=True)
 spec=importlib.util.spec_from_file_location('paper_xi_accepted_verifier',root/'tools/verify_release.py');v=importlib.util.module_from_spec(spec);sys.modules[spec.name]=v;spec.loader.exec_module(v)
 verifier=v.Verifier(root)
 for label,fn in [('pdfs',verifier.check_pdfs),('visual_review',verifier.check_visual),('build',verifier.check_build)]:verifier.run(label,fn)
 verifier.close()
 assert verifier.report['errors']==[],verifier.report['errors']
 dump(out/'ACCEPTED_READER_CHECKER_FRESH.json',verifier.report)
 manifest=json.loads((root/'MANIFEST.json').read_text());pins={r['path']:r for r in manifest['files']}
 accepted=None
 if args.receipt:
  accepted=json.loads(args.receipt.read_text());assert accepted['status']=='passed';external={r['file']:r for r in accepted['checks']['pdfs']['files']}
 summaries=[]
 for kind,(name,pages,digest) in EXPECTED.items():
  path=root/'publication/pdfs'/name;assert sha(path)==digest
  assert pins['publication/pdfs/'+name]['sha256']==digest
  if accepted:assert external[name]['sha256']==digest and external[name]['pages']==pages
  copies=[]
  for cp in root.rglob(name):
   if cp.is_file():copies.append({'path':cp.relative_to(root).as_posix(),'sha256':sha(cp),'selected_bytes_match':sha(cp)==digest})
  with fitz.open(path) as doc:
   assert len(doc)==pages
   span_count=0;outside=[];empty=[];texts=[]
   for page in doc:
    text=page.get_text();texts.append(text)
    if not text.strip():empty.append(page.number+1)
    rect=page.rect+(-2,-2,2,2)
    for b in page.get_text('dict')['blocks']:
     for l in b.get('lines',[]):
      for s in l['spans']:
       if not s['text'].strip():continue
       span_count+=1
       if not rect.contains(fitz.Rect(s['bbox'])):outside.append({'page':page.number+1,'text':s['text'][:120],'bbox':s['bbox']})
   names=doc.resolve_names();toc=doc.get_toc(simple=False);links=[l for pg in doc for l in pg.get_links()]
   searched={phrase:[i+1 for i,t in enumerate(texts) if phrase.casefold() in t.casefold()] for phrase in ['Conjecture 66','H5','same candidate','realization','occurrence','noncompact','Block 2','native','phase']}
   if args.render:
    thumbs=[]
    for pg in CONTACTS[kind]:
     im=render(doc,pg,40);im.thumbnail((250,350));tile=Image.new('RGB',(270,385),'#e9e9e9');tile.paste(im,((270-im.width)//2,24));ImageDraw.Draw(tile).text((10,5),f'{kind} · {pg}',fill='black');thumbs.append(tile)
    rows=(len(thumbs)+3)//4;canvas=Image.new('RGB',(1080,rows*385),'#cccccc')
    for i,im in enumerate(thumbs):canvas.paste(im,((i%4)*270,(i//4)*385))
    canvas.save(out/(kind+'_contact.png'))
    for pg in DETAILS[kind]:render(doc,pg,110).save(out/(kind+f'_detail_{pg:03}.png'))
   summaries.append({'kind':kind,'file':name,'pages':pages,'bytes':path.stat().st_size,'sha256':digest,'same_named_copies':copies,'named_destinations':len(names),'bookmarks':len(toc),'annotation_links':len(links),'link_kinds':dict(Counter(str(l['kind']) for l in links)),'nonempty_text_spans':span_count,'text_spans_beyond_page_2pt_tolerance':outside,'pages_without_extracted_text':empty,'scope_phrase_pages':searched,'contact_pages':CONTACTS[kind] if args.render else [],'detail_pages':DETAILS[kind] if args.render else []})
  dump(out/(kind+'_check.json'),summaries[-1])
 routes=json.loads((root/'evidence/release_1_1/READING_ROUTES.json').read_text())
 raster=json.loads((root/'evidence/release_1_1/ASSEMBLY_RASTER_CHECK.json').read_text())
 assert raster['status']=='passed'
 for r in raster['records']:
  assert r['all_pages_pixel_identical'];assert sha(root/'publication/pdfs'/r['file'])==r['assembled_pdf_sha256'];assert r['pages']==next(d['pages'] for d in summaries if d['file']==r['file'])
 total=Counter()
 for d in verifier.report['checks']['pdfs']['files']:total.update(d['action_counts'])
 result={'status':'PASS','checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Fresh read-only selected reader identity, current accepted checker, navigation, all-page text bounds and representative rendering. No PDF source build.','documents':summaries,'selected_reader_pages':sum(d['pages'] for d in summaries),'fresh_navigation_totals':{'annotation_links':sum(d['annotation_links'] for d in summaries),'bookmarks':sum(d['bookmarks'] for d in summaries),'named_destinations':sum(d['named_destinations'] for d in summaries),'raw_action_counts':dict(total)},'route_map_rows':len(routes['routes']),'current_accepted_assembly_record':{'status':raster['status'],'dpi':raster['dpi'],'records':[{'file':r['file'],'pages':r['pages'],'raw_pdf_sha256':r['raw_pdf_sha256'],'assembled_pdf_sha256':r['assembled_pdf_sha256'],'all_pages_pixel_identical':r['all_pages_pixel_identical']} for r in raster['records']]},'replay_boundary':'The current 1.1.0 raw-versus-companion-assembled raster comparison is recorded assembly consistency, not an isolated rebuild. Historical v1.0.0 rebuild receipts and B02/B04 binary differences remain separate. Two research companions preserve mathematical text, pages and links after targeted cover-only path-paint edits; no unified editable-source rebuild is claimed.','external_accepted_delivery_receipt':None if not args.receipt else {'path':str(args.receipt),'sha256':sha(args.receipt),'status':accepted['status'],'current_pdf_hashes_match':True},'scope_qualifications':['Conjecture 66 remains open.','Four arithmetic tasks: general realization; full H5 for that same realized candidate; corrected full-character occurrence in fixed Continuation113 candidate and required noncompact extension; actual native square/section/phase certificate when the stronger prescribed contract is required.','Characteristic-zero rank-three fixed candidate is distinct from characteristic-p rank-nine two-cubic-stage branch.','Complete Block02 editable archive remains unavailable; its original 33-page reader survives in the research PDF.','Original historical terminal receipt is absent. Current repaired terminal replay is separately dated and restricted.','Accepted 423-module/4342-name/7672-owned-logical-declaration population, terminal51 and interface1 remain separate.','This freeze performs no new compiler, auditor, scientific/control suite, PDF builder or whole-paper proof audit.'],'release_blockers':[],'visual_review':{'status':'PENDING_MANUAL_REVIEW' if args.render else 'NOT_RENDERED','contact_selected_pages':sum(len(CONTACTS[k]) for k in EXPECTED) if args.render else 0,'detail_renders':sum(len(DETAILS[k]) for k in EXPECTED) if args.render else 0}}
 dump(out/'reader_check.json',result);print(json.dumps({'status':result['status'],'pages':result['selected_reader_pages'],'navigation':result['fresh_navigation_totals'],'outside_spans':sum(len(d['text_spans_beyond_page_2pt_tolerance']) for d in summaries),'contact_pages':result['visual_review']['contact_selected_pages'],'details':result['visual_review']['detail_renders']}))
if __name__=='__main__':main()
