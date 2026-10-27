"""Conservative, bounded prose edits to preserved PDF reading derivatives.

Input originals are never modified. Mathematical fonts, drawing/image content,
page count, outlines, and existing annotation objects are preserved. A proposed
edit is skipped rather than forced when its exact anchor, pure-prose scope, or
legible geometric fit cannot be established. Root's branding adapter may run
on the resulting PDFs afterwards.
"""
from __future__ import annotations
from pathlib import Path
import argparse,collections,copy,difflib,hashlib,json,math,re,statistics
import fitz
import numpy as np

ROOT=Path(__file__).resolve().parent
DEFAULT_PROPOSALS=ROOT/'editorial/book_revision/preserved_prose_edits.json'
FONTROOT=Path('/usr/share/fonts/opentype/urw-base35')
MATH=re.compile(r'Math|^CM(?:MI|SY|EX|R|SS|TI)|^MS[AB]|Symbol|rsfs|stmary|msbm',re.I)

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rect_values(r):return [float(x) for x in r]
def rgb(i):return ((i>>16&255)/255,(i>>8&255)/255,(i&255)/255)
def plain(s):return re.sub(r'\s+',' ',s).strip()
def block_text(b):return ''.join(''.join(s['text'] for s in l['spans'])+'\n' for l in b.get('lines',[]))
def all_spans(b):return [s for l in b.get('lines',[]) for s in l['spans']]
def ismath(s):return bool(MATH.search(s['font']))
def font_file(name):
 sans=any(k in name.lower() for k in ['sans','sanl','helvetica'])
 mono=any(k in name.lower() for k in ['mono','courier'])
 bold=any(k in name.lower() for k in ['bold','boldital','demi'])
 italic=any(k in name.lower() for k in ['italic','ital','oblique'])
 family='NimbusMonoPS' if mono else 'NimbusSans' if sans else 'P052'
 style=('BoldItalic' if italic else 'Bold') if bold else ('Italic' if italic else 'Regular' if family!='P052' else 'Roman')
 p=FONTROOT/(family+'-'+style+'.otf')
 if not p.exists():raise ValueError('Native-family font unavailable: '+str(p))
 return p

def native_style(spans):
 weights=collections.Counter()
 for s in spans:
  if s['text'].strip():weights[s['font']]+=len(s['text'])
 name=weights.most_common(1)[0][0]
 selected=[s for s in spans if s['font']==name]
 size=statistics.median(s['size'] for s in selected)
 color=collections.Counter(s['color'] for s in selected).most_common(1)[0][0]
 p=font_file(name);f=fitz.Font(fontfile=str(p))
 return {'source_font':name,'font_path':str(p),'font':f,'size':size,'color':rgb(color)}

def find_block(page,e):
 box=fitz.Rect(e['bbox_optional']);blocks=[b for b in page.get_text('dict')['blocks'] if b.get('type')==0]
 exact=[b for b in blocks if block_text(b)==e['old_text_exact'] and fitz.Rect(b['bbox']).intersects(box)]
 if len(exact)!=1:raise ValueError(f'Expected one exact text block, found {len(exact)}')
 b=exact[0]
 if max(abs(a-z) for a,z in zip(b['bbox'],box))>.05:raise ValueError('Exact block geometry differs from proposal')
 return b

def wrap_text(text,font,size,width_first,width_rest):
 words=plain(text).split();lines=[];line='';width=width_first
 for w in words:
  candidate=(line+' '+w).strip()
  if font.text_length(candidate,fontsize=size)<=width+.01:line=candidate
  elif line:
   lines.append(line);line=w;width=width_rest
   if font.text_length(w,fontsize=size)>width+.01:raise ValueError('Unbreakable token exceeds edited region')
  else:raise ValueError('Unbreakable token exceeds edited region')
 if line:lines.append(line)
 return lines

