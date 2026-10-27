#!/usr/bin/env python3
"""Render the Core Papers' Physics-derived outer book design.

This builds editorial pages only. It does not build scientific sources, execute
formal projects, or modify the frozen reader PDFs. No font fallback is permitted.
"""
from pathlib import Path
import argparse, hashlib, json, re
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
import fitz

ROOT=Path(__file__).resolve().parent
W,H=612.0,792.0
LEFT=62.64; WIDTH=W-2*LEFT
PRIMARY='#3C263F'; ACCENT='#7B4165'; GOLD='#A68A56'
INK='#22282C'; MUTED='#675D68'; PALE='#E8DDE8'; RULE='#D9CFD8'; WHITE='#FFFFFF'
TITLE='Realization Calculus'
SUBTITLE='Projectors, Transfer and Arithmetic'
ALIASES={'CoreSerif':'P052-Roman','CoreBold':'P052-Bold','CoreItalic':'P052-Italic','CoreBoldItalic':'P052-BoldItalic','CoreSans':'NimbusSans-Regular','CoreSansBold':'NimbusSans-Bold'}


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def clean(text):
    # These are editorial labels; preserve scientific sources elsewhere.
    return str(text).replace('\u2011','-').replace('\u2013','-').replace('\u2014',', ').replace('\u2212','-')
def text(s): return escape(clean(s))
def C(s): return HexColor(s)
def roman(n):
    out=''
    for k,s in [(1000,'m'),(900,'cm'),(500,'d'),(400,'cd'),(100,'c'),(90,'xc'),(50,'l'),(40,'xl'),(10,'x'),(9,'ix'),(5,'v'),(4,'iv'),(1,'i')]:
        while n>=k: out+=s; n-=k
    return out

def register_fonts():
    records=[]
    for alias,stem in ALIASES.items():
        afm=Path('/usr/share/fonts/type1/urw-base35')/(stem+'.afm')
        pfb=Path('/usr/share/fonts/X11/Type1')/(stem+'.pfb')
        for p in [afm,pfb]:
            if not p.is_file(): raise FileNotFoundError(f'Required explicit font unavailable: {p}')
        face=pdfmetrics.EmbeddedType1Face(str(afm),str(pfb));pdfmetrics.registerTypeFace(face)
        pdfmetrics.registerFont(pdfmetrics.Font(alias,face.name,'WinAnsiEncoding'))
        records.append({'alias':alias,'face':face.name,'afm':str(afm),'afm_sha256':sha(afm),'pfb':str(pfb),'pfb_sha256':sha(pfb)})
    pdfmetrics.registerFontFamily('CoreSerif',normal='CoreSerif',bold='CoreBold',italic='CoreItalic',boldItalic='CoreBoldItalic')
    pdfmetrics.registerFontFamily('CoreSans',normal='CoreSans',bold='CoreSansBold',italic='CoreSans',boldItalic='CoreSansBold')
    return records


def para(c,body,x,y,width=WIDTH,size=11.4,lead=16.2,font='CoreSerif',color=INK,min_y=62):
    st=ParagraphStyle('p',fontName=font,fontSize=size,leading=lead,textColor=C(color),splitLongWords=True,allowWidows=0,allowOrphans=0)
    p=Paragraph(body,st);_,height=p.wrap(width,1200)
    if y-height<min_y: raise ValueError(f'Editorial page overflow: bottom={y-height:.2f}, text={body[:120]}')
    p.drawOn(c,x,y-height);return y-height

def tracked(c,label,x,y,size=8,font='CoreSans',color=ACCENT,space=1.4):
    c.saveState();t=c.beginText(x,y);t.setFont(font,size);t.setFillColor(C(color));t.setCharSpace(space);t.textOut(clean(label));c.drawText(t);c.restoreState()

def rule(c,x,y,width=WIDTH,color=RULE,lw=.35):
    c.saveState();c.setStrokeColor(C(color));c.setLineWidth(lw);c.line(x,y,x+width,y);c.restoreState()

def front_folio(c,number,heading=''):
    if heading:
        tracked(c,'REALIZATION CALCULUS',LEFT,H-37,size=7,color=MUTED,space=1.05)
        c.setFillColor(C(MUTED));c.setFont('CoreSans',7.3);c.drawRightString(W-LEFT,H-37,heading)
    c.setFillColor(C(INK));c.setFont('CoreSerif',10);c.drawRightString(W-LEFT,28,roman(number))

def section_title(c,kicker,title):
    tracked(c,kicker,LEFT,H-86,size=8.2,space=1.35)
    y=para(c,text(title),LEFT,H-108,size=27,lead=33,color=PRIMARY)-18
    rule(c,LEFT,y,42,GOLD,.8)
    return y-25

