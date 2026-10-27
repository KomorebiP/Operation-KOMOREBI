#!/usr/bin/env python3
"""Render the cohesive Realization Calculus book furniture.

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
INK='#22282C'; MUTED='#615963'; PALE='#E8DDE8'; RULE='#D9CDD7'; WHITE='#FFFFFF'
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

def get_label(e): return e.get('label',e.get('title',''))
def get_target(e):
    for k in ['target','book_index','index_start','divider_index']:
        if e.get(k) is not None:return int(e[k])
    return None

def get_folio(e):
    for k in ['folio','page_start','page']:
        if e.get(k) is not None:return str(e[k])
    return ''

def pdf_record(path):
    doc=fitz.open(path);fail=[];bad=[]
    for i,page in enumerate(doc):
        for b in page.get_text('dict')['blocks']:
            for l in b.get('lines',[]):
                for s in l['spans']:
                    r=fitz.Rect(s['bbox'])
                    if r.x0<-.1 or r.y0<-.1 or r.x1>W+.1 or r.y1>H+.1:fail.append({'page':i+1,'bbox':list(r),'text':s['text']})
        if '\ufffd' in page.get_text():bad.append(i+1)
    return {'pages':len(doc),'sha256':sha(path),'bounds_failures':fail,'missing_character_pages':bad}

def item(c,e,y,links,page,x=LEFT,width=WIDTH,size=11.4,lead=15.5,deck_size=9.1,gap=12):
    top=y;folio=get_folio(e);measure=width-42 if folio else width
    y=para(c,text(get_label(e)),x,y,width=measure,size=size,lead=lead)
    if folio:
        c.setFillColor(C(ACCENT));c.setFont('CoreSerif',10.5);c.drawRightString(x+width,top-10.5,folio)
    if e.get('deck'):
        y-=3;y=para(c,text(e['deck']),x,y,width=measure,size=deck_size,lead=deck_size+3.2,font='CoreSans',color=MUTED)
    target=get_target(e)
    if target is not None:links.append({'page':page,'rect':[x,H-top-3,x+width,H-y+2],'target':target,'kind':'editorial_navigation'})
    return y-gap


def fallback_front(spec,leaves):
    result={'chapters':[],'formal':[],'studies':[]}
    for leaf in leaves:
        kind=leaf['kind'];e={'label':leaf.get('title',''),'target':leaf['book_index'],'folio':leaf['folio'],'deck':leaf.get('subtitle','')}
        if kind=='chapter':
            e['label']=leaf.get('paper','')+'  '+e['label'];result['chapters'].append(e)
        elif kind=='formal_companion':
            e['label']=leaf.get('paper','')+'  '+e['label'];result['formal'].append(e)
        elif kind in ('study','studies_division','glossary'):result['studies'].append(e)
    return result


def frontmatter(spec,out,links):
    leaves=spec['leaves'];contents=fallback_front(spec,leaves)
    contents.update(spec.get('front_contents',{}))
    # A glossary entry may be supplied separately from further studies.
    if contents.get('glossary'):
        g=contents['glossary'];g=[g] if isinstance(g,dict) else g
        contents['studies']=list(contents.get('studies',[]))+g
    chapters=contents['chapters'];formal=contents.get('formal',[]);studies=contents.get('studies',[])
    if len(chapters)!=12:raise ValueError('Expected twelve main-chapter contents entries.')
    c=make_canvas(out/'frontmatter.pdf');draw_cover(c);c.showPage()
    tracked(c,'THE CORE PAPERS',LEFT,714,size=8.5,space=1.9)
    y=para(c,'Realization<br/>Calculus',LEFT,633,size=46,lead=54,color=PRIMARY)-22
    y=para(c,'Projectors, Transfer<br/>and Arithmetic',LEFT,y,size=25,lead=33,color=PRIMARY)-22
    rule(c,LEFT,y,42,GOLD,.9)
    para(c,'Komorebi P.',LEFT,284,size=14,lead=19)
    para(c,'A mathematical monograph in twelve chapters.',LEFT,215,size=11.4,lead=16.2,color=MUTED)
    front_folio(c,1);c.showPage()
    front_folio(c,2,'INTRODUCTION');y=section_title(c,'INTRODUCTION','Objects, operators and arithmetic')
    y=body_sections(c,y,[
      ('','Realization Calculus studies how mathematical objects are generated from seeds, resolved into packets and related by operators. Projectors specify the components retained in a description. Transfer records their interaction and the passage from one resolution to another.'),
      ('','The first four chapters develop the Projector Resolved Seed Calculus. The argument then moves through multiresolution signals, evolution and memory, quantum dynamics and packet operator algorithms. The final chapters examine congruences, residual seeds, packet geometry and patching support.'),
      ('','Three questions recur. Which objects can be generated from the available seeds? Which relations survive a change of resolution? What additional hypotheses permit a compatible description to be realized in the intended analytic or arithmetic setting? Each construction is read with its own domain and assumptions.'),
      ('','The arithmetic conclusions retain their conditional character. Conjecture 66 in Chapter XI remains open. Chapter XII requires suitable residual and deformation data, patching and full support, a compatible Hecke point over the same coefficient field, classicality and an attached representation. A universal supply of these inputs is not a conclusion of the chapter.'),
      ('','The mathematical text and visual studies form the main sequence. The formal companions follow the twelve chapters, and the glossary provides a route back to the principal definitions.')])
    c.showPage()
    front_folio(c,3,'READING MAP');y=section_title(c,'READING MAP','Following the argument')
    y=body_sections(c,y,[
      ('The main sequence','Read Chapters I-XII in order for the development from seed constructions to conditional arithmetic realization. Each chapter opening connects its subject to the surrounding chapters and identifies the mathematical text and visual studies that follow.'),
      ('Visual studies','The visual material stays with the chapter whose objects it illustrates. Figures and examples retain their stated inputs and ranges. A chapter identifier accompanies a global plate reference, as in Plate VIII.32.'),
      ('Formal companions','The Lean guides are collected at the back. They identify the statements, hypotheses and source correspondences in their own formal scope. The machine-native treatment of Chapter I appears with its formal companion.'),
      ('Further studies and glossary','Further studies retain their own hypotheses and open questions. The glossary gives short definitions with links to the relevant treatment. The definitions and assumptions in each chapter take precedence over those summaries.')])
    y-=5
    routes=[]
    for label,es in [('Begin with Chapter I',chapters[:1]),('Open the formal companions',formal[:1])]:
        if es:routes.append({'label':label,'target':get_target(es[0]),'folio':get_folio(es[0])})
    glossary=[e for e in studies if 'glossary' in get_label(e).lower()]
    if glossary:routes.append({'label':'Open the glossary','target':get_target(glossary[0]),'folio':get_folio(glossary[0])})
    for e in routes:y=item(c,e,y,links,3,size=10.7,lead=14.5,gap=8)
    c.showPage()
    front_folio(c,4,'NOTATION AND REFERENCES');y=section_title(c,'NOTATION AND REFERENCES','Conventions across the book')
    y=body_sections(c,y,[
      ('Local notation','Each chapter specifies its ambient spaces, scalar fields, domains and index sets. A symbol reused elsewhere need not denote the same object. Read every operator with its stated domain and codomain.'),
      ('Finite and infinite settings','Finite algebra, limits and infinite-dimensional constructions have different assumptions. A formal identity does not by itself extend an operator to a larger space or supply continuity. The passage between settings is made where the text provides it.'),
      ('Exact and numerical statements','Exact identities and numerical examples retain their stated roles. Numerical illustrations support the specified comparisons within their parameter ranges.'),
      ('References within the volume','Continuous page numbers and PDF bookmarks navigate this book. Theorem, equation, figure and section numbers remain local to their named treatment unless a chapter prefix is given. Cite the chapter and treatment with the local number.'),
      ('References to original pages','Page references marked frozen in an individual treatment refer to its original PDF. The original PDFs are supplied as attachments and in the accompanying folder frozen_readers. Attachment support varies by viewer.')],size=11.1,lead=15.7,gap=16)
    c.showPage()
    for page,entries,label in [(5,chapters[:6],'Chapters I-VI'),(6,chapters[6:],'Chapters VII-XII')]:
        front_folio(c,page,'CONTENTS');y=section_title(c,'CONTENTS',label)
        for e in entries:y=item(c,e,y,links,page,size=13.2,lead=17.2,deck_size=9.4,gap=22)
        c.showPage()
    front_folio(c,7,'CONTENTS');y=section_title(c,'CONTENTS','Further studies and reference')
    if studies:
        for e in studies:y=item(c,e,y,links,7,size=12.2,lead=16.2,deck_size=9.2,gap=18)
    else:y=para(c,'The formal companions complete the reading sequence. Use the glossary to return to the principal definitions.',LEFT,y)-20
    y-=8;rule(c,LEFT,y,42,GOLD,.8);y-=23
    y=body_sections(c,y,[
      ('The scope of the companions','A written proof, a formal declaration and a finite computation answer different questions. The companions state their own coverage and the assumptions on which it depends.'),
      ('Using the glossary','The glossary is a navigation aid. Its definitions are intentionally brief, and its references lead to the fuller statements and hypotheses in the text.')],size=11.15,lead=15.8)
    c.showPage()
    front_folio(c,8,'CONTENTS');y=section_title(c,'CONTENTS','Formal companions')
    for e in formal:y=item(c,e,y,links,8,size=10.9,lead=14.2,deck_size=8.5,gap=10)
    c.showPage()
    front_folio(c,9,'RIGHTS AND SOURCES');y=section_title(c,'RIGHTS AND SOURCES','Use, attribution and sources')
    body_sections(c,y,[
      ('Original material','Original writing, figures and editable writing sources are licensed under Creative Commons Attribution 4.0 International. Original software and machine-readable material are licensed under the MIT License. The accompanying files contain the full license texts.'),
      ('Third-party material','Third-party sources, fonts and other incorporated material retain their own terms. Their notices accompany the collection and apply alongside the licenses for original material.'),
      ('Attribution','Komorebi P., Realization Calculus: Projectors, Transfer and Arithmetic. When citing an individual result, include its chapter, named treatment and local result number.'),
      ('Sources and companions','The accompanying files preserve the original papers, editable source material and supporting references. Each formal companion describes the relationship between the written argument, formal sources and computational examples.'),
      ('Book design','The typographic format is adapted from Komorebi Physics. A plum palette, serif reading face and restrained navigation give this volume its own visual identity.')])
    c.showPage();c.save()


def leaf_pages(spec,out,links):
    c=make_canvas(out/'leaves.pdf');records=[]
    bridgefile=ROOT/'editorial/book_revision/design_reading_bridges.json'
    bridges=json.loads(bridgefile.read_text()).get('chapters',{}) if bridgefile.exists() else {}
    for i,l in enumerate(spec['leaves']):
        kind=l['kind'];paper=str(l.get('paper',''));page=int(l['book_index'])
        kicker={'chapter':'CHAPTER '+paper,'formal_division':'FORMAL COMPANIONS','formal_companion':'FORMAL COMPANION '+paper,'studies_division':'FURTHER STUDIES','study':'FURTHER STUDY','glossary':'REFERENCE'}.get(kind,kind.upper().replace('_',' '))
        tracked(c,kicker,LEFT,700,size=8.8,space=1.8)
        leaf_title=re.sub(r' (I|II|III|IV|V|VI|VII|VIII|IX|X|XI|XII)$',r'&nbsp;\1',text(l['title']))
        y=para(c,leaf_title,LEFT,653,width=WIDTH-12,size=32,lead=39,color=PRIMARY)-16
        if l.get('subtitle'):y=para(c,text(l['subtitle']),LEFT,y,width=WIDTH-10,size=11.6,lead=16.5,font='CoreSans',color=MUTED)-18
        rule(c,LEFT,y,48,GOLD,.9);y-=26
        before=l.get('bridge_before',bridges.get(paper,{}).get('bridge_before','') if kind=='chapter' else '')
        intro=l.get('intro',l.get('description',''))
        if before:y=para(c,text(before),LEFT,y,width=WIDTH-10,size=10.8,lead=15.3,font='CoreItalic',color=MUTED)-15
        if intro:y=para(c,text(intro),LEFT,y,width=WIDTH-10,size=11.4,lead=16.2)-22
        entries=l.get('entries',[])
        if entries:
            heading='IN THIS CHAPTER' if kind=='chapter' else 'IN THIS COMPANION' if kind=='formal_companion' else 'BROWSE ALPHABETICALLY' if kind=='glossary' else 'READING ROUTES'
            tracked(c,heading,LEFT,y,size=7.8,space=1.3);y-=21
            if kind=='glossary':
                cell=(WIDTH-40)/3
                for start in range(0,len(entries),3):
                    bottoms=[]
                    for col,e in enumerate(entries[start:start+3]):bottoms.append(item(c,e,y,links,page,x=LEFT+col*(cell+20),width=cell,size=10.9,lead=14.7,gap=11))
                    y=min(bottoms)
            else:
                for e in entries:y=item(c,e,y,links,page,size=10.9,lead=14.7,deck_size=8.5,gap=8)
        if l.get('scope') or l.get('boundary'):
            y-=9;rule(c,LEFT,y,42,GOLD,.7);y-=17
            y=para(c,'Scope',LEFT,y,size=10.4,lead=14,font='CoreSansBold',color=ACCENT)-5
            y=para(c,text(l.get('scope',l.get('boundary',''))),LEFT,y,size=10.4,lead=14.5,color=MUTED)-16
        after=l.get('bridge_after',bridges.get(paper,{}).get('bridge_after','') if kind=='chapter' else '')
        if after:
            y=para(c,text(after),LEFT,y,size=10.8,lead=15.3,color=MUTED)-15
        if l.get('companion_target') is not None:
            e={'label':l.get('companion_label','Formal companion for Chapter '+paper),'target':l['companion_target'],'folio':l.get('companion_folio','')}
            y=item(c,e,y,links,page,size=10.5,lead=14.4,gap=8)
        for e in l.get('related_routes',[]):y=item(c,e,y,links,page,size=10.5,lead=14.4,gap=8)
        if l.get('return_target') is not None:
            e={'label':l.get('return_label','Return to Chapter '+paper),'target':l['return_target'],'folio':l.get('return_folio','')}
            y=item(c,e,y,links,page,size=10.5,lead=14.4,gap=8)
        records.append({'id':l['id'],'kind':kind,'leaf_pdf_page':i,'book_index':page,'folio':l['folio'],'content_bottom':y})
        # Global folios and running furniture belong to the assembler.
        c.showPage()
    c.save();(out/'leaf_map.json').write_text(json.dumps(records,indent=2)+'\n')


def render(spec,out):
    if spec.get('front_pages')!=10:raise ValueError('The book renderer requires ten preliminary pages.')
    if len([l for l in spec['leaves'] if l['kind']=='chapter'])!=12:raise ValueError('Expected twelve chapter leaves.')
    out.mkdir(parents=True,exist_ok=True);fonts=register_fonts();links=[]
    frontmatter(spec,out,links);leaf_pages(spec,out,links)
    (out/'outer_links.json').write_text(json.dumps(links,indent=2)+'\n')
    provenance={'schema':'realization-calculus.outer-fonts/2','fonts':fonts,'fallback_used':False,'standalone_font_files_packaged':False,'palette':{'primary':PRIMARY,'accent':ACCENT,'gold':GOLD}}
    (out/'outer_font_provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
    record={'schema':'realization-calculus.book-matter/2','front_pages':10,'leaves':len(spec['leaves']),'links':len(links),'files':{n:pdf_record(out/n) for n in ['frontmatter.pdf','leaves.pdf']}}
    if record['files']['frontmatter.pdf']['pages']!=10:raise ValueError('Unexpected front matter count')
    (out/'outer_build.json').write_text(json.dumps(record,indent=2)+'\n')
    if any(r['bounds_failures'] or r['missing_character_pages'] for r in record['files'].values()):raise ValueError('Outer pages failed structural checks')
    return record

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--spec',type=Path,default=ROOT/'book/build_spec.json');ap.add_argument('--output-dir',type=Path,default=ROOT/'book');a=ap.parse_args()
    print(json.dumps(render(json.loads(a.spec.read_text()),a.output_dir),indent=2))
