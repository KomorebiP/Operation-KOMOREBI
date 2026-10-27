#!/usr/bin/env python3
"""Assemble all recovered Komorebi physics PDFs into a normalized, bookmarked volume.
Preserves source PDFs separately. Source content imported as vector/text PDF pages;
source internal links are recreated where possible after coordinate transform.
"""
import os,json,hashlib,math,collections
from pathlib import Path
import fitz
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor,Color
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'book'; OUT.mkdir(exist_ok=True)
SOURCE=Path('/mnt/data/Komorebi_Physics_Latest_Reading_2026-10-20')
BASE=Path('/mnt/data')
NAVY='#10283F'; MID='#173F5A'; TEAL='#078A98'; COPPER='#C99853'; ICE='#E5F3F4'; INK='#1C3445'; MUTED='#586C77'; PAPER='#FCFDFD'; WHITE='#FFFFFF'
W,H=letter
for name,path in [('EB','/usr/share/fonts/truetype/ebgaramond/EBGaramond12-Regular.ttf'),('EBBold','/usr/share/fonts/truetype/ebgaramond/EBGaramond12-Bold.ttf'),('Lato','/usr/share/fonts/truetype/lato/Lato-Regular.ttf'),('LatoBold','/usr/share/fonts/truetype/lato/Lato-Bold.ttf'),('LatoLight','/usr/share/fonts/truetype/lato/Lato-Light.ttf')]:
    pdfmetrics.registerFont(TTFont(name,path))
parts=[
('I','Resolution and the Free Continuum','From finite projector packets to a fully defined torus Hamiltonian and its generator',[
('Projectors, Packets and Transfer','Original foundation monograph; existing formal source coverage','Physics_Foundations_Monograph.pdf','earlier'),
('Fourier Packets and the Continuum Dirac Operator','Checked endpoint through Block 49; continuum free field','Physics_Dirac_Monograph.pdf','checked'),
('The Dirac Group and Its Generator','NEW: Block 50 analytic proofs; Lean port pending','@BLOCK50','analytic')]),
('II','Gauge Covariance and Gravity','Ordered gauge transport, geometric refinement, constraint systems, and strong fields',[
('Gauge Covariance and Geometric Refinement','Gauge calculus, lattice conservation and regularity conditions','Physics_Gauge_Monograph.pdf','mixed'),
('Constrained Gravity and Strong Fields','Canonical reduction, boundary constraints and spherical examples','Physics_Gravity_Monograph.pdf','mixed')]),
('III','Adic and Polyphase Quantum Physics','Prime-register packets, Haar refinement, spectral elimination and compatible limits',[
('Adic and Polyphase Quantum Refinement','Finite adelic structures, quantum walks and infinite depth','Physics_Adic_Monograph.pdf','mixed')]),
('IV','Backreaction and Cosmological Transport','Covariant fiber dynamics, physical budgets, and cosmological rejection tests',[
('Covariant Refinement-Fiber Dynamics','Earlier research edition; energy availability obstruction retained','@BACKREACTION','conditional'),
('Cosmology, Dark Sectors and Structure Formation','Earlier research monograph; candidate model and comparisons','@COSMO','model')]),
('V','Visual Atlases','Reproducible figures and interpretation guides for the five newer monographs',[
('Foundations Visual Atlas','Resolution, flow and projector diagrams','Physics_Foundations_Visual_Atlas.pdf','guide'),
('Dirac Continuum Visual Atlas','Spinor, Fourier and continuum diagrams','Physics_Visual_Atlas.pdf','guide'),
('Gauge Visual Atlas','Ordered transport and curvature diagnostics','Physics_Gauge_Visual_Atlas.pdf','guide'),
('Gravity Visual Atlas','Constraints and strong-field test figures','Physics_Gravity_Visual_Atlas.pdf','guide'),
('Adic and Polyphase Visual Atlas','Hierarchical spectral and refinement diagrams','Physics_Adic_Visual_Atlas.pdf','guide')]),
('VI','Lean and Verification Companions','Exact source correspondence, checks, gaps and mathematical status',[
('Foundations Lean Companion','Block 1–16 map and proof boundaries','Physics_Foundations_Lean_Companion.pdf','audit'),
('Dirac Lean Companion','Block 41–49 checked declarations and build receipts','Physics_Lean_Companion.pdf','audit'),
('Gauge Lean Companion','Selected Lean modules and source receipt discrepancies','Physics_Gauge_Lean_Companion.pdf','audit'),
('Gravity Verification Companion','Independent calculations and conditional result audit','Physics_Gravity_Verification_Companion.pdf','audit'),
('Adic Verification Companion','Numerical and formal coverage limits','Physics_Adic_Verification_Companion.pdf','audit')]),
('A','Editorial Appendix','Status language, sources and continuity for subsequent physics volumes',[
('Physics Collection Guide','Previous series guide, v0.5.0','Physics_Collection_Guide.pdf','audit')]),
]

