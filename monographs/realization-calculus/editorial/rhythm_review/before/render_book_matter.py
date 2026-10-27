#!/usr/bin/env python3
"""Render a linked glossary before global pagination is assigned.

The assembler resolves the semantic reference records in glossary_links.json.
No mathematical claim, source reference or page target is invented here.
"""
from pathlib import Path
import argparse,hashlib,json,re,unicodedata
from xml.sax.saxutils import escape
import fitz
from reportlab.pdfgen import canvas
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from render_outer import W,H,LEFT,WIDTH,PRIMARY,ACCENT,GOLD,INK,MUTED,ROOT,C,text,clean,register_fonts,tracked,rule,para,pdf_record


def validate_text(s):
    try:clean(s).encode('cp1252')
    except UnicodeEncodeError as e:raise ValueError(f'Glossary text needs explicit mathematical typography: {s!r}') from e

def height(body,width=WIDTH,size=11,lead=15.4,font='CoreSerif'):
    p=Paragraph(text(body),ParagraphStyle('m',fontName=font,fontSize=size,leading=lead));return p.wrap(width,1200)[1]

def ref_label(ref):
    if ref.get('label'):return str(ref['label'])
    cid=ref.get('component_id','');paper=ref.get('paper',cid.split('_')[0] if cid else '')
    section=str(ref.get('section','')).strip()
    prefix='Chapter '+str(paper) if paper else 'Source treatment'
    if section:return prefix+', '+section
    return prefix


def render_glossary(data,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);register_fonts()
    terms=data.get('terms',data.get('entries',[])) if isinstance(data,dict) else data
    if not terms:raise ValueError('Glossary has no terms')
    terms=sorted(terms,key=lambda t:unicodedata.normalize('NFKD',str(t.get('term',t.get('name','')))).casefold())
    names={str(t.get('term',t.get('name',''))):f'glossary_term_{i:04d}' for i,t in enumerate(terms)}
    if len(names)!=len(terms):raise ValueError('Duplicate glossary term names')
    for t in terms:
        for s in [t.get('term',t.get('name','')),t.get('definition',t.get('description',''))]:validate_text(s)
        for ref in t.get('refs',t.get('references',[])):validate_text(ref_label(ref))
        for related in t.get('see_also',[]):
            validate_text(related)
            if related not in names:raise ValueError(f'Unknown glossary cross-reference: {related}')
    c=canvas.Canvas(str(out/'glossary.pdf'),pagesize=(W,H),pageCompression=1)
    c.setTitle('Realization Calculus: Glossary');c.setAuthor('Komorebi P.')
    page=0;y=H-69;links=[];term_map=[];letter_starts={};last_letter=None;have_page=False
    def next_page():
        nonlocal page,y,have_page
        if have_page:c.showPage();page+=1
        have_page=True;y=H-69
        # Furniture and global folios are supplied by the assembler.
    next_page()
    for n,t in enumerate(terms):
        name=str(t.get('term',t.get('name','')));definition=str(t.get('definition',t.get('description','')))
        refs=t.get('refs',t.get('references',[]));ident=t.get('id',str(n+1));related=t.get('see_also',[])
        related_html='See also: '+', '.join(f'<link href="#{names[v]}" color="{ACCENT}">{text(v)}</link>' for v in related) if related else ''
        related_height=Paragraph(related_html,ParagraphStyle('rel',fontName='CoreSans',fontSize=9.3,leading=12.4)).wrap(WIDTH-12,1200)[1] if related else 0
        letter=next((x.upper() for x in name if x.isalpha()),'#')
        letter=letter if 'A'<=letter<='Z' else '#'
        needed=height(name,size=12.4,lead=16.4,font='CoreBold')+5+height(definition)+7
        needed+=sum(height(ref_label(ref),size=9.3,lead=12.4,font='CoreSans')+3 for ref in refs)+17
        if related:needed+=related_height+6
        if letter!=last_letter:needed+=29
        if needed>H-69-64:raise ValueError(f'Glossary entry too long for one page: {name}')
        if y-needed<64:next_page()
        if letter!=last_letter:
            if letter not in letter_starts:letter_starts[letter]=page
            tracked(c,letter,LEFT,y,size=9,space=1.5);rule(c,LEFT+24,y+2,WIDTH-24,GOLD,.45);y-=26;last_letter=letter
        top=y;c.bookmarkHorizontalAbsolute(names[name],top)
        y=para(c,text(name),LEFT,y,size=12.4,lead=16.4,font='CoreBold',color=PRIMARY)-5
        y=para(c,text(definition),LEFT,y,size=11,lead=15.4)-7
        term_map.append({'id':ident,'term':name,'page':page,'rect':[LEFT,H-top,LEFT+WIDTH,H-y],'references':refs})
        for ref in refs:
            rtop=y;label=ref_label(ref);y=para(c,text(label),LEFT+12,y,width=WIDTH-12,size=9.3,lead=12.4,font='CoreSans',color=ACCENT)
            # ReportLab coordinates are bottom-origin; PyMuPDF rectangles are top-origin.
            links.append({**ref,'page':page,'rect':[LEFT+10,H-rtop-2,LEFT+WIDTH,H-y+2],'label':label,'kind':'glossary_reference'})
            y-=3
        if related:
            y-=3;y=para(c,related_html,LEFT+12,y,width=WIDTH-12,size=9.3,lead=12.4,font='CoreSans',color=MUTED)-3
        y-=17
    c.showPage();c.save()
    with fitz.open(out/'glossary.pdf') as gd:
        for i,gp in enumerate(gd):
            for lk in gp.get_links():
                if lk['kind']!=fitz.LINK_GOTO or lk.get('page',-1)<0:raise ValueError('Unexpected glossary cross-reference kind')
                links.append({'kind':'glossary_see_also','page':i,'rect':list(lk['from']),'target_glossary_page':lk['page'],'target_point':list(lk.get('to',(0,0)))})
    record={'schema':'realization-calculus.glossary-layout/1','terms':len(terms),'pages':page+1,'links':len(links),'letter_starts':letter_starts,'pdf':pdf_record(out/'glossary.pdf')}
    (out/'glossary_links.json').write_text(json.dumps(links,indent=2,ensure_ascii=False)+'\n')
    (out/'glossary_term_map.json').write_text(json.dumps(term_map,indent=2,ensure_ascii=False)+'\n')
    (out/'glossary_layout.json').write_text(json.dumps(record,indent=2)+'\n')
    if record['pdf']['bounds_failures'] or record['pdf']['missing_character_pages']:raise ValueError('Glossary structural check failed')
    return record

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--data',type=Path,default=ROOT/'editorial/book_revision/glossary.json');ap.add_argument('--output-dir',type=Path,default=ROOT/'book');a=ap.parse_args()
    print(json.dumps(render_glossary(json.loads(a.data.read_text()),a.output_dir),indent=2))
