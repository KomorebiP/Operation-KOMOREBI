#!/usr/bin/env python3
"""Build the vector visual companion. No network, neural model, or image service.

Fonts are resolved from the host and are not distributed in the source package.
All illustrations are original programmatic diagrams of the cited manuscript.
"""
from __future__ import annotations
import argparse, csv, hashlib, itertools, json, math, os
from pathlib import Path
from html import escape
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle

ROOT=Path(__file__).resolve().parents[1]
W,H=612,792
INK=colors.HexColor('#172A3A'); MUTED=colors.HexColor('#586777')
TEAL=colors.HexColor('#176B70'); BLUE=colors.HexColor('#355B92')
AMBER=colors.HexColor('#93601A'); RED=colors.HexColor('#A33F46')
LINE=colors.HexColor('#CBD4DC'); PALE=colors.HexColor('#F2F5F7')
SEA=colors.HexColor('#EAF4F2'); SKY=colors.HexColor('#EDF2F9')
SAND=colors.HexColor('#FBF2E4'); ROSE=colors.HexColor('#FAECEB'); WHITE=colors.white
FONT_RECORD={}
FONT_CMAP={}

def fonts():
    paths={
      'Body':['/usr/share/fonts/truetype/lato/Lato-Regular.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'],
      'Bold':['/usr/share/fonts/truetype/lato/Lato-Bold.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'],
      'Italic':['/usr/share/fonts/truetype/lato/Lato-Italic.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf'],
      'Serif':['/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'],
      'SerifBold':['/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'],
      'Math':['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']}
    extra=os.environ.get('KOMOREBI_FONT_DIR')
    for name,choices in paths.items():
        if extra: choices=[str(Path(extra)/(name+'.ttf'))]+choices
        found=next((Path(p) for p in choices if Path(p).is_file()),None)
        if found is None:
            raise RuntimeError(f'Missing font for {name}. Set KOMOREBI_FONT_DIR to a directory with {name}.ttf. Font files are not bundled.')
        pdfmetrics.registerFont(TTFont(name,str(found)))
        FONT_CMAP[name]=set(pdfmetrics.getFont(name).face.charToGlyph)
        FONT_RECORD[name]={'filename':found.name,'sha256':hashlib.sha256(found.read_bytes()).hexdigest()}
    pdfmetrics.registerFontFamily('Body',normal='Body',bold='Bold',italic='Italic',boldItalic='Bold')
    pdfmetrics.registerFontFamily('Serif',normal='Serif',bold='SerifBold',italic='Serif',boldItalic='SerifBold')

C=None; PAGES=[]; TEXTBOXES=[]; CURRENT=0

def rect(x,y,w,h,fill=WHITE,stroke=LINE,r=9,lw=.8):
    C.setLineWidth(lw)
    C.setStrokeColor(stroke or fill)
    C.setFillColor(fill or WHITE)
    C.roundRect(x,H-y-h,w,h,r,stroke=bool(stroke),fill=bool(fill))

def line(x1,y1,x2,y2,color=LINE,width=1,dash=None):
    C.saveState(); C.setStrokeColor(color); C.setLineWidth(width)
    if dash:C.setDash(*dash)
    C.line(x1,H-y1,x2,H-y2); C.restoreState()

def arrow(points,color=TEAL,width=1.7,head=6,dash=None):
    C.saveState();C.setStrokeColor(color);C.setFillColor(color);C.setLineWidth(width)
    if dash:C.setDash(*dash)
    p=C.beginPath();p.moveTo(points[0][0],H-points[0][1])
    for x,y in points[1:]:p.lineTo(x,H-y)
    C.drawPath(p,stroke=1)
    a,b=points[-2],points[-1];theta=math.atan2(b[1]-a[1],b[0]-a[0])
    left=(b[0]-head*math.cos(theta)+head*.5*math.sin(theta),b[1]-head*math.sin(theta)-head*.5*math.cos(theta))
    right=(b[0]-head*math.cos(theta)-head*.5*math.sin(theta),b[1]-head*math.sin(theta)+head*.5*math.cos(theta))
    p=C.beginPath();p.moveTo(b[0],H-b[1]);p.lineTo(left[0],H-left[1]);p.lineTo(right[0],H-right[1]);p.close()
    C.drawPath(p,stroke=0,fill=1); C.restoreState()

def para(txt,x,y,w,size=12,leading=None,font='Body',color=INK,align=0,maxh=None):
    for ch in set(txt):
        if ord(ch)>127 and ord(ch) not in FONT_CMAP[font]:
            if ord(ch) not in FONT_CMAP['Math']:
                raise ValueError(f'Page {CURRENT}: no paragraph glyph U+{ord(ch):04X}')
            txt=txt.replace(ch, '<font name="Math">'+ch+'</font>')
    st=ParagraphStyle('p',fontName=font,fontSize=size,leading=leading or size*1.32,textColor=color,alignment=align,spaceAfter=0,allowWidows=0,allowOrphans=0)
    p=Paragraph(txt,st);aw,ah=p.wrap(w,1000)
    if maxh is not None and ah>maxh+.1:
        raise ValueError(f'Page {CURRENT}: text overflow {ah:.1f}>{maxh}: {txt[:90]}')
    p.drawOn(C,x,H-y-ah)
    TEXTBOXES.append({'page':CURRENT,'x':x,'y':y,'w':w,'h':ah,'text':txt,'size':size})
    return ah

def label(txt,x,y,size=11,font='Body',color=INK,align='left'):
    # Mathematical glyphs missing from the display serif use the math font.
    # Keep digits and ordinary text in the requested face; never render .notdef.
    runs=[]
    for ch in txt:
        use=font if ord(ch) in FONT_CMAP[font] else 'Math'
        if ord(ch) not in FONT_CMAP[use]:
            raise ValueError(f'Page {CURRENT}: no glyph U+{ord(ch):04X} for {ch!r}')
        if runs and runs[-1][0]==use:runs[-1]=(use,runs[-1][1]+ch)
        else:runs.append((use,ch))
    tw=sum(pdfmetrics.stringWidth(t,f,size) for f,t in runs)
    if align=='center':x-=tw/2
    elif align=='right':x-=tw
    C.setFillColor(color)
    tx=C.beginText();tx.setTextOrigin(x,H-y-size*.82)
    for f,t in runs:tx.setFont(f,size);tx.textOut(t)
    C.drawText(tx)
    TEXTBOXES.append({'page':CURRENT,'x':x,'y':y,'w':tw,'h':size*1.05,'text':txt,'size':size,'font':font,'runs':runs})

def pill(txt,x,y,w=None,fill=SEA,color=TEAL,size=10,h=24):
    if w is None:w=pdfmetrics.stringWidth(txt,'Bold',size)+22
    rect(x,y,w,h,fill,None,r=h/2)
    label(txt,x+w/2,y+(h-size)/2-1,size,'Bold',color,'center')

def box(x,y,w,h,title,body='',fill=WHITE,accent=TEAL,ts=13,bs=11):
    rect(x,y,w,h,fill,LINE,r=9)
    line(x+13,y+14,x+13,y+h-14,accent,2.3)
    th=para(title,x+25,y+13,w-38,ts,font='Bold',maxh=h-24)
    if body:para(body,x+25,y+th+20,w-38,bs,color=MUTED,maxh=h-th-26)

def note(x,y,w,title,body,fill=PALE,h=90,ts=11,bs=11):
    rect(x,y,w,h,fill,None)
    th=para(title,x+14,y+12,w-28,ts,font='Bold',color=TEAL if fill==SEA else INK,maxh=h-24)
    para(body,x+14,y+th+18,w-28,bs,color=MUTED,maxh=h-th-25)

def cells(vals,x,y,size=42,gap=8,selected=None,fill=PALE,active=SEA):
    for i,v in enumerate(vals):
        color=active if selected is not None and v in selected else fill
        rect(x+i*(size+gap),y,size,size,color,TEAL if selected and v in selected else LINE,6)
        label(str(v),x+i*(size+gap)+size/2,y+size/2-7,14,'Bold',TEAL if selected and v in selected else INK,'center')