def abspath(name):
    if name=='@BLOCK50': return ROOT/'manuscript'/'Block50_Spectral_Generator_Bridge.pdf'
    if name=='@BACKREACTION': return BASE/'Projector_Refinement_Physics_Covariant_Backreaction_Bridge_v1.0.0.pdf'
    if name=='@COSMO': return BASE/'Projector_Refinement_Physics_Volume_II.pdf'
    return SOURCE/name

front_count=5
cursor=front_count
manifest=[]
for idx,(letter_num,ptitle,deck,docs) in enumerate(parts):
    part_index=cursor
    cursor+=1
    for name,desc,source,status in docs:
        fn=abspath(source)
        if not fn.exists(): raise FileNotFoundError(fn)
        d=fitz.open(fn); count=len(d); size=fn.stat().st_size
        manifest.append({'part':letter_num,'part_title':ptitle,'title':name,'deck':desc,'source':source,'source_filename':fn.name,'source_path':str(fn),
                         'source_sha256':hashlib.sha256(fn.read_bytes()).hexdigest(),
                         'status':status,'page_start':cursor+1,'page_end':cursor+count,'page_count':count,'index_start':cursor,
                         'part_index':part_index,'size_bytes':size})
        cursor+=count
expected_pages=cursor

def C(x):return HexColor(x)

def textblock(c,txt,x,y,width,size=11,lead=17,font='Lato',color=INK):
    st=ParagraphStyle('p',fontName=font,fontSize=size,leading=lead,textColor=C(color),alignment=TA_LEFT,spaceAfter=0)
    p=Paragraph(txt,st)
    _,h=p.wrap(width,500)
    p.drawOn(c,x,y-h)
    return y-h

def rectline(c,x,y,x1,y1,col=TEAL,lw=1):
    c.setStrokeColor(C(col));c.setLineWidth(lw);c.line(x,y,x1,y1)

def smallhead(c,number,label):
    c.setFillColor(C(NAVY));c.rect(0,H-22,W,22,fill=1,stroke=0)
    c.setFont('LatoBold',7.4);c.setFillColor(C(ICE));c.drawString(42,H-15,'OPERATION KOMOREBI')
    c.setFillColor(C('#65D5D6'));c.drawRightString(W-42,H-15,'PHYSICS  /  COLLECTED VOLUME')
    c.setFillColor(C(MUTED));c.setFont('Lato',7.8);c.drawString(42,31,label.upper());c.drawRightString(W-42,31,f'{number:02d}')
    rectline(c,42,42,W-42,42,TEAL,.65)

