#!/usr/bin/env python3
"""Resolve the preserved arithmetic atlas's reader-facing routes after book layout.

Only navigation rectangles and their annotations are changed. The original
77-page companion remains the zero-based remote-link target; visible folios are
computed from the final book map. An atomic save follows preservation checks.
"""
from pathlib import Path
import hashlib, json, math, os, re, tempfile
import fitz
import numpy as np

ROOT = Path(__file__).resolve().parent

def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def _lines(page):
    return [line for block in page.get_text('dict')['blocks'] for line in block.get('lines', [])]

def _text(line):
    return ''.join(s['text'] for s in line['spans'])

def _color(value):
    return (((value >> 16) & 255)/255, ((value >> 8) & 255)/255, (value & 255)/255)

def _fonts(doc):
    cache = {}
    for page in doc:
        for row in page.get_fonts():
            name = row[3].split('+')[-1]
            if name not in cache:
                data = doc.extract_font(row[0])[3]
                if data:
                    font = fitz.Font(fontbuffer=data)
                    replacements={'URWPalladioL-Roma':'P052-Roman.otf','NimbusSanL-Regu':'NimbusSans-Regular.otf','NimbusSanL-Bold':'NimbusSans-Bold.otf'}
                    if name in replacements and any(not font.has_glyph(ord(ch)) for ch in 'Book page XI.0123456789'):
                        full=Path('/usr/share/fonts/opentype/urw-base35')/replacements[name]
                        data=full.read_bytes();font=fitz.Font(fontbuffer=data)
                    cache[name] = (data, font)
                    aliases={'Nimbus Sans Bold':'NimbusSans-Bold','Nimbus Sans Regular':'NimbusSans-Regular','P052 Roman':'P052-Roman'}
                    if name in aliases:cache[aliases[name]]=(data,font)
    return cache

def _outside_chars(page, boxes):
    answer=[]
    for block in page.get_text('rawdict')['blocks']:
        for line in block.get('lines', []):
            for span in line['spans']:
                for char in span['chars']:
                    r=fitz.Rect(char['bbox'])
                    if r.width==0:r.x1=r.x0+.001
                    if r.height==0:r.y1=r.y0+.001
                    if not any(r.intersects(b) for b in boxes):
                        answer.append((char['c'], tuple(round(v,3) for v in char['origin'])))
    return sorted(answer)

def _image_signature(page):
    return sorted((x['width'],x['height'],x['colorspace'],bytes(x['digest']).hex(),tuple(round(v,4) for v in x['bbox'])) for x in page.get_image_info(hashes=True))

def _pixel_changes_outside(a,b,boxes):
    pa,pb=a.get_pixmap(alpha=False,annots=False),b.get_pixmap(alpha=False,annots=False)
    aa=np.frombuffer(pa.samples,dtype=np.uint8).reshape(pa.height,pa.width,pa.n)
    bb=np.frombuffer(pb.samples,dtype=np.uint8).reshape(pb.height,pb.width,pb.n)
    if aa.shape!=bb.shape:raise ValueError('Atlas page geometry changed')
    diff=np.any(aa!=bb,axis=2)
    for r in boxes:
        # Two raster pixels cover antialiasing at the rectangle boundary.
        x0=max(0,math.floor(r.x0)-2);y0=max(0,math.floor(r.y0)-2)
        x1=min(pa.width,math.ceil(r.x1)+2);y1=min(pa.height,math.ceil(r.y1)+2)
        diff[y0:y1,x0:x1]=False
    return int(diff.sum())

