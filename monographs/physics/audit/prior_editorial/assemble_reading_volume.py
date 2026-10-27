#!/usr/bin/env python3
"""Assemble the source-built physics chapters into the publication reading volume.
No theorem checking is performed by this document build. See the technical record.
"""
from pathlib import Path
import json, math, hashlib, re, os
import fitz
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT

ROOT=Path(__file__).resolve().parent
BUILD=ROOT/'compiled'; OUT=ROOT/'book';OUT.mkdir(exist_ok=True)
W,H=letter
NAVY='#10283F';TEAL='#078A98';COPPER='#C99853';INK='#1C3445';MUTED='#586C77';ICE='#E5F3F4';WHITE='#FFFFFF'
FONT_PATHS={'BookSerif':'/usr/share/fonts/truetype/ebgaramond/EBGaramond12-Regular.ttf','BookBold':'/usr/share/fonts/truetype/ebgaramond/EBGaramond12-Bold.ttf','BookItalic':'/usr/share/fonts/truetype/ebgaramond/EBGaramond12-Italic.ttf','BookSans':'/usr/share/fonts/truetype/lato/Lato-Regular.ttf','BookSansBold':'/usr/share/fonts/truetype/lato/Lato-Bold.ttf'}
if os.environ.get('KOMOREBI_BOOK_FONT_CONFIG'):
 FONT_PATHS.update(json.loads(Path(os.environ['KOMOREBI_BOOK_FONT_CONFIG']).read_text()))
for n,p in FONT_PATHS.items():
 if not Path(p).exists():raise FileNotFoundError('Install the documented fonts before building: '+p)
 pdfmetrics.registerFont(TTFont(n,p))
pdfmetrics.registerFontFamily('BookSerif',normal='BookSerif',bold='BookBold',italic='BookItalic',boldItalic='BookItalic')
pdfmetrics.registerFontFamily('BookSans',normal='BookSans',bold='BookSansBold',italic='BookSans',boldItalic='BookSansBold')

def color(s):return HexColor(s)
def para(c,text,x,y,width,size=12.4,lead=17.2,font='BookSerif',col=INK):
 p=Paragraph(text,ParagraphStyle('body',fontName=font,fontSize=size,leading=lead,textColor=color(col),alignment=TA_LEFT))
 _,h=p.wrap(width,1000)
 if y-h<55:raise ValueError('Page content overflow: '+text[:80])
 p.drawOn(c,x,y-h);return y-h

def line(c,y,x=57,right=W-57,col=TEAL,lw=.7):
 c.setStrokeColor(color(col));c.setLineWidth(lw);c.line(x,y,right,y)
def header(c,heading,number=None):
 c.setFillColor(color(NAVY));c.setFont('BookSansBold',8);c.drawString(57,H-38,'KOMOREBI PHYSICS')
 c.setFillColor(color(MUTED));c.setFont('BookSans',7.5);c.drawRightString(W-57,H-38,heading.upper())
 if number:
  c.setFont('BookSans',8.5);c.setFillColor(color(TEAL));c.drawRightString(W-57,30,str(number))
  c.setFont('BookSans',7);c.setFillColor(color(MUTED));c.drawString(57,30,'CONTINUUM, GEOMETRY AND REFINEMENT')
def title(c,text,sub=None):
 y=H-91;y=para(c,text,57,y,W-114,26,30,'BookBold',NAVY)-13
 if sub:y=para(c,sub,57,y,W-114,10,14,'BookSans',MUTED)-15
 line(c,y);return y-22

def cover(c):
 c.setFillColor(color(NAVY));c.rect(0,0,W,H,fill=1,stroke=0)
 c.setFillColor(color(TEAL));c.rect(0,H-21,W,6,fill=1,stroke=0)
 c.setFillColor(color(ICE));c.setFont('BookSansBold',10);c.drawString(57,H-72,'OPERATION KOMOREBI')
 c.setFillColor(color('#59C2C9'));c.setFont('BookSans',9.5);c.drawString(57,H-96,'A COLLECTED MATHEMATICAL MONOGRAPH')
 y=H-186;y=para(c,'Komorebi<br/>Physics',55,y,W-110,46,48,'BookBold',WHITE)-24
 y=para(c,'Continuum, Geometry<br/>and Refinement',57,y,W-114,28,34,'BookSerif',ICE)-24
 line(c,y,57,160,COPPER,1.7)
 y=para(c,'Resolved dynamics, free fields, gauge transport,<br/>gravity, arithmetic structure, and cosmological models',57,y-22,W-114,11.5,17,'BookSans',ICE)
 for j in range(8):
  path=c.beginPath();path.moveTo(-10,145+j*10)
  for k in range(60):
   x=-10+k*11;path.lineTo(x,145+j*10+14*math.sin(.015*x+.20*j)+4*math.sin(.04*x))
  c.setStrokeColor(color('#184557'));c.setLineWidth(.65);c.drawPath(path,stroke=1)
 c.setFillColor(color(ICE));c.setFont('BookSerif',15);c.drawString(57,73,'Komorebi P.')
 c.setFont('BookSans',9);c.drawString(57,49,'2026')