def cover(c):
    c.setFillColor(C(NAVY));c.rect(0,0,W,H,fill=1,stroke=0)
    c.setFillColor(C(TEAL));c.rect(0,H-22,W,7,fill=1,stroke=0)
    c.setFillColor(C(ICE));c.setFont('LatoBold',10);c.drawString(52,H-72,'OPERATION KOMOREBI')
    c.setFillColor(C('#51C1C7'));c.setFont('LatoBold',9.2);c.drawString(52,H-94,'PHYSICS MONOGRAPH SERIES  /  COLLECTED EDITION')
    c.setFillColor(C(WHITE));c.setFont('EBBold',35);c.drawString(50,H-198,'Physics')
    c.setFont('EB',31);c.drawString(51,H-242,'Continuum, Geometry')
    c.drawString(51,H-279,'and Refinement')
    rectline(c,51,H-305,153,H-305,COPPER,2)
    c.setFillColor(C(ICE));c.setFont('Lato',11.2)
    c.drawString(52,H-335,'Free Dirac evolution  /  Gauge transport  /  Gravity')
    c.drawString(52,H-355,'Adic structure  /  Backreaction  /  Cosmology')
    # Deterministic geometric wave structure, not an AI generated illustration.
    for j in range(11):
        path=c.beginPath();x0=-20; y0=116+j*11.4;path.moveTo(x0,y0)
        for k in range(51):
            x=x0+k*13.5
            yy=y0+19*math.sin(.016*x+.26*j)+5*math.sin(.047*x+.3*j)
            path.lineTo(x,yy)
        c.setStrokeColor(Color(0.10,0.67,0.70,alpha=max(.07,.17-.006*j)))
        c.setLineWidth(.75);c.drawPath(path,stroke=1)
    c.setFillColor(C('#D6E6E9'));c.setFont('EB',12);c.drawString(52,65,'Komorebi P.')
    c.setFont('Lato',8.9);c.drawString(52,43,'20 October 2026  /  Collected edition 0.6.0  /  7 research themes')

def reader_note(c):
    smallhead(c,2,'Reader note')
    c.setFillColor(C(NAVY));c.setFont('EBBold',24);c.drawString(42,H-83,'An integrated physics volume')
    rectline(c,42,H-100,W-42,H-100,TEAL,.9)
    y=H-129
    for text in [
      'This edition places the recovered physics research in one reading sequence. It retains the <b>original manuscripts, visual atlases, and verification companions</b> as separate identifiable chapters. A new analytic Block 50 paper is inserted immediately after the completed Dirac continuum monograph.',
      'The new physics identity uses <b>midnight navy, ocean teal, and warm copper</b>. It is intentionally distinct from the mathematics collection. A uniform book frame, folios, section leaves, contents, and PDF bookmarks tie the manuscripts together without rewriting their underlying mathematical claims.',
      'The original editions range across different dates and proof statuses. In particular, the earlier covariant backreaction and cosmology research remains conditional where its own assumptions demand that status. No changes to historical theorems, analyses, negative results, or source receipts are implied by the new binding.',
    ]:
        y=textblock(c,text,42,y,W-84,size=11.2,lead=18.2,font='Lato')-18
    c.setFillColor(C(ICE));c.roundRect(42,y-115,W-84,105,10,fill=1,stroke=0)
    c.setFillColor(C(NAVY));c.setFont('LatoBold',10);c.drawString(59,y-37,'WHAT IS NEW IN THIS EDITION')
    yy=textblock(c,'Block 50 gives analytic proofs of the maximal generator identification, centered strong resolvent convergence, and a third order regularity bound with quadratic spacing error. Its accompanying Lean draft is <b>not compiled</b>. Numerical verification remains a separate layer of evidence.',59,y-46,W-118,size=10.25,lead=15.4)
    y=y-153
    c.setFont('EBBold',16);c.setFillColor(C(NAVY));c.drawString(42,y,'How to use this book')
    y=textblock(c,'Read Parts I–IV for the primary research narrative. Use Part V for figures and worked diagrams. Consult Part VI before transferring a mathematical statement into a formal verification claim. The final appendix records the scope and chronology of the previous 0.5.0 collection.',42,y-17,W-84,size=10.7,lead=16.2)-18
    c.setFillColor(C(MUTED));c.setFont('Lato',9);c.drawString(42,max(y-20,78),'Text remains searchable; the contents and PDF bookmarks navigate to each source chapter.')

