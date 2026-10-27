"""Resolve reviewed prose operations to exact native PDF blocks and lines."""
from pathlib import Path
import json,re,sys,unicodedata,collections,zipfile,argparse
import fitz
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from preserved_pdf_proofread import block_text,all_spans,ismath,prepare_region,targeted_region,prepare_table
from volume_finish_adapter import prepare_native_substring
DIR=ROOT/'editorial/volume_finish'
def canon(s):
 s=unicodedata.normalize('NFKC',s)
 s=re.sub(r'(?<=[A-Za-z])-\s*\n\s*(?=[a-z])','',s)
 return re.sub(r'\s+',' ',s).strip()
def load_ops():
 ops=[];omit=collections.defaultdict(set)
 for name,key in [('i_iv_plan.json','entries'),('v_viii_plan.json','operations'),('ix_xii_plan.json','operations'),('bibliography_prose_plan.json','operations')]:
  p=DIR/name
  if not p.exists():continue
  j=json.loads(p.read_text());entries=j.get(key,j.get('changes',j.get('entries',j.get('edits',[]))))
  for i,x in enumerate(entries):
   action=x.get('kind',x.get('action','replace_phrase'))
   kind={'replace_line':'exact_lines','remove_line':'exact_lines','remove_block':'replace_block','omit_block':'replace_block'}.get(action,action)
   ops.append({**x,'kind':kind,'plan':name,'plan_index':i})
  for x in j.get('whole_page_exclusions',j.get('whole_page_exclusion_candidates',[])):omit[x['component_id']].update(x.get('source_pages_1based',x.get('pages_1based',[])))
  if name=='ix_xii_plan.json':
   # Standalone technical receipts, without bibliographic or mathematical text.
   omit['IX_traditional'].update([73,74,75,76,77,78])
   omit['XI_lean'].update([35,36])
 return ops,omit

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--baseline-package',type=Path,default=Path('/workspace/scratch/fbc994080222/komorebi_core_monograph_delivery/Realization_Calculus_Publication_Package.zip'),help='Exact preceding publication package, retained separately as provenance.')
 args=parser.parse_args();archive=zipfile.ZipFile(args.baseline_package)
 def baseline_doc(c):
  name='Realization_Calculus_Publication_Package/'+c['path']
  data=archive.read(name)
  import hashlib
  if hashlib.sha256(data).hexdigest()!=c['sha256']:raise ValueError('Baseline component hash mismatch: '+c['id'])
  return fitz.open(stream=data,filetype='pdf')
 ops,omit=load_ops();spec=json.loads((DIR/'baseline_build_spec.json').read_text());comps={c['id']:c for p in spec['parts'] for c in p['components']};docs={}
 groups={};linegroups={};errors=[];decisions=[]
 def record(o,status,**kw):decisions.append({'plan':o['plan'],'plan_index':o['plan_index'],'component_id':o['component_id'],'page':o.get('source_page_1based',o.get('page_1based')),'status':status,**kw})
 for o in ops:
  cid=o['component_id'];pn=o.get('source_page_1based',o.get('page_1based'))
  if pn in omit[cid]:record(o,'OMITTED_PAGE');continue
  if o.get('category')=='protected_catalogue':record(o,'PROTECTED_SOURCE_QUOTATION');continue
  if cid not in docs:docs[cid]=baseline_doc(comps[cid])
  page=docs[cid][pn-1];blocks=[b for b in page.get_text('dict')['blocks'] if b.get('type')==0]
  old=o.get('old',o.get('old_text',''));new=o.get('new',o.get('new_text'))
  kind=o.get('kind','replace_phrase')
  if new is None:
   record(o,'REQUIRES_EXPLICIT_SOURCE_RECORD_SCOPE');continue
  if kind=='exact_lines':
   box=fitz.Rect(o['bbox']);hits=[]
   for bi,b in enumerate(blocks):
    for li,l in enumerate(b['lines']):
     if canon(''.join(s['text'] for s in l['spans']))==canon(old) and fitz.Rect(l['bbox']).intersects(box):hits.append((bi,li,l))
   if len(hits)!=1:
    errors.append({**o,'failure':'exact line anchor not unique','matches':len(hits)});continue
   bi,li,l=hits[0];key=(cid,pn,bi,li)
   linegroups[key]={'component_id':cid,'page_1based':pn,'kind':'exact_lines','old_text_exact':''.join(s['text'] for s in l['spans']),'bbox_optional':list(l['bbox']),'new_text':new,'proposals':[o]}
   record(o,'RESOLVED_LINE');continue
  if kind=='omit_region':
   box=fitz.Rect(o['bbox']);bad=[];marker_count=0
   for b in page.get_text('rawdict')['blocks']:
    for l in b.get('lines',[]):
     for s in l['spans']:
      for char in s['chars']:
       rr=fitz.Rect(char['bbox'])
       if rr.intersects(box) and ismath(s) and char['c'].strip():
        if o.get('nonmathematical_layout_marker_exception') and char['c']=='↪':marker_count+=1
        else:bad.append(char['c'])
   if bad:errors.append({**o,'failure':'bounded omission crosses mathematical glyphs','glyphs':bad});continue
   key=(cid,pn,'rect',tuple(box));linegroups[key]={'component_id':cid,'page_1based':pn,'kind':'bounded_omission','old_text_exact':page.get_text(clip=box),'bbox_optional':list(box),'new_text':'','proposals':[o],'layout_marker_exception':marker_count,'clear_table_rules':bool(o.get('nonmathematical_table_rules_in_region'))}
   record(o,'RESOLVED_REGION',layout_markers=marker_count);continue
  matches=[(bi,b) for bi,b in enumerate(blocks) if canon(old) in canon(block_text(b))]
  if len(matches)!=1:
   errors.append({**o,'failure':'anchor block not unique','matches':len(matches)});record(o,'UNRESOLVED');continue
  bi,b=matches[0];key=(cid,pn,bi)
  groups.setdefault(key,{'component_id':cid,'page_1based':pn,'kind':'replace_block','old_text_exact':block_text(b),'bbox_optional':list(b['bbox']),'new_text':canon(block_text(b)),'proposals':[],'math_spans_present':any(ismath(s) for s in all_spans(b))})
  g=groups[key]
  if canon(old) not in g['new_text']:
   errors.append({**o,'failure':'overlapping or duplicate replacement'});continue
  if g['new_text'].count(canon(old))!=1 and not o.get('all_occurrences'):
   errors.append({**o,'failure':'anchor repeats inside block'});continue
  g['new_text']=g['new_text'].replace(canon(old),canon(new));g['proposals'].append(o);record(o,'RESOLVED_BLOCK')
 edits=[]
 for key,g in groups.items():
  cid,pn,bi=key;page=docs[cid][pn-1];b=[x for x in page.get_text('dict')['blocks'] if x.get('type')==0][bi]
  try:
   if any(o['kind']=='targeted_substitutions' for o in g['proposals']):
    pairs=[(o.get('old',o.get('old_text','')),o.get('new',o.get('new_text'))) for o in g['proposals']]
    for a,z in pairs:prepare_native_substring(page,b,a,z)
    g['kind']='native_substrings';g['text_substitutions']=pairs
   elif any(o['kind']=='replace_table_cells' for o in g['proposals']):
    pairs=[(o.get('old',o.get('old_text','')),o.get('new',o.get('new_text'))) for o in g['proposals']]
    prepare_table(page,b,pairs)
    g['kind']='replace_table_cells';g['text_substitutions']=pairs
   elif g['math_spans_present']:
    pairs=[(o.get('old',o.get('old_text','')),o.get('new',o.get('new_text'))) for o in g['proposals']]
    for a,z in pairs:targeted_region(page,b,a,z)
    g['kind']='targeted_substitutions';g['text_substitutions']=pairs
   else:prepare_region(page,g['bbox_optional'],g['new_text'],all_spans(b),b['lines'])
   edits.append(g)
  except Exception as ex:
   errors.append({'component_id':cid,'page':pn,'failure':'native prose fit: '+str(ex),'group':g})
 for key,g in linegroups.items():
  # A table cell and a different physical line can share one extracted block.
  # Their actual prepared rectangles are checked for overlap before application.
  edits.append(g)
 for d in docs.values():d.close()
 for e in edits:
  if e['component_id']=='V_traditional' and e['page_1based']==40:
   e['reviewed_image_edge_region']=[212,76,522,316]
   e['image_edge_reason']='MuPDF resamples the indexed heatmap image differently at existing color edges after native text editing. Permit only those edge pixels when the exact native image digest, dimensions, placement and all vector paths/styles and outside glyphs are independently preserved.'
 result={'schema':'realization-calculus.volume-display/1','edits':edits,'omit_pages_1based':{k:sorted(v) for k,v in omit.items() if v},'decisions':decisions,'unresolved':errors}
 (DIR/'display_edits.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
 (DIR/'display_resolution_summary.json').write_text(json.dumps({'resolved':len(edits),'omitted_pages':sum(map(len,omit.values())),'unresolved':len(errors),'decisions':collections.Counter(x['status'] for x in decisions)},indent=2)+'\n')
 print((DIR/'display_resolution_summary.json').read_text())
if __name__=='__main__':main()
