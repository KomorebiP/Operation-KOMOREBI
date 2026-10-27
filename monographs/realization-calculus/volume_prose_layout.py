"""Translate reviewed pure-prose regions without reflow or font substitution.

Call after prose substitutions on a disposable display document. A failed
assertion must cause the caller to discard that document. Original inputs are
never opened for writing by this module.
"""
import collections,hashlib,math,re
import fitz
import numpy as np
from preserved_pdf_proofread import (ismath,annotations_snapshot,restore_annotations,pix)
from rebrand_components import _snapshot,_vector_difference

TOLERANCE_PT=.01


def _box(value):
 r=fitz.Rect(value)
 if not r.is_valid or r.is_empty:raise ValueError('Relocation needs a nonempty valid rectangle')
 return r


def _touches(rect,box):
 r=fitz.Rect(rect)
 if r.width==0:r.x1=r.x0+.001
 if r.height==0:r.y1=r.y0+.001
 return r.intersects(box)


def _inside(rect,box,tol=.005):
 r=fitz.Rect(rect)
 return r.x0>=box.x0-tol and r.y0>=box.y0-tol and r.x1<=box.x1+tol and r.y1<=box.y1+tol


def _chars(page):
 records=[]
 for block in page.get_text('rawdict')['blocks']:
  if block.get('type')!=0:continue
  for line in block.get('lines',[]):
   for span in line['spans']:
    for char in span['chars']:
     records.append({'c':char['c'],'font':span['font'],'size':span['size'],
      'color':span['color'],'alpha':span.get('alpha',255),'flags':span.get('flags',0),
      'origin':list(char['origin']),'bbox':list(char['bbox']),
      'dir':list(line.get('dir',(1,0))),'wmode':line.get('wmode',0),'math':ismath(span)})
 return records


def _ordered(chars):
 return sorted(chars,key=lambda c:(round(c['origin'][1],2),round(c['origin'][0],2),c['font'],c['c']))


def _compare_chars(expected,actual,tol=TOLERANCE_PT,bboxes=False):
 a,b=_ordered(expected),_ordered(actual)
 if len(a)!=len(b):raise ValueError('Native character count changed: '+str((len(a),len(b))))
 maximum=0.0
 for x,y in zip(a,b):
  for key in ('c','font','color','alpha','flags','dir','wmode'):
   if x[key]!=y[key]:raise ValueError('Native character/style changed: '+key+' '+repr((x[key],y[key])))
  maximum=max(maximum,abs(x['size']-y['size']),*(abs(v-w) for v,w in zip(x['origin'],y['origin'])))
  if bboxes:maximum=max(maximum,*(abs(v-w) for v,w in zip(x['bbox'],y['bbox'])))
 if maximum>tol:raise ValueError('Native character geometry changed beyond tolerance: '+str(maximum))
 return maximum


def _native_font_records(doc,page,chars):
 names={c['font'] for c in chars};normalize=lambda s:''.join(x for x in s.casefold() if x.isalnum())
 wanted={normalize(n) for n in names};records=[];seen=set()
 for row in page.get_fonts(full=True):
  pdf_name=row[3];face=re.sub(r'-Identity-[HV]$','',pdf_name.split('+')[-1])
  if normalize(face) not in wanted or row[0] in seen:continue
  seen.add(row[0]);data=doc.extract_font(row[0])[3]
  records.append({'source_face':face,'pdf_basefont_name':pdf_name,'source_resource':row[4],
    'native_font_program_sha256':hashlib.sha256(data).hexdigest() if data else None,
    'font_program_bytes':len(data),'source_pdf_font_reused_without_substitution':True})
 if not records:raise ValueError('Native prose font resources could not be authenticated')
 return records


def _shift_char(char,dx,dy):
 c=dict(char);c['origin']=[char['origin'][0]+dx,char['origin'][1]+dy]
 c['bbox']=[char['bbox'][0]+dx,char['bbox'][1]+dy,char['bbox'][2]+dx,char['bbox'][3]+dy]
 return c