def expand_into_blank_right(page,rect):
 rect=fitz.Rect(rect);limit=page.rect.width-58.0
 for block in page.get_text('dict')['blocks']:
  if block.get('type')!=0:continue
  for span in all_spans(block):
   rr=fitz.Rect(span['bbox'])
   if rr.x0>=rect.x1-.05 and rr.y0<rect.y1-.1 and rr.y1>rect.y0+.1:
    limit=min(limit,rr.x0-.5)
 if limit>rect.x1:rect.x1=limit
 return rect

def prepare_region(page,rect,new,spans,lines,kind='paragraph',allow_line_reflow=True):
 """Prepare original-family, measured text; never paint outside a known region."""
 rect=expand_into_blank_right(page,rect);sty=native_style(spans);font=sty['font'];size=sty['size']
 if any(ismath(s) for s in spans):raise ValueError('Region includes mathematical font spans')
 if not new:return {'rect':rect,'new':'','draw':[],'style':{k:v for k,v in sty.items() if k!='font'}}
 ys=sorted(set(round(s['origin'][1],3) for s in spans));base=ys[0]
 diffs=[b-a for a,b in zip(ys,ys[1:]) if b-a>size*.5]
 leading=statistics.median(diffs) if diffs else size*1.3165
 first_x=min(s['origin'][0] for s in spans if abs(s['origin'][1]-base)<.5)
 next_x=first_x
 next_lines=[l for l in lines if min(s['origin'][1] for s in l['spans'])>base+size*.5]
 if next_lines:
  second=min(s['origin'][0] for s in next_lines[0]['spans'])
  # Preserve bibliographic hanging indents; ordinary prose has only subpoint jitter.
  if second-first_x>12:next_x=second
 width_first=rect.x1-first_x; width_rest=rect.x1-next_x
 # Native-size first, then at most 5% reduction, preserving original line spacing.
 for scale in [1.0,.99,.98,.97,.96,.95]:
  ss=size*scale
  text_lines=wrap_text(new,font,ss,width_first,width_rest)
  if not allow_line_reflow and len(text_lines)!=1:continue
  last=base+(len(text_lines)-1)*leading
  # Original glyph extents, not a font's generous global ascender box.
  bottom_pad=max(1.0,max(s['bbox'][3]-s['origin'][1] for s in spans))*scale
  if last+bottom_pad<=rect.y1+.12:
   draw=[{'origin':(first_x if i==0 else next_x,base+i*leading),'text':v,'size':ss} for i,v in enumerate(text_lines)]
   return {'rect':rect,'new':new,'draw':draw,'style':{k:v for k,v in sty.items() if k!='font'},'scale':scale}
 raise ValueError('Replacement cannot fit the exact region at >=95% original type size')

def minimal_substitution(a,b):
 # Keep unchanged prefixes and suffixes in place, especially around formulas.
 i=0
 while i<min(len(a),len(b)) and a[i]==b[i]:i+=1
 # Do not start inside a word.
 while i and i<len(a) and a[i-1].isalnum() and a[i].isalnum():i-=1
 j=0
 while j<min(len(a)-i,len(b)-i) and a[len(a)-1-j]==b[len(b)-1-j]:j+=1
 while j and len(a)-j>0 and a[len(a)-j-1].isalnum() and a[len(a)-j].isalnum():j-=1
 return a[i:len(a)-j if j else None],b[i:len(b)-j if j else None]

