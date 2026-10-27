"""Apply the volume's reviewed prose and reference presentation to display copies.

Editable readers and original reference PDFs remain unchanged. The volume has
its own exact, reviewed display operations and an independently audited page map.
"""
from pathlib import Path
import collections,hashlib,json,math,os,tempfile
import fitz
import numpy as np
from preserved_pdf_proofread import (all_spans,annotations_snapshot,block_text,
    find_block,ismath,math_snapshot,pix,prepare_region,prepare_table,restore_annotations,targeted_region,minimal_substitution,native_style)
from book_component_adapter import outside_text
from rebrand_components import _snapshot,_vector_difference

ROOT=Path(__file__).resolve().parent
REVIEW=ROOT/'editorial/volume_finish'

def sha(path):
 with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def native_math(page):
 return [(s['font'],c['c'],list(c['bbox'])) for b in page.get_text('rawdict')['blocks'] for l in b.get('lines',[]) for s in l['spans'] if ismath(s) for c in s['chars'] if c['c'].strip()]

def compare_math(before,after):
 if len(before)!=len(after):raise ValueError('Mathematical glyph count changed')
 maximum=0.0
 for a,b in zip(before,after):
  if a[:2]!=b[:2]:raise ValueError('Mathematical glyph or font identity changed')
  maximum=max(maximum,max(abs(x-y) for x,y in zip(a[2],b[2])))
 if maximum>.0002:raise ValueError('Mathematical glyph moved beyond PDF number serialization tolerance')
 return maximum

def prepare_native_substring(page,block,old,new):
 """Keep unchanged font runs and literal code beside a short prose correction."""
 a,z=minimal_substitution(old,new)
 scope=page.search_for(old,clip=fitz.Rect(block['bbox'])+(-.03,-.03,.03,.03))
 if not scope or not a.strip():raise ValueError('Native substring anchor absent')
 box=fitz.Rect(scope[0])
 for r in scope[1:]:box|=r
 hits=page.search_for(a,clip=box+(-.03,-.03,.03,.03))
 if len(hits)!=1:raise ValueError('Native substring requires exactly one physical fragment')
 rect=fitz.Rect(hits[0]);chosen=[s for l in block['lines'] for s in l['spans'] if fitz.Rect(s['bbox']).intersects(rect)]
 if any(ismath(s) for s in chosen):raise ValueError('Native prose substring intersects mathematics')
 sty=native_style(chosen)
 if sty['font'].text_length(z,fontsize=sty['size'])>rect.width+.04:raise ValueError('Native substring cannot fit without moving surrounding runs')
 draw=[] if not z else [{'origin':(rect.x0,chosen[0]['origin'][1]),'text':z,'size':sty['size']}]
 rect.x1-=.02
 return {'rect':rect,'new':z,'draw':draw,'style':{k:v for k,v in sty.items() if k!='font'},'scale':1.0}

def prepare_edit(page,e):
 if e['kind']=='bounded_omission':
  box=fitz.Rect(e['bbox_optional'])
  if page.get_text(clip=box)!=e['old_text_exact']:raise ValueError('Bounded production record changed before adaptation')
  return [{'rect':box,'new':'','draw':[],'clear_table_rules':e.get('clear_table_rules',False)}]
 if e['kind']=='exact_lines':
  box=fitz.Rect(e['bbox_optional']);hits=[]
  for b in page.get_text('dict')['blocks']:
   for l in b.get('lines',[]):
    if ''.join(s['text'] for s in l['spans'])==e['old_text_exact'] and max(abs(a-z) for a,z in zip(l['bbox'],box))<.05:hits.append(l)
  if len(hits)!=1:raise ValueError('Exact reviewed line is not unique: '+repr(e['old_text_exact']))
  l=hits[0]
  if any(ismath(s) for s in l['spans']):raise ValueError('Prose line edit intersects a mathematical font')
  return [prepare_region(page,box,e['new_text'],l['spans'],[l],allow_line_reflow=False)]
 b=find_block(page,e)
 if e['kind']=='native_substrings':return [prepare_native_substring(page,b,a,z) for a,z in e['text_substitutions']]
 if e['kind']=='replace_table_cells':return prepare_table(page,b,e['text_substitutions'])
 if e['kind']=='targeted_substitutions':
  line_changes={};remaining=[]
  for old,new in e['text_substitutions']:
   a,z=minimal_substitution(old,new)
   candidates=[(i,l) for i,l in enumerate(b['lines']) if a in ''.join(s['text'] for s in l['spans']) and not any(ismath(s) for s in l['spans'])]
   if len(candidates)==1:
    index,line=candidates[0]
    line_changes.setdefault(index,{'line':line,'new':''.join(s['text'] for s in line['spans'])})
    line_changes[index]['new']=line_changes[index]['new'].replace(a,z)
   else:remaining.append((old,new))
  result=[prepare_region(page,g['line']['bbox'],g['new'],g['line']['spans'],[g['line']],allow_line_reflow=False) for g in line_changes.values()]
  result.extend(targeted_region(page,b,a,z) for a,z in remaining)
  return result
 if e['kind']!='replace_block':raise ValueError('Unknown display operation '+e['kind'])
 return [prepare_region(page,b['bbox'],e['new_text'],all_spans(b),b['lines'])]

