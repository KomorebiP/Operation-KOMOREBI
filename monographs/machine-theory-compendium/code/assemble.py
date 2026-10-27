#!/usr/bin/env python3
"""Assemble the selected, unchanged source pages and the connected synthesis.

No source manuscript is reflowed or stamped. PDF entry cards, page labels, a
page map, bookmarks and cross-document links are added around the source pages.
Requires PyMuPDF and ReportLab. Fonts are system dependencies, not redistributed.
"""
from __future__ import annotations
import csv, hashlib, html, json
from collections import Counter
from pathlib import Path
import fitz
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'readers'
NAV = ROOT / 'validation' / 'generated_navigation'
TITLE = 'Machine-Native Reasoning'
SUBTITLE = 'Representation, Learning, and Computational Organization'
MASTER = 'Komorebi_Machine_Theory_Compendium_v1.0.0.pdf'
GROUPS = {
 'core': ('I', 'Core Machine Theory', 'Evidence, understanding, signal models, executable semantics, inference, discovery and institutions.'),
 'foundations': ('II', 'Mathematical and Architectural Foundations', 'Representation calculus, nonlinear inference, shared workspaces, complexity, structured execution and preservation.'),
 'companions': ('III', 'Formal, Visual and Lineage Companions', 'Source-level formal guides, Python visual explanations, continuity protocols and the extended historical recursive theory.')
}
RELATED = {
 'GA':['MU','LSM','SR','PRIQ'], 'MU':['GA','OSL','PPT','SII'],
 'LSM':['GA','PRIQ','NEU','PRISM'], 'OSL':['NEU','MU','AVOC','SII'],
 'NEU':['OSL','LSM','SRWT'], 'CBI':['GA','AVOC','CBL','PRIQ'],
 'AVOC':['CBI','OSL','AVL','MS'], 'PPT':['MU','SII','KPP'],
 'SII':['MU','OSL','PPT','SRIC'], 'MS':['SRWT','AVOC','SII','PCL'],
 'SU':['SR','LSM','SRWT'], 'SR':['GA','MU','LSM'],
 'PRIQ':['LSM','GA','CBI'], 'SRWT':['MS','NEU','SU'],
 'CIR':['SII','PRISM','SU'], 'PRISM':['LSM','CIR','OSL'],
 'KPP':['PPT','SII','PCL'], 'AVL':['AVOC','CBI'], 'CBL':['CBI','AVOC'],
 'SIV':['SII','AD'], 'AD':['SII','MS','SIV'], 'LSV':['LSM','PRIQ'],
 'PCL':['KPP','MS','SRWT'], 'SRIC':['SII','SRWT','NEU']
}
FONTDIR = Path('/usr/share/fonts/truetype/dejavu')
for name, filename in [('NavSans','DejaVuSans.ttf'),('NavBold','DejaVuSans-Bold.ttf'),('NavSerif','DejaVuSerif.ttf')]:
    path=FONTDIR/filename
    if not path.exists():
        raise FileNotFoundError(f'Missing system font {path}. Install DejaVu fonts. Font files are not shipped.')
    pdfmetrics.registerFont(TTFont(name,str(path)))
W,H=612,792
INK=HexColor('#203D37'); MUTED=HexColor('#566660'); PALE=HexColor('#F4F3ED'); LINE=HexColor('#C8D1CC')
STYLES={
 'body':ParagraphStyle('body',fontName='NavSerif',fontSize=10.7,leading=16,textColor=INK),
 'small':ParagraphStyle('small',fontName='NavSans',fontSize=8.7,leading=13,textColor=MUTED),
 'title':ParagraphStyle('title',fontName='NavBold',fontSize=27,leading=33,textColor=INK),
 'h2':ParagraphStyle('h2',fontName='NavBold',fontSize=16,leading=21,textColor=INK),
 'label':ParagraphStyle('label',fontName='NavBold',fontSize=9,leading=13,textColor=INK),
 'toc':ParagraphStyle('toc',fontName='NavBold',fontSize=10.3,leading=14,textColor=INK)
}

def digest(p:Path)->str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