def token_row(bits,x,y,size=36,gap=8,cut=None):
    for i,b in enumerate(bits):
        fill=SEA if b==1 else SKY if b==0 else PALE
        if cut is not None and i>=cut:fill=PALE
        rect(x+i*(size+gap),y,size,size,fill,LINE,5)
        label(str(b) if b is not None else '?',x+i*(size+gap)+size/2,y+size/2-7,14,'Bold',MUTED if b is None else INK,'center')

def cardmetric(x,y,w,n,caption,fill=SEA,color=TEAL,h=87):
    rect(x,y,w,h,fill,None)
    label(n,x+w/2,y+12,29,'SerifBold',color,'center')
    para(caption,x+10,y+52,w-20,10.5,align=1,maxh=h-55)

def source(sec,pp):return f'[S] {sec} | manuscript pp. {pp}'

def begin(n,title,dek,chapter,src,bottom_left,bottom_right):
    global CURRENT
    CURRENT=n;C.bookmarkPage(f'p{n}');C.addOutlineEntry(f'{n:02d}  {title}',f'p{n}',0,False)
    C.setFillColor(WHITE);C.rect(0,0,W,H,fill=1,stroke=0)
    label('OPERATION KOMOREBI',40,23,8.8,'Bold',MUTED)
    label('SELF-IMPROVING INTELLIGENCE',572,23,8.4,'Body',MUTED,'right')
    line(40,43,572,43,LINE,.7)
    label(chapter.upper(),40,58,9.7,'Bold',TEAL)
    th=para(title,40,79,532,26,30,'SerifBold',maxh=63)
    para(dek,40,87+th,532,12,16,color=MUTED,maxh=58)
    line(40,596,572,596,LINE,.8)
    para(bottom_left[0].upper(),40,612,252,9.1,font='Bold',color=TEAL,maxh=24)
    para(bottom_left[1],40,632,252,11,14.6,maxh=83)
    para(bottom_right[0].upper(),320,612,252,9.1,font='Bold',color=AMBER,maxh=24)
    para(bottom_right[1],320,632,252,11,14.6,maxh=83)
    line(40,727,572,727,LINE,.7)
    para(src,40,738,483,8.3,11,color=MUTED,maxh=24)
    label(f'{n:02d}',572,739,12,'Bold',INK,'right')
    label('VISUAL GUIDE 1.0.0',40,772,7.6,'Body',MUTED)
    label('Companion to the first edition',572,772,7.6,'Body',MUTED,'right')
    PAGES.append({'page':n,'title':title,'chapter':chapter,'source':src,'intro':dek,'interpretation':bottom_left[1],'boundary':bottom_right[1]})

def end():C.showPage()

def bal_tree(y0=258,dy=70,xl=55,xr=557,highlight=False,leafnames=None):
    # Full 8-leaf canonical bit-query tree; left is report 0, right is report 1.
    lv=[[(xl+xr)/2],[(xl+xr)/2-(xr-xl)/4,(xl+xr)/2+(xr-xl)/4],
        [xl+(xr-xl)*(i+.5)/4 for i in range(4)],
        [xl+(xr-xl)*(i+.5)/8 for i in range(8)]]
    path=[0,1,2,5] # ordinal branch positions for reports 1,0,1
    for d in range(3):
        for i,x in enumerate(lv[d]):
            for b in range(2):
                k=2*i+b
                hi=highlight and i==path[d] and k==path[d+1]
                line(x,y0+d*dy+14,lv[d+1][k],y0+(d+1)*dy-14,TEAL if hi else LINE,2.6 if hi else 1)
    # leaves correspond to little-endian query order b0, b1, b2
    names=leafnames or ['0','4','2','6','1','5','3','7']
    for d,row in enumerate(lv):
        for i,x in enumerate(row):
            hi=highlight and i==path[d]
            C.setFillColor(SEA if hi else WHITE);C.setStrokeColor(TEAL if hi else LINE);C.setLineWidth(1.6 if hi else .9)
            C.circle(x,H-(y0+d*dy),15 if d<3 else 16,fill=1,stroke=1)
            label(('b'+str(d)) if d<3 else names[i],x,y0+d*dy-6.5,10.5,'Bold',TEAL if hi else INK,'center')
    return lv

