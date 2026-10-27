from pathlib import Path
import json,zipfile,fitz,re,sys,unicodedata,collections
R=Path('/dev/shm/komorebi_core_monograph_fbc994080222');sys.path.insert(0,str(R));from preserved_pdf_proofread import prepare_region,targeted_region,prepare_table,all_spans,ismath,block_text
O=R/'editorial/volume_finish';J=json.loads((O/'ix_residual_additions.json').read_text());S=json.loads((O/'baseline_build_spec.json').read_text());C={c['id']:c for p in S['parts'] for c in p['components']};Z=zipfile.ZipFile('/workspace/scratch/fbc994080222/komorebi_core_monograph_delivery/Realization_Calculus_Publication_Package.zip');D={cid:fitz.open(stream=Z.read('Realization_Calculus_Publication_Package/'+C[cid]['path']),filetype='pdf') for cid in ['IX_traditional','IX_lean','IX_visual']}
def canon(s):
 s=unicodedata.normalize('NFKC',s);s=re.sub(r'(?<=[A-Za-z])-\s*\n\s*(?=[a-z])','',s);return re.sub(r'\s+',' ',s).strip()
groups={};errors=[];nrect=nline=0
for ix,x in enumerate(J['changes']):
 cid=x['component_id'];pn=x['source_page_1based'];pg=D[cid][pn-1];kind=x['kind'];old=x['old'];new=x['new']
 if kind=='omit_region':
  box=fitz.Rect(x['bbox']);bad=[c['c'] for b in pg.get_text('rawdict')['blocks'] for l in b.get('lines',[]) for s in l['spans'] if ismath(s) for c in s['chars'] if c['c'].strip() and fitz.Rect(c['bbox']).intersects(box)]
  if bad:errors.append({'index':ix,'component_id':cid,'page':pn,'failure':'bounded omission crosses math','glyphs':bad})
  nrect+=1;continue
 blocks=[b for b in pg.get_text('dict')['blocks'] if b.get('type')==0]
 if kind=='exact_lines':
  hits=[l for b in blocks for l in b['lines'] if canon(''.join(s['text'] for s in l['spans']))==canon(old) and fitz.Rect(l['bbox']).intersects(fitz.Rect(x['bbox']))]
  if len(hits)!=1:errors.append({'index':ix,'failure':'line-anchor','matches':len(hits)})
  else:
   l=hits[0]
   try:prepare_region(pg,l['bbox'],new,l['spans'],[l])
   except Exception as e:errors.append({'index':ix,'component_id':cid,'page':pn,'failure':str(e)})
  nline+=1;continue
 hits=[(bi,b) for bi,b in enumerate(blocks) if canon(old) in canon(block_text(b))]
 if len(hits)!=1:errors.append({'index':ix,'component_id':cid,'page':pn,'failure':'block-anchor','matches':len(hits),'old':old});continue
 bi,b=hits[0];key=(cid,pn,bi);g=groups.setdefault(key,{'block':b,'new':canon(block_text(b)),'ops':[]})
 if g['new'].count(canon(old))!=1:errors.append({'index':ix,'failure':'repeated-or-overlap','old':old});continue
 g['new']=g['new'].replace(canon(old),canon(new));g['ops'].append((ix,x))
for (cid,pn,bi),g in groups.items():
 b=g['block'];pg=D[cid][pn-1];pairs=[(x['old'],x['new']) for _,x in g['ops']]
 try:
  if any(x['kind']=='replace_table_cells' for _,x in g['ops']):prepare_table(pg,b,pairs)
  elif any(ismath(s) for s in all_spans(b)):
   for a,z in pairs:targeted_region(pg,b,a,z)
  else:prepare_region(pg,b['bbox'],g['new'],all_spans(b),b['lines'])
 except Exception as e:errors.append({'indices':[i for i,_ in g['ops']],'component_id':cid,'page':pn,'failure':str(e),'pairs':pairs})
res={'status':'PASS' if not errors else 'FAIL','bounded_regions':nrect,'exact_lines':nline,'prose_groups':len(groups),'errors':errors};(O/'ix_residual_native_fit.json').write_text(json.dumps(res,indent=2,ensure_ascii=False)+'\n');print(json.dumps(res,indent=2,ensure_ascii=False))