def body_sections(c,y,sections,size=11.4,lead=16.2,gap=17):
    for heading,body in sections:
        if heading: y=para(c,text(heading),LEFT,y,size=12.2,lead=16,font='CoreBold',color=PRIMARY)-6
        y=para(c,text(body),LEFT,y,size=size,lead=lead)-gap
    return y

def draw_cover(c):
    c.setFillColor(C(PRIMARY));c.rect(0,0,W,H,fill=1,stroke=0)
    tracked(c,'THE CORE PAPERS',65,714,size=8.8,color=PALE,space=2)
    rule(c,65,681,42,GOLD,1.25)
    c.setFillColor(C(WHITE));c.setFont('CoreSerif',62);c.drawString(60,609,'Realization')
    c.setFont('CoreSerif',76);c.drawString(59,528,'Calculus')
    c.setFont('CoreSerif',23);c.drawString(65,462,'Projectors, Transfer')
    c.drawString(65,430,'and Arithmetic')
    rule(c,65,129,W-130,'#705D73',.45)
    c.setFillColor(C(WHITE));c.setFont('CoreSerif',14);c.drawString(65,94,'Komorebi P.')

def make_canvas(path):
    c=canvas.Canvas(str(path),pagesize=(W,H),pageCompression=1)
    c.setTitle(TITLE);c.setAuthor('Komorebi P.');c.setSubject(SUBTITLE)
    return c

def exceptions_for(parts):
    ans=[]
    for p in parts:
        for e in p['components']:
            if e.get('build_kind')!='source_retypeset':
                ans.append({'paper':p['paper'],'component':e['title'],'build_kind':e.get('build_kind','unspecified'),'id':e.get('id')})
    return ans

def exceptions_copy(exceptions):
    if not exceptions: return 'The treatments share a common reading layout. Their original PDFs remain available for comparison and citation.'
    groups={}
    for e in exceptions:
        titles=groups.setdefault(e['paper'],[])
        if e['component'] not in titles: titles.append(e['component'])
    def joined(items):
        if len(items)==1: return items[0]
        return ', '.join(items[:-1])+' and '+items[-1]
    entries=[f"Paper {paper} ({joined(titles)})" for paper,titles in groups.items()]
    return 'Original page layouts are retained in '+joined(entries)+'.'