def build(out):
    global C
    PAGES.clear();TEXTBOXES.clear()
    fonts();C=canvas.Canvas(str(out),pagesize=(W,H),pageCompression=1,invariant=1,initialFontName='Body')
    C.setTitle('Self-Improving Intelligence | A Visual Guide')
    C.setAuthor('Komorebi P.');C.setSubject('Visual companion to Self-Improving Intelligence v1.0.0. Exact finite constructions, assumptions, and costs.')
    C.setKeywords('Operation Komorebi, recursive improvement, visual guide, diagnosis, synthesis, certificates')
    # 01 COVER
    global CURRENT;CURRENT=1
    C.bookmarkPage('p1');C.addOutlineEntry('01  Self-Improving Intelligence: A Visual Guide','p1',0,False)
    label('OPERATION KOMOREBI',40,33,10,'Bold',MUTED)
    pill('VISUAL COMPANION',416,27,156,PALE,MUTED,9)
    para('Self-Improving<br/>Intelligence',40,88,532,37,44,'SerifBold',maxh=100)
    para('A visual guide to representation,<br/>discovery, and recursive revision',40,199,520,19,26,'Serif',maxh=60)
    line(40,281,572,281,INK,1)
    para('What improves when a system becomes<br/><b>better at making itself better?</b>',40,305,520,16,23,maxh=55)
    # ladder, output objects, not a claim of infinite recursion
    ys=[394,437,480,523]
    labels=[('01','Repair a case','a diagnostic policy'),('02','Improve discovery','a better compiler'),('03','Acquire a search rule','a composed predicate'),('04','Improve rule acquisition','a checked search representation')]
    for i,(num,head,tail) in enumerate(labels):
        x=40+i*17;rect(x,ys[i],532-i*17,36,SEA if i%2==0 else SKY,None,6)
        label(num,x+12,ys[i]+10,11,'Bold',TEAL)
        label(head,x+48,ys[i]+9,12,'Bold')
        label(tail,555,ys[i]+10,10,'Body',MUTED,'right')
    para('Each step retains its assumptions, evidence, and costs.',40,580,532,13,18,'Italic',color=TEAL,maxh=42)
    line(40,644,572,644,LINE,1)
    label('Komorebi P.',40,666,13,'Bold')
    label('Guide v1.0.0',572,666,11,'Body',MUTED,'right')
    label('Companion to the 60-page first edition',40,692,11,'Body',MUTED)
    label('8 October 2026',572,692,11,'Body',MUTED,'right')
    para('Analytical constructions, not agent-performance experiments.<br/>The diagrams explain the manuscript; they do not replace its proofs.',40,737,532,9.5,13,color=MUTED,maxh=30)
    PAGES.append({'page':1,'title':'Self-Improving Intelligence: A Visual Guide','chapter':'Cover','source':'[S] First-edition scope, pp. ii-iii','intro':'A standalone visual companion.','interpretation':'Four different objects improve across the finite chain.','boundary':'No claim of general intelligence or indefinite recursive acceleration.'});end()
    # 02 MAP
    begin(2,'The route through this guide','Read the worked world first. Then follow the discovery procedure outward, keeping the supplied machinery in view.','Orientation',source('Scope guide; §§1-3','iii, 1-4'),('How to use it','Every plate identifies its source section. Manuscript page numbers are the printed numbers, not the PDF viewer index.'),('What a diagram means','A solid arrow is a specified transition or dependency. Dashed paths are explicitly labeled as recurrence or a qualified extension. Counts retain their original units.'))
    routes=[('03-12','The repair problem','States, observations, trees, uncertainty, and transport.'),('13-21','Changing the compiler','Certified shortcuts, learned pruning, and repair scope.'),('22-28','Changing acquisition','Checked equations, preserved evidence, invalidation, and costs.'),('29-36','What the result supports','Evaluation, continuation, the learned bridge, and source routes.')]
    for i,(p,t,b) in enumerate(routes):
        y=210+84*i;rect(40,y,532,73,PALE if i%2 else SEA,None,8)
        pill(p,52,y+20,69,WHITE,TEAL,10)
        para(t,136,y+12,420,14,font='Bold',maxh=26);para(b,136,y+36,418,11.5,color=MUTED,maxh=31)
    end()
    # 03 COMPARISON
    begin(3,'A better system is not always a better improver','Changing a library and changing the procedure that uses it answer different questions. A crossed comparison keeps them separate.','I / What changes',source('§3; Counterexample 3.2','3-4'),('Read the horizontal comparison','Holding the library fixed isolates a change in the improvement procedure. The combined descendant may improve for a different reason.'),('No free starting advantage','Use comparable starting solvers, task laws, installed information, and budgets. A stronger base model or an extra library is another changed component.'))
    label('IMPROVEMENT PROCEDURE',370,211,10,'Bold',MUTED,'center')
    label('Parent U',276,241,13,'Bold',align='center');label('Revised U′',463,241,13,'Bold',align='center')
    label('Old library L',49,310,11,'Bold');label('New library L′',49,427,11,'Bold')
    for x,y,h,b,fil in [(189,277,'U with L','Reference system',PALE),(376,277,'U′ with L','Process-only change',SEA),(189,394,'U with L′','Library-only change',SKY),(376,394,'U′ with L′','Combined descendant',SEA)]:box(x,y,171,92,h,b,fil,ts=14)
    arrow([(360,323),(373,323)]);arrow([(360,440),(373,440)])
    note(40,510,532,'Counterexample','Storing all four task answers improves retrieval over storing one. The retrieval procedure can remain exactly the same.',h=73,bs=11)
    end()
    #04 WORLD
    begin(4,'One defect. Eight possible cells.','The procedure cannot see the defect index. It receives only the reports of the questions it is allowed to ask.','II / The diagnostic world',source('§4; §32','4, 49-51'),('The learning target','Retain an executable way to find a justified repair in a later episode. Do not install the next episode’s hidden answer.'),('What is supplied','The binary sensors and repair meanings come from a declared finite model. The 88 query-table entries are supplied, not learned through executed calibration.'))
    label('Possible hidden defect j',306,219,13,'Bold',align='center');cells(list(range(8)),70,252,52,8)
    box(40,344,249,119,'A query names a subset','Ask whether j belongs to A.<br/>The report is 0 or 1.<br/>A query does not move the defect.',SEA,bs=12)
    box(323,344,249,119,'A repair names one cell','Repair rᵢ succeeds only at cell i.<br/>Commit only when every remaining possibility supports it.',SKY,bs=12)
    note(40,499,532,'The old state is too coarse','“There is one defect” is true in all eight cases. It gives no basis for choosing which cell to repair.',h=80,bs=12)
    end()
    #05 TREES
    begin(5,'Two investigations, the same installed sensors','Equality-first testing and coordinate queries use the same declared language. Their paths have different depths, but their complete trees have the same size.','II / The diagnostic world',source('§4; Theorem 32.1','4, 49-50'),('Worst-case execution','Equality-first: seven questions, then repair. Coordinate queries: three questions, then repair. Total costs are eight and four calls.'),('Complete stored controller','Both full binary trees have eight repair leaves and seven query nodes: fifteen records. These are literal tree records, not bytes or minimal program sizes.'))
    label('Equality-first',161,210,15,'Bold',align='center');label('Coordinate queries',435,210,15,'Bold',align='center')
    # equality chain vertical; all fifteen records shown
    for i in range(7):
        y=250+i*40
        if i<6:line(126,y+12,126,y+28,LINE)
        line(142,y,195,y,LINE)
        rect(89,y-13,74,26,PALE,LINE,5);label(f'j = {i}?',126,y-5.5,10.5,'Bold',align='center')
        rect(192,y-13,51,26,SEA,LINE,5);label(f'r{i}',217,y-5.5,11,'Bold',TEAL,'center')
    line(126,502,126,521,LINE);rect(100,521,52,26,SEA,LINE,5);label('r7',126,528,11,'Bold',TEAL,'center')
    label('yes →',166,232,9,'Body',MUTED);label('no ↓',49,300,10,'Body',MUTED)
    # small full balanced tree right half
    xs=[[429],[365,493],[333,397,461,525],[317,349,381,413,445,477,509,541]]
    yy=[267,339,411,483]
    for d in range(3):
        for i,x in enumerate(xs[d]):
            for b in range(2):line(x,yy[d]+13,xs[d+1][2*i+b],yy[d+1]-12,LINE)
    for d,row in enumerate(xs):
        for i,x in enumerate(row):
            C.setFillColor(SEA if d==3 else SKY);C.setStrokeColor(LINE);C.circle(x,H-yy[d],14 if d<3 else 12,fill=1,stroke=1)
            label(f'b{d}' if d<3 else ['0','4','2','6','1','5','3','7'][i],x,yy[d]-5.5,9.5,'Bold',align='center')
    label('Leaf number = cell to repair',429,518,10,'Body',MUTED,'center')
    para('b0: {1,3,5,7} · b1: {2,3,6,7}<br/>b2: {4,5,6,7}. Left edge: 0. Right: 1.',303,542,272,9.2,12,color=MUTED,align=1,maxh=30)
    end()
    #06 TRACE
    begin(6,'Follow one episode: the defect is at cell 5','This page follows the canonical coordinate policy. The procedure knows the reports, not the hidden index shown to the reader.','II / The diagnostic world',source('§4; §32; Appendix A','4, 49-54'),('What was acquired','The three reports select a repair for this episode. The reusable artifact is the branching procedure that works for every allowed starting cell.'),('One exact trace, not the only tree','The shipped compiler can use an equality query at the last two-case branch. It has the same cost. This plate deliberately shows the canonical all-coordinate tree.'))
    stages=[('Start',list(range(8)),'Eight possibilities'),('bit 0 = 1',[1,3,5,7],'Odd-indexed cells remain'),('bit 1 = 0',[1,5],'Second bit is zero'),('bit 2 = 1',[5],'Only cell 5 remains')]
    for i,(head,vals,sub) in enumerate(stages):
        y=210+84*i
        para(head,40,y+10,118,12,font='Bold',maxh=32)
        cells(vals,169,y,38,7,selected=set(vals))
        label(sub,169,y+46,10.5,'Body',MUTED)
        if i<3:arrow([(147,y+43),(147,y+72)],color=TEAL,width=1.5)
    pill('Execute r5: the fourth call',169,552,267,SEA,TEAL,12,h=28)
    end()
    #07 MEMORY
    begin(7,'The path is not the stored program','A single successful run touches four records. Its complete reusable controller still contains all fifteen.','II / The diagnostic world',source('§6; Theorem 11.1; §28','6-7, 14-15, 44'),('Count the two resources separately','Execution follows one branch. Literal storage sums every branch. The highlighted path for reports 1, 0, 1 reaches repair 5.'),('Scope of the bound','Immutable cases, binary observations, a different successful repair for each case, and one record per node. Shared code or state-reset operations change the model.'))
    bal_tree(y0=251,dy=76,highlight=True)
    label('Report order: bit 0, bit 1, bit 2',306,522,11,'Body',MUTED,'center')
    pill('4 visited records',92,551,190,SEA,TEAL,12,28);pill('15 stored records',330,551,190,PALE,INK,12,28)
    end()
    #08 RESIDUAL
    begin(8,'A residual is a question, not a diagnosis','The same mismatch can be consistent with several causes. A useful next experiment separates repair-relevant explanations.','II / Investigation',source('§5; Proposition 5.1','5-6'),('Use the failure','Retain competing explanations. Seek an admitted observation whose possible outcomes change which correction is justified.'),('Do not invent missing access','A representation cannot recover a distinction unavailable in its complete transcript. With disjoint repairs and identical transcript laws, equal-prior success is at most one half.'))
    box(152,215,308,69,'Prediction ≠ observation','Which assumption failed?',ROSE,RED,ts=16)
    nodes=[(40,335,'Missing distinction','The state merges relevant cases.',SEA),(318,335,'Wrong transition','An operator predicts the wrong effect.',SKY),(40,447,'Noisy observation','The report is not an exact reading.',SAND),(318,447,'Omitted side effect','The experiment changes another variable.',PALE)]
    for x,y,t,b,f in nodes:box(x,y,254,90,t,b,f,ts=13,bs=11.5)
    arrow([(235,284),(167,327)],MUTED,1.2);arrow([(377,284),(445,327)],MUTED,1.2)
    line(306,296,306,437,LINE,1);arrow([(306,437),(284,476)],MUTED,1.2);arrow([(306,437),(320,476)],MUTED,1.2)
    end()
    #09 REPAIR ALIGNED
    begin(9,'The best question need not identify the most','A repair may work for several hidden cases. The right stopping condition is a common successful action, not complete knowledge of the state.','II / Investigation',source('Counterexample 6.3; §5.1','6-8'),('Balanced is not automatically best','The 2/2 question has more information about four equally likely cases, but one branch still mixes incompatible repairs.'),('The exact objective','Both questions cost one unit and preserve the state. The 3/1 question supports a correct repair after one observation in every case.'))
    label('Repair A works on {0,1,2}',306,212,13,'Bold',TEAL,'center');label('Repair B works on {3}',306,236,13,'Bold',BLUE,'center')
    for x,t in [(40,'Balanced 2 / 2 split'),(318,'Repair-aligned 3 / 1 split')]:
        rect(x,287,254,252,PALE,None);para(t,x+15,301,224,13,font='Bold',align=1,maxh=38)
    for x,vals in [(59,[0,1]),(180,[2,3])]:cells(vals,x,379,37,6)
    cells([0,1,2],331,379,36,6);cells([3],497,379,36,6)
    pill('Repair A',59,441,100,SEA,TEAL,10);pill('Unresolved',180,441,99,SAND,AMBER,10)
    pill('Repair A',342,441,120,SEA,TEAL,10);pill('Repair B',479,441,80,SKY,BLUE,10)
    para('Another query is needed<br/>on the {2,3} branch.',66,487,220,11,align=1,maxh=37)
    para('Both branches already<br/>support one valid action.',335,487,220,11,align=1,maxh=37)
    end()
    #10 RECURSION COST
    begin(10,'One tree must satisfy both resource limits','The synthesis combines complete child policies. Worst-case execution takes a maximum. Stored controller size takes a sum.','II / Investigation',source('Theorem 6.2','6-7'),('Read the arithmetic','This illustrative root has cost 1. Its children cost (2 calls, 3 records) and (4 calls, 7 records). The combined tree costs (5 calls, 11 records).'),('What is not being claimed','This is an illustration of the recurrence, not a new optimality result. A real child must be valid on the actual post-experiment support, and every possible branch needs a witness.'))
    box(183,209,246,70,'Run one experiment','Cost 1; one stored root record',SEA,ts=14)
    arrow([(245,279),(167,329)]);arrow([(367,279),(445,329)])
    box(47,338,241,99,'Report 0 → child policy','Work 2<br/>Stored records 3',SKY,ts=14,bs=13)
    box(324,338,241,99,'Report 1 → child policy','Work 4<br/>Stored records 7',SKY,ts=14,bs=13)
    rect(59,480,494,91,PALE,None)
    label('Work = 1 + max(2, 4) = 5',306,495,18,'Math',INK,'center')
    label('Storage = 1 + 3 + 7 = 11',306,534,18,'Math',INK,'center')
    end()
    #11 CALIBRATE
    begin(11,'An unknown sensor needs a reference','A correct procedure for each known model need not give a common procedure when the model itself is unknown.','II / Investigation',source('Theorem 7.1; Counterexample 7.2','8-10'),('Ordinary reading alone','The report o = x ⊕ θ cannot distinguish (x,θ) = (0,0) from (1,1). They require different repairs. Repeating that same reading adds no information.'),('The additional channel is paid','A reference reports θ at cost 2. An ordinary query costs 1, then repair costs 1. Total work is 4, and the complete binary controller stores 7 records.'))
    label('Hidden repair bit x; fixed sensor convention θ',306,211,12,'Bold',align='center')
    rect(40,249,246,216,ROSE,None);label('Without calibration',163,266,14,'Bold',RED,'center')
    label('o = x ⊕ θ',163,304,21,'Math',INK,'center')
    box(59,352,208,80,'Report 0','(0,0) or (1,1)<br/>No common repair.',WHITE,RED,ts=12,bs=12)
    box(330,249,242,75,'Reference → θ','Cost 2',SEA,ts=14)
    arrow([(451,324),(451,345)])
    box(330,353,242,75,'Ordinary report → o','Recover x = o ⊕ θ; cost 1',SKY,ts=13)
    arrow([(451,428),(451,449)])
    box(330,457,242,75,'Execute the justified repair','Cost 1',SEA,ts=13)
    label('The model tag does not change between steps.',306,557,11,'Italic',MUTED,'center')
    end()
    #12 TRANSFER
    begin(12,'Transport the investigation, not only the repair','A translated answer can be correct while the observation needed to obtain it is unavailable in the target system.','II / Transfer',source('Theorem 9.1; Counterexample 9.2','12-13'),('A valid transport retains','Experiment permissions, report labels, state effects, successful-repair meanings, and costs. Correspondences are supplied in this finite theorem.'),('The missing-sensor obstruction','Copying the two possible repairs into a world with no bit-revealing observation does not transport the policy that chooses between them.'))
    box(49,231,220,83,'Source support B','Possible cases before querying',SEA,ts=14)
    box(343,231,220,83,'Target support σ(B)','The corresponding possible cases',SKY,ts=14)
    box(49,418,220,83,'Source child Bₑ,ₒ','Actual post-query possibilities',SEA,ts=14)
    box(343,418,220,83,'Target child','Corresponding effects and reports',SKY,ts=14)
    arrow([(269,272),(338,272)],TEAL);label('σ',306,247,15,'Math',TEAL,'center')
    arrow([(269,459),(338,459)],TEAL);label('σ',306,435,15,'Math',TEAL,'center')
    arrow([(159,314),(159,411)],MUTED);label('experiment e',72,350,11,'Bold',MUTED)
    arrow([(453,314),(453,411)],MUTED);label('matched experiment',369,350,11,'Bold',MUTED)
    pill('Both routes reach the same target child',97,544,418,SEA,TEAL,11,29)
    end()
    #13 COMPILER
    begin(13,'Now improve the procedure that builds the tree','A checked candidate can end an exhaustive search only when it is valid and attains the relevant global lower bounds.','III / Improving discovery',source('Theorem 11.1; §11.2','14-15'),('The decisive certificate','For n immutable cases with binary unit-cost queries and singleton repairs, a valid tree attaining both 1 + ceil(log₂ n) calls and 2n − 1 records closes the frontier.'),('A failed proposal is not infeasibility','An invalid scope, missing candidate, or unattained bound sends control to the exact parent. That preliminary work still counts.'))
    entries=[('Check semantic scope','Binary, immutable, unit cost, singleton repairs'),('Propose a controller','A supplied heuristic searches the observation table'),('Check the complete witness','All cases, branches, costs, and both lower bounds'),('Return the proved optimum','Only after every required check passes')]
    for i,(t,b) in enumerate(entries):
        y=212+i*90;box(45,y,338,72,t,b,SEA if i==3 else PALE,ts=12.5,bs=10.5)
        if i<3:arrow([(213,y+72),(213,y+87)],TEAL,1.5)
    box(423,319,146,141,'Exact parent','Run the general compiler.<br/><br/>Keep all costs.',SKY,ts=13,bs=11)
    for i in [0,1,2]:
        y=248+i*90;arrow([(383,y),(404,y),(404,354),(419,354)],AMBER,1.1)
    label('not certified',451,295,9.8,'Bold',AMBER)
    end()
    #14 COST
    begin(14,'What the shortcut actually reads','On the sixteen-case model, both compilers return an optimal controller with 5 execution calls and 31 stored records.','III / Improving discovery',source('Proposition 12.1; §13.3','16, 19'),('A precise saving','The recorded compilation count is 576,128 reads for the parent and 1,728 for the shortcut. Both include completed witness checking.'),('Keep the boundary visible','Each also pays 320 common input-validation reads. Selection among all candidates costs 21,124 development reads. Table accesses are not total CPU instructions.'))
    cardmetric(40,211,251,'576,128','exact parent: model-record reads',PALE,INK,96)
    cardmetric(321,211,251,'1,728','shortcut: model-record reads',SEA,TEAL,96)
    rows=[('Scope guard','320'),('Construct the proposed tree','1,280'),('Reconstruct branch supports','64'),('Replay every case','64')]
    for i,(t,n) in enumerate(rows):
        y=336+i*46;rect(59,y,494,39,PALE if i%2 else WHITE,LINE,5)
        label(t,74,y+11,12);label(n,534,y+10,14,'Bold',TEAL,'right')
    pill('320 + 1,280 + 64 + 64 = 1,728',84,542,444,SEA,TEAL,13,32)
    end()
    #15 FAILURE STATUS
    begin(15,'A fallback preserves meaning, not free speed','A preliminary shortcut can fail to prove an optimum and then spend extra work before invoking the same exact parent.','III / Improving discovery',source('Counterexample 13.1; §16.2','18, 24-25'),('The equality-only control','With four cells and only singleton queries, the shortcut falls back. Both return the same optimum. The wrapper uses 472 reads instead of 402.'),('Keep these outcomes different','A successful witness, a proved finite-horizon impossibility, and an interrupted search are different results. A timeout cannot certify infeasibility.'))
    label('Four-cell equality-only problem',306,213,14,'Bold',align='center')
    for y,t,n,fil,col in [(264,'Parent',402,SKY,BLUE),(329,'Wrapper + fallback',472,SAND,AMBER)]:
        label(t,50,y-20,11,'Bold',color=col);rect(50,y,470*n/500,33,fil,None,4);label(str(n),60+470*n/500,y+7,15,'Bold',col)
    label('70 extra model reads; same correct result',306,390,12,'Bold',AMBER,'center')
    for x,t,b,f,a in [(40,'SUCCESS','A checked tree fits the contract.',SEA,TEAL),(222,'INFEASIBLE','Complete search rules out this finite target.',ROSE,RED),(404,'INCOMPLETE','The allowance ended before a conclusion.',SAND,AMBER)]:box(x,452,168,122,t,b,f,a,ts=11,bs=11)
    end()
    #16 FEATURE
    begin(16,'Sometimes the search state is too coarse','No longer formula can recover a feature the learner was never given. Here, the missing distinction is remaining branch capacity.','IV / Learning a search rule',source('Proposition 14.1; Counterexample 14.2','20-21'),('The conflict is exact','Both contexts have (a,b,m) = (0,3,4). With capacity 2 the root must fail. With capacity 4, a completion with branch sizes (1,3) is possible.'),('What the learner did not invent','Capacity is exposed from a supplied feature registry. This repairs an internal search representation, not a physical sensor model or the definition of depth.'))
    pill('Same visible prefix: a = 0, b = 3, m = 4',61,217,490,SEA,TEAL,12,31)
    for x,cap,title,f,col in [(40,2,'Reject this root',ROSE,RED),(318,4,'Capacity still possible',SEA,TEAL)]:
        rect(x,280,254,276,PALE,None);label(f'Child capacity C = {cap}',x+127,299,14,'Bold',align='center')
        for i in range(4):
            yy=449-i*34
            if i<cap:rect(x+77,yy,100,27,WHITE,LINE,3)
            if i<3:rect(x+88,yy+4,78,19,f,None,3)
        line(x+58,478-cap*34,x+198,478-cap*34,col,2,(3,2))
        para(title,x+17,500,220,14,font='Bold',color=col,align=1,maxh=42)
    end()
    #17 CEGIS
    begin(17,'Four proposals, three counterexamples','The learner composes an arithmetic predicate. Retained counterexamples prevent it from proposing the same rejected behavior again.','IV / Learning a search rule',source('Theorem 15.1; §15.2; rule trace','21-23'),('The acquired object','The final five-node expression is max(a,b) > C. The reference learner visits 190 of 3,960 candidates and makes four teacher calls.'),('Finite success has a scope','The teacher checks 198 developmental contexts. That certifies this finite agreement, not validity at every larger capacity. Installation needs a separate scope argument.'))
    rows=[('a > a','(a,b,m,C) = (0,2,2,1)','Misses an overfull branch.',RED),('b > a','(0,1,2,1)','Rejects a feasible completion.',RED),('b > C','(2,0,2,1)','Misses too many zeros.',RED),('max(a,b) > C','All 198 development contexts','Accepted on the finite domain.',TEAL)]
    for i,(expr,ctx,desc,col) in enumerate(rows):
        y=210+i*91;rect(40,y,532,77,SEA if i==3 else PALE,None)
        pill(str(i+1),52,y+22,31,WHITE,col,11,30)
        label(expr,102,y+11,17,'Math',col)
        label(ctx,102,y+41,10.5,'Body',MUTED)
        para(desc,347,y+14,207,11.2,maxh=50)
        if i<3:arrow([(69,y+77),(69,y+89)],MUTED,1.1)
    end()
    #18 PREFIX
    begin(18,'Stop reading when no suffix can rescue the root','Eight cases must fit into two branches of capacity four. After five equal reports, the outcome is already decided.','IV / Learning a search rule',source('Proposition 16.1; Theorem 16.3','23-25'),('Why pruning is sound','Counts cannot decrease. Once one count exceeds C, no unread report can bring that branch back within capacity. The suffix cannot change rejection.'),('Necessary is not sufficient','Passing the capacity test does not prove that the remaining query library can separate either child. The compiler must still search and verify complete subtrees.'))
    pill('m = 8      remaining query depth d = 3      C = 4',58,211,496,PALE,INK,11,30)
    label('Read this query’s model rows in their fixed order',306,263,12,'Bold',align='center')
    token_row([1,1,1,1,1,None,None,None],57,304,53,10)
    for i in range(5):label(str(i+1),83+i*63,368,11,'Bold',TEAL,'center')
    label('count b',55,393,10,'Body',MUTED)
    arrow([(340,361),(340,426),(410,426)],RED,1.7)
    box(415,398,157,100,'Reject now','b = 5 > C = 4',ROSE,RED,ts=14,bs=12)
    note(52,488,335,'Three rows stay unread','Whatever they say, the branch already contains too many cases.',h=83,bs=12)
    end()
    #19 PROOF VS FIT
    begin(19,'A training-perfect rule can prune the answer','A dangerous shortcut is not made safe by a final answer checker: it may delete the only successful candidate before that checker sees it.','IV / Learning a search rule',source('Counterexample 16.2','23-24'),('The larger context','At (a,b,m,C) = (0,5,16,8), the bounded-cap formula rejects. But the unread cases can complete both branches to eight, so capacity remains feasible.'),('Separate selection from admission','Examples help select a formula. A proof with applicable premises authorizes deleting possibilities. The supplied structural gate accepts only the supported rule form.'))
    box(40,217,532,73,'Development capacities: 1, 2, 4','These two formulas agree throughout the development domain.',PALE,ts=14)
    box(40,331,251,93,'Supported rule','max(a,b) > C',SEA,TEAL,ts=14,bs=14)
    box(321,331,251,93,'Training-perfect impostor','max(a,b) > min(C,4)',ROSE,RED,ts=12.5,bs=12.2)
    arrow([(165,425),(165,451)],TEAL);arrow([(446,425),(446,451)],RED)
    pill('5 > 8 is false',64,463,203,SEA,TEAL,13,32)
    pill('5 > 4 is true',345,463,203,ROSE,RED,13,32)
    para('Keep investigating.<br/>No capacity obstruction yet.',49,523,232,12,align=1,maxh=43)
    para('Incorrectly discard<br/>a feasible completion.',333,523,232,12,align=1,maxh=43)
    end()
    #20 COUNTS VS COST
    begin(20,'Fewer model reads can still mean more work','The same ordered compiler returns the same literal controller. Streaming changes when impossible roots are abandoned.','IV / Learning a search rule',source('§18; Theorem 16.3','24-28'),('What the count supports','At 64 cases, streaming avoids 8,287 model rows. The returned controller still costs 7 online calls and 127 stored records.'),('No universal speedup','Streaming also adds 14,209 comparisons in the conservative account. At equal prices for reads and comparisons, that isolated modification costs more.'))
    label('64-case compilation: model-record reads',306,211,13,'Bold',align='center')
    for y,t,n,f,col in [(268,'Full scan',27744,SKY,BLUE),(344,'Streaming',19457,SEA,TEAL)]:
        label(t,53,y-23,12,'Bold',color=col);rect(53,y,451*n/27744,35,f,None,3);label(f'{n:,}',min(513,63+451*n/27744),y+8,13,'Bold',col)
    pill('8,287 reads avoided',67,415,213,SEA,TEAL,11,27)
    pill('14,209 extra comparisons',305,415,250,SAND,AMBER,11,27)
    note(51,475,510,'Declare a common price before subtracting','If a read costs w and a comparison costs 1, saving = 8,287w − 14,209. It is positive only when w > 14,209 / 8,287.',h=98,bs=12)
    end()
    #21 REPAIR WEIGHTS
    begin(21,'Count repair distinctions, not hidden states','If one repair fixes a pair of cases, a diagnostic policy need not identify which member of the pair occurred.','V / Extending the repair scope',source('Propositions 17.1, 22.1; Theorem 22.2','25, 33-35'),('The weight certificate','Put nonnegative weights on cases so every repair-success set has total at most 1. A successful leaf then carries at most 1 unit. Binary depth h supports at most 2ʰ leaves.'),('A changed repair can break the bound','Adding a universal repair makes the old total weight of 4 violate its success-set constraint. Recheck the weights before using the old pruning rule.'))
    for i in range(4):
        x=40+i*138;rect(x,225,118,148,SEA if i%2==0 else SKY,None)
        para(f'Repair {i}',x+9,240,100,12,font='Bold',align=1,maxh=23)
        cells([2*i,2*i+1],x+15,278,38,10)
        label('weights 1, 0',x+59,339,10.5,'Bold',TEAL,'center')
    label('8 hidden cases → 4 repair groups',306,413,21,'SerifBold',INK,'center')
    para('Total weight 4 requires at least 4 leaves.<br/>The supplied pair-index queries attain depth 2.',53,454,506,14,21,align=1,maxh=50)
    pill('2 questions + 1 repair | 7 stored records',64,539,484,PALE,INK,12,31)
    end()
    #22 LEARN EQ
    begin(22,'A useful equation begins as a proposal','The next acquired object is a task-independent library of equations. Evaluations suggest candidates; derivations decide which can be used.','VI / Improving acquisition',source('§§19-20','29-30'),('What is acquired','The finite proposer constructs 1,068 equations from equal probe vectors. The limited proof procedure admits 336 with replayable arithmetic derivations.'),('Unproved is not false','The remaining 732 may be false, valid only on a narrower scope, or simply beyond this proof search. The primitive arithmetic axioms and checking machinery are supplied.'))
    box(141,211,330,62,'135 schemas on 9 probe inputs','Generate equal-value proposals',PALE,ts=14,bs=11)
    arrow([(306,273),(306,296)])
    box(141,304,330,60,'1,068 proposed equations','A probe match is not an admission',SKY,ts=14,bs=11)
    arrow([(249,364),(168,401)],TEAL);arrow([(363,364),(444,401)],AMBER)
    cardmetric(40,414,251,'336','admitted by the limited checker',SEA,TEAL,93)
    cardmetric(321,414,251,'732','not proved by this procedure',SAND,AMBER,93)
    para('Example: max(x,1) = x matches x = 1,2,3.<br/>It fails at x = 0 and is not admitted.',54,536,504,12,17,align=1,maxh=42)
    end()
    #23 QUOTIENT
    begin(23,'Keep the earliest checked representative','Equivalent expressions can share a search representative without changing the original program submitted to the teacher.','VI / Improving acquisition',source('Theorems 21.1-21.2','30-32'),('What is preserved','The exact proposed program trees, retained counterexamples, final result, and exhaustion outcome. Removed later equivalents would already fail a retained counterexample.'),('What the theorem needs','Pure total arithmetic, sound equations, fixed order, an extensional deterministic teacher, and no forgotten counterexamples. It does not preserve every possible cost-sensitive objective.'))
    # illustrative classes, explicitly not the released grammar order
    examples=[('x + 0','x','x + 0'),('max(a,b)','max(b,a)','max(a,b)'),('a < b','b > a','a < b')]
    label('Schematic classes; left entry is assumed earlier',306,209,10.8,'Italic',MUTED,'center')
    for i,(a,b,rep) in enumerate(examples):
        y=245+i*82;rect(45,y,269,62,PALE,None)
        label(a,65,y+20,15,'Math');label('≡',172,y+20,16,'Math',TEAL);label(b,200,y+20,14,'Math')
        arrow([(318,y+31),(356,y+31)])
        rect(363,y,204,62,SEA,None);label(rep,465,y+20,15,'Math',TEAL,'center')
    pill('3,960 expressions → 1,362 representatives',59,514,494,SEA,TEAL,12,31)
    para('Stronger supplied normalizer: 1,352 representatives.<br/>The acquired library is not claimed to beat that prior.',52,558,508,10.8,15,align=1,maxh=33)
    end()
    #24 SAVINGS TRACE
    begin(24,'Less repetition. The same corrective evidence.','The quotient changes which redundant candidates are evaluated. It does not change the task teacher or smuggle in the target rule.','VI / Improving acquisition',source('§21.1; Theorem 21.2','30-32'),('Cold reacquisition','Both learners begin the new task with no task-specific counterexamples. They submit the same four programs and receive the same three counterexamples.'),('Costs still outside these numbers','Equation discovery, proof admission, quotient preparation, dispatch, and storage must be charged separately. The ten targets are finite tasks in one arithmetic language.'))
    for x,t in [(40,'Original enumeration'),(321,'Acquired quotient')]:label(t,x+125,214,13,'Bold',align='center')
    cardmetric(40,251,251,'190','candidates visited on the capacity task',PALE,INK,92)
    cardmetric(321,251,251,'76','candidates visited on the same task',SEA,TEAL,92)
    cardmetric(40,361,251,'1,898','interpreter-node visits',PALE,INK,87)
    cardmetric(321,361,251,'1,376','interpreter-node visits',SEA,TEAL,87)
    note(45,478,522,'The evidence transcript does not shrink','a > a  →  b > a  →  b > C  →  max(a,b) > C<br/>Same proposals; same counterexamples; same accepted program.',fill=SKY,h=96,bs=11.8)
    end()
    #25 JOINED
    begin(25,'One chain, not multiplied headline gains','The representation that speeds up rule acquisition feeds a separately certified compiler change. Each link keeps its own comparison.','VI / Improving acquisition',source('Proposition 23.1; §25','35-40'),('The composite claim','If the quotient preserves rule acquisition and the acquired rule passes the unchanged compiler gate, the complete chain returns the same rule and controller.'),('Meaning and savings are separate','Let K be extra preparation. The composite saves work in a common additive unit only if (A − A′) + (D − D′) > K. Do not multiply ratios from different baselines or units.'))
    items=[('Checked equations','An acquired, reusable library'),('Ordered quotient','A representation of the candidate grammar'),('Acquired predicate','The same target rule and teacher transcript'),('Revised compiler','A scope-checked change in discovery work'),('Diagnostic controller','A checked policy for future repair episodes')]
    for i,(t,b) in enumerate(items):
        y=207+i*73;box(107,y,398,59,t,b,SEA if i%2==0 else PALE,ts=12.5,bs=10.5)
        if i<4:arrow([(306,y+59),(306,y+71)],TEAL,1.4)
    end()
    #26 DAG
    begin(26,'A certificate has a dependency address','When a premise changes, mark the affected claims and their descendants. Reuse unaffected witnesses only under a complete dependency declaration.','VII / Continued applicability',source('Theorem 24.1; §24.2','37-38'),('Selective rechecking','Arithmetic equations and a repair-weight witness belong to different branches. A change in one branch need not invalidate everything.'),('The graph is a premise','This is not automatic discovery of every dependency in arbitrary code. An omitted premise can leave a registry green while its claim becomes false. Hashes do not repair missing semantics.'))
    label('Arithmetic / acquisition branch',172,207,11,'Bold',MUTED,'center');label('Repair / controller branch',439,207,11,'Bold',MUTED,'center')
    for x,y,t,b,fil in [(43,242,'Equation proofs','Arithmetic + local proof rules',SEA),(43,353,'Ordered quotient','Library + full grammar order',SEA),(43,464,'Capacity expression','Rule record + supported form',SEA),(323,242,'Repair weights','All repair-success sets',SKY),(323,353,'Controller witness','Model + weights + horizon',SKY),(323,464,'Cost assessment','Actual controller + ledger + prices',SKY)]:box(x,y,246,81,t,b,fil,ts=13,bs=11)
    for x in [166,446]:
        arrow([(x,323),(x,346)]);arrow([(x,434),(x,457)])
    label('The branches are not interchangeable certificates.',306,568,11,'Italic',MUTED,'center')
    end()
    #27 REVISION
    begin(27,'A stronger repair can invalidate an old proof','The conclusion “this controller is valid” and the conclusion “this change saves work” do not automatically survive together.','VII / Continued applicability',source('Counterexample 22.3; §24.3','35, 38-39'),('Repair and recheck','For the 32-case paired model, adding a universal repair invalidates the old weight constraints. Rebuilt weights permit a one-step, one-record controller.'),('Do not inherit the old performance claim','The earlier assessment referred to another controller and compilation. The replacement needs a new comparison. The unaffected arithmetic equation library remains applicable.'))
    stages=[(40,'BEFORE','Weight total 16','Controller: 5 calls / 31 records',SEA,TEAL),(224,'REVISE','Universal repair added','Old weight load is now 16 > 1',SAND,AMBER),(408,'RECHECK','Weight total 1','Controller: 1 call / 1 record',SEA,TEAL)]
    for x,h,t,b,f,col in stages:
        rect(x,227,164,203,f,None);label(h,x+82,243,10,'Bold',col,'center');para(t,x+14,281,136,18,24,'SerifBold',align=1,maxh=69);para(b,x+14,356,136,11.5,16,align=1,maxh=62)
    arrow([(206,329),(221,329)],AMBER,1.5);arrow([(390,329),(405,329)],TEAL,1.5)
    box(40,473,251,98,'Semantic result: valid','The new tree is checked under the new repair contract.',SEA,ts=13)
    box(321,473,251,98,'Old cost claim: blocked','It is not evidence about the new search or workload.',SAND,AMBER,ts=13)
    end()
    #28 LEDGER
    begin(28,'The same controller, opposite cost conclusions','Before claiming improvement, choose a common ledger and state the prices used to combine its event counts.','VII / Resource accounting',source('Proposition 25.1; Counterexample 25.2','39-40'),('The exact difference','These are old-minus-new search events on the same 32-case weighted problem. Scope and witness checks are equal and cancel only in this isolated difference.'),('What remains to charge','Weight preparation, equation acquisition, installed programs, storage, and revision management do not become free. Event counts alone do not determine processor time or energy.'))
    rows=[('Model-record reads','+1,552',SEA,TEAL),('Rational additions','+1,552',SEA,TEAL),('Capacity comparisons','−1,868',SAND,AMBER)]
    for i,(t,v,f,col) in enumerate(rows):
        y=214+i*59;rect(46,y,520,49,f,None,6);label(t,63,y+15,13,'Bold');label(v,548,y+11,23,'SerifBold',col,'right')
    label('Assign prices in that same order',306,414,12,'Bold',align='center')
    for x,pr,val,f,col in [(40,'(1, 1, 1)','+1,236',SEA,TEAL),(223,'(1, 0, 1)','−316',ROSE,RED),(406,'(0, 0, 1)','−1,868',ROSE,RED)]:
        rect(x,451,166,118,f,None);label(pr,x+83,468,14,'Math',INK,'center');label(val,x+83,501,25,'SerifBold',col,'center');label('priced units saved',x+83,543,10,'Body',MUTED,'center')
    end()
    #29 EVIDENCE
    begin(29,'Do not turn selection evidence into a fresh audit','What the improver has already inspected belongs to its developmental history, even when the inner solver never saw it.','VIII / Evidence and continuation',source('§26; Proposition 26.1','41-42'),('A claim has an evidence type','A proof supports a conditional statement. A checker validates a finite witness. A fresh performance audit supports a comparison on a declared task law.'),('None substitutes for the others','Repeatedly reading a “holdout” exposes it to the outer loop. A correct proof does not establish its physical premises. Finite algorithm counters are not independent neural trials.'))
    boxes=[(40,218,('Develop','Generate and revise candidates'),PALE),(224,218,('Select','Choose among alternatives'),SKY),(408,218,('Freeze','Candidate + comparator + budget'),SEA)]
    for x,y,(t,b),f in boxes:box(x,y,164,109,t,b,f,ts=14,bs=11.5)
    arrow([(206,272),(221,272)],MUTED,1.3);arrow([(390,272),(405,272)],MUTED,1.3)
    arrow([(490,328),(490,367),(306,367),(306,393)],TEAL)
    box(143,401,326,85,'Fresh assessment','Use a justified sampling and stopping rule.',SEA,ts=15,bs=12)
    para('Across attempts: valid conditional error allowances<br/>may be summed. Merely writing δ₁ + δ₂ + … ≤ δ<br/>does not make an invalid audit valid.',58,519,496,12,18,align=1,maxh=58)
    end()
    #30 SEQUENTIAL
    begin(30,'An audit can stop early without betting in hindsight','Choose the evidence update before seeing its paired score. Stopping after observing evidence is a different operation.','VIII / Evidence and continuation',source('Theorem 27.1; Counterexample 27.2','42-43'),('Valid order','Freeze the comparison, choose the next bet from past information, observe the next paired score, then update the evidence process.'),('The hindsight counterexample','With four fair ± scores, betting only after seeing a positive doubles the evidence on positives. The nominal threshold 4 is crossed on 11 of 16 paths, not at most 1/4.'))
    for x,t in [(43,'Choose λₜ'),(228,'Observe Yₜ'),(413,'Update Eₜ')]:box(x,211,158,59,t,'',SEA if x!=228 else SKY,ts=15)
    arrow([(203,242),(224,242)]);arrow([(388,242),(409,242)])
    label('HINDSIGHT CONTROL: all 16 fair four-score paths',306,305,10.5,'Bold',MUTED,'center')
    for i,bits in enumerate(itertools.product([0,1],repeat=4)):
        x=48+(i%4)*135;y=341+(i//4)*47;bad=sum(bits)>=2
        rect(x,y,119,34,ROSE if bad else PALE,None,6)
        label(' '.join('+' if q else '−' for q in bits),x+59.5,y+8,14,'Math',RED if bad else MUTED,'center')
    label('Highlighted: at least two positive scores',306,546,11,'Body',MUTED,'center')
    end()
    #31 COMMON POLICY
    begin(31,'Safe repetition is not guaranteed progress','An authorized attempt must be selected before its outcome is known. One policy must meet the continuation requirement on every allowed branch.','VIII / Evidence and continuation',source('Theorem 29.1; Counterexample 29.2','45-46'),('The finite theorem','Given fully observed lineage states, a finite attempt catalogue, and separately justified progress marks, the recurrence decides whether one policy guarantees k gains within h attempts.'),('The repeated-rejection path','If every attempt can reject and return to the same safe state, any finite horizon admits an all-rejection path. Safety can hold without a bounded sure gain.'))
    box(178,220,256,74,'Choose one admitted attempt','Before its outcome is observed',PALE,ts=14)
    arrow([(236,294),(166,346)]);arrow([(376,294),(446,346)],AMBER)
    box(40,358,254,102,'Checked improvement','Progress = 1<br/>Preserve required evidence and resources.',SEA,ts=14,bs=12)
    box(318,358,254,102,'Rejected candidate','Progress = 0<br/>Return to a safe configuration.',SAND,AMBER,ts=14,bs=12)
    arrow([(446,460),(446,489),(586,489),(586,256),(438,256)],AMBER,1.2,dash=(4,3))
    note(49,501,342,'Possible again does not mean guaranteed','This loop can repeat h times without any improvement. The supplied progress criterion cannot be replaced by “a file changed.”',h=83,bs=11)
    end()
    #32 ACCELERATION
    begin(32,'Positive gains need not accelerate','Recursion, continued improvement, and increasing productivity per unit resource are separate claims.','VIII / Evidence and continuation',source('Proposition 30.1; §30','46-47'),('A simple limiting example','The gains 1/2, 1/4, 1/8, … are all positive. Their accumulated total remains below 1 after every finite number of steps.'),('The missing additional argument','Faster improvement requires a claim about gain divided by complete discovery-and-acceptance cost. More headroom or a successful feedback loop does not establish it.'))
    label('Successive gains on a fixed bounded score',306,210,12,'Bold',align='center')
    base=423
    for i in range(6):
        x=61+i*85;hh=162/(2**i);rect(x,base-hh,55,hh,SEA if i%2==0 else SKY,None,2)
        label(['1/2','1/4','1/8','1/16','1/32','1/64'][i],x+27.5,base-hh-23,11,'Bold',TEAL,'center')
        label(str(i+1),x+27.5,base+16,10,'Body',MUTED,'center')
    line(47,base,564,base,LINE,1)
    note(54,482,504,'There is also a fixed-margin ceiling','On a nondecreasing score in [a,b], gains of at least γ > 0 can occur at most floor((b−a)/γ) times. Changing the score changes the comparison.',h=96,bs=12)
    end()
    #33 BRIDGE
    begin(33,'The learned semantic bridge is still a research target','A commuting square specifies meaningful reuse. It does not discover the representation, learn the operations, or demonstrate their use by a neural system.','IX / What remains open',source('§31; Proposition 31.1; §34','48-49, 52-53'),('The conditional result','If the domain is invariant, every admitted operation commutes with q, and q preserves the required output, the relation extends to every finite operation sequence.'),('The architectural proposal','Learning encoders, operations, experiment selectors, and proposers is a separate problem. The complete learned Neuralese–OSL bridge is not implemented in this edition.'))
    box(49,235,206,67,'Underlying state','x',PALE,ts=14,bs=15);box(357,235,206,67,'After operation','Fₐ(x)',PALE,ts=14,bs=15)
    box(49,436,206,67,'Retained meaning','q(x)',SEA,ts=14,bs=15);box(357,436,206,67,'Updated meaning','Gₐ(q(x))',SEA,ts=14,bs=15)
    arrow([(258,267),(352,267)],MUTED);label('Fₐ',306,238,15,'Math',MUTED,'center')
    arrow([(258,469),(352,469)],TEAL);label('Gₐ',306,440,15,'Math',TEAL,'center')
    arrow([(152,303),(152,429)],TEAL);label('q',130,357,18,'Math',TEAL)
    arrow([(460,303),(460,429)],TEAL);label('q',439,357,18,'Math',TEAL)
    label('q Fₐ = Gₐ q',306,359,23,'Math',INK,'center')
    pill('Specification ≠ discovery algorithm',83,552,446,PALE,INK,12,29)
    end()
    #34 SUMMARY LADDER
    begin(34,'Locate the recursive achievement exactly','The finite chain acquires objects at several levels. It does not erase the supplied foundations of the next outer level.','IX / What remains open',source('First-edition scope; §§23, 34','iii, 35-36, 52-53'),('What the construction supports','A generated equation library changes the search representation used to acquire later discovery rules, while preserving the specified evidence and final programs.'),('What it does not close','General intelligence, learned physical semantics, autonomous invention of the primitive proof system, and indefinite improvement of the equation learner remain open.'))
    headers=[('ACQUIRED OR CONSTRUCTED','STILL SUPPLIED')]
    label(headers[0][0],55,211,9.5,'Bold',TEAL);label(headers[0][1],340,211,9.5,'Bold',MUTED)
    rr=[('Diagnostic tree','Sensors and repair meanings'),('Improved compiler','Skeleton, bound, and checker'),('Pruning expression','Grammar, teacher, and features'),('Equations and quotient','Axioms and equation learner'),('Replayed certificates','Complete dependency registry')]
    for i,(a,b) in enumerate(rr):
        y=249+i*64;rect(40,y,532,53,SEA if i%2==0 else PALE,None,5)
        para(a,55,y+15,245,12,font='Bold',maxh=31);para(b,330,y+15,225,11.3,maxh=32)
    end()
    #35 GLOSSARY
    begin(35,'A small vocabulary for reading the proofs','Use these distinctions to avoid turning several different achievements into one word such as “intelligence” or “success.”','Reference / Concepts',source('Definitions 3.1, 6.1; §§5, 24-25','3, 5-7, 37-40'),('Keep the objects separate','The repair changes a target. The compiler discovers a policy. The learner can change a compiler rule. The equation library can change the learner’s candidate representation.'),('Keep the evidence separate','A witness is checked under a model. A proof has hypotheses. A resource claim has a ledger. A generalization claim needs evidence beyond semantic relabeling.'))
    glossary=[('Support','The cases still possible after the reports actually received.'),('Repair','An action with a specified set of cases in which it succeeds.'),('Controller','A complete branching investigation ending in justified repairs.'),('Compiler','The procedure that constructs or searches for controllers.'),('Quotient','A representation that groups expressions using checked equivalences.'),('Certificate','A witness tied to a claim, its inputs, and applicable assumptions.')]
    for i,(t,b) in enumerate(glossary):
        col=i%2;row=i//2;box(40+col*278,211+row*126,254,108,t,b,SEA if col==0 else PALE,ts=14,bs=11.3)
    end()
    #36 MAP
    begin(36,'Return to the source at the right level','This companion prioritizes mechanisms and counterexamples. The first-edition manuscript is the authority for complete hypotheses and proofs.','Reference / Reading routes','[S] Komorebi P., Self-Improving Intelligence, v1.0.0, 8 October 2026.',('Scope of this guide','All substantive claims are restatements or worked illustrations of [S]. Source statistics are attributed to the supplied first-edition records, not presented as new learning runs.'),('Verification boundary','The guide’s examples and numerical transcriptions were checked separately. The full original 336,867-assertion suite was not rerun to make this visual companion.'))
    rows=[('03-07','Comparison and eight-cell diagnosis','§§3-4, 6, 32'),('08-12','Investigation, uncertainty, transport','§§5-7, 9'),('13-15','Certified compiler revision','§§11-13, 16'),('16-20','Synthesis and safe pruning','§§14-16, 18'),('21-25','Repair scope and acquired equations','§§17, 19-23'),('26-28','Dependencies and complete costs','§§24-25'),('29-32','Evidence and recursive continuation','§§26-30'),('33-35','Architecture, boundaries, vocabulary','§§31-35')]
    label('GUIDE',52,211,9.5,'Bold',TEAL);label('TOPIC',128,211,9.5,'Bold',TEAL);label('MANUSCRIPT',457,211,9.5,'Bold',TEAL)
    for i,(p,t,s) in enumerate(rows):
        y=240+i*39;rect(40,y,532,34,PALE if i%2==0 else WHITE,None,3)
        label(p,52,y+10,10.2,'Bold',TEAL);para(t,128,y+8,312,10.2,maxh=24);label(s,559,y+10,10,'Body',MUTED,'right')
        C.linkRect('',f'p{int(p[:2])}',(40,H-y-34,572,H-y),relative=0,thickness=0)
    para('Included in the editable guide package: the unchanged source PDF,<br/>page-to-section crosswalk, diagram-generation code, data, and review notes.',49,560,514,10.3,14,align=1,maxh=30)
    end()
    C.save()
    return PAGES


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'Self_Improving_Intelligence_Visual_Guide_v1.0.0.pdf')
    args=parser.parse_args();args.output.parent.mkdir(parents=True,exist_ok=True)
    pages=build(args.output)
    (ROOT/'data').mkdir(exist_ok=True)
    (ROOT/'data/page_map.json').write_text(json.dumps(pages,indent=2,ensure_ascii=False)+'\n')
    with (ROOT/'data/source_crosswalk.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['page','title','chapter','source']);w.writeheader()
        for p in pages:w.writerow({k:p[k] for k in w.fieldnames})
    (ROOT/'validation').mkdir(exist_ok=True)
    (ROOT/'validation/text_layout.json').write_text(json.dumps({'page_count':len(pages),'fonts':FONT_RECORD,'text_boxes':TEXTBOXES},indent=2,ensure_ascii=False)+'\n')
    print(f'Built {len(pages)} vector pages: {args.output}')

if __name__=='__main__':main()