# A short, stable verification synthesis supplements, rather than replaces, the detailed records.
scope=OUT/'verification_scope.pdf';c=canvas.Canvas(str(scope),pagesize=letter,pageCompression=1)
scope_pages=[
('Mathematics, evidence, and interpretation',[
('The scope of a proof','A theorem asserts what follows from its stated hypotheses. A conditional theorem remains a theorem under those hypotheses. Numerical evidence concerns the declared inputs, tolerances, and implementation. A physical model adds an identification of mathematical objects with quantities in nature. These roles are kept separate throughout the volume.'),
('The free Dirac construction','The retained formal record covers mode algebra, completed coefficient and torus evolution, the maximal unbounded Hamiltonian, its exact first-order Fourier domain, and physical self-adjointness. The generator chapter supplies written proofs of strong continuity, equality of the full generator domain with the Hamiltonian domain, the spectral-exponential identity, centered strong-resolvent convergence, and quadratic rates under a third-order Fourier moment. Those extensions do not have compiler certificates in the supplied evidence set.'),
('The comparison spaces matter','The centered operators act on the same infinite torus Fourier index space. A changing finite spatial grid additionally needs sampling, interpolation, and aliasing control. A background coupling changes the operator-domain problem. A dynamical gauge or gravitational field requires further evolution and constraint arguments.'),
('Reading the technical appendices','The detailed companions identify exact declarations, hypotheses, source records, computations, and missing corroboration. A recorded compiler pass is not a new independent compilation. A checksum validates identity relative to a reference file, not the physical assumptions or the truth of every surrounding interpretation.')]),
('Formal and computational source identity',[
('Pinned formal source','The formal endpoint is identified by the source archive Komorebi Physics Lean v0.49.0, Checked Block 49. The production record names Lean 4.34.0-rc2 and Mathlib revision aeb72f1e9981b6d35b426b16dca7759be3e7ba06. These identifiers are retained here for reproducibility, not as publication chapter names. The exact module target is Relativistic3DWeightedDiracDomain. Its namespace is KomorebiPhysics.Relativistic3DWeightedDomain.'),
('What the recorded pass establishes','The record reports a 3,064-job module import closure, checks of 40 named declarations, axiom inspection of 30 theorem or lemma declarations, and rejection of three negative controls. The cumulative inventory is reported as 147 active mathematical modules, 3,920 named declarations, and 2,968 theorem declarations. These are source-inventory and verification counts, not counts of independent physical laws.'),
('Known evidence limitations','The gauge records contain a cumulative-build log with a digest discrepancy and a Git exit-code-128 failure. Six referenced logs for two later source checkpoints are absent. Source identity checks do not turn those gaps into successful builds. The detailed gauge companion identifies the affected records. The generic aggregate Lean root also does not establish the full formal endpoint by itself. The named module and its exact import closure are the relevant target.'),
('Numerical evidence','Finite Fourier tests, symbolic Clifford checks, atlas examples, electrovac tables, and scalar-collapse diagnostics retain their declared domains and evidence histories. The figure files in this book are not a new replay of every underlying evolution. Some legacy programs require external input or a staged directory layout. The reproduction appendices preserve those limitations rather than counting unavailable runs as passes.')]),
('Physical assumptions and source conventions',[
('Energy availability controls the matter interpretation','For the specified rapid-crossing benchmark, the unprojected spectrum exceeds the available crossing energy by about 2.63 × 10<super>20</super>. A common normalization factor does not solve the coupled production equations. The cosmology calculations therefore propagate a prescribed distribution. They are conditional model results, not a demonstrated microscopic production prediction.'),
('Gravity and arithmetic refinement','The gravitational results retain their chart, nondegeneracy, boundary, spectral-support, and numerical hypotheses. The classical master equation does not define a quantum measure or settle anomalies. Arithmetic refinement supplies written finite and infinite constructions under their stated compatibility and domain assumptions. Related formal tower interfaces are not a Lean certificate for the whole arithmetic model.'),
('Bibliographic scope','The bibliography supplies context for the constructions and records direct comparisons where supported. It is not an exhaustive specialist literature-priority audit. The book does not infer historical priority, independent reproduction, or empirical preference from the extent of the material or from its internal checks.'),
('Source correspondence and reproduction','The accompanying source concordance maps reading passages to the implementation notes moved out of the mathematical narrative. The editorial record preserves the provenance of the source texts, unchanged proof material, document-build results, and known verification limits. Source files, displayed figure assets, and assembly scripts allow the reading volume to be rebuilt. Compiler replay and a full numerical reproduction are separate tasks with their own dependency requirements.')])]
for n,(heading,sections) in enumerate(scope_pages,1):
 header(c,'Verification scope',n);y=title(c,heading)
 for h,body in sections:
  y=para(c,h,57,y,W-114,13.1,17,'BookBold',NAVY)-6
  y=para(c,body,57,y,W-114,11.8,16.1)-17
 c.showPage()
