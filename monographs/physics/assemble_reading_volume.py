#!/usr/bin/env python3
"""Build the publication PDF from source-built chapters; preserve vector content and links.

This script is a document build. It does not run Lean or reproduce physical calculations.
Fonts are discovered in the local TeX installation and are not distributed in the package.
"""
from pathlib import Path
import ast,hashlib,json,subprocess,math
import fitz
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'book';BUILD=ROOT/'compiled';OUT.mkdir(exist_ok=True)
W,H=612.0,792.0
NAVY='#142D3B';TEAL='#286B6D';COPPER='#A97D4E';INK='#22282C';MUTED='#55616A';PALE='#D8E6E3';RULE='#CBD3D3';WHITE='#FFFFFF'
LEFT=62.64;WIDTH=W-2*LEFT
FONT_NAMES={'BookSerif':'qplr','BookBold':'qplb','BookItalic':'qplri','BookBoldItalic':'qplbi','BookSans':'qhvr','BookSansBold':'qhvb'}
for alias,stem in FONT_NAMES.items():
 paths=[]
 for ext in ('afm','pfb'):
  p=subprocess.check_output(['kpsewhich',stem+'.'+ext],text=True).strip()
  if not p or not Path(p).exists():raise FileNotFoundError(f'Install TeX Gyre Type 1 fonts: {stem}.{ext}')
  paths.append(p)
 face=pdfmetrics.EmbeddedType1Face(*paths);pdfmetrics.registerTypeFace(face)
 pdfmetrics.registerFont(pdfmetrics.Font(alias,face.name,'WinAnsiEncoding'))
pdfmetrics.registerFontFamily('BookSerif',normal='BookSerif',bold='BookBold',italic='BookItalic',boldItalic='BookBoldItalic')
pdfmetrics.registerFontFamily('BookSans',normal='BookSans',bold='BookSansBold',italic='BookSans',boldItalic='BookSansBold')
CONTENT=json.loads((OUT/'reading_text.json').read_text())

def C(s):return HexColor(s)
def roman(n):
 out=''
 for k,s in [(1000,'m'),(900,'cm'),(500,'d'),(400,'cd'),(100,'c'),(90,'xc'),(50,'l'),(40,'xl'),(10,'x'),(9,'ix'),(5,'v'),(4,'iv'),(1,'i')]:
  while n>=k:out+=s;n-=k
 return out

def para(c,text,x,y,width=WIDTH,size=11.4,lead=16.2,font='BookSerif',col=INK,min_y=52):
 st=ParagraphStyle('p',fontName=font,fontSize=size,leading=lead,textColor=C(col),splitLongWords=True,allowWidows=0,allowOrphans=0)
 p=Paragraph(text,st);_,height=p.wrap(width,1200)
 if y-height<min_y:raise ValueError(f'Page overflow at y={y-height:.1f}: {text[:100]}')
 p.drawOn(c,x,y-height);return y-height

def tracked(c,text,x,y,size=8,font='BookSans',col=TEAL,space=1.4):
 c.saveState();t=c.beginText(x,y);t.setFont(font,size);t.setFillColor(C(col));t.setCharSpace(space);t.textOut(text);c.drawText(t);c.restoreState()

def rule(c,x,y,width=WIDTH,col=RULE,lw=.35):
 c.setStrokeColor(C(col));c.setLineWidth(lw);c.line(x,y,x+width,y)

def front_folio(c,num,heading=''):
 if heading:
  tracked(c,'KOMOREBI PHYSICS',LEFT,H-37,size=7,col=MUTED,space=1.05)
  c.setFillColor(C(MUTED));c.setFont('BookSans',7.3);c.drawRightString(W-LEFT,H-37,heading)
 if num:
  c.setFillColor(C(INK));c.setFont('BookSerif',10);c.drawRightString(W-LEFT,28,roman(num))

def section_title(c,kicker,title):
 tracked(c,kicker,LEFT,H-86,size=8.2,space=1.35)
 y=para(c,title,LEFT,H-108,WIDTH,27,33,'BookSerif',NAVY)-18
 rule(c,LEFT,y,42,COPPER,.8)
 return y-24