class PageWriter:
    def __init__(self,path:Path):
        self.path=path
        self.c=canvas.Canvas(str(path),pagesize=(W,H),invariant=1,pageCompression=1)
        self.c.setTitle(TITLE+' | collection navigation'); self.c.setAuthor('Komorebi P.')
        self.page=0; self.links=[]; self.headings=[]
    def start(self,label:str,heading:str|None=None):
        c=self.c;c.setFillColor(PALE);c.rect(0,0,W,H,fill=1,stroke=0)
        c.setFillColor(INK);c.rect(0,0,9,H,fill=1,stroke=0)
        c.setFont('NavBold',8.5);c.drawString(48,H-40,'OPERATION KOMOREBI')
        c.setFont('NavSans',8);c.drawRightString(W-48,H-40,label.upper())
        c.setStrokeColor(LINE);c.line(48,55,W-48,55)
        c.setFont('NavSans',8);c.setFillColor(MUTED);c.drawString(48,37,'Collection edition 1.0.0  /  9 October 2026')
        c.drawRightString(W-48,37,'Komorebi P.')
        if heading:self.headings.append((self.page,heading))
    def para(self,text,x=48,y=H-88,width=W-96,style='body'):
        p=Paragraph(text,STYLES[style]);_,height=p.wrap(width,H)
        if y-height<70: raise ValueError(f'Navigation overflow: {self.path.name}, page {self.page+1}, {text[:75]}')
        p.drawOn(self.c,x,y-height);return y-height
    def target(self,target:str,rect):
        x0,y0,x1,y1=rect
        self.links.append({'page':self.page,'rect':[x0,H-y1,x1,H-y0],'target':target})
    def finish(self):self.c.showPage();self.page+=1
    def save(self):self.c.save();return {'path':str(self.path.relative_to(ROOT)),'pages':self.page,'links':self.links,'headings':self.headings}

def cover(w:PageWriter,group:str|None,docs,syn_pages):
    w.start('Connected source compilation',TITLE)
    y=w.para('Machine-Native<br/>Reasoning',y=H-142,style='title')-22
    y=w.para('Representation, Learning,<br/>and Computational Organization',y=y,style='h2')-28
    if group:
        y=w.para('VOLUME '+GROUPS[group][0]+'<br/>'+GROUPS[group][1],y=y,style='label')-20
    else:y=w.para('THE COMPLETE SELECTED READER',y=y,style='label')-20
    y=w.para('A connected compilation of the machine-related<br/>and theoretical computer science program.',y=y)-25
    s=sum(d['pages'] for d in docs)
    y=w.para(f'{len(docs)} source documents  ·  {s:,} original source pages'+(f'<br/>{syn_pages}-page connected synthesis' if syn_pages else ''),y=y,style='small')
    w.para('The interfaces matter as much as the components.',y=230,style='h2')
    w.para('Read the organizing argument, follow the connections, and return to the preserved proofs. Source editions retain their own assumptions, evidence and limits.',y=187)
    w.finish()

def contents(w,docs,offsets,label):
    w.start('Source directory',label)
    y=w.para(label,y=H-85,style='h2')-24
    for s in docs:
        top=y
        dest=offsets[s['code']]['source_start']
        y=w.para(f"{s['code']}  /  {html.escape(s['title'])}",y=y,width=426,style='toc')-3
        y=w.para(f"{html.escape(s['edition'])}  ·  {s['pages']} source pages",y=y,width=426,style='small')-14
        w.c.setFont('NavSans',9);w.c.setFillColor(INK);w.c.drawRightString(564,top-12,str(dest))
        w.target(s['code'],(48,y+10,564,top+3))
    w.para('Numbers at right are physical pages in this reader. Click an entry to open its source card. Original source pagination remains visible.',y=100,style='small')
    w.finish()

def scope(w):
    w.start('Editorial and evidence boundary','What has been assembled')
    y=w.para('What this collection establishes',y=H-85,style='h2')-22
    blocks=[
    ('Connected, not conflated','The new synthesis maps relationships among the source works. Exact mathematical interfaces, conditional compositions, implementation gaps and proposed architectures remain different kinds of connection.'),
    ('Preserved full texts','Every selected PDF appears unabridged. Its pages, theorem numbering, evidence classifications and historical sections are retained. An older experimental section is not new evidence for the complete architecture.'),
    ('Theory is the principal product','No new training campaign, broad agent implementation, hardware experiment or corpus-wide Lean run is claimed. Small exact checks cover the newly written connecting example only.'),
    ('A selected corpus, not every archive','The collection includes the listed twenty-four PDFs and six earlier complete source archives. Typed Proof Learner and Resolution Completion are represented by a recovered handoff note. Other unresolved source branches are listed in the package rather than silently claimed included.'),
    ('Independent identities and permissions','Source versions and rights are retained independently. This compilation does not relicense the source works or establish a public repository release. A manuscript proof, a runtime test, an archived kernel record and an external empirical result are not interchangeable.'),
    ]
    for head,body in blocks:
        y=w.para(html.escape(head),y=y,style='label')-4
        y=w.para(html.escape(body),y=y)-17
    w.finish()