# Two contents pages, with record of their absolute positions for link annotation.
link_regions=[]

def contents_page(c,number,groups,heading):
    smallhead(c,number,'Contents')
    c.setFillColor(C(NAVY));c.setFont('EBBold',26);c.drawString(42,H-84,heading)
    c.setFillColor(C(MUTED));c.setFont('Lato',9.5);c.drawString(42,H-106,'Physical page numbers in the combined volume')
    rectline(c,42,H-119,W-42,H-119,TEAL,.85)
    y=H-153
    for part in groups:
        nr,title,deck,docs=part
        c.setFillColor(C(TEAL));c.setFont('LatoBold',9.3);c.drawString(42,y,f'{nr}  /  {title.upper()}')
        y-=21
        for ent in manifest:
            if ent['part']!=nr:continue
            title=ent['title']; status=ent['status'];page=ent['page_start']
            if len(title)>52: title=title[:49]+'…'
            c.setFillColor(C(INK));c.setFont('EB',13.5);c.drawString(51,y,title)
            c.setFillColor(C(TEAL));c.setFont('LatoBold',9.5);c.drawRightString(W-43,y-1,str(page))
            link_regions.append({'front_page':number-1,'x0':45,'y0':H-y-6,'x1':W-40,'y1':H-y+17,'dest_index':ent['index_start']})
            y-=15
            c.setFillColor(C(MUTED));c.setFont('Lato',8.1);c.drawString(51,y,ent['deck'][:97])
            y-=27
        y-=12
    if y<70: raise RuntimeError(f'Contents page overflow: {number} at {y}')


def status_note(c):
    smallhead(c,5,'Verification guide')
    c.setFillColor(C(NAVY));c.setFont('EBBold',25);c.drawString(42,H-83,'Evidence, continuity, and scope')
    rectline(c,42,H-101,W-42,H-101,TEAL,.85)
    y=H-130
    pairs=[
      ('RECORDED LEAN','Block 49 is the last recovered checked formal checkpoint. The source reports successful exact-target and replay gates.'),
      ('ANALYTIC PAPER','Block 50 contains complete written proofs at the mathematical level. These proofs have not been translated into compiler-certified Lean theorems.'),
      ('CONTROLLED NUMERICS','A finite Fourier regression checks identities, rates and signs, with an intentional failed sign control. It cannot prove infinite-dimensional limits.'),
      ('CONDITIONAL MODEL','Gauge, gravity, adic, backreaction and cosmology retain each source’s stated assumptions, failure modes and verification boundaries.'),
    ]
    for k,t in pairs:
        c.setFillColor(C(TEAL));c.roundRect(42,y-22,5,25,2,stroke=0,fill=1)
        c.setFont('LatoBold',9.2);c.setFillColor(C(NAVY));c.drawString(57,y,k)
        y=textblock(c,t,57,y-9,W-102,size=10,lead=14.5)-25
    rectline(c,42,y-6,W-42,y-6,COPPER,.85)
    y-=45
    c.setFillColor(C(NAVY));c.setFont('EBBold',16.5);c.drawString(42,y,'The technical continuation')
    y-=16
    y=textblock(c,'<b>Generator:</b> the free torus Hamiltonian now has a manuscript-level spectral bridge to the constructed unitary group. <b>Operator limit:</b> centered multipliers converge on the common coefficient space in graph and strong resolvent senses. <b>Separate obligation:</b> a genuine changing finite spatial grid needs sampling, aliasing, and geometry-compatible interpolation, none of which is supplied by the centered multiplier alone.',42,y,W-84,size=10.15,lead=16)-18
    c.setFillColor(C(MUTED));c.setFont('Lato',8.5)
    c.drawString(42,max(55,y-14),'No constituent source is relicensed or silently modified by this collected edition.')