def targeted_region(page,b,old,new):
 """Replace one pure prose substring, or its whole pure-prose line if needed."""
 a,z=minimal_substitution(old,new)
 if not a.strip():raise ValueError('Insertion-only substitution needs a larger explicit anchor')
 anchor=page.search_for(old,clip=fitz.Rect(b['bbox'])+(-.03,-.03,.03,.03))
 if not anchor:raise ValueError('Full substitution anchor not found')
 scope=fitz.Rect(anchor[0])
 for r in anchor[1:]:scope|=r
 matches=page.search_for(a,clip=scope+(-.03,-.03,.03,.03))
 if not matches:raise ValueError('Target prose substring not found: '+repr(a))
 # Distinct multi-line hits are allowed only if they belong to one occurrence.
 normalized=plain(block_text(b));needle=plain(old)
 if normalized.count(needle)!=1:raise ValueError('Full substitution anchor is not unique in its block')
 rect=fitz.Rect(matches[0])
 for r in matches[1:]:rect|=r
 intersect=[l for l in b['lines'] if fitz.Rect(l['bbox']).intersects(rect)]
 chosen=[]
 for l in intersect:
  for s in l['spans']:
   if fitz.Rect(s['bbox']).intersects(rect):chosen.append(s)
 if any(ismath(s) for s in chosen):raise ValueError('Target crosses a mathematical font')
 # Reflow a pure-prose physical line to avoid gaps left by shorter substitutions.
 if len(intersect)==1 and not any(ismath(s) for s in intersect[0]['spans']):
  line=intersect[0];line_text=''.join(s['text'] for s in line['spans'])
  if a in line_text:
   return prepare_region(page,line['bbox'],line_text.replace(a,z),line['spans'],[line],kind='line',allow_line_reflow=False)
 # Restrict span metrics to the target's line(s), keeping neighboring formula baselines intact.
 sty=native_style(chosen);origin=(rect.x0,intersect[0]['spans'][0]['origin'][1]);size=sty['size']
 width=sty['font'].text_length(plain(z),fontsize=size)
 if len(matches)==1 and width<=rect.width+.04:
  # Avoid a floating-point edge intersection with an unchanged punctuation glyph.
  rect.x1-=.05
  return {'rect':rect,'new':z,'draw':[{'origin':origin,'text':plain(z),'size':size}], 'style':{k:v for k,v in sty.items() if k!='font'},'scale':1.0}
 # A pure-prose physical line may be reflowed without disturbing any formula.
 if len(intersect)==1 and not any(ismath(s) for s in intersect[0]['spans']):
  line=intersect[0];line_text=''.join(s['text'] for s in line['spans'])
  if a in line_text:
   new_line=line_text.replace(a,z)
   return prepare_region(page,line['bbox'],new_line,line['spans'],[line],kind='line',allow_line_reflow=False)
 raise ValueError('Longer target would move adjacent text or mathematical spans')

def table_cell(page,b,anchor):
 hits=page.search_for(anchor,clip=fitz.Rect(b['bbox'])+(-.03,-.03,.03,.03))
 if not hits:raise ValueError('Table anchor not found')
 h=hits[0];lines=b['lines'];cont=[l for l in lines if fitz.Rect(l['bbox']).intersects(h)]
 line=min(cont,key=lambda l:abs(l['bbox'][0]-h.x0));left=min(s['origin'][0] for s in line['spans']);yy=line['spans'][0]['origin'][1]
 left_rows=[l for l in lines if l['bbox'][0]<left-10]
 if left_rows:
  start=max((l['spans'][0]['origin'][1] for l in left_rows if l['spans'][0]['origin'][1]<=yy+.2),default=yy)
  end=min((l['bbox'][1] for l in left_rows if l['spans'][0]['origin'][1]>start+.5),default=b['bbox'][3]+.1)
 else:
  start=yy;end=min((l['bbox'][1] for l in lines if abs(l['bbox'][0]-left)<1 and l['spans'][0]['origin'][1]>yy+.5),default=b['bbox'][3]+.1)
 right=min((l['bbox'][0]-.5 for l in lines if l['bbox'][0]>left+10 and abs(l['spans'][0]['origin'][1]-start)<.3),default=page.rect.width-58)
 selected=[l for l in lines if l['bbox'][0]>=left-.5 and l['bbox'][0]<right and l['spans'][0]['origin'][1]>=start-.3 and l['bbox'][1]<end-.1]
 if not selected:raise ValueError('No bounded table cell')
 rect=fitz.Rect(selected[0]['bbox'])
 for l in selected[1:]:rect|=fitz.Rect(l['bbox'])
 rect.x1=right
 return rect,selected