def relocate_prose(doc,cid,configs):
 """Return per-page preservation records and point routes after native moves."""
 grouped=collections.defaultdict(list)
 for config in configs:
  if config.get('component_id',cid)!=cid:continue
  pn=int(config['source_page_1based'])-1
  if not 0<=pn<len(doc):raise ValueError('Relocation source page is out of range')
  grouped[pn].append(config)
 records=[];routes=[]
 for pn,items in sorted(grouped.items()):
  page=doc[pn];before_chars=_chars(page);before_pixels=pix(page)
  maths=[c for c in before_chars if c['math']];ann=annotations_snapshot(doc,page)
  graphics=_snapshot(page);plans=[];all_selected=[]
  for config in items:
   source=_box(config['source_bbox']);dx,dy=map(float,config['translation_points'])
   target=source+fitz.Rect(dx,dy,dx,dy)
   if not _inside(source,page.rect,0) or not _inside(target,page.rect,0):raise ValueError('Relocation rectangle leaves its page')
   if any(source.intersects(p['source']) for p in plans):raise ValueError('Relocation sources overlap')
   selected=[c for c in before_chars if _touches(c['bbox'],source)]
   if not selected:raise ValueError('Reviewed prose region has no native characters')
   if any(not _inside(c['bbox'],source) for c in selected):raise ValueError('Relocation would cut a source character')
   if any(c['math'] for c in selected):raise ValueError('Relocation would move mathematical font text')
   expected=config.get('expected_text_exact_after_edits')
   if expected is not None and page.get_text(clip=source)!=expected:
    raise ValueError('Exact reviewed post-edit prose does not match the source region')
   for char in selected:
    if char['dir']!=[1.0,0.0] or char['wmode']!=0:raise ValueError('Rotated or vertical prose is not supported')
   plans.append({'config':config,'source':source,'target':target,'dx':dx,'dy':dy,'chars':selected})
   all_selected.extend(selected)
  source_boxes=[p['source'] for p in plans];target_boxes=[p['target'] for p in plans];union=source_boxes+target_boxes
  for char in before_chars:
   if any(_touches(char['bbox'],box) for box in source_boxes):continue
   if any(_touches(char['bbox'],box) for box in target_boxes):raise ValueError('Target overlaps text outside the moved sources')
  for link in page.get_links():
   if any(fitz.Rect(link['from']).intersects(box) for box in union):raise ValueError('Prose relocation intersects a link')
  for annot in page.annots() or []:
   if any(annot.rect.intersects(box) for box in union):raise ValueError('Prose relocation intersects an annotation')
  for image in page.get_image_info(hashes=True):
   if any(fitz.Rect(image['bbox']).intersects(box) for box in union):raise ValueError('Prose relocation intersects an image')
  for drawing in page.get_drawings():
   if any(fitz.Rect(drawing['rect']).intersects(box) for box in union):raise ValueError('Prose relocation intersects a vector drawing')
  outside=[c for c in before_chars if not any(_touches(c['bbox'],box) for box in union)]
  # Retain native glyph programs and ToUnicode maps, including ligatures whose
  # raw Unicode continuations have zero width. A separate page copy is cleared
  # of every non-source character/image/vector before it is grafted as a Form.
  # This avoids both glyph reconstruction and hidden duplicate page content.
  fragments=[];moved=[];font_records=_native_font_records(doc,page,all_selected)
  try:
   for plan in plans:
    fragment=fitz.open();fragments.append(fragment);fragment.insert_pdf(doc,from_page=pn,to_page=pn,links=False,annots=False)
    fp=fragment[0];w,h=fp.rect.width,fp.rect.height;box=plan['source']
    complement=[fitz.Rect(0,0,w,box.y0),fitz.Rect(0,box.y1,w,h),
                fitz.Rect(0,box.y0,box.x0,box.y1),fitz.Rect(box.x1,box.y0,w,box.y1)]
    for remove in complement:
     if not remove.is_empty:fp.add_redact_annot(remove,fill=False,cross_out=False)
    fp.apply_redactions(images=2,graphics=2,text=0)
    _compare_chars(plan['chars'],_chars(fp),tol=.0002,bboxes=True)
    if fp.get_image_info() or fp.get_drawings():
     raise ValueError('Nonprose objects survived in the isolated native fragment')
   # Targets may overlap sources; clear all sources before showing any target.
   for box in source_boxes:page.add_redact_annot(box,fill=False,cross_out=False)
   page.apply_redactions(images=0,graphics=0,text=0)
   for plan,fragment in zip(plans,fragments):
    if abs(plan['target'].width-plan['source'].width)>.00001 or abs(plan['target'].height-plan['source'].height)>.00001:
     raise ValueError('A native prose fragment must be translated at exactly unit scale')
    page.show_pdf_page(plan['target'],fragment,0,clip=plan['source'],keep_proportion=False,overlay=True)
    moved.extend(_shift_char(c,plan['dx'],plan['dy']) for c in plan['chars'])
   restore_annotations(doc,page,ann);page=doc.reload_page(page)
  finally:
   for fragment in fragments:fragment.close()
  after_chars=_chars(page)
  actual_moved=[c for c in after_chars if any(_touches(c['bbox'],box) for box in target_boxes)]
  moved_delta=_compare_chars(moved,actual_moved,bboxes=True)
  outside_after=[c for c in after_chars if not any(_touches(c['bbox'],box) for box in union)]
  outside_delta=_compare_chars(outside,outside_after,tol=.0002,bboxes=True)
  math_delta=_compare_chars(maths,[c for c in after_chars if c['math']],tol=.0002,bboxes=True)
  if annotations_snapshot(doc,page)!=ann:raise ValueError('Prose relocation changed annotations')
  after_graphics=_snapshot(page)
  if graphics['images']!=after_graphics['images']:raise ValueError('Prose relocation changed native image data/placement')
  vector_delta=_vector_difference(graphics['drawings'],after_graphics['drawings'])
  after_pixels=pix(page);changed=np.any(before_pixels!=after_pixels,axis=2);mask=np.zeros(changed.shape,dtype=bool)
  for box in union:
   x0=max(0,math.floor(box.x0));y0=max(0,math.floor(box.y0))
   x1=min(mask.shape[1],math.ceil(box.x1));y1=min(mask.shape[0],math.ceil(box.y1));mask[y0:y1,x0:x1]=True
  changed_outside=int(np.count_nonzero(changed&~mask))
  if changed_outside:raise ValueError('Pixels changed outside prose relocation regions: '+str(changed_outside))
  row={'status':'PASS','component_id':cid,'source_page_1based':pn+1,'moves':[],
   'native_characters_moved':len(moved),'native_fonts':font_records,
   'method':'Exact native PDF prose Form at unit scale, with non-source content removed before grafting',
   'ligatures_and_original_ToUnicode_preserved':True,'hidden_non_source_fragment_content_removed':True,
   'native_text_font_style_and_origins_preserved':True,'moved_origin_tolerance_pt':TOLERANCE_PT,
   'max_moved_character_origin_size_or_bbox_delta_pt':moved_delta,
   'outside_characters_preserved':True,'max_outside_character_geometry_delta_pt':outside_delta,
   'mathematical_characters_unchanged':True,'max_math_geometry_delta_pt':math_delta,
   'annotations_unchanged':True,'native_images_unchanged':True,'native_vectors_unchanged':True,
   'max_vector_serialization_delta_pt':vector_delta,'pixels_changed_outside_source_target_union':0}
  for plan in plans:
   config=plan['config'];route_rect=list(_box(config.get('route_bbox',config['source_bbox'])))
   row['moves'].append({'source_bbox':list(plan['source']),'target_bbox':list(plan['target']),
     'translation_points':[plan['dx'],plan['dy']],'native_characters':len(plan['chars'])})
   routes.append({'source_page':pn,'rect':route_rect,'point_offset':[plan['dx'],plan['dy']]})
  records.append(row)
 return {'records':records,'prose_routes':routes}