c.save()

# source name, title, concise subtitle, page subset (None means complete)
def entry(stem,name,deck,span=None):
 path=BUILD/stem/(stem+'.pdf') if stem!='verification_scope' else scope
 with fitz.open(path) as d:count=len(d)
 return {'stem':stem,'title':name,'deck':deck,'path':str(path),'source_pages':list(range(count)) if span is None else list(range(*span))}
parts=[
('I','Resolution and free dynamics','Exact packet algebra becomes field dynamics only after reconstruction, completion, and domain control are supplied. The argument moves from finite transfers to a torus Hamiltonian and then identifies its full unitary group.',[
entry('Physics_Foundations_Monograph','Projectors, Packets, and Transfer','Resolution, conservation, and operator reconstruction'),
entry('Physics_Dirac_Monograph','Fourier Packets and the Continuum Dirac Operator','Clifford matrices, Fourier completion, and the exact domain'),
entry('Block50_Spectral_Generator_Bridge','The Dirac Group and Its Generator','Spectral evolution, resolvents, and regularity-dependent rates')]),
('II','Gauge transport and gravity','A compatible link law is not yet a coupled field evolution. Gauge transport introduces ordered paths and curvature. Gravity adds dynamical geometry, constraints, boundary conditions, and a distinct continuum comparison.',[
entry('Physics_Gauge_Monograph','Gauge Covariance and Geometric Refinement','Ordered transport, conservation, and curvature estimates'),
entry('Physics_Gravity_Monograph','Constrained Gravity and Strong Fields','Canonical structure, local reduction, and spherical tests')]),
('III','Arithmetic and polyphase refinement','Arithmetic registers provide another exact resolution of a quantum state. Compatibility determines when refinement preserves the dynamics. Eliminating hidden channels produces self-energy and memory, while infinite depth requires its own analytic domain.',[
entry('Physics_Adic_Monograph','Adic and Polyphase Quantum Refinement','Haar packets, spectral reduction, and infinite hierarchies')]),
('IV','Matter and cosmological transport','A mathematical refinement fiber becomes a physical proposal only after a coupling and production history are specified. The energy-budget obstruction is examined before the distribution is propagated through cosmological observables.',[
entry('Projector_Refinement_Physics_Covariant_Backreaction_Bridge','Covariant Refinement-Fiber Dynamics','Symmetry, stress exchange, production, and ultraviolet bounds',(0,30)),
entry('Projector_Refinement_Physics_Volume_II','Cosmology, Dark Sectors, and Structure Formation','Conditional transport, structure, and linked rejection tests',(0,142))]),
('V','Visual studies','The figures follow the same objects through explicit examples. Their purpose is to make algebra, geometry, approximation, and failure modes inspectable. Every numerical illustration retains its stated input and does not replace the corresponding theorem.',[
entry('Physics_Foundations_Visual_Atlas','Foundations Visual Atlas','Packets, currents, reconstruction, and domains'),
entry('Physics_Visual_Atlas','Dirac Continuum Visual Atlas','Spinors, Fourier tails, operator domains, and evidence layers'),
entry('Physics_Gauge_Visual_Atlas','Gauge Visual Atlas','Endpoint covariance, path ordering, and curvature'),
entry('Physics_Gravity_Visual_Atlas','Gravity Visual Atlas','Constraints, reduction, and strong-field diagnostics'),
entry('Physics_Adic_Visual_Atlas','Adic and Polyphase Visual Atlas','Hierarchy, spectral channels, and compatible limits')]),
('VI','Verification and computational evidence','A proof, a compiler certificate, a numerical check, and a physical interpretation answer different questions. The following appendices identify their exact scope. Source and toolchain identifiers appear here only where they are needed to inspect or reproduce the evidence.',[
entry('verification_scope','Verification Scope and Source Conventions','Mathematical claims, formal coverage, and physical assumptions'),
entry('Physics_Foundations_Lean_Companion','Foundations Formalization Companion','Declarations, dependencies, and the foundations certificate'),
entry('Physics_Lean_Companion','Dirac Formalization Companion','The physical Hamiltonian and its exact source correspondence'),
entry('Physics_Gauge_Lean_Companion','Gauge Formalization Companion','Transport sources, recorded checks, and evidence gaps'),
entry('Physics_Gravity_Verification_Companion','Gravity Verification Companion','Conditional constructions and computational records'),
entry('Physics_Adic_Verification_Companion','Adic Verification Companion','Finite tests and the limits of formal coverage'),
entry('Projector_Refinement_Physics_Covariant_Backreaction_Bridge','Fiber Model: Computational Evidence','Provenance, numerical methods, claims, and parameters',(30,37)),
entry('Projector_Refinement_Physics_Volume_II','Cosmology: Reproducibility and Data','Source dependencies, reproduction limits, and bibliography',(142,144))])]
# Fail instead of silently slicing a changed chapter incorrectly.
for stem,expected in [('Projector_Refinement_Physics_Covariant_Backreaction_Bridge',37),('Projector_Refinement_Physics_Volume_II',144)]:
 with fitz.open(BUILD/stem/(stem+'.pdf')) as d:
  assert len(d)==expected,(stem,len(d),expected)