def cover(c):
 c.setFillColor(C(NAVY));c.rect(0,0,W,H,fill=1,stroke=0)
 # Pure typography and restrained rules; no illustrative claim or decorative physics figure.
 tracked(c,'REALIZATION CALCULUS',65,714,size=9,col=PALE,space=2.0)
 rule(c,65,681,42,COPPER,1.25)
 c.setFillColor(C(WHITE));c.setFont('BookSerif',32);c.drawString(61,607,'Komorebi')
 c.setFont('BookSerif',78);c.drawString(59,523,'Physics')
 c.setFont('BookSerif',23);c.drawString(65,463,'Continuum, Geometry')
 c.drawString(65,432,'and Refinement')
 tracked(c,'FIELDS  /  STRUCTURE  /  LIMITS',65,373,size=8.5,col=PALE,space=1.7)
 rule(c,65,129,W-130,'#43606A',.45)
 c.setFillColor(C(WHITE));c.setFont('BookSerif',14);c.drawString(65,94,'Komorebi P.')
 c.setFillColor(C(PALE));c.setFont('BookSans',9);c.drawRightString(W-65,95,'2026')

# Generate the three-page verification synthesis, retaining its exact substantive text.
scope=OUT/'verification_scope.pdf';c=canvas.Canvas(str(scope),pagesize=(W,H),pageCompression=1)
for i,(name,sections) in enumerate(CONTENT['scope_pages']):
 y=section_title(c,'VERIFICATION AND SOURCES',name)
 for head,body in sections:
  y=para(c,head,LEFT,y,WIDTH,12.4,16,'BookBold',NAVY)-5
  y=para(c,body,LEFT,y,WIDTH,11.0,15.3)-17
 c.showPage()
c.save()

BREAK_TITLES={
 'Projector_Refinement_Physics_Covariant_Backreaction_Bridge':'Computational Evidence and Reproducibility',
 'Projector_Refinement_Physics_Volume_II':'Reproducibility and Data Map'}
def entry(stem,name,deck,span=None):
 path=BUILD/stem/(stem+'.pdf') if stem!='verification_scope' else scope
 with fitz.open(path) as d:
  count=len(d);pages=list(range(count))
  if span is not None:
   matches=[p-1 for lvl,title,p in d.get_toc() if title==BREAK_TITLES[stem]]
   if len(matches)!=1:raise ValueError(f'Cannot uniquely locate source split: {stem}: {matches}')
   split=matches[0];pages=list(range(0,split)) if span[0]==0 else list(range(split,count))
 return {'stem':stem,'title':name,'deck':deck,'path':str(path),'source_pages':pages}
# The specification is a local source asset with literal entry calls, not external code.
expr=ast.parse((OUT/'parts_spec.py').read_text()).body[0].value
parts=eval(compile(ast.Expression(expr),'<parts_spec>','eval'),{'entry':entry,'__builtins__':{}})
FRONT=8
cursor=FRONT;manifest=[]
for nr,name,deck,docs in parts:
 divider=cursor;cursor+=1
 for e in docs:
  e.update(part=nr,part_title=name,part_index=divider,index_start=cursor,page_start=cursor-FRONT+1,page_end=cursor-FRONT+len(e['source_pages']))
  e['source_sha256']=hashlib.sha256(Path(e['path']).read_bytes()).hexdigest()
  cursor+=len(e['source_pages']);manifest.append(e)