def normalize_atlas_routes(spec, *, root=None, report_path=None):
    root=Path(root or ROOT)
    comps={c['id']:c for p in spec['parts'] for c in p['components']}
    atlas,progress=comps['XI_research_atlas'],comps['XI_research_progress']
    path=root/atlas['path'];source_path=root/progress['path']
    route_data=json.loads((root/'editorial/book_revision/preserved_prose_edits.json').read_text())['atlas_source_routes']
    if len(route_data)!=32:raise ValueError('Expected the 32 verified atlas routes')
    source=fitz.open(source_path)
    if len(source)!=77:raise ValueError('Arithmetic source page count changed; re-resolve atlas routes first')
    source.close()
    original=fitz.open(path);doc=fitz.open(path);font_cache=_fonts(doc)
    plans={};new_links={};rows=[]
    def plan(pn,box,runs,kind,old):
        page=doc[pn];box=fitz.Rect(box)
        # Runs retain native fonts. Test every glyph and horizontal extent before mutation.
        for run in runs:
            buf,font=font_cache[run['font']]
            if any(not font.has_glyph(ord(ch)) for ch in run['text'] if not ch.isspace()):
                raise ValueError(f'Missing native glyph in {kind} on atlas page {pn+1}')
            width=font.text_length(run['text'],fontsize=run['size'])
            if run['x']+width>box.x1+0.05 or run['x']<box.x0-0.05:
                raise ValueError(f'Unsafe navigation fit in {kind} on atlas page {pn+1}')
        plans.setdefault(pn,[]).append({'bbox':list(box),'runs':runs,'kind':kind,'old_text':old})
    def run(span,text,x=None,size=None):
        return {'text':text,'x':span['origin'][0] if x is None else x,'y':span['origin'][1], 'size':span['size'] if size is None else size,'font':span['font'],'color':span['color']}
    for record in route_data:
        n=int(record['plate'].split('.')[-1]);pn=record['source_local_page']-1;sp=record['destination_original_local_page']-1
        if str(sp) not in progress['book_pages']:raise ValueError(f'Atlas source page {sp+1} is not selected')
        folio=progress['book_pages'][str(sp)]-9
        candidates=[l for l in _lines(doc[pn]) if _text(l).startswith('Companion source:')]
        if len(candidates)!=1:raise ValueError(f'Expected one footer on atlas page {pn+1}')
        line=candidates[0];text=_text(line)
        if not re.search(r'(?:PDF|Book) page \d+(?: onward)?',text):raise ValueError(f'Unknown source footer: {text}')
        tail=text[len('Companion source:'):]
        tail=re.sub(r'(?:PDF|Book) page \d+(?: onward)?',f'Book page {folio}',tail)
        bold=line['spans'][0];regular=line['spans'][-1];size=8.0;x=bold['origin'][0]
        prefix=run(bold,'Companion source:',x,size)
        x2=x+font_cache[bold['font']][1].text_length(prefix['text'],fontsize=size)
        suffix=run(regular,tail,x2,size)
        box=fitz.Rect(58,line['bbox'][1]-.5,560,line['bbox'][3]+.5)
        plan(pn,box,[prefix,suffix],'companion_footer',text)
        new_links.setdefault(pn,[]).append({'kind':fitz.LINK_GOTOR,'from':fitz.Rect(58,box.y0,560,box.y1+1),'file':source_path.name,'page':sp,'to':fitz.Point(0,0),'zoom':0})
        # Concordance labels and page column are separate from mathematical titles.
        cp=record['concordance_local_page']-1;ls=_lines(doc[cp])
        labels=[l for l in ls if re.fullmatch(r'(?:V0?'+str(n)+r'|(?:Plate )?XI\.'+str(n)+r')',_text(l))]
        if len(labels)!=1:raise ValueError(f'Expected concordance label XI.{n}')
        label=labels[0];span=label['spans'][0];y=span['origin'][1]
        column=[l for l in ls if abs(l['spans'][0]['origin'][1]-y)<.2 and l['bbox'][0]>475 and _text(l).isdigit()]
        if len(column)!=1:raise ValueError(f'Expected one source-page cell for plate XI.{n}')
        page_line=column[0];ps=page_line['spans'][0]
        plan(cp,fitz.Rect(86,span['bbox'][1]-.4,130,span['bbox'][3]+.4),[run(span,f'XI.{n}')],'concordance_plate_label',_text(label))
        width=font_cache[ps['font']][1].text_length(str(folio),fontsize=ps['size'])
        box=fitz.Rect(480,ps['bbox'][1]-.4,526,ps['bbox'][3]+.4)
        plan(cp,box,[run(ps,str(folio),524.694-width)],'concordance_book_folio',_text(page_line))
        new_links.setdefault(cp,[]).append({'kind':fitz.LINK_GOTOR,'from':fitz.Rect(480,box.y0,526,box.y1),'file':source_path.name,'page':sp,'to':fitz.Point(0,0),'zoom':0})
        rows.append({'plate':f'XI.{n}','atlas_page_1based':pn+1,'source_page_1based':sp+1,'book_folio':folio})
    # The opening reading map uses the same qualified plate identifiers.
    opening=0
    for line in _lines(doc[1]):
        match=re.fullmatch(r'(?:V(\d+)–V(\d+)|XI\.(\d+)–XI\.(\d+))',_text(line))
        if match:
            nums=[v for v in match.groups() if v is not None]
            span=line['spans'][0];label=f'XI.{int(nums[0])}–XI.{int(nums[1])}'
            plan(1,fitz.Rect(74,line['bbox'][1]-5,140,line['bbox'][3]+3),[run(span,label,size=9)],'opening_plate_range',_text(line));opening+=1
    if opening!=5:raise ValueError('Expected five opening atlas plate ranges')
    for pn in (34,35):
        headers=[l for l in _lines(doc[pn]) if _text(l) in ('PDF page','Book page')]
        if len(headers)!=1:raise ValueError('Expected one concordance page heading')
        line=headers[0];span=line['spans'][0]
        plan(pn,fitz.Rect(480,line['bbox'][1]-.4,526,line['bbox'][3]+.4),[run(span,'Book page',480,8)],'concordance_heading',_text(line))
    # Explain the new convention explicitly, rather than leave an incorrect PDF-page legend.
    legends=[b for b in doc[34].get_text('dict')['blocks'] if b.get('lines') and _text(b['lines'][0]).startswith(('Page numbers below are physical','The page numbers below refer'))]
    if len(legends)!=1:raise ValueError('Expected one concordance pagination legend')
    b=legends[0];ls=b['lines'];s=ls[0]['spans'][0]
    runs=[run(s,'The page numbers below refer to the arithmetic studies in this book.')]
    if len(ls)<2:raise ValueError('Expected two-line concordance legend')
    runs.append(run(ls[1]['spans'][0],'Each plate also has a direct link to its source argument.'))
    plan(34,fitz.Rect(58,b['bbox'][1]-.4,560,b['bbox'][3]+.4),runs,'concordance_legend','\n'.join(_text(l) for l in ls))
    # Editorial prose no longer claims that the displayed research reader is unchanged.
    scope_text='The source package includes editable atlas material, model data, a figure generator and test runner. The first part of the research study remains a preserved reader because its complete earlier editable archive has not been recovered.'
    scope_blocks=[b for b in doc[34].get_text('dict')['blocks'] if b.get('lines') and _text(b['lines'][0]).startswith(('The new plate files','The source package includes editable atlas material'))]
    if len(scope_blocks)!=1:raise ValueError('Expected one editable-atlas source scope paragraph')
    block=scope_blocks[0];old_lines=block['lines'];span=old_lines[0]['spans'][0]
    font=font_cache[span['font']][1];available=560-span['origin'][0]
    wrapped=[];current=''
    for word in scope_text.split():
        candidate=(current+' '+word).strip()
        if current and font.text_length(candidate,fontsize=span['size'])>available:
            wrapped.append(current);current=word
        else:current=candidate
    if current:wrapped.append(current)
    if len(wrapped)>len(old_lines):raise ValueError('Source-scope paragraph does not fit its preserved rectangle')
    runs=[run(old_lines[i]['spans'][0],line) for i,line in enumerate(wrapped)]
    plan(34,fitz.Rect(58,block['bbox'][1]-.4,560,block['bbox'][3]+.4),runs,'source_scope_claim','\n'.join(_text(l) for l in old_lines))
    before_hash=_sha(path);restored_links=0
    for pn,items in plans.items():
        page=doc[pn];boxes=[fitz.Rect(x['bbox']) for x in items]
        # Preserve links whose text is replaced, except obsolete source-footer and
        # page-column remote links, which are replaced below by current routes.
        restore=[]
        for link in page.get_links():
            intersects=any(link['from'].intersects(b) for b in boxes)
            is_replaced_remote=link.get('kind')==fitz.LINK_GOTOR and any(link['from'].intersects(z['from']) for z in new_links.get(pn,[]))
            if is_replaced_remote:
                page.delete_link(link)
            elif intersects:
                saved={k:v for k,v in link.items() if k not in ('xref','id','nameddest')}
                if saved['kind']==fitz.LINK_NAMED and 'page' in saved:saved['kind']=fitz.LINK_GOTO
                restore.append(saved);page.delete_link(link)
        for b in boxes:page.add_redact_annot(b,fill=None,cross_out=False)
        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE,graphics=fitz.PDF_REDACT_LINE_ART_NONE,text=fitz.PDF_REDACT_TEXT_REMOVE)
        for item in items:
            for r in item['runs']:
                resource='ABR'+hashlib.sha256(r['font'].encode()).hexdigest()[:10]
                page.insert_font(fontname=resource,fontbuffer=font_cache[r['font']][0])
                page.insert_text((r['x'],r['y']),r['text'],fontname=resource,fontsize=r['size'],color=_color(r['color']),overlay=True)
        for link in restore:page.insert_link(link);restored_links+=1
        for link in new_links.get(pn,[]):page.insert_link(link)
    fd,temp=tempfile.mkstemp(prefix='atlas_book_routes_',suffix='.pdf',dir=path.parent);os.close(fd)
    try:
        doc.save(temp,garbage=3,deflate=True,no_new_id=True);doc.close()
        check=fitz.open(temp);checks=[]
        if len(check)!=len(original):raise ValueError('Atlas page count changed')
        for pn in range(len(check)):
            boxes=[fitz.Rect(x['bbox']) for x in plans.get(pn,[])]
            ca,cb=_outside_chars(original[pn],boxes),_outside_chars(check[pn],boxes)
            if len(ca)!=len(cb) or any(a[0]!=b[0] or max(abs(x-y) for x,y in zip(a[1],b[1]))>.002 for a,b in zip(ca,cb)):
                raise ValueError(f'Non-navigation text changed on atlas page {pn+1}')
            if _image_signature(original[pn])!=_image_signature(check[pn]):raise ValueError(f'Atlas image changed on page {pn+1}')
            delta=_pixel_changes_outside(original[pn],check[pn],boxes)
            if delta:raise ValueError(f'{delta} pixels changed outside navigation geometry on page {pn+1}')
            checks.append({'page_1based':pn+1,'outside_text_identical':True,'images_identical':True,'pixels_changed_outside_rectangles':delta})
        remotes=[l for p in check for l in p.get_links() if l.get('kind')==fitz.LINK_GOTOR and Path(l.get('file','')).name==source_path.name]
        if len(remotes)!=64:raise ValueError(f'Expected 32 footer and 32 concordance source links, found {len(remotes)}')
        check.close();original.close();os.replace(temp,path)
    except Exception:
        try:doc.close()
        except Exception:pass
        original.close();Path(temp).unlink(missing_ok=True);raise
    atlas['numeric_remotes_edition']='current';atlas['sha256']=_sha(path)
    report={'schema':'realization-calculus.atlas-book-routes/1','status':'PASS','before_sha256':before_hash,'after_sha256':atlas['sha256'],'pages':36,'routes':rows,'source_links':64,'footer_links':32,'concordance_links':32,'preserved_label_links':restored_links,'numeric_remotes_edition':'current','folio_rule':'final zero-based book_index minus 9','edits':[dict(page_1based=pn+1,**e) for pn,es in plans.items() for e in es],'checks':checks}
    destination=Path(report_path) if report_path else root/'book/atlas_book_routes_report.json'
    destination.parent.mkdir(parents=True,exist_ok=True);destination.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    return report