front_count=6;cursor=front_count;manifest=[]
for nr,pt,deck,docs in parts:
 divider=cursor;cursor+=1
 for e in docs:
  e.update(part=nr,part_title=pt,part_index=divider,index_start=cursor,page_start=cursor+1,page_end=cursor+len(e['source_pages']))
  e['source_sha256']=hashlib.sha256(Path(e['path']).read_bytes()).hexdigest()
  cursor+=len(e['source_pages']);manifest.append(e)

front=OUT/'frontmatter.pdf';c=canvas.Canvas(str(front),pagesize=letter,pageCompression=1)
cover(c);c.showPage()
header(c,'Introduction',2);y=title(c,'A common language for resolved physics')
for t in [
'A physical description often begins by choosing what to resolve. A state may be separated into spatial cells, Fourier modes, spin channels, or arithmetic registers. The useful questions begin after that choice: how is the state reconstructed, how do its components exchange information, and what is retained when the resolution changes?',
'This book develops those questions through a sequence of concrete constructions. Projector and transfer identities supply the finite algebra. Hilbert-space completion and operator domains supply the analytic control. The free Dirac model carries that route through to a self-adjoint Hamiltonian and the identification of its unitary evolution.',
'Gauge transport and constrained gravity introduce further requirements. Paths must keep their order, constraints must retain their hypotheses, and a comparison between resolutions must name its topology. Arithmetic and polyphase refinement show how compatible embeddings differ from elimination of hidden degrees of freedom. The latter can create self-energy and memory rather than a smaller autonomous copy of the original dynamics.',
'The final physical-model chapters ask what follows when a refinement fiber is coupled to spacetime and used in cosmology. Their interpretation is controlled by the production-energy test. A consistent transport calculation from a prescribed distribution does not establish that a microscopic crossing produced that distribution.',
'The chapters share a language, not a claim that all their physical problems have the same solution. Exact identities, analytic limits, compiler certificates, numerical examples, and proposed interpretations remain distinguishable. The book can therefore be read as one mathematical argument without treating every application as an established theory of nature.'
]:y=para(c,t,57,y,W-114)-18
c.showPage()
header(c,'Reading conventions',3);y=title(c,'The argument and its conventions')
for h,t in [
('From local structure to complete spaces','Read the first part in order. Packet identities establish what is conserved. Fourier completion makes the state space complete. The operator-domain argument makes the Hamiltonian meaningful. The generator proof then connects that operator to the constructed evolution.'),
('From structure to a physical model','The middle parts change the model while retaining the same discipline: name the state space, the transfer or refinement map, the mathematical assumptions, and the residual obstruction. In the matter and cosmology part, the distribution used for transport remains an explicit input until a controlled production calculation supplies it.'),
('Notation and references','Each named treatment retains its local section, equation, figure, and theorem numbering. References to those numbers are local to that treatment unless another title is named. Page numbers and the contents are continuous across the book. The PDF bookmarks provide the detailed navigation within each treatment.'),
('Proof and verification','The mathematical chapters carry their hypotheses and written proofs. The visual studies illustrate declared examples. The technical appendices identify the formal statements and recorded computations, including missing evidence and uncompiled extensions. A document build is not a theorem check.'),
('The free-field comparison','The continuum and centered Fourier families use the same infinite mode index set. A changing finite sampled lattice is not silently substituted for that setting. The first-order Hamiltonian domain and the third-order moment required by the quadratic rate are also kept distinct.')
]:
 y=para(c,h,57,y,W-114,13.3,17,'BookBold',NAVY)-6;y=para(c,t,57,y,W-114,12.1,16.6)-17