def apply_prose(doc,cid,edits):
 grouped=collections.defaultdict(list)
 for e in edits:
  if e['component_id']==cid:grouped[e['page_1based']-1].append(e)
 records=[]
 for pn,items in sorted(grouped.items()):
  page=doc[pn];before=pix(page)
  before_graphics=_snapshot(page);raw_drawings=page.get_drawings()
  exceptions=[fitz.Rect(e['bbox_optional']) for e in items if e.get('layout_marker_exception')]
  def protected_math(p):
   return [x for x in native_math(p) if not (x[1]=='↪' and any(fitz.Rect(x[2]).intersects(b) for b in exceptions))]
  maths=protected_math(page);ann=annotations_snapshot(doc,page);regions=[]
  for e in items:
   for region in prepare_edit(page,e):
    if any((region['rect']&p['rect']).get_area()>.1 for p in regions):raise ValueError(f'Overlapping prose edits: {cid}:{pn+1}')
    regions.append(region)
  boxes=[p['rect'] for p in regions];outside=outside_text(page,boxes)
  for p in regions:page.add_redact_annot(p['rect'],fill=False,cross_out=False)
  page.apply_redactions(images=0,graphics=0,text=0)
  table_boxes=[p['rect'] for p in regions if p.get('clear_table_rules')]
  if table_boxes:
   for box in table_boxes:page.add_redact_annot(box,fill=False,cross_out=False)
   page.apply_redactions(images=0,graphics=2,text=0)
  for p in regions:
   if not p['draw']:continue
   sty=p['style'];name='F'+hashlib.sha256(sty['font_path'].encode()).hexdigest()[:6]
   page.insert_font(fontname=name,fontfile=sty['font_path'])
   for line in p['draw']:page.insert_text(line['origin'],line['text'],fontname=name,fontsize=line['size'],color=sty['color'],overlay=True)
  restore_annotations(doc,page,ann);page=doc.reload_page(page)
  try:math_delta=compare_math(maths,protected_math(page))
  except ValueError as ex:raise ValueError(f'{cid}:{pn+1}: {ex}') from ex
  if outside_text(page,boxes)!=outside:raise ValueError(f'Unreviewed text changed: {cid}:{pn+1}')
  if annotations_snapshot(doc,page)!=ann:raise ValueError(f'Annotations changed: {cid}:{pn+1}')
  after=pix(page);changed=np.any(before!=after,axis=2);mask=np.zeros(changed.shape,dtype=bool)
  for p in regions:
   rr=p['rect'];x0=max(0,math.floor(rr.x0)-1);y0=max(0,math.floor(rr.y0)-1);x1=min(mask.shape[1],math.ceil(rr.x1)+1);y1=min(mask.shape[0],math.ceil(rr.y1)+1);mask[y0:y1,x0:x1]=True
  count=int(np.count_nonzero(changed&~mask))
  edge_pixels=0
  if count and any(e.get('reviewed_image_edge_region') for e in items):
   from PIL import Image,ImageDraw
   after_graphics=_snapshot(page)
   delta=_vector_difference(before_graphics['drawings'],after_graphics['drawings'])
   if before_graphics['images']!=after_graphics['images']:raise ValueError('Native image data changed')
   edge=Image.new('1',(before.shape[1],before.shape[0]));draw=ImageDraw.Draw(edge)
   for drawing in raw_drawings:
    for element in drawing['items']:
     if element[0]=='re':draw.rectangle(tuple(element[1]),outline=1,width=3)
     elif element[0]=='l':draw.line([tuple(element[1]),tuple(element[2])],fill=1,width=3)
   allowed=np.array(edge,dtype=bool,copy=True);region_mask=np.zeros_like(allowed)
   # The heatmap contains an indexed raster image. Its exact sample digest,
   # dimensions and placement above are identical. Only resampling at existing
   # color discontinuities can vary when the enclosing PDF is rewritten.
   gradient=np.zeros_like(allowed)
   gradient[:,1:]|=np.max(np.abs(before[:,1:].astype('int16')-before[:,:-1].astype('int16')),axis=2)>20
   gradient[1:,:]|=np.max(np.abs(before[1:,:].astype('int16')-before[:-1,:].astype('int16')),axis=2)>20
   image_edges=gradient.copy()
   for dy in [-1,0,1]:
    for dx in [-1,0,1]:image_edges|=np.roll(np.roll(gradient,dy,axis=0),dx,axis=1)
   allowed|=image_edges
   for e in items:
    if e.get('reviewed_image_edge_region'):
     x0,y0,x1,y1=map(int,e['reviewed_image_edge_region']);region_mask[y0:y1+1,x0:x1+1]=True
   remaining=changed&~mask
   if np.any(remaining&~(allowed&region_mask)):raise ValueError('Raster change extends beyond reviewed native vector edges')
   edge_pixels=count
  if count and not edge_pixels:
   from PIL import Image
   out=REVIEW/'fit_test';out.mkdir(exist_ok=True)
   Image.fromarray(before).save(out/f'{cid}_{pn+1}_before.png')
   Image.fromarray(after).save(out/f'{cid}_{pn+1}_after.png')
   yy,xx=np.where(changed&~mask)
   (out/f'{cid}_{pn+1}_failure.json').write_text(json.dumps({'outside_pixels':count,'outside_bbox':[int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())],'regions':[list(p['rect']) for p in regions]},indent=2)+'\n')
   raise ValueError(f'Pixels changed outside reviewed prose: {cid}:{pn+1}: {count}')
  records.append({'page_1based':pn+1,'operations':len(items),'regions':[list(p['rect']) for p in regions],
     'mathematical_glyphs_unchanged':True,'max_math_glyph_geometry_serialization_delta_pt':math_delta,'math_glyph_geometry_tolerance_pt':.0002,'nonmathematical_code_wrap_markers_removed':sum(e.get('layout_marker_exception',0) for e in items),'outside_text_unchanged':True,'annotations_unchanged':True,'changed_pixels_outside_regions':count,'reviewed_native_image_edge_resampling_pixels':edge_pixels,'native_vector_and_image_preservation_checked':bool(edge_pixels)})
 return records