# Front matter: unnumbered cover, formal title, scope, preface, conventions, three contents pages.
front=OUT/'frontmatter.pdf';c=canvas.Canvas(str(front),pagesize=(W,H),pageCompression=1)
cover(c);c.showPage()
tracked(c,'KOMOREBI PHYSICS',LEFT,714,size=8.5,space=1.9)
y=para(c,'Komorebi Physics',LEFT,628,WIDTH,42,48,'BookSerif',NAVY)-18
y=para(c,'Continuum, Geometry<br/>and Refinement',LEFT,y,WIDTH,25,33,'BookSerif',NAVY)-22
rule(c,LEFT,y,42,COPPER,.9)
para(c,'Komorebi P.',LEFT,302,WIDTH,14,19,'BookSerif',INK)
para(c,'A mathematical account of resolved dynamics, free fields,<br/>gauge transport, gravity, arithmetic structure,<br/>and cosmological models.',LEFT,231,WIDTH,11,16,'BookSerif',MUTED)
tracked(c,'2026',LEFT,82,size=9,col=MUTED,space=1.8);c.showPage()
front_folio(c,2,'SCOPE');y=section_title(c,'ABOUT THIS VOLUME','Mathematics, models, and evidence')
for t in [
'The volume brings together a shared mathematical language and several physical applications. Projector identities and transfer maps lead to complete state spaces, unbounded operators, compatible refinements, and controlled comparisons between descriptions.',
'Written proofs, recorded compiler checks, finite computations, and physical interpretations have different roles. The mathematical chapters state their hypotheses. The source studies identify the formal declarations, recorded evidence, and remaining verification limits. The visual studies illustrate specified examples rather than replace their proofs.',
'The free Dirac group, maximal generator domain, and strong Schrödinger equation have compiler-checked proofs. The centered Fourier family also has checked graph-domain and strong-resolvent limits and quadratic bounds under a finite third-order moment. The abstract spectral-functional-calculus identification remains a written deduction without a separate Lean API linkage. Physical-model chapters retain the production-energy obstruction and their stated assumptions.',
'The equation, theorem, figure, and local section numbers belong to their named treatment. The contents and book folios provide a single navigation system. Source identifiers are retained in the verification material where they are needed for reproducibility.'
]:y=para(c,t,LEFT,y,WIDTH,11.5,16.5)-18
rule(c,LEFT,151,WIDTH,RULE,.4)
para(c,'Copyright © 2026 Komorebi P.<br/>Original text and figures: Creative Commons Attribution 4.0 International.<br/>Original code: MIT License. Third-party material retains its own terms.<br/><link href="https://creativecommons.org/licenses/by/4.0/">creativecommons.org/licenses/by/4.0/</link>',LEFT,137,WIDTH,9.2,13,'BookSerif',MUTED)
c.showPage()
front_folio(c,3,'INTRODUCTION');y=section_title(c,'INTRODUCTION','A common language for resolved physics')
for text in CONTENT['introduction']:y=para(c,text,LEFT,y,WIDTH,11.5,16.3)-16
c.showPage()
front_folio(c,4,'READING CONVENTIONS');y=section_title(c,'READING THE BOOK','The argument and its conventions')
for name,text in CONTENT['conventions']:
 y=para(c,name,LEFT,y,WIDTH,12.2,16,'BookBold',NAVY)-5
 y=para(c,text,LEFT,y,WIDTH,11.1,15.8)-17
c.showPage()
links=[]
def contents(num,subtitle,groups):
 front_folio(c,num,'CONTENTS');y=section_title(c,'CONTENTS',subtitle)
 for nr in groups:
  _,name,_,docs=next(p for p in parts if p[0]==nr)
  y=para(c,f'{nr} &nbsp; {name}',LEFT,y,WIDTH,12,16,'BookBold',TEAL)-12
  for e in docs:
   top=y
   y=para(c,e['title'],LEFT+13,y,WIDTH-57,12.1,15.3,'BookSerif',INK)
   c.setFont('BookSerif',11);c.setFillColor(C(INK));c.drawRightString(W-LEFT,top-11,str(e['page_start']))
   y-=3;y=para(c,e['deck'],LEFT+13,y,WIDTH-57,8.7,12,'BookSans',MUTED)-12
   links.append({'page':num,'rect':[LEFT,H-top-3,W-LEFT,H-y-4],'dest':e['index_start']})
  y-=9
contents(5,'Mathematical constructions',['I','II','III','IV']);c.showPage()
contents(6,'Visual studies',['V']);
# A quiet navigation aid rather than a large empty remainder.
rule(c,LEFT,222,42,COPPER,.8)
para(c,'The visual studies follow the objects developed in the main text. Each example retains its stated inputs and limits. Use the source studies for formal declarations and computational provenance.',LEFT,201,WIDTH-30,11,16,'BookSerif',MUTED)
c.showPage()
contents(7,'Verification and sources',['VI']);c.showPage();c.save()

