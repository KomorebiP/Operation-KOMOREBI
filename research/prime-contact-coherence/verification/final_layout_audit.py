from __future__ import annotations
from pathlib import Path
import fitz, re, json, math, statistics

ROOT=Path('/mnt/data/final_verification_work')
PDF=ROOT/'Projector_Resolved_Prime_Contact_Coherence_Calculus_Final.pdf'
doc=fitz.open(PDF)

out_of_bounds=[]
low_content=[]
rotations=[]
visible_semicolons=0
header_pages=[]
header_overlap=[]
text_overlap=[]
blank_pages=[]
page_stats=[]


def area(rect):
    return max(0.0, rect.width)*max(0.0, rect.height)

for pi,page in enumerate(doc, start=1):
    rect=page.rect
    rotations.append(page.rotation)
    text=page.get_text()
    visible_semicolons += text.count(';')
    words=page.get_text('words')
    if not text.strip(): blank_pages.append(pi)
    body_words=[]
    header_words=[]
    for w in words:
        x0,y0,x1,y1,txt,*_=w
        if x0 < -0.5 or y0 < -0.5 or x1 > rect.width+0.5 or y1 > rect.height+0.5:
            out_of_bounds.append({'page':pi,'text':txt,'bbox':[x0,y0,x1,y1]})
        if y0 < 52:
            header_words.append((fitz.Rect(x0,y0,x1,y1),txt))
        if y0 > 52 and y1 < rect.height-45:
            body_words.append(txt)
    wc=len(re.findall(r"\b[\w'-]+\b",' '.join(body_words)))
    if wc < 25:
        low_content.append({'page':pi,'body_word_count':wc,'preview':text.strip().replace('\n',' ')[:180]})
    page_stats.append({'page':pi,'body_word_count':wc,'total_words':len(words)})
    if header_words:
        header_pages.append({'page':pi,'text':' '.join(t for _,t in header_words),'count':len(header_words)})
        for i,(r1,t1) in enumerate(header_words):
            for r2,t2 in header_words[i+1:]:
                inter=r1 & r2
                if not inter.is_empty and area(inter)>0.4:
                    header_overlap.append({'page':pi,'a':t1,'b':t2,'area':area(inter),'r1':list(r1),'r2':list(r2)})
    # Detect strong overlaps between distinct text spans, excluding nearly identical span boxes and math glyph crowding.
    spans=[]
    d=page.get_text('dict')
    for block in d.get('blocks',[]):
        if 'lines' not in block: continue
        for line in block['lines']:
            for span in line['spans']:
                s=span.get('text','').strip()
                if not s: continue
                r=fitz.Rect(span['bbox'])
                spans.append((r,s,span.get('size',0)))
    for i,(r1,s1,z1) in enumerate(spans):
        for r2,s2,z2 in spans[i+1:]:
            # same line adjacent glyph spans can touch; only flag meaningful area overlap
            inter=r1 & r2
            if inter.is_empty: continue
            ia=area(inter)
            if ia <= 2.0: continue
            small=min(area(r1),area(r2))
            if small<=0: continue
            frac=ia/small
            # Ignore superscript/subscript containment unless the overlap is almost total and both have several chars.
            if frac>0.35 and len(s1)>2 and len(s2)>2:
                # avoid duplicate invisible link text or exact duplicate rendering
                if s1==s2 and abs(r1.x0-r2.x0)<0.2 and abs(r1.y0-r2.y0)<0.2:
                    continue
                text_overlap.append({'page':pi,'a':s1[:80],'b':s2[:80],'fraction':frac,'r1':list(r1),'r2':list(r2)})

summary={
    'path':str(PDF),
    'pages':len(doc),
    'page_size':[doc[0].rect.width,doc[0].rect.height],
    'blank_pages':blank_pages,
    'low_content_pages':low_content,
    'out_of_bounds_words':out_of_bounds,
    'visible_semicolons':visible_semicolons,
    'unique_rotations':sorted(set(rotations)),
    'header_pages_count':len(header_pages),
    'header_overlap_count':len(header_overlap),
    'header_overlaps':header_overlap[:50],
    'strong_text_overlap_count':len(text_overlap),
    'strong_text_overlaps':text_overlap[:100],
    'body_word_count_min':min(x['body_word_count'] for x in page_stats),
    'body_word_count_median':statistics.median(x['body_word_count'] for x in page_stats),
    'body_word_count_max':max(x['body_word_count'] for x in page_stats),
    'header_samples':header_pages[:8]+header_pages[-8:],
}
(ROOT/'final_layout_audit.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k not in {'strong_text_overlaps','header_overlaps','out_of_bounds_words','low_content_pages','header_samples'}},indent=2))
print('low-content:',low_content)
print('header overlaps:',header_overlap[:5])
print('strong overlaps sample:',text_overlap[:10])