front=OUT/'_frontmatter.pdf'
c=canvas.Canvas(str(front),pagesize=letter,pageCompression=1)
c.setTitle('Komorebi Physics: Continuum, Geometry and Refinement')
cover(c);c.showPage()
reader_note(c);c.showPage()
contents_page(c,3,parts[:4],'Contents / Research papers');c.showPage()
contents_page(c,4,parts[4:],'Contents / Companions');c.showPage()
status_note(c);c.showPage();c.save()

# Separate divider pages to make the collection flow across the original editions.
divpath=OUT/'_dividers.pdf'
c=canvas.Canvas(str(divpath),pagesize=letter,pageCompression=1)
for number,title,deck,docs in parts:
    c.setFillColor(C(NAVY));c.rect(0,0,W,H,stroke=0,fill=1)
    c.setFillColor(C(TEAL));c.rect(0,H-21,W,5,stroke=0,fill=1)
    c.setFillColor(C(COPPER));c.rect(54,190,80,2,stroke=0,fill=1)
    c.setFillColor(C('#3C8591'));c.setFont('LatoBold',10);c.drawString(54,H-97,'KOMOREBI PHYSICS  /  COLLECTED VOLUME')
    c.setFillColor(C('#52C3C9'));c.setFont('LatoLight',86);c.drawString(48,H-237,str(number))
    yy=H-288
    from reportlab.platypus import Paragraph
    y=textblock(c,title,54,yy,W-110,size=30,lead=32,font='EBBold',color=WHITE)
    rectline(c,54,y-28,150,y-28,COPPER,1.75)
    y=textblock(c,deck,54,y-49,W-125,size=13,lead=19,font='Lato',color=ICE)
    c.setFillColor(C(ICE));c.setFont('Lato',9)
    c.drawString(54,75,f'{len(docs)} CHAPTER' + ('S' if len(docs)!=1 else '') + '   /   ORIGINAL EDITIONS PRESERVED')
    c.showPage()
c.save()

book=fitz.open();frontdoc=fitz.open(front);divdoc=fitz.open(divpath)
book.insert_pdf(frontdoc)
toc=[[1,'Collected physics volume',1],[2,'Reader note and provenance',2],[2,'Contents: primary research',3],[2,'Contents: guides and companions',4],[2,'Evidence and boundaries',5]]
source_links=0; chapter_ranges=[]
# Return center destination dimensions and scalar for converting source link rectangles.
for part_idx,(pn,ptitle,deck,docs) in enumerate(parts):
    part_page=len(book)
    book.insert_pdf(divdoc,from_page=part_idx,to_page=part_idx)
    toc.append([1,('Appendix' if pn=='A' else f'Part {pn}')+': '+ptitle,part_page+1])
    for title,desc,source,status in docs:
        ent=next(e for e in manifest if e['title']==title and e['part']==pn)
        start=len(book)
        expected=ent['index_start']
        if start!=expected: raise RuntimeError(f'pagination mismatch at {title}: got {start}, planned {expected}')
        doc=fitz.open(abspath(source))
        toc.append([2,title,start+1])
        raw_toc=doc.get_toc()
        # Nested source bookmarks help navigate the source without importing PDFs as isolated artifacts.
        for bk in raw_toc:
            lvl,bt,bpage=bk[:3]
            if bpage<1 or bpage>len(doc):continue
            level=min(4,max(3,int(lvl)+2))
            toc.append([level,bt,start+bpage])
        links_to_add=[]
        for source_i in range(len(doc)):
            sp=doc[source_i]
            page=book.new_page(width=W,height=H)
            # Leave clean space for book edge and independent global folio.
            target=fitz.Rect(11,22,W-11,H-29)
            factor=min(target.width/sp.rect.width,target.height/sp.rect.height)
            display=fitz.Rect((W-sp.rect.width*factor)/2,(22+(target.height-sp.rect.height*factor)/2),
                              (W+sp.rect.width*factor)/2,(22+(target.height-sp.rect.height*factor)/2)+sp.rect.height*factor)
            page.show_pdf_page(display,doc,source_i,keep_proportion=True,overlay=True)
            # Book identity: a tiny brand rail and global folio, outside the source content.
            page.draw_rect(fitz.Rect(0,0,W,3),color=None,fill=(7/255,138/255,152/255),overlay=True)
            page.insert_text((21,14.5),'KOMOREBI / PHYSICS',fontname='helv',fontsize=6.3,color=(.11,.28,.36))
            chapter_name=title if len(title)<=50 else title[:46]+'...'
            page.insert_text((18,H-13.5),chapter_name.upper(),fontname='helv',fontsize=6.4,color=(.33,.42,.46))
            page.insert_text((W-43,H-13.5),str(len(book)),fontname='hebo',fontsize=8,color=(.06,.45,.49))
            # Reconstruct local PDF jumps, based on original link rectangles.
            try: slinks=sp.get_links()
            except Exception:slinks=[]
            for link in slinks if 'slinks' in locals() else []:
                src_rect=link.get('from')
                if not src_rect:continue
                mapped=fitz.Rect(display.x0+src_rect.x0*factor,display.y0+src_rect.y0*factor,
                                 display.x0+src_rect.x1*factor,display.y0+src_rect.y1*factor)
                kind=link.get('kind')
                if kind==fitz.LINK_GOTO and 0<=link.get('page',-1)<len(doc):
                    links_to_add.append((len(book)-1,{'kind':fitz.LINK_GOTO,'from':mapped,'page':start+link['page']}))
                elif kind==fitz.LINK_URI and link.get('uri'):
                    links_to_add.append((len(book)-1,{'kind':fitz.LINK_URI,'from':mapped,'uri':link['uri']}))
        for source_page,link in links_to_add:
            try:book[source_page].insert_link(link);source_links+=1
            except Exception:pass
        ent['book_start_actual']=start+1
        chapter_ranges.append((start,len(book),title))
        doc.close()
        print(f'Added {title}: {len(book)-start} pp @ {start+1}')