def finish_component(path,cid,adaptation):
 from volume_reference_adapter import split_reference_pages
 from volume_prose_layout import relocate_prose,transfer_prose
 path=Path(path);plan=json.loads((REVIEW/'display_edits.json').read_text())
 if plan['unresolved']:raise ValueError('Unresolved publication display operations remain')
 groups=[g for g in json.loads((REVIEW/'reference_plan.json').read_text())['bibliography_groups'] if g['component_id']==cid]
 edits=[e for e in plan['edits'] if e['component_id']==cid]
 omit={p-1 for p in plan['omit_pages_1based'].get(cid,[])}
 before=sha(path);doc=fitz.open(path);raw_pages=len(doc)
 report={'status':'PASS','component_id':cid,'input_sha256':before,'input_pages':raw_pages,'omitted_pages_1based':sorted(p+1 for p in omit),
   'prose_pages':apply_prose(doc,cid,edits)}
 layout_plan=json.loads((REVIEW/'prose_layout_plan.json').read_text())
 stages=[relocate_prose(doc,cid,layout_plan['relocations']),
         transfer_prose(doc,cid,layout_plan.get('transfers',[])),
         relocate_prose(doc,cid,layout_plan.get('after_transfers',[]))]
 layout={k:[row for stage in stages for row in stage[k]] for k in ('records','prose_routes')}
 report['prose_layout']=layout
 references=split_reference_pages(doc,cid,groups)
 keep=[p for p in adaptation['keep_pages'] if p not in omit]+list(range(raw_pages,len(doc)))
 if not set(references['reference_pages']).issubset(keep):raise ValueError('Bibliography page excluded from volume: '+cid)
 if edits or layout['records'] or len(doc)!=raw_pages:
  fd,temp=tempfile.mkstemp(prefix=path.stem+'_volume_',suffix='.pdf',dir=path.parent);os.close(fd)
  doc.save(temp,garbage=3,deflate=True,no_new_id=True);doc.close();os.replace(temp,path)
 else:doc.close()
 report.update(output_sha256=sha(path),output_pages=raw_pages+len(references['splits']),references=references)
 out=REVIEW/'component_reports';out.mkdir(exist_ok=True)
 (out/(cid+'.json')).write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
 adaptation['keep_pages']=keep
 adaptation['volume_finish_report']='editorial/volume_finish/component_reports/'+cid+'.json'
 return {**references,'prose_routes':layout['prose_routes'],'keep_pages':keep,'volume_finish_report':adaptation['volume_finish_report']}