def orientation(w,offsets,syn_start,syn_pages):
    w.start('Reading routes','How the collection fits together')
    y=w.para('One argument. Three depths of reading.',y=H-85,style='h2')-24
    y=w.para(f'Begin with the <b>connected synthesis</b> on physical page {syn_start}. It supplies the common vocabulary, four connecting results, a sixteen-interface register and one exact example that follows observation through action, correction, communication and revision.',y=y)-22
    w.target('SYN',(48,y+17,564,H-132))
    for g,(roman,title,description) in GROUPS.items():
        pg=offsets['GROUP:'+g]['entry']
        top=y
        y=w.para(f'{roman}  /  {html.escape(title)}',y=y,style='label')-4
        y=w.para(html.escape(description)+f' <b>Starts on page {pg}.</b>',y=y)-22
        w.target('GROUP:'+g,(48,y+17,564,top+3))
    y=w.para('The conceptual route',y=y,style='h2')-10
    y=w.para('Evidence → representation → executable method → correction → discovery → shared work → accountable institutions.',y=y)-16
    w.para('The companion volumes in the ZIP make the same sources easier to navigate on smaller devices. The package also contains the standalone synthesis, preserved source PDFs, original archives, an offline index and exact page maps.',y=y,style='small')
    w.finish()

def front(path,docs,offsets,group,syn_start,syn_pages):
    w=PageWriter(path);cover(w,group,docs,syn_pages)
    if group is None:
        orientation(w,offsets,syn_start,syn_pages)
        for g in GROUPS:contents(w,[d for d in docs if d['group']==g],offsets,GROUPS[g][1])
    else:contents(w,docs,offsets,GROUPS[group][1])
    scope(w);return w.save()

def groupcard(path,g):
    w=PageWriter(path);roman,title,desc=GROUPS[g]
    w.start('Part '+roman,title)
    w.para('PART '+roman,y=H-150,style='label')
    y=w.para(html.escape(title),y=H-195,style='title')-32
    y=w.para(html.escape(desc),y=y)-35
    w.para('Source-entry cards explain the role and boundary of each selected work. The original document follows immediately after its card, without reflow or renumbering of its statements.',y=y)
    w.para('The new synthesis is a guide to these works, not a replacement for their proofs.',y=150,style='small')
    w.finish();return w.save()

def entry(path,s):
    w=PageWriter(path);w.start('Source '+s['code'],s['title'])
    y=w.para(s['code']+'  /  SOURCE READING CARD',y=H-105,style='label')-17
    y=w.para(html.escape(s['title']),y=y,style='title')-18
    y=w.para(html.escape(s['edition'])+f"  ·  {s['pages']} original pages",y=y,style='small')-30
    y=w.para('READ THIS FOR',y=y,style='label')-6
    y=w.para(html.escape(s['role']),y=y)-24
    y=w.para('KEEP THIS BOUNDARY',y=y,style='label')-6
    y=w.para(html.escape(s['boundary']),y=y)-24
    y=w.para('CONNECTED SOURCES',y=y,style='label')-6
    x=48
    for code in RELATED[s['code']]:
        w.c.setStrokeColor(LINE);w.c.setFillColor(PALE);w.c.roundRect(x,y-30,67,27,5,fill=1,stroke=1)
        w.c.setFont('NavBold',9);w.c.setFillColor(INK);w.c.drawCentredString(x+33.5,y-21,code)
        w.target(code,(x,y-30,x+67,y-3));x+=79
    y-=58
    y=w.para('Original text begins on the next page.',y=y,style='label')
    w.target('SOURCE:'+s['code'],(48,y-5,564,y+18))
    w.para('The source pages that follow are preserved without editorial stamps. Page labels in the PDF navigation use the source code and physical source-page number. The package retains the byte-identical original PDF and its SHA-256 digest.',y=157,style='small')
    w.finish();return w.save()

def child_toc(d,offset,baselevel):
    """Preserve source titles/destinations while normalizing impossible level jumps."""
    rows=[];prev=baselevel
    for row in d.get_toc():
        level,title,page=row[:3]
        if page<1 or page>len(d):continue
        lev=min(baselevel+max(1,level),prev+1)
        lev=max(baselevel+1,lev);rows.append([lev,str(title),offset+page]);prev=lev
    return rows

