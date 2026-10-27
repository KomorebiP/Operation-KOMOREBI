from pathlib import Path
import fitz
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,KeepTogether
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
import json

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'checkpoint_v0.3.0' if (ROOT/'checkpoint_v0.3.0').exists() else ROOT.parent/'Paper_III_Continuation_v0.3.0'
OUT=ROOT/'publication';OUT.mkdir(exist_ok=True)
colors={'ink':HexColor('#193139'),'teal':HexColor('#326d6b'),'muted':HexColor('#55686a'),'line':HexColor('#cfd9d6')}
ss=getSampleStyleSheet()
ss.add(ParagraphStyle(name='KickerK',parent=ss['Normal'],fontName='Helvetica-Bold',fontSize=10,tracking=1.1,leading=14,textColor=colors['teal'],spaceAfter=13))
ss.add(ParagraphStyle(name='MainK',parent=ss['Title'],fontName='Times-Bold',fontSize=27,leading=31,textColor=colors['ink'],spaceAfter=10,alignment=TA_LEFT))
ss.add(ParagraphStyle(name='SubK',parent=ss['Normal'],fontName='Times-Roman',fontSize=15,leading=20,textColor=colors['muted'],spaceAfter=17))
ss.add(ParagraphStyle(name='HeadK',parent=ss['Heading2'],fontName='Helvetica-Bold',fontSize=11.4,leading=16,textColor=colors['ink'],spaceBefore=13,spaceAfter=8))
ss.add(ParagraphStyle(name='BodyK',parent=ss['BodyText'],fontName='Times-Roman',fontSize=10.5,leading=15,spaceAfter=9))
ss.add(ParagraphStyle(name='SmallK',parent=ss['BodyText'],fontName='Helvetica',fontSize=8.8,leading=12,spaceAfter=6))
ss.add(ParagraphStyle(name='CellK',parent=ss['Normal'],fontName='Helvetica',fontSize=9,leading=12))
ss.add(ParagraphStyle(name='CellHeadK',parent=ss['Normal'],fontName='Helvetica-Bold',fontSize=9,leading=12))
def P(t,style='BodyK'):return Paragraph(t,ss[style])

def onpage(c,d):
 c.saveState();w,h=letter
 c.setStrokeColor(colors['line']);c.setLineWidth(.65);c.line(55,h-46,w-55,h-46)
 c.setFont('Helvetica',7.5);c.setFillColor(colors['muted']);c.drawString(56,30,'OPERATION KOMOREBI / PAPER III — PRIVATE SCOPE REVIEW')
 c.drawRightString(w-56,30,str(d.page));c.restoreState()

