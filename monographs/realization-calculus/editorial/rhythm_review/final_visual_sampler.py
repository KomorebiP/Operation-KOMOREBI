from pathlib import Path
import fitz,json,hashlib,sys,re,unicodedata
from PIL import Image,ImageDraw,ImageFont,ImageOps
R=Path(__file__).resolve().parents[2];D=R/'editorial/rhythm_review';O=D/'final_visual_samples';O.mkdir(exist_ok=True)
s=json.loads((R/'book/build_spec.json').read_text());cs={c['id']:c for p in s['parts']for c in p['components']};pdf=R/'output/Realization_Calculus.pdf';sha=hashlib.sha256(pdf.read_bytes()).hexdigest();assert sha==sys.argv[1];doc=fitz.open(pdf);assert len(doc)==s['expected_total_pages']
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',12)
sel=[]
def add(idx,reason,category):
 idx=int(idx);same=next((x for x in sel if x['book_index']==idx),None)
 if same:same['reasons'].append(reason);return
 sel.append({'book_index':idx,'physical_page':idx+1,'reasons':[reason],'category':category})
# Systematic sample uses the final auditor's selection policy, but renders the
# actual hash-bound book into our own path so a concurrent audit cannot replace it.
ss={}
def sy(idx,reason):ss.setdefault(int(idx),[]).append(reason)
for n in range(s['front_pages']):sy(n,'front matter')
for leaf in s['leaves']:sy(leaf['book_index'],leaf['kind']+' '+str(leaf.get('paper','')))
for c in cs.values():
 kept=sorted(c['keep_pages'],key=lambda raw:c['book_pages'][str(raw)])
 if kept:sy(c['book_pages'][str(kept[len(kept)//2])],c['id']+' retained interior')
g=s['glossary']
for offset in (0,g['pages']//2,g['pages']-1):sy(g['index_start']+offset,'glossary')
for p in ['II','III','V','VI','VII','VIII']:
 plate=next((x for x in doc.get_toc() if re.search(r'Plate\s+'+p+r'\.',x[1],re.I)),None)
 if plate:sy(plate[2]-1,'Chapter '+p+' canonical plate')
sysrecords=[];thumbs=[];sheets=[]
for idx,why in sorted(ss.items()):
 pix=doc[idx].get_pixmap(matrix=fitz.Matrix(1.25,1.25),alpha=False);name=O/f'systematic_page_{idx+1:04}.png';pix.save(name)
 im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples);th=ImageOps.contain(im,(235,304));tile=Image.new('RGB',(251,338),'#e9e5e8');tile.paste(th,((251-th.width)//2,5));dr=ImageDraw.Draw(tile);dr.text((8,312),f'PDF {idx+1}: '+why[0][:28],fill='black');thumbs.append(tile)
 sysrecords.append({'physical_page':idx+1,'reasons':why,'image':str(name.relative_to(R))})
for start in range(0,len(thumbs),16):
 im=Image.new('RGB',(1004,1352),'white')
 for j,tile in enumerate(thumbs[start:start+16]):im.paste(tile,((j%4)*251,(j//4)*338))
 name=O/f'systematic_{start//16+1:02}.png';im.save(name);sheets.append({'path':str(name.relative_to(R)),'category':'systematic','pages':[x['physical_page'] for x in sysrecords[start:start+16]]})
# Focused sample covers retained prose on mixed Contents leaves.
f=json.loads((R/'editorial/prose_review/frontmatter_keep_reconciled.json').read_text())
for c in f['components']:
 for pn in c.get('mixed_toc_pages_1based',[]):add(cs[c['component_id']]['book_pages'][str(pn-1)],f"{c['component_id']} retained mixed Contents source physical {pn}",'mixed_contents')
for cid,raw,reason in [('XI_research_progress',63,'Preserved progress p64 parenthetical list'),('XI_research_atlas',26,'Preserved atlas p27 caption full stop')]:add(cs[cid]['book_pages'][str(raw)],reason,'preserved_changes')
def norm(t):return re.sub(r'\s+',' ',unicodedata.normalize('NFKC',t).replace('\xad','')).strip()
queries=[
 ('I_machine_native','the Banach space result in the countable setting','Late approved Chapter I computational phrase'),
 ('I_traditional','Higher powers of','Chapter I changed proof paragraph'),
 ('II_traditional','The worked plates supply concrete models','Chapter II changed explanatory prose'),
 ('III_traditional','The two bridge equalities then yield','Chapter III changed proof paragraph'),
 ('IV_visual','Higher moments emphasize the nearest zero','Chapter IV changed preserved caption'),
 ('V_traditional','Theorem statements specify the ambient norm','Chapter V changed explanatory paragraph'),
 ('V_traditional','The endpoint calculation below is symbolic','Chapter V changed caption or plate prose'),
 ('VI_traditional','The modes stay as their clocks change','Chapter VI changed plate heading/caption'),
 ('VII_traditional','The recovery from the previous block is instantiated','Chapter VII changed proof paragraph'),
 ('VIII_traditional','The timings are inherited observations','Chapter VIII changed measured-scope prose'),
 ('IX_traditional','It describes ordinary Cauchy multiplication','Chapter IX changed explanatory proof prose'),
 ('X_traditional','Refinement adds digits vertically','Chapter X changed caption'),
 ('XI_traditional','The Gauss sum is its defining finite sum','Chapter XI changed mathematical prose'),
 ('XII_visual','Hecke','Chapter XII plate/prose layout sample')]
miss=[]
for cid,q,why in queries:
 c=cs[cid];found=[]
 for raw,idx in c['book_pages'].items():
  if norm(q).lower() in norm(doc[idx].get_text()).lower():found.append((int(raw),idx))
 if found:add(found[0][1],why+' | '+q,'changed_source_prose')
 else:miss.append({'component_id':cid,'query':q,'reason':why})
terms=json.loads((R/'book/glossary_term_map.json').read_text())
for term in ['Bridge datum','Hecke packet','Zero power sum']:
 t=next(x for x in terms if x['term']==term);add(s['glossary']['index_start']+t['page'],'Glossary/reference layout: '+term,'glossary_reference')
for cat in ['mixed_contents','preserved_changes','changed_source_prose','glossary_reference']:
 group=[x for x in sel if x['category']==cat]
 for start in range(0,len(group),2):
  pair=group[start:start+2];im=Image.new('RGB',(1248,830),(237,232,238));dr=ImageDraw.Draw(im)
  for j,x in enumerate(pair):
   pix=doc[x['book_index']].get_pixmap(matrix=fitz.Matrix(1,1),alpha=False);pi=Image.frombytes('RGB',[pix.width,pix.height],pix.samples);name=O/f'focused_page_{x["physical_page"]:04}.png';pi.save(name);x['image']=str(name.relative_to(R));im.paste(pi,(j*624+6,6));dr.text((j*624+7,800),'PDF '+str(x['physical_page'])+' | '+x['reasons'][0][:66],fill='black',font=font)
  name=O/f'{cat}_{start//2+1:02}.png';im.save(name);sheets.append({'path':str(name.relative_to(R)),'category':cat,'pages':[x['physical_page'] for x in pair]})
report={'status':'REVIEWING','pdf':'output/Realization_Calculus.pdf','pdf_sha256':sha,'pages':len(doc),'systematic_sample_count':len(sysrecords),'systematic_samples':sysrecords,'focused_sample_count':len(sel),'focused_samples':sel,'contact_sheets':sheets,'inspected_sheets':[],'unresolved_sampler_queries':miss,'findings':[],'review_scope':'Sampled actual-book visual QA, not a new prose or mathematical audit. All sample images rendered from the hash-bound assembled PDF.'}
(D/'final_visual_review.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'systematic':len(sysrecords),'focused':len(sel),'sheets':len(sheets),'missing_queries':miss,'sheet_pages':sheets},indent=2))