def assemble(cat,group=None,master_offsets=None):
    docs=[s for s in cat['source_documents'] if group is None or s['group']==group]
    use_syn=group in (None,'core')
    syn=fitz.open(ROOT/'editorial/connected_synthesis.pdf');syn_n=len(syn) if use_syn else 0
    nfront=6 if group is None else 3
    syn_start=nfront+1 if use_syn else None
    cursor=nfront+syn_n
    offsets={}
    for g in GROUPS:
        gd=[s for s in docs if s['group']==g]
        if not gd:continue
        offsets['GROUP:'+g]={'entry':cursor+1};cursor+=1
        for s in gd:
            offsets[s['code']]={'entry':cursor+1,'source_start':cursor+2,'source_end':cursor+1+s['pages']}
            cursor+=1+s['pages']
    if use_syn:offsets['SYN']={'entry':syn_start,'source_start':syn_start}
    tag='master' if group is None else group
    f=front(NAV/f'{tag}_front.pdf',docs,offsets,group,syn_start,syn_n)
    if f['pages']!=nfront:raise AssertionError('Unexpected front page count')
    output=fitz.open();toc=[[1,'Collection cover',1]];labels=[];pending=[];newpages=[];page_rows=[]
    def navblock(block,labelprefix):
        off=len(output)
        with fitz.open(ROOT/block['path']) as d:output.insert_pdf(d)
        for l in block['links']:pending.append(dict(l,page=l['page']+off))
        for p,h in block['headings']:
            if off==0 and p>0:toc.append([1,h,p+1])
        for j in range(block['pages']):newpages.append(off+j)
        labels.append({'startpage':off,'prefix':labelprefix,'style':'D','firstpagenum':1})
    navblock(f,'C-')
    if use_syn:
        off=len(output);output.insert_pdf(syn)
        toc.append([1,'Connected synthesis: Machine-Native Reasoning',off+1]);toc+=child_toc(syn,off,1)
        labels.append({'startpage':off,'prefix':'S-','style':'D','firstpagenum':1})
        newpages.extend(range(off,off+len(syn)))
    sources_added=[]
    for g in GROUPS:
        gd=[s for s in docs if s['group']==g]
        if not gd:continue
        gp=groupcard(NAV/f'part_{g}.pdf',g);off=len(output)
        navblock(gp,'PART-'+GROUPS[g][0]+'-');toc.append([1,GROUPS[g][0]+'  |  '+GROUPS[g][1],off+1])
        for s in gd:
            ep=entry(NAV/(s['code']+'_entry.pdf'),s);off=len(output);navblock(ep,s['code']+'-entry-')
            toc.append([2,s['code']+'  |  '+s['title'],off+1])
            soff=len(output)
            if soff+1!=offsets[s['code']]['source_start']:raise AssertionError('Page-map drift')
            with fitz.open(ROOT/s['path']) as d:
                if len(d)!=s['pages'] or digest(ROOT/s['path'])!=s['sha256']:raise AssertionError('Source changed')
                output.insert_pdf(d,links=True,annots=True)
                toc+=child_toc(d,soff,2)
            labels.append({'startpage':soff,'prefix':s['code']+'-','style':'D','firstpagenum':1})
            for j in range(s['pages']):page_rows.append({'code':s['code'],'source_page':j+1,'compiled_page':soff+j+1,'page_label':s['code']+'-'+str(j+1),'source_file':s['filename']})
            sources_added.append({**s,**offsets[s['code']]})
    if len(output)!=cursor:raise AssertionError('Total-page mismatch')
    remote=master_offsets or offsets
    for l in pending:
        target=l['target'];direct=target.startswith('SOURCE:');key=target.split(':',1)[1] if direct else target
        source=offsets if key in offsets else remote
        if key not in source:raise ValueError('Unknown link target '+key)
        targetpage=source[key].get('source_start') if direct else source[key]['entry']
        link={'from':fitz.Rect(l['rect']),'page':targetpage-1,'to':fitz.Point(0,0),'zoom':0}
        if key in offsets:link['kind']=fitz.LINK_GOTO
        else:link.update(kind=fitz.LINK_GOTOR,file=MASTER)
        output[l['page']].insert_link(link)
    output.set_toc(toc,collapse=2);output.set_page_labels(labels)
    output.set_metadata({'title':TITLE+(' | '+GROUPS[group][1] if group else ' | Complete selected compendium'),'author':'Komorebi P.','subject':'Connected theory-first compilation; source-specific proof and implementation boundaries preserved.','creator':'Operation Komorebi / Python assembly','creationDate':'D:20261009000000Z','modDate':'D:20261009000000Z'})
    name=MASTER if group is None else {'core':'01_Core_Machine_Theory.pdf','foundations':'02_Mathematical_and_Architectural_Foundations.pdf','companions':'03_Formal_Visual_and_Lineage_Companions.pdf'}[group]
    path=OUT/name
    output.save(path,garbage=3,deflate=True,no_new_id=True)
    result={'file':str(path.relative_to(ROOT)),'pages':len(output),'source_count':len(docs),'source_pages':sum(s['pages'] for s in docs),'synthesis_pages':syn_n,'navigation_pages':nfront+len(docs)+sum(any(s['group']==g for s in docs) for g in GROUPS),'bookmarks':len(toc),'new_page_indices':newpages,'documents':sources_added,'offsets':offsets,'sha256':digest(path)}
    with (ROOT/(tag+'_PAGE_MAP.csv')).open('w',newline='',encoding='utf-8') as h:
        writer=csv.DictWriter(h,fieldnames=['code','source_page','compiled_page','page_label','source_file']);writer.writeheader();writer.writerows(page_rows)
    output.close();syn.close();return result