cover=OUT/'Paper_III_Release_Scope_v1.0.0_rc1.pdf'
doc=SimpleDocTemplate(str(cover),pagesize=letter,leftMargin=55,rightMargin=55,topMargin=65,bottomMargin=58,title='Paper III release scope and evidence',author='Komorebi P.')
s=[]
s += [P('OPERATION KOMOREBI · REALIZATION CALCULUS','KickerK'),P('Projector Resolved Seed Calculus III','MainK'),P('Release scope and verification record','SubK'),P('Version 1.0.0-rc1 · 20 October 2026 · Private prepublication candidate','SmallK')]
s += [P('Publication decision','HeadK'),P('<b>Technical package assembled and source identities authenticated. Unrestricted formal closeout is not certified.</b> The expanded manuscript is supplied in full, with the historical Lean formal core and the Section 16 continuation. Section 17 gains a new full ordinary proof supplement. Two candidate Lean modules remain uncompiled and are not imported into the accepted development.')]
s += [P('What the evidence supports','HeadK')]
data=[['Layer','Accepted boundary'],['Finite algebraic core','Historical 41-row formal map and 143 mapped targets, retained with its original evidence.'],['Section 16','12 recorded production modules, with 558 logical declarations replayed in the inherited record; 14 generated runtime helpers separately inventoried.'],['Section 17','Ordinary proofs of continuous packet jets, norm estimates, Taylor remainders, and higher composition. No new Lean acceptance.'],['Independent tests','15,331 retained Section 16 controls, 2,622 Section 17 controls, and 677 new higher-order symbolic checks passed in this closeout.']]
rows=[[P(t,'CellHeadK') if i==0 else P(t,'CellK') for t in row] for i,row in enumerate(data)]
tab=Table(rows,colWidths=[137,361],hAlign='LEFT',repeatRows=1)
tab.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#e8f0ee')),('LINEBELOW',(0,0),(-1,0),.7,colors['teal']),('LINEBELOW',(0,1),(-1,-1),.35,colors['line']),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
s.append(tab)
s += [P('Critical restriction','HeadK'),P('The 16 October visual edition asserts 2,693 replayed declarations and 98+2 accepted results. Its matching Lean source and independent receipts were not recovered. Those claims are <b>not</b> release certified here. The 8 October visual guide is the selected reproducible edition.')]
s += [P('Licensing and distribution','HeadK'),P('No project-wide manuscript or code license was selected in the preserved materials. This package is a private release candidate, not permission for public redistribution. No license has been inferred or assigned.')]
s += [PageBreak(),P('Evidence guide and reading order','KickerK'),P('A bounded, reproducible reading edition','MainK'),P('What each document is','HeadK')]
for lead, desc in [
('Traditional monograph (98 pages)','The complete October 8 mathematical edition, unchanged. It includes established theorems, qualified reductions, research directions, and ordinary proofs across the expanded paper.'),
('Analytic proof supplement (5 pages)','Additional rigorous Section 17 arguments. In particular, the literal range jet has a sharper norm bound than its ambient extension. No new Lean result is claimed.'),
('Visual guide (26 pages)','The source-bound finite companion, with 24 worked plates and 22 exact model figures. This is the earlier edition, deliberately selected over an October 16 edition with unauthenticated formal claims.'),
('Lean and evidence guide (49 pages)','Documents the historical finite 41-row contract. It is preserved, not silently retrofitted to claim expanded monograph coverage.'),
('Statement register (167 environments)','The JSON and CSV map identifies source hashes and evidence classes, including 98 theorem-like environments and two classical standard-fact environments.')]:
 s.append(P('<b>'+lead+'.</b> '+desc))
s += [P('Reproducibility','HeadK'),P('Run <font face="Courier">python VERIFY_RELEASE.py</font> after extraction to validate all packaged bytes and PDF structure. The exact symbolic tests and inherited proof source/object identity checks have separate commands in the release README. Fresh Lean kernel verification requires the absent pinned 2.9 GB toolchain and dependencies.')]
s += [P('What remains open','HeadK'),P('The two Section 17 draft Lean modules, the analytic derivative API correspondence, exact higher-order formalization, and comprehensive Lean correspondence for the expanded manuscript. The public license decision also remains outstanding. An accepted historical proof transcript is not a new compilation in this environment.')]
s += [P('Interpretation','HeadK'),P('The mathematical language of packet reconstruction and obstruction is usable now. Closing a narrowly stated theorem and proving general existence are different achievements. This release preserves that distinction, including all known failures and unrecovered evidence.')]
doc.build(s,onFirstPage=onpage,onLaterPages=onpage)

parts=[('Release scope',cover),('Traditional monograph',BASE/'baseline/publication/pdfs/Paper_III_Traditional_Final.pdf'),('Analytic packet proof supplement',ROOT/'docs/Paper_III_Section17_Analytic_Closeout.pdf'),('Visual guide',BASE/'baseline/publication/pdfs/Paper_III_Visual_Guide_Final.pdf'),('Historical Lean and evidence guide',BASE/'baseline/publication/pdfs/Paper_III_Lean_Guide_Final.pdf')]
merged=fitz.open();toc=[];metadata=[]
for name,path in parts:
 d=fitz.open(path);start=len(merged)+1
 toc.append([1,name,start]);metadata.append({'name':name,'source':str(path),'pages':len(d),'start_page':start})
 merged.insert_pdf(d,links=False,annots=False)
merged.set_toc(toc)
merged.set_metadata({'title':'Projector Resolved Seed Calculus III — Private Scoped Reading Edition','author':'Komorebi P.','subject':'Original monograph and scoped release evidence. New Lean Section 17 work remains uncompiled.','keywords':'Komorebi, Lean, packet calculus, nonlinear reconstruction, conditional release'})
out=OUT/'Paper_III_Integrated_Reading_Edition_v1.0.0_rc1.pdf'
merged.save(out,garbage=4,deflate=True)
(ROOT/'evidence/INTEGRATED_READER_LAYOUT.json').write_text(json.dumps({'status':'BUILT','pages':len(merged),'toc':toc,'parts':metadata},indent=2)+'\n')
print('Reader pages',len(merged),'Parts:',metadata)