def prepare_table(page,b,pairs):
 groups={}
 for old,new in pairs:
  rect,lines=table_cell(page,b,old);key=tuple(round(x,2) for x in rect)
  groups.setdefault(key,{'rect':rect,'lines':lines,'pairs':[]})['pairs'].append((old,new))
 result=[]
 for g in groups.values():
  spans=[s for l in g['lines'] for s in l['spans']]
  if any(ismath(s) for s in spans):
   for old,new in g['pairs']:result.append(targeted_region(page,b,old,new))
  else:
   text=' '.join(''.join(s['text'] for s in l['spans']) for l in g['lines'])
   for old,new in g['pairs']:
    if plain(old) not in plain(text):raise ValueError('Cell replacement exceeds inferred cell')
    text=plain(text).replace(plain(old),plain(new))
   result.append(prepare_region(page,g['rect'],text,spans,g['lines']))
 return result

def math_snapshot(page):
 return [(s['font'],c['c'],[round(x,3) for x in c['bbox']]) for b in page.get_text('rawdict')['blocks'] if b.get('type')==0 for l in b['lines'] for s in l['spans'] if ismath(s) for c in s['chars'] if not c['c'].isspace()]

def annotations_snapshot(doc,page):
 typ,val=doc.xref_get_key(page.xref,'Annots')
 refs=[]
 if typ=='array':refs=[int(n) for n in re.findall(r'(\d+)\s+0\s+R',val)]
 elif typ=='xref':
  arrayxref=int(val.split()[0]);array=doc.xref_object(arrayxref);refs=[int(n) for n in re.findall(r'(\d+)\s+0\s+R',array)]
 return typ,val,{x:doc.xref_object(x,compressed=False) for x in refs}

def restore_annotations(doc,page,snapshot):
 typ,val,objs=snapshot
 for x,obj in objs.items():doc.update_object(x,obj)
 if typ!='null':doc.xref_set_key(page.xref,'Annots',val)
 else:doc.xref_set_key(page.xref,'Annots','null')

def pix(page,scale=1):
 p=page.get_pixmap(matrix=fitz.Matrix(scale,scale),alpha=False);return np.frombuffer(p.samples,np.uint8).reshape(p.height,p.width,p.n)