# Restrained white part openings with a linked route through the following material.
div=OUT/'part_leaves.pdf';c=canvas.Canvas(str(div),pagesize=(W,H),pageCompression=1)
part_links=[]
for idx,(nr,name,deck,docs) in enumerate(parts):
 tracked(c,'PART '+nr,LEFT,698,size=9,space=2.2)
 y=para(c,name,LEFT,650,WIDTH-25,34,41,'BookSerif',NAVY)-24
 rule(c,LEFT,y,48,COPPER,.95)
 y=para(c,deck,LEFT,y-28,WIDTH-25,12.3,18.4,'BookSerif',MUTED)-35
 tracked(c,'IN THIS PART',LEFT,y,size=7.8,space=1.4);y-=23
 for e in docs:
  top=y;y=para(c,e['title'],LEFT,y,WIDTH-46,11,15,'BookSerif',INK)
  c.setFont('BookSerif',10.5);c.setFillColor(C(TEAL));c.drawRightString(W-LEFT,top-10,str(e['page_start']))
  y-=11
  part_links.append({'part':idx,'rect':[LEFT,H-top-3,W-LEFT,H-y+2],'dest':e['index_start']})
 c.showPage()
c.save()

# Build a single complete source-page map before reconstructing cross-page links.
book=fitz.open();fd=fitz.open(front);dd=fitz.open(div);book.insert_pdf(fd,links=False)
if len(fd)!=FRONT:raise ValueError(f'Front matter has {len(fd)} pages, expected {FRONT}')
source_docs={};mapping={};orig_links={};shifts={};page_records={};part_indices=[]
toc=[[1,'Title',2],[1,'Scope of the volume',3],[1,'Introduction',4],[2,'Reading conventions',5],[1,'Contents',6],[2,'Visual studies',7],[2,'Verification and sources',8]]
for idx,(nr,name,deck,docs) in enumerate(parts):
 part_indices.append(len(book));book.insert_pdf(dd,from_page=idx,to_page=idx,links=False)
 page_records[len(book)-1]={'part':nr,'title':name,'opening':True,'divider':True}
 toc.append([1,f'{nr}. {name}',len(book)])
 for e in docs:
  stem=e['stem'];source_docs.setdefault(stem,fitz.open(e['path']));d=source_docs[stem]
  assert len(book)==e['index_start'],(len(book),e)
  for off,sp in enumerate(e['source_pages']):
   dest=len(book);arabic=dest-FRONT+1;shift=6 if arabic%2 else -6
   mapping[(stem,sp)]=dest;orig_links[(stem,sp)]=d[sp].get_links();shifts[dest]=shift
   p=book.new_page(width=W,height=H)
   p.show_pdf_page(fitz.Rect(shift,0,W+shift,H),d,sp,keep_proportion=True)
   page_records[dest]={'part':nr,'title':e['title'],'opening':off==0,'divider':False}
  toc.append([2,e['title'],e['index_start']+1])
  for level,label,sp in d.get_toc():
   if sp-1 in e['source_pages']:toc.append([level+2,label,mapping[(stem,sp-1)]+1])

# Render running furniture as a font-embedded vector overlay, separate from the science.
SHORT={
'Fourier Packets and the Continuum Dirac Operator':'The continuum Dirac operator',
'Cosmology, Dark Sectors, and Structure Formation':'Cosmology and structure formation',
'Adic and Polyphase Quantum Refinement':'Adic and polyphase refinement',
'Gauge Covariance and Geometric Refinement':'Gauge covariance and refinement',
'Verification Scope and Source Conventions':'Verification scope',
'Foundations Formalization Companion':'Foundations: formalization',
'Dirac Formalization Companion':'Dirac operator: formalization',
'Gauge Formalization Companion':'Gauge structure: formalization',
'Gravity Verification Companion':'Gravity: verification',
'Adic Verification Companion':'Adic refinement: verification',
'Fiber Model: Computational Evidence':'Fiber model: computational evidence',
'Cosmology: Reproducibility and Data':'Cosmology: reproducibility'}
overlay=OUT/'running_furniture.pdf';c=canvas.Canvas(str(overlay),pagesize=(W,H),pageCompression=1)
return_links=[]
for i in range(FRONT,len(book)):
 rec=page_records[i];num=i-FRONT+1;odd=num%2;dx=shifts.get(i,6 if odd else -6);left=LEFT+dx;right=left+WIDTH
 if not rec['opening']:
  label=SHORT.get(rec['title'],rec['title']) if odd else 'Komorebi Physics'
  c.setFont('BookSans',7.7);c.setFillColor(C(MUTED))
  if odd:c.drawRightString(right,756,label)
  else:c.drawString(left,756,label)
  tracked(c,'PART '+rec['part'],left if odd else right-43,756,size=7,col=TEAL,space=.7)
  rule(c,left,746,WIDTH,RULE,.35)
  dest=5 if rec['part'] in ['I','II','III','IV'] else 6 if rec['part']=='V' else 7
  return_links.append({'page':i,'rect':[left,24,right,49],'dest':dest})
 c.setFillColor(C(INK));c.setFont('BookSerif',10.5)
 if odd:c.drawRightString(right,27,str(num))
 else:c.drawString(left,27,str(num))
 c.showPage()
