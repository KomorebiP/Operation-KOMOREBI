#!/usr/bin/env python3
"""Read-only current Paper XII reader, recorded rebuild, navigation and render QA.
No builder, compiler, auditor, science gate or control suite is executed.
"""
from pathlib import Path
from collections import Counter
import argparse,datetime,hashlib,importlib.util,json,sys,zipfile
sys.dont_write_bytecode=True
import fitz
from PIL import Image,ImageDraw
EXPECTED={
 'traditional':('Paper_XII_Traditional_v1.0.0.pdf',40,'24358e5607b1d51561131c9475f2177d146b548836aa29cc18747b43fb7bd53e'),
 'visual':('Paper_XII_Visual_Guide_v1.0.0.pdf',28,'c166da190d198fa500505b53c3e5af7c381ed1b3e559b3658087ac414de458d5'),
 'lean':('Paper_XII_Lean_Guide_v1.0.0.pdf',31,'af2333bbb064ca58d24bb4f585b2597e6a55d0bc8dc061b25d491af94b0111e9')}
DETAILS={'traditional':[2,3,14,29,34,35,40],'visual':[2,7,18,24,28],'lean':[2,3,22,30,31]}

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
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--reader-archive',type=Path);ap.add_argument('--render',action='store_true');a=ap.parse_args()
 root=a.root.resolve();out=a.output.resolve();assert not out.is_relative_to(root);out.mkdir(parents=True,exist_ok=True)
 spec=importlib.util.spec_from_file_location('paper_xii_accepted_publication_audit',root/'tools/audit_publication.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
 fresh=v.check(root);dump(out/'ACCEPTED_PUBLICATION_CHECK_FRESH.json',fresh);assert fresh['status']=='PASS',fresh['errors']
 man=json.loads((root/'MANIFEST_SHA256.json').read_text());pins={r['path']:r for r in man['files']}
 build=json.loads((root/'evidence/block01/BUILD.json').read_text());built={d['file']:d for d in build['outputs'].values()}
 repro=json.loads((root/'verification/block01/REPRODUCIBILITY.json').read_text());assert repro['status']=='PASS' and repro['fresh_lean'] is False
 rp={r['file']:r for r in repro['pdfs']}
 archive_binding=None
 if a.reader_archive:
  with zipfile.ZipFile(a.reader_archive) as z:
   am=json.loads(z.read('MANIFEST_SHA256.json'));ar={r['path']:r for r in am['files']}
   for name,pg,digest in EXPECTED.values():
    assert ar[name]['sha256']==digest and hashlib.sha256(z.read(name)).hexdigest()==digest
  archive_binding={'path':str(a.reader_archive),'sha256':sha(a.reader_archive),'current_three_PDF_bytes_match':True}
 docs=[];total=Counter()
 for kind,(name,pages,digest) in EXPECTED.items():
  path=root/'publication/pdfs'/name;assert sha(path)==digest
  assert pins['publication/pdfs/'+name]['sha256']==digest
  assert built[name]['sha256']==digest and built[name]['pages']==pages
  assert rp[name]['sha256']==digest and rp[name]['pages']==pages
  assert rp[name]['byte_identical'] and rp[name]['text_identical'] and rp[name]['render_identical_100dpi']
  copies=[{'path':p.relative_to(root).as_posix(),'sha256':sha(p),'selected_bytes_match':sha(p)==digest} for p in sorted(root.rglob(name)) if p.is_file()]
  with fitz.open(path) as d:
   assert len(d)==pages
   names=d.resolve_names();toc=d.get_toc(simple=False);links=[l for pg in d for l in pg.get_links()];counts=Counter(str(l['kind']) for l in links);total.update(counts)
   for n,target in names.items():assert 0<=target['page']<pages,(name,n,target)
   for row in toc:
    assert 1<=row[2]<=pages,(name,row)
    if row[3].get('nameddest'):assert row[3]['nameddest'] in names
   spans=0;outside=[];replacements=[];empty=[];texts=[]
   for page in d:
    text=page.get_text();texts.append(text)
    if not text.strip():empty.append(page.number+1)
    rect=page.rect+(-.5,-.5,.5,.5)
    for b in page.get_text('dict')['blocks']:
     for line in b.get('lines',[]):
      for s in line['spans']:
       if not s['text'].strip():continue
       spans+=1
       if not rect.contains(fitz.Rect(s['bbox'])):outside.append({'page':page.number+1,'text':s['text'],'bbox':s['bbox']})
       if '\ufffd' in s['text']:replacements.append(page.number+1)
   assert outside==[] and replacements==[],(name,outside,replacements)
   contact_files=[]
   if a.render:
    for start in range(1,pages+1,20):
     selected=list(range(start,min(start+20,pages+1)));canvas=Image.new('RGB',(800,5*300),'#c7c7c7')
     for i,pg in enumerate(selected):
      im=render(d,pg,34);im.thumbnail((186,270));tile=Image.new('RGB',(200,300),'#efefef');tile.paste(im,((200-im.width)//2,22));ImageDraw.Draw(tile).text((8,4),f'{kind} / {pg}',fill='black');canvas.paste(tile,((i%4)*200,(i//4)*300))
     fn=kind+f'_contact_{start:03}.png';canvas.save(out/fn);contact_files.append({'file':fn,'pages':selected})
    for pg in DETAILS[kind]:render(d,pg,110).save(out/(kind+f'_detail_{pg:03}.png'))
   searched={phrase:[i+1 for i,t in enumerate(texts) if phrase.casefold() in t.casefold()] for phrase in ['conditional','same field','classical','nonempty','continuity','compatible','41','49','patching','full support','Frobenius','Conjecture 66']}
   docs.append({'kind':kind,'file':'publication/pdfs/'+name,'pages':pages,'bytes':path.stat().st_size,'sha256':digest,'same_named_copies':copies,'bookmarks':len(toc),'named_destinations':len(names),'annotation_links':len(links),'link_kinds':dict(counts),'all_named_destinations_and_bookmarks_in_range':True,'nonempty_text_spans':spans,'out_of_page_spans_0_5pt_tolerance':outside,'replacement_glyph_pages':replacements,'pages_without_extracted_text':empty,'scope_phrase_pages':searched,'contact_sheets':contact_files,'detail_pages':DETAILS[kind] if a.render else []})
  dump(out/(kind+'_check.json'),docs[-1])
 loc=json.loads((root/'evidence/block01/LOCATORS.json').read_text());routes=json.loads((root/'evidence/block01/ROUTES.json').read_text())
 assert len(routes)==94==loc['registered_routes'] and len(loc['routes'])==95==loc['annotations']
 assert fresh['registered_routes']==94 and fresh['companion_links']==95 and fresh['visual_lesson_pages']==list(range(1,28))
 result={'status':'PASS','checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Fresh read-only three current reader identities, all-page structural/navigation checks, exact recorded remote coordinates, source preservation audit and optional rendered review. No source/PDF build.','documents':docs,'selected_reader_pages':sum(d['pages'] for d in docs),'fresh_navigation_totals':{'annotation_links':sum(d['annotation_links'] for d in docs),'internal_links':fresh['internal_links'],'companion_links':fresh['companion_links'],'bookmarks':sum(d['bookmarks'] for d in docs),'named_destinations':sum(d['named_destinations'] for d in docs),'link_kinds':dict(total)},'registered_routes':94,'companion_annotations':95,'claim_routes':sum(k.startswith('claim-') for k in routes),'visual_lesson_pages':27,'reader_archive_binding':archive_binding,'recorded_rebuild':{'receipt':'verification/block01/REPRODUCIBILITY.json','receipt_sha256':sha(root/'verification/block01/REPRODUCIBILITY.json'),'scope':repro['scope'],'PDFs_byte_text_and_100dpi_pixels_equal':True,'four_regenerated_figure_records':repro['regenerated_figures'],'fresh_build_for_freeze':False,'cross_platform_byte_identity_claim':False},'accepted_publication_check_fresh_sha256':sha(out/'ACCEPTED_PUBLICATION_CHECK_FRESH.json'),'scope_qualifications':['Forty-nine revised claim links remain separate from original41complete/7partial/1unchecked census and eight amendments.','Conditional arithmetic applications must supply actual residual/deformation data, applicable patching and full support, compatible same-field Hecke point, classicality, attached representation, Frobenius comparison and required comparison inputs.','Companion completion starts with nonempty finite admissible classes plus actual coefficient/continuity assumptions; it does not create those classes.','Propagation assumes two already existing compatible families for the same automorphic object.','Paper XI Conjecture66 is not assumed proved.','Compiler evidence remains inherited. No fresh Lean/Lake or kernel acceptance is claimed for this freeze.','No new scientific/control suite, PDF builder, figure generator, external-source audit or whole-paper proof audit is performed.'],'release_blockers':[],'visual_review':{'status':'PENDING_MANUAL_REVIEW' if a.render else 'NOT_RENDERED','contact_pages':sum(len(s['pages']) for d in docs for s in d['contact_sheets']),'contact_sheets':sum(len(d['contact_sheets']) for d in docs),'detail_renders':sum(len(d['detail_pages']) for d in docs)}}
 dump(out/'reader_check.json',result)
 print(json.dumps({'status':result['status'],'pages':result['selected_reader_pages'],'navigation':result['fresh_navigation_totals'],'claim_routes':result['claim_routes'],'visual':result['visual_review']}))
if __name__=='__main__':main()