def apply_to_document(doc,cid,proposals,render_dir=None):
 edits=[(i,e) for i,e in enumerate(proposals['edits']) if e['component_id']==cid];by_page=collections.defaultdict(list)
 for i,e in edits:by_page[e['page_1based']-1].append((i,e))
 report={'component_id':cid,'applied':[],'skipped':[],'pages':[]};original_toc=doc.get_toc(simple=False)
 for pn,items in sorted(by_page.items()):
  page=doc[pn];before=pix(page);math_before=math_snapshot(page);ann=annotations_snapshot(doc,page);regions=[]
  for index,e in items:
   try:
    b=find_block(page,e);prepared=[]
    if e['kind']=='replace_table_cells' or e.get('math_spans_present'):
     pairs=e.get('cell_substitutions',e.get('text_substitutions',[]))
     if not pairs:raise ValueError('No safe scoped substitutions supplied')
     if e['kind']=='replace_table_cells':prepared=prepare_table(page,b,pairs)
     else:
      for old,new in pairs:prepared.append(targeted_region(page,b,old,new))
    else:
     prepared.append(prepare_region(page,b['bbox'],e['new_text'],all_spans(b),b['lines']))
    for p in prepared:
     if any(p['rect'].intersects(q['rect']) and abs((p['rect']&q['rect']).get_area())>.1 for q in regions):raise ValueError('Edit regions overlap another replacement')
    for p in prepared:p['proposal_index']=index
    regions.extend(prepared);report['applied'].append({'proposal_index':index,'page_1based':pn+1,'kind':e['kind'],'regions':[rect_values(p['rect']) for p in prepared],'scales':[p.get('scale',1) for p in prepared]})
   except (ValueError,RuntimeError) as ex:report['skipped'].append({'proposal_index':index,'page_1based':pn+1,'reason':str(ex)})
  if not regions:continue
  # No fill: native background/vector content remains visible and unchanged.
  for p in regions:page.add_redact_annot(p['rect'],fill=False,cross_out=False)
  page.apply_redactions(images=0,graphics=0,text=0)
  for p in regions:
   if not p['draw']:continue
   sty=p['style'];name='RCProofread'+hashlib.sha256(sty['font_path'].encode()).hexdigest()[:12]
   page.insert_font(fontname=name,fontfile=sty['font_path'])
   for line in p['draw']:page.insert_text(line['origin'],line['text'],fontname=name,fontsize=line['size'],color=sty['color'],overlay=True)
  restore_annotations(doc,page,ann)
  page=doc.reload_page(page)
  if math_snapshot(page)!=math_before:raise RuntimeError(f'Mathematical glyph spans changed on {cid} p{pn+1}')
  after=pix(page);changed=np.any(before!=after,axis=2);mask=np.zeros(changed.shape,dtype=bool)
  for p in regions:
   r=p['rect'];x0=max(0,math.floor(r.x0)-1);y0=max(0,math.floor(r.y0)-1);x1=min(mask.shape[1],math.ceil(r.x1)+1);y1=min(mask.shape[0],math.ceil(r.y1)+1);mask[y0:y1,x0:x1]=True
  outside=int(np.count_nonzero(changed&~mask))
  if outside:raise RuntimeError(f'{outside} changed pixels outside exact edit rectangles on {cid} p{pn+1}')
  if annotations_snapshot(doc,page)!=ann:raise RuntimeError(f'Annotation objects changed on {cid} p{pn+1}')
  entry={'page_1based':pn+1,'regions':len(regions),'outside_changed_pixels':outside,'mathematical_glyphs_unchanged':True,'annotations_unchanged':True}
  if render_dir:
   dest=Path(render_dir);dest.mkdir(parents=True,exist_ok=True)
   fn=dest/f'{cid}_p{pn+1:03d}.png';page.get_pixmap(matrix=fitz.Matrix(1.25,1.25),alpha=False).save(fn);entry['render']=str(fn)
  report['pages'].append(entry)
 if doc.get_toc(simple=False)!=original_toc:raise RuntimeError('Outline changed during text edits')
 return report

def proofread_preserved_pdf(input_pdf,component_id,output_pdf,proposals_path=DEFAULT_PROPOSALS,render_dir=None):
 src=Path(input_pdf).resolve();dst=Path(output_pdf).resolve()
 if src==dst:raise ValueError('Refusing to overwrite preserved input')
 proposal_path=Path(proposals_path);j=json.loads(proposal_path.read_text());basis=next(x for x in j['source_basis'] if x['component_id']==component_id)
 if sha(src)!=basis['sha256']:raise ValueError('Input hash differs from exact proposal basis')
 doc=fitz.open(src);pages=len(doc);report=apply_to_document(doc,component_id,j,render_dir)
 assert len(doc)==pages==basis['pages'];dst.parent.mkdir(parents=True,exist_ok=True)
 doc.save(dst,garbage=0,deflate=True,no_new_id=True);doc.close();check=fitz.open(dst);assert len(check)==pages
 report.update(input_pdf=str(src),input_sha256=sha(src),output_pdf=str(dst),output_sha256=sha(dst),pages_preserved=pages,proposals_sha256=sha(proposal_path))
 return report

def main():
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('--proposals',type=Path,default=DEFAULT_PROPOSALS);a.add_argument('--output',type=Path,default=ROOT/'editorial/book_revision/preserved_proofread');args=a.parse_args();j=json.loads(args.proposals.read_text());args.output.mkdir(parents=True,exist_ok=True);reports=[]
 for b in j['source_basis']:
  report=proofread_preserved_pdf(ROOT/b['path'],b['component_id'],args.output/(b['component_id']+'.pdf'),args.proposals,args.output/'renders');reports.append(report);(args.output/'report.json').write_text(json.dumps(reports,indent=2)+'\n');print(b['component_id'],len(report['applied']),'applied',len(report['skipped']),'skipped',flush=True)
if __name__=='__main__':main()