c.save();od=fitz.open(overlay)
for i in range(FRONT,len(book)):book[i].show_pdf_page(book[i].rect,od,i-FRONT,overlay=True)

# Restore explicit and resolved named destinations, including split appendices.
internal=external=0;dropped=[]
for (stem,sp),ll in orig_links.items():
 pidx=mapping[(stem,sp)];page=book[pidx];dx=shifts[pidx]
 for old in ll:
  box=fitz.Rect(old['from'])+ (dx,0,dx,0)
  if old['kind'] in (fitz.LINK_GOTO,fitz.LINK_NAMED) and old.get('page',-1)>=0:
   key=(stem,old['page'])
   if key not in mapping:dropped.append({'source':stem,'page':sp+1,'target':old['page']});continue
   target=mapping[key];to=fitz.Point(old.get('to',fitz.Point(0,0)));to.x+=shifts.get(target,0)
   page.insert_link({'kind':fitz.LINK_GOTO,'from':box,'page':target,'to':to});internal+=1
  elif old['kind']==fitz.LINK_URI:
   page.insert_link({'kind':fitz.LINK_URI,'from':box,'uri':old['uri']});external+=1
  elif old['kind']!=fitz.LINK_NONE:dropped.append({'source':stem,'page':sp+1,'kind':old['kind']})
for lk in links+return_links:
 book[lk['page']].insert_link({'kind':fitz.LINK_GOTO,'from':fitz.Rect(lk['rect']),'page':lk['dest'],'to':fitz.Point(0,0)})
for lk in part_links:
 book[part_indices[lk['part']]].insert_link({'kind':fitz.LINK_GOTO,'from':fitz.Rect(lk['rect']),'page':lk['dest'],'to':fitz.Point(0,0)})
book.set_toc(toc,collapse=2)
book.set_page_labels([{'startpage':0,'prefix':'Cover','style':'','firstpagenum':1},{'startpage':1,'prefix':'','style':'r','firstpagenum':1},{'startpage':FRONT,'prefix':'','style':'D','firstpagenum':1}])
book.set_metadata({'title':'Komorebi Physics: Continuum, Geometry and Refinement','author':'Komorebi P.','subject':'Resolved dynamics, fields, geometry, arithmetic refinement and cosmological models','keywords':'Komorebi, physics, realization calculus, Dirac, gauge, gravity, refinement','creator':'Komorebi Physics publication source','producer':'Source-built LaTeX and vector PDF assembly'})
book.xref_set_key(book.pdf_catalog(),'Lang','(en-US)')
book.xref_set_key(book.pdf_catalog(),'PageMode','/UseOutlines')
book.xref_set_key(book.pdf_catalog(),'ViewerPreferences','<< /DisplayDocTitle true >>')
output=ROOT/'Komorebi_Physics.pdf';book.save(output,garbage=3,deflate=True)
record={'page_count':len(book),'front_matter_pages_including_cover':FRONT,'arabic_pages':len(book)-FRONT,'contents_entries':len(manifest),'bookmarks':len(toc),'restored_internal_links':internal,'external_links':external,'contents_links':len(links),'part_route_links':len(part_links),'return_to_contents_links':len(return_links),'unresolved_source_links':dropped,'output_sha256':hashlib.sha256(output.read_bytes()).hexdigest()}
(OUT/'book_manifest.json').write_text(json.dumps(manifest,indent=2))
(OUT/'assembly_validation.json').write_text(json.dumps(record,indent=2))
(OUT/'page_map.json').write_text(json.dumps({'pages':page_records,'source_map':[{'source':k[0],'source_page':k[1]+1,'book_page_index':v,'folio':v-FRONT+1} for k,v in mapping.items()]},indent=2))
print(json.dumps(record,indent=2))