def transfer_prose(doc,cid,configs):
 """Transfer one reviewed native prose fragment between two distinct pages.

 The caller must supply a disposable display document after its phase-zero
 local moves. Original glyph programs, ToUnicode mappings and ligatures are
 grafted intact, and both affected pages are checked independently.
 """
 selected_configs=[c for c in configs if c.get('component_id',cid)==cid]
 if not selected_configs:return {'records':[],'prose_routes':[]}
 if len(selected_configs)!=1:raise ValueError('Only one reviewed cross-page fragment is supported per component')
 config=selected_configs[0]
 sp=int(config['source_page_1based'])-1;tp=int(config['target_page_1based'])-1
 if sp==tp or not 0<=sp<len(doc) or not 0<=tp<len(doc):
  raise ValueError('Prose transfer needs two distinct valid pages')
 source=doc[sp];target_page=doc[tp];box=_box(config['source_bbox'])
 dx,dy=map(float,config['translation_points']);target=box+fitz.Rect(dx,dy,dx,dy)
 if not _inside(box,source.rect,0) or not _inside(target,target_page.rect,0):
  raise ValueError('Transferred prose rectangle leaves a page')
 before={sp:{'chars':_chars(source),'pixels':pix(source),'annotations':annotations_snapshot(doc,source),'graphics':_snapshot(source)},
         tp:{'chars':_chars(target_page),'pixels':pix(target_page),'annotations':annotations_snapshot(doc,target_page),'graphics':_snapshot(target_page)}}
 chars=[c for c in before[sp]['chars'] if _touches(c['bbox'],box)]
 if not chars or any(not _inside(c['bbox'],box) for c in chars):
  raise ValueError('Transferred source is empty or cuts a native character')
 if any(c['math'] or c['dir']!=[1.0,0.0] or c['wmode']!=0 for c in chars):
  raise ValueError('Only horizontal pure prose may be transferred')
 expected=config.get('expected_text_exact_after_edits',config.get('expected_text_exact'))
 if expected is None or source.get_text(clip=box)!=expected:
  raise ValueError('Transferred source does not match exact reviewed prose')
 if any(_touches(c['bbox'],target) for c in before[tp]['chars']):
  raise ValueError('Transferred prose target contains existing text')
 for page,region in [(source,box),(target_page,target)]:
  for link in page.get_links():
   if fitz.Rect(link['from']).intersects(region):raise ValueError('Prose transfer intersects a link')
  for annot in page.annots() or []:
   if annot.rect.intersects(region):raise ValueError('Prose transfer intersects an annotation')
  for image in page.get_image_info(hashes=True):
   if fitz.Rect(image['bbox']).intersects(region):raise ValueError('Prose transfer intersects an image')
  for drawing in page.get_drawings():
   if fitz.Rect(drawing['rect']).intersects(region):raise ValueError('Prose transfer intersects a vector drawing')
 font_records=_native_font_records(doc,source,chars)
 fragment=fitz.open()
 try:
  fragment.insert_pdf(doc,from_page=sp,to_page=sp,links=False,annots=False)
  fp=fragment[0];w,h=fp.rect.width,fp.rect.height
  complement=[fitz.Rect(0,0,w,box.y0),fitz.Rect(0,box.y1,w,h),
              fitz.Rect(0,box.y0,box.x0,box.y1),fitz.Rect(box.x1,box.y0,w,box.y1)]
  for remove in complement:
   if not remove.is_empty:fp.add_redact_annot(remove,fill=False,cross_out=False)
  fp.apply_redactions(images=2,graphics=2,text=0)
  fragment_delta=_compare_chars(chars,_chars(fp),tol=.0002,bboxes=True)
  if fp.get_image_info() or fp.get_drawings():
   raise ValueError('Nonprose content survived in transferred native fragment')
  if abs(target.width-box.width)>.00001 or abs(target.height-box.height)>.00001:
   raise ValueError('Transferred native prose must retain unit scale')
  source.add_redact_annot(box,fill=False,cross_out=False)
  source.apply_redactions(images=0,graphics=0,text=0)
  restore_annotations(doc,source,before[sp]['annotations'])
  target_page.show_pdf_page(target,fragment,0,clip=box,keep_proportion=False,overlay=True)
  restore_annotations(doc,target_page,before[tp]['annotations'])
 finally:fragment.close()
 expected_moved=[_shift_char(c,dx,dy) for c in chars];page_records=[];moved_delta=None
 source=doc.reload_page(source);target_page=doc.reload_page(target_page)
 for pn,region,page in [(sp,box,source),(tp,target,target_page)]:
  after_chars=_chars(page);state=before[pn]
  if pn==sp:
   if any(_touches(c['bbox'],region) for c in after_chars):
    raise ValueError('Transferred prose source was not cleared')
  else:
   actual_moved=[c for c in after_chars if _touches(c['bbox'],region)]
   moved_delta=_compare_chars(expected_moved,actual_moved,bboxes=True)
  outside_before=[c for c in state['chars'] if not _touches(c['bbox'],region)]
  outside_after=[c for c in after_chars if not _touches(c['bbox'],region)]
  outside_delta=_compare_chars(outside_before,outside_after,tol=.0002,bboxes=True)
  math_delta=_compare_chars([c for c in state['chars'] if c['math']],
                            [c for c in after_chars if c['math']],tol=.0002,bboxes=True)
  if annotations_snapshot(doc,page)!=state['annotations']:
   raise ValueError('Prose transfer changed annotations')
  graphics=_snapshot(page)
  if graphics['images']!=state['graphics']['images']:
   raise ValueError('Prose transfer changed an image or its placement')
  vector_delta=_vector_difference(state['graphics']['drawings'],graphics['drawings'])
  after_pixels=pix(page);changed=np.any(state['pixels']!=after_pixels,axis=2)
  x0=max(0,math.floor(region.x0));y0=max(0,math.floor(region.y0))
  x1=min(changed.shape[1],math.ceil(region.x1));y1=min(changed.shape[0],math.ceil(region.y1))
  changed[y0:y1,x0:x1]=False
  count=int(np.count_nonzero(changed))
  if count:raise ValueError('Pixels changed outside a prose-transfer region: '+str(count))
  page_records.append({'page_1based':pn+1,'role':'source' if pn==sp else 'target','status':'PASS',
    'outside_characters_preserved':True,'max_outside_character_geometry_delta_pt':outside_delta,
    'mathematical_characters_unchanged':True,'max_math_geometry_delta_pt':math_delta,
    'annotations_unchanged':True,'native_images_unchanged':True,'native_vectors_unchanged':True,
    'max_vector_serialization_delta_pt':vector_delta,'pixels_changed_outside_region':0})
 record={'status':'PASS','component_id':cid,'source_page_1based':sp+1,'target_page_1based':tp+1,
  'source_bbox':list(box),'target_bbox':list(target),'translation_points':[dx,dy],
  'native_characters_transferred':len(chars),'native_fonts':font_records,
  'method':'Exact native PDF prose Form at unit scale, with non-source content removed before grafting',
  'ligatures_and_original_ToUnicode_preserved':True,'hidden_non_source_fragment_content_removed':True,
  'native_text_font_style_origins_and_bboxes_preserved':True,
  'max_fragment_geometry_serialization_delta_pt':fragment_delta,
  'max_moved_character_origin_size_or_bbox_delta_pt':moved_delta,
  'moved_origin_tolerance_pt':TOLERANCE_PT,'source_cleared':True,
  'target_previously_empty':True,'page_checks':page_records}
 route={'source_page':sp,'target_source_page':tp,
        'rect':list(_box(config.get('route_bbox',config['source_bbox']))),
        'point_offset':[dx,dy]}
 return {'records':[record],'prose_routes':[route]}