c.showPage()
links=[]
def contents(c,num,heading,groups):
 header(c,'Contents',num);y=title(c,heading,'Page numbers refer to this complete volume.')
 for nr in groups:
  p=next(x for x in parts if x[0]==nr)
  y=para(c,nr+'  /  '+p[1].upper(),57,y,W-114,9.1,12,'BookSansBold',TEAL)-12
  for e in p[3]:
   top=y
   y=para(c,e['title'],64,y,W-154,13.4,16,'BookSerif',INK)
   c.setFont('BookSansBold',9.5);c.setFillColor(color(TEAL));c.drawRightString(W-57,top-10,str(e['page_start']))
   y-=3;y=para(c,e['deck'],64,y,W-154,8.6,11.7,'BookSans',MUTED)-17
   links.append({'page':num-1,'rect':[60,H-top-2,W-52,H-y-7],'dest':e['index_start']})
  y-=11
contents(c,4,'Contents / Mathematical constructions',['I','II','III','IV']);c.showPage()
contents(c,5,'Contents / Visual studies',['V']);c.showPage()
contents(c,6,'Contents / Verification and sources',['VI']);c.showPage();c.save()

# Subject leaves provide mathematical transitions, rather than release notes.
div=OUT/'part_leaves.pdf';c=canvas.Canvas(str(div),pagesize=letter,pageCompression=1)
for nr,name,deck,docs in parts:
 c.setFillColor(color(NAVY));c.rect(0,0,W,H,fill=1,stroke=0)
 c.setFillColor(color(TEAL));c.rect(0,H-21,W,5,fill=1,stroke=0)
 c.setFont('BookSansBold',9);c.setFillColor(color('#59C2C9'));c.drawString(57,H-72,'KOMOREBI PHYSICS')
 c.setFont('BookSerif',75);c.drawString(54,H-198,nr)
 y=para(c,name,57,H-251,W-114,32,37,'BookBold',WHITE)-25
 line(c,y,57,157,COPPER,1.6)
 y=para(c,deck,57,y-24,W-128,13,19,'BookSerif',ICE)-26
 for e in docs:
  y=para(c,e['title'],57,y,W-128,10.3,14.5,'BookSans',ICE)-7
 c.showPage()
c.save()

# Import without links and rebuild against one complete source-to-book map.
book=fitz.open();fd=fitz.open(front);dd=fitz.open(div);book.insert_pdf(fd,links=False)
source_docs={};mapping={};orig_links={};toc=[[1,'Introduction',2],[2,'Reading conventions',3],[1,'Contents',4],[2,'Visual studies',5],[2,'Verification and sources',6]]
for idx,(nr,name,deck,docs) in enumerate(parts):
 book.insert_pdf(dd,from_page=idx,to_page=idx,links=False)
 toc.append([1,f'{nr}. {name}',len(book)])
 for e in docs:
  key=e['stem'];source_docs.setdefault(key,fitz.open(e['path']));d=source_docs[key]
  assert len(book)==e['index_start']
  first=len(book)
  for offset,sp in enumerate(e['source_pages']):
   mapping[(key,sp)]=first+offset;orig_links[(key,sp)]=d[sp].get_links()
  book.insert_pdf(d,from_page=e['source_pages'][0],to_page=e['source_pages'][-1],links=False,annots=False)
  print('Imported',e['title'],len(book),flush=True)
  toc.append([2,e['title'],e['page_start']])
  for level,label,sp in d.get_toc():
   if sp-1 in e['source_pages']:
    toc.append([level+2,label,mapping[(key,sp-1)]+1])