def write_index(cat,results):
    master=results[0];rows=[]
    for s in master['documents']:
        rows.append(f'<tr><td>{s["code"]}</td><td><a href="{master["file"]}#page={s["entry"]}">{html.escape(s["title"])}</a></td><td>{html.escape(s["edition"])}</td><td>{s["source_start"]}–{s["source_end"]}</td><td><a href="{s["path"]}">Original PDF</a></td></tr>')
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Machine-Native Reasoning | Operation Komorebi</title><style>body{max-width:1100px;margin:3rem auto;padding:0 1.2rem;font:17px/1.6 Georgia,serif;color:#203d37;background:#f7f6f0}h1,h2{font-family:Arial,sans-serif}a{color:#20594b}td,th{text-align:left;padding:.8rem;border-bottom:1px solid #ced5d0;vertical-align:top}table{border-collapse:collapse;width:100%;font-size:14px}.note{padding:1.2rem;border-left:3px solid #203d37;background:white}nav a{display:block;margin:.5rem 0}</style><h1>Machine-Native Reasoning</h1><h2>Representation, Learning, and Computational Organization</h2><p>Komorebi P. · Operation Komorebi · Collection edition 1.0.0 · 9 October 2026</p><p class="note">A connected theoretical synthesis and twenty-four preserved source documents. Mathematical proofs, finite calculations, historical experimental records and implementation status retain their original boundaries.</p><nav>'''
    page+=f'<a href="{master["file"]}">Complete selected reader — {master["pages"]:,} pages</a><a href="editorial/connected_synthesis.pdf">Start with the connected synthesis — 27 pages</a>'
    for r in results[1:]:page+=f'<a href="{r["file"]}">{html.escape(Path(r["file"]).stem.replace("_"," "))} — {r["pages"]:,} pages</a>'
    page+='</nav><h2>Source directory</h2><table><tr><th>Code</th><th>Work</th><th>Edition</th><th>Reader pages</th><th>Original</th></tr>'+''.join(rows)+'</table><h2>Interactive companion</h2><p><a href="companion/Agent_Dynamics_Interactive.html">Python agent-dynamics player</a> · <a href="companion/Agent_Dynamics_Animated.gif">Animation</a></p><p>Source page ranges are physical pages in the complete reader. Browser support for opening PDF fragments varies. The reader itself also provides bookmarks and clickable source-entry cards.</p><p>See README.md, REVIEW_NOTES.md and UNASSEMBLED_BRANCHES.md for scope, reproduction and outstanding source coverage. No network connection is required.</p></html>'
    (ROOT/'index.html').write_text(page,encoding='utf-8')

def main():
    OUT.mkdir(exist_ok=True);NAV.mkdir(parents=True,exist_ok=True)
    cat=json.loads((ROOT/'SOURCE_CATALOG.json').read_text())
    master=assemble(cat);results=[master]
    for g in GROUPS:results.append(assemble(cat,g,master['offsets']))
    (ROOT/'ASSEMBLY_MAP.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    write_index(cat,results)
    with (ROOT/'DOCUMENT_INDEX.csv').open('w',newline='',encoding='utf-8') as f:
        fields=['code','group','title','edition','pages','entry','source_start','source_end','filename','sha256'];w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(master['documents'])
    for r in results:print(f'{r["file"]}: {r["pages"]} pages, {r["bookmarks"]} bookmarks, {r["source_count"]} preserved documents')
if __name__=='__main__':main()