def render(spec,out):
    parts=spec['parts']
    if spec.get('front_pages')!=12 or len(parts)!=12: raise ValueError('Expected twelve preliminary pages and twelve parts.')
    out.mkdir(parents=True,exist_ok=True)
    fonts=register_fonts(); links=[]; exceptions=exceptions_for(parts)
    c=make_canvas(out/'frontmatter.pdf')
    draw_cover(c);c.showPage()
    tracked(c,'THE CORE PAPERS',LEFT,714,size=8.5,space=1.9)
    y=para(c,'Realization<br/>Calculus',LEFT,633,size=46,lead=54,color=PRIMARY)-22
    y=para(c,'Projectors, Transfer<br/>and Arithmetic',LEFT,y,size=25,lead=33,color=PRIMARY)-22
    rule(c,LEFT,y,42,GOLD,.9)
    para(c,'Komorebi P.',LEFT,284,size=14,lead=19)
    para(c,'Mathematical treatments, visual studies<br/>and formal companions.',LEFT,215,size=11.4,lead=16.2,color=MUTED)
    front_folio(c,1);c.showPage()
    front_folio(c,2,'SCOPE');y=section_title(c,'SCOPE','Objects, operators and arithmetic')
    y=body_sections(c,y,[
      ('','Realization Calculus studies how mathematical objects are generated from seeds, resolved into packets and related by operators. The twelve core papers develop this language across linear and nonlinear constructions, signal analysis, dynamics and arithmetic.'),
      ('','Projectors specify the components retained in a description. Transfer records the action between components and the passage from one resolution to another. The resulting questions concern reconstruction, compatibility, analytic control and the additional structure required for a realization.'),
      ('','Each result is read with its stated hypotheses. Finite identities, analytic arguments and arithmetic constructions occupy different settings. The visual studies illustrate selected examples, while the formal companions identify the precise declarations and assumptions covered by their mathematical interfaces.'),
      ('','The final arithmetic realization theorems depend on specified inputs. Conjecture 66 in Paper XI remains open. Paper XII requires suitable residual and deformation data, patching and full support, a Hecke point over the same coefficient field with the required compatibility, classicality and an attached representation. The existence of these inputs is not a universal conclusion of the paper.'),
      ('','The collection presents the core sequence as a connected course of study. Its scope is the mathematics of these twelve papers, with the boundaries of each construction stated where they are used.')])
    c.showPage()
    front_folio(c,3,'INTRODUCTION');y=section_title(c,'INTRODUCTION','A route through the calculus')
    y=body_sections(c,y,[
      ('','A choice of resolution determines which components of an object are visible and how their interactions are represented. Across these papers, seed constructions, projectors and packet coordinates organize this passage between an object and its descriptions.'),
      ('','Three questions recur. Which objects can be generated from the available seeds? Which relations survive a change of resolution? What further hypotheses permit a compatible description to be realized in the intended analytic or arithmetic setting?'),
      ('','The Projector Resolved Seed Calculus establishes the initial constructions. The later papers develop multiresolution signal methods, transfer semigroups and memory, quantum dynamics, and packet operator algorithms. The final arithmetic treatments examine congruences, residual seeds, packet geometry and patching support.'),
      ('','The mathematical treatment in each part gives the principal argument. Visual studies supply examples and geometric interpretations. Formal and verification companions provide a route to exact hypotheses, source correspondences and the limits of formal coverage.'),
      ('','The papers may be read in sequence or approached through a particular construction. Part openings identify the constituent treatments and their scope. The contents and bookmarks connect these local routes to the whole collection.')])
    c.showPage()
    front_folio(c,4,'READING CONVENTIONS');y=section_title(c,'READING THE BOOK','References and conventions')
    sections=[
      ('Page numbers and references','Continuous page numbers and PDF bookmarks navigate this volume. Theorem, equation, figure and section numbers remain local to their named treatment. Page references marked frozen in an individual treatment refer to its original PDF, not to the page numbers of this volume.'),
      ('Mathematical and formal scope','Read every result with its stated domain and hypotheses. The formal companions identify their own coverage. Written proofs, formal declarations and finite computations retain the distinct roles assigned to them in each paper.'),
      ('Figures and examples','Figures illustrate the objects and parameter ranges described in their captions and surrounding text. Numerical examples support the stated comparisons within those ranges.'),
      ('Original PDFs','The original PDFs are supplied as attachments and in the accompanying folder frozen_readers. Attachment support varies by PDF viewer. Use these originals when following a reference to original pagination.'),
    ]
    y=body_sections(c,y,sections,size=11.15,lead=15.7,gap=15)
    ex=exceptions_copy(exceptions)
    y=para(c,'Original page layouts',LEFT,y,size=12.2,lead=16,font='CoreBold',color=PRIMARY)-6
    y=para(c,text(ex),LEFT,y,size=10.2 if len(ex)>650 else 11.15,lead=14.1 if len(ex)>650 else 15.7,min_y=61)
    c.showPage()
    for pair in range(6):
        physical=5+pair;subset=parts[2*pair:2*pair+2]
        front_folio(c,physical,'CONTENTS')
        y=section_title(c,'CONTENTS',f"Papers {subset[0]['paper']} and {subset[1]['paper']}")
        for p in subset:
            top=y
            heading=f"{p['paper']}  {p['title']}"
            y=para(c,text(heading),LEFT,y,width=WIDTH-36,size=12.6,lead=16.6,font='CoreBold',color=ACCENT)
            c.setFont('CoreSerif',11);c.setFillColor(C(ACCENT));c.drawRightString(W-LEFT,top-11,str(p['folio']))
            links.append({'page':physical,'rect':[LEFT,H-top-3,W-LEFT,H-y+2],'target':p['divider_index'],'kind':'contents_part'})
            y-=13
            for e in p['components']:
                top=y
                y=para(c,text(e['title']),LEFT+13,y,width=WIDTH-59,size=11.3,lead=14.6)
                c.setFont('CoreSerif',10.5);c.setFillColor(C(INK));c.drawRightString(W-LEFT,top-10.5,str(e['page_start']))
                if e.get('deck'):
                    y-=2;y=para(c,text(e['deck']),LEFT+13,y,width=WIDTH-59,size=8.6,lead=11.5,font='CoreSans',color=MUTED)
                links.append({'page':physical,'rect':[LEFT+9,H-top-3,W-LEFT,H-y+2],'target':e['index_start'],'kind':'contents_component'})
                y-=11
            y-=18
        c.showPage()
    front_folio(c,11,'RIGHTS AND SOURCES');y=section_title(c,'RIGHTS AND SOURCES','Use, attribution and sources')
    y=body_sections(c,y,[
      ('Original material','Original writing, figures and editable writing sources are licensed under Creative Commons Attribution 4.0 International. Original software and machine-readable material are licensed under the MIT License. The accompanying files contain the full license texts.'),
      ('Third-party material','Third-party sources, fonts and other incorporated material retain their own terms. Their notices accompany the collection and apply alongside the licenses for original material.'),
      ('Attribution','Komorebi P., Realization Calculus: Projectors, Transfer and Arithmetic. When citing an individual result, include its paper, named treatment and local result number.'),
      ('Sources and companions','The accompanying files preserve the original papers, editable source material and supporting references. The companions within each part describe the relationship between the written argument, formal sources and computational examples.'),
      ('Book design','The typographic format is adapted from Komorebi Physics. A plum palette, serif reading face and quiet sans-serif navigation give this collection its own visual identity.')])
    c.showPage();c.save()
    d=make_canvas(out/'part_leaves.pdf')
    for i,p in enumerate(parts):
        tracked(d,'PART '+p['paper'],LEFT,698,size=9,space=2.2)
        y=para(d,text(p['title']),LEFT,651,width=WIDTH-18,size=32,lead=39,color=PRIMARY)-17
        if p.get('subtitle'):
            y=para(d,text(p['subtitle']),LEFT,y,width=WIDTH-10,size=12,lead=17,font='CoreSans',color=MUTED)-19
        rule(d,LEFT,y,48,GOLD,.95);y-=26
        if p.get('description'):y=para(d,text(p['description']),LEFT,y,width=WIDTH-12,size=11.4,lead=16.2,color=MUTED)-25
        tracked(d,'IN THIS PART',LEFT,y,size=7.8,space=1.4);y-=22
        for e in p['components']:
            top=y;y=para(d,text(e['title']),LEFT,y,width=WIDTH-45,size=11.1,lead=15.1)
            d.setFont('CoreSerif',10.5);d.setFillColor(C(ACCENT));d.drawRightString(W-LEFT,top-10.5,str(e['page_start']))
            links.append({'page':p['divider_index'],'rect':[LEFT,H-top-3,W-LEFT,H-y+3],'target':e['index_start'],'kind':'part_component','part_leaf_index':i})
            y-=11
        if p.get('boundary'):
            y-=13;rule(d,LEFT,y,42,GOLD,.7);y-=17
            y=para(d,'Scope of this part',LEFT,y,size=10.4,lead=14,font='CoreSansBold',color=ACCENT)-5
            y=para(d,text(p['boundary']),LEFT,y,size=10.3,lead=14.4,color=MUTED,min_y=61)
        # The assembler owns all Arabic folios, including these divider leaves.
        d.showPage()
    d.save()
    (out/'outer_links.json').write_text(json.dumps(links,indent=2)+'\n')
    provenance={'schema':'komorebi.core.outer-font-provenance/1','fonts':fonts,'fallback_used':False,'standalone_font_files_packaged':False,'template':'Komorebi Physics publication design','reference_palette_replaced':True,'palette':{'primary':PRIMARY,'accent':ACCENT,'gold':GOLD,'ink':INK,'muted':MUTED,'pale':PALE,'rule':RULE}}
    (out/'outer_font_provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
    record={'schema':'komorebi.core.outer-build/1','front_pages':12,'part_leaves':12,'links':len(links),'source_spec_sha256':hashlib.sha256(json.dumps(spec,sort_keys=True).encode()).hexdigest(),'facsimile_exceptions':exceptions,'files':{},'bounds_failures':[],'missing_character_pages':[]}
    for name,n in [('frontmatter.pdf',12),('part_leaves.pdf',12)]:
        doc=fitz.open(out/name)
        if len(doc)!=n:raise AssertionError((name,len(doc),n))
        for i,page in enumerate(doc):
            raw=page.get_text('dict')
            for b in raw['blocks']:
                for l in b.get('lines',[]):
                    for s in l['spans']:
                        r=fitz.Rect(s['bbox'])
                        if r.x0<-.1 or r.y0<-.1 or r.x1>W+.1 or r.y1>H+.1:record['bounds_failures'].append({'file':name,'page':i+1,'bbox':list(r),'text':s['text']})
            if '\ufffd' in page.get_text():record['missing_character_pages'].append({'file':name,'page':i+1})
        record['files'][name]={'pages':len(doc),'sha256':sha(out/name)}
    (out/'outer_build.json').write_text(json.dumps(record,indent=2)+'\n')
    if record['bounds_failures'] or record['missing_character_pages']:raise ValueError('Outer document structural checks failed')
    return record

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--spec',type=Path,default=ROOT/'book/build_spec.json');ap.add_argument('--output-dir',type=Path,default=ROOT/'book');a=ap.parse_args()
    print(json.dumps(render(json.loads(a.spec.read_text()),a.output_dir),indent=2))