# Continuous folios: remove only text in the footer band, not content or figures.
footer_log=[]
for i,p in enumerate(book):
 # front matter and part leaves have their own design.
 if i<front_count or any(i==x['part_index'] for x in manifest):continue
 boxes=[]
 for b in p.get_text('dict')['blocks']:
  if b['type']!=0:continue
  for l in b['lines']:
   txt=''.join(s['text'] for s in l['spans']).strip();r=fitz.Rect(l['bbox'])
   if r.y0>744 and (txt.isdigit() or 'CONTINUUM, GEOMETRY' in txt or txt in ['KOMOREBI PHYSICS','SPECTRAL GENERATOR BRIDGE']):boxes.append(r+(-1,-1,1,1))
 for r in boxes:p.add_redact_annot(r,fill=(1,1,1))
 if boxes:p.apply_redactions(images=0,graphics=0)
 # Same quiet running footer on every reading page.
 p.insert_text((57,765),'CONTINUUM, GEOMETRY AND REFINEMENT',fontsize=7,fontname='helv',color=(.345,.424,.467))
 p.insert_textbox(fitz.Rect(W-108,752,W-57,770),str(i+1),fontsize=9,fontname='helv',align=2,color=(.027,.541,.596))
 footer_log.append({'page':i+1,'old_footer_items':len(boxes)})
internal=external=0;dropped=[]
for (key,sp),ls in orig_links.items():
 p=book[mapping[(key,sp)]]
 for old in ls:
  if old['kind'] in (fitz.LINK_GOTO, fitz.LINK_NAMED) and old.get('page', -1) >= 0:
   target=(key,old.get('page',-1))
   if target not in mapping:dropped.append({'source':key,'page':sp+1,'target':old.get('page')});continue
   p.insert_link({'kind':fitz.LINK_GOTO,'from':old['from'],'page':mapping[target],'to':old.get('to',fitz.Point(0,0))});internal+=1
  elif old['kind']==fitz.LINK_URI:
   p.insert_link({'kind':fitz.LINK_URI,'from':old['from'],'uri':old['uri']});external+=1
  elif old['kind']!=fitz.LINK_NONE:dropped.append({'source':key,'page':sp+1,'kind':old['kind']})
for lk in links:book[lk['page']].insert_link({'kind':fitz.LINK_GOTO,'from':fitz.Rect(lk['rect']),'page':lk['dest'],'to':fitz.Point(0,0)})
book.set_toc(toc)
book.set_metadata({'title':'Komorebi Physics: Continuum, Geometry and Refinement','author':'Komorebi P.','subject':'Resolved dynamics, fields, geometry, arithmetic refinement and cosmological models','keywords':'Komorebi, physics, realization calculus, Dirac, gauge, gravity, refinement','creator':'Komorebi Physics publication source','producer':'Source-built LaTeX and PDF assembly'})
book.set_page_labels([{'startpage':0,'prefix':'','style':'D','firstpagenum':1}])
output=ROOT/'Komorebi_Physics_Collected_Monograph.pdf'
print('Saving complete volume',len(book),'pages',flush=True)
book.save(output,garbage=3,deflate=True)
record={'page_count':len(book),'contents_entries':len(manifest),'bookmarks':len(toc),'restored_internal_links':internal,'external_links':external,'contents_links':len(links),'unresolved_source_links':dropped,'output_sha256':hashlib.sha256(output.read_bytes()).hexdigest()}
(OUT/'book_manifest.json').write_text(json.dumps(manifest,indent=2))
(OUT/'assembly_validation.json').write_text(json.dumps(record,indent=2))
(OUT/'footer_log.json').write_text(json.dumps(footer_log,indent=2))
print(json.dumps(record,indent=2))