if len(book)!=expected_pages: raise RuntimeError(f'Final length {len(book)} != computed {expected_pages}')

# Make prefatory Contents entries into direct PDF links.
for lr in link_regions:
    r=fitz.Rect(lr['x0'],lr['y0'],lr['x1'],lr['y1'])
    book[lr['front_page']].insert_link({'kind':fitz.LINK_GOTO,'from':r,'page':lr['dest_index']})

# Keep bookmarks consecutive; source PDFs occasionally skip nesting levels.
normalized=[]
last=0
for level,title,page in toc:
    level=min(level,last+1) if last>0 else 1
    normalized.append([level,title,page]);last=level
book.set_toc(normalized)
book.set_metadata({'title':'Komorebi Physics | Continuum, Geometry and Refinement | Collected Edition 0.6.0',
                   'author':'Komorebi P.','subject':'Physics research collection, source editions and analytic Block 50 bridge',
                   'keywords':'Komorebi, Physics, Dirac, Fourier, Gauge, Gravity, Adic, Cosmology, Lean, Generator',
                   'creator':'Operation Komorebi, reproducible Python volume assembler'})
bookfile=OUT/'Komorebi_Physics_Collected_Volume_0.6.0_2026-10-20.pdf'
book.save(bookfile,garbage=4,deflate=True,clean=False)
book.close()

manifest_obj={'edition':'0.6.0','compiled':'2026-10-20','title':'Physics: Continuum, Geometry and Refinement',
              'page_count':expected_pages,'front_pages':front_count,'section_dividers':len(parts),
              'source_documents':len(manifest),'source_page_count':sum(e['page_count'] for e in manifest),
              'bookmarks':len(normalized),'source_links_recreated':source_links,
              'physics_color':{'navy':NAVY,'teal':TEAL,'copper':COPPER},
              'components':manifest}
(OUT/'volume_manifest.json').write_text(json.dumps(manifest_obj,indent=2),encoding='utf-8')
print(f'WROTE {bookfile} pages={expected_pages} sources={len(manifest)} bookmark_count={len(normalized)} links={source_links}')
