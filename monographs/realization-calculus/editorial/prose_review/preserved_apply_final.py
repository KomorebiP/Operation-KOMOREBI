"""Apply only exact, bounded proposals to read-only preserved PDF input copies.

The root helper supplies native-font fitting, math snapshots, annotation handling,
and pixel comparisons. This extension adds bounded pure-prose spans/line tails and
a punctuation-only rectangle that leaves the adjoining mathematical number fixed.
"""
from pathlib import Path
import copy, hashlib, json, math, re, sys
import fitz
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import preserved_pdf_proofread as H
BASE=ROOT/'editorial/prose_review'
PLAN=BASE/'preserved_final_proposals.json'
OUT=BASE/'preserved_final_outputs'

def prepare(page,b,e):
    if e['kind']=='replace_exact_occurrence':
        rect=fitz.Rect(e['target_bbox']);hits=page.search_for(e['target_substring'],clip=rect+(-.03,-.03,.03,.03))
        if len(hits)!=1:raise ValueError('Exact target occurrence differs')
        chosen=[s for l in b['lines'] for s in l['spans'] if fitz.Rect(s['bbox']).intersects(rect)]
        if not chosen or any(H.ismath(s) for s in chosen):raise ValueError('Exact word target crosses mathematical spans')
        sty=H.native_style(chosen)
        for scale in [1,.99,.98,.97,.96,.95]:
            size=sty['size']*scale
            if sty['font'].text_length(e['new_text'],fontsize=size)<=rect.width+.04:
                # Italic f has a native left ink overhang. The paint/check box
                # includes that measured margin, while removal stays restricted
                # to the original word and cannot erase its neighbor.
                paint=fitz.Rect(rect);paint.x0-=2.1;paint.x1+=1.1
                removal=fitz.Rect(rect);removal.x1-=.05
                return [{'rect':paint,'redact_rect':removal,'new':e['new_text'],'draw':[{'origin':(rect.x0,chosen[0]['origin'][1]),'text':e['new_text'],'size':size}],'style':{k:v for k,v in sty.items() if k!='font'},'scale':scale}]
        raise ValueError('Exact word replacement cannot fit at >=95% original type size')
    if e['kind']=='replace_prose_spans':
        result=[]
        for old,new in e['span_substitutions']:
            spans=[s for s in H.all_spans(b) if s['text']==old]
            if len(spans)!=1 or H.ismath(spans[0]):raise ValueError('Expected one pure-prose span')
            s=spans[0]
            result.append(H.prepare_region(page,s['bbox'],new,[s],[{'bbox':s['bbox'],'spans':[s]}],allow_line_reflow=False))
        return result
    if e['kind']=='replace_pure_lines':
        lines=[b['lines'][i] for i in e['line_indexes']]
        if [''.join(s['text'] for s in l['spans']) for l in lines]!=e['old_lines_exact']:raise ValueError('Pure line anchors differ')
        spans=[s for l in lines for s in l['spans']]
        if any(H.ismath(s) for s in spans):raise ValueError('Selected line tail includes mathematics')
        rect=fitz.Rect(lines[0]['bbox'])
        for line in lines[1:]:rect|=fitz.Rect(line['bbox'])
        return [H.prepare_region(page,rect,e['new_text'],spans,lines)]
    if e['kind']=='remove_punctuation':
        anchors=page.search_for(e['anchor'],clip=fitz.Rect(b['bbox'])+(-.03,-.03,.03,.03))
        if len(anchors)!=1:raise ValueError('Punctuation sentence anchor is not unique')
        hits=page.search_for(e['target_substring'],clip=anchors[0]+(-.01,-.01,.01,.01))
        if len(hits)!=1:raise ValueError('Punctuation target is not unique')
        target=fitz.Rect(hits[0]);rect=fitz.Rect(target)
        # The math glyph ends at this left edge. Move inward so a rounding-level
        # intersection cannot erase it, and expand right only into blank space.
        rect.x0+=.05;rect.x1+=e['pad_right_points']
        rect.y0-=e['pad_vertical_points'];rect.y1+=e['pad_vertical_points']
        for bb in page.get_text('rawdict')['blocks']:
            if bb.get('type')!=0:continue
            for line in bb['lines']:
                for span in line['spans']:
                    for c in span['chars']:
                        rr=fitz.Rect(c['bbox'])
                        if not c['c'].isspace() and rr.intersects(rect) and c['c']!=e['target_substring']:
                            raise ValueError('Expanded punctuation rectangle touches another glyph: '+repr(c['c']))
        return [{'rect':rect,'new':'','draw':[],'style':{},'scale':1.0}]
    if e['kind']=='replace_table_cells':return H.prepare_table(page,b,e['cell_substitutions'])
    if e.get('math_spans_present'):
        return [H.targeted_region(page,b,a,z) for a,z in e['text_substitutions']]
    return [H.prepare_region(page,b['bbox'],e['new_text'],H.all_spans(b),b['lines'])]

def geometry(page):
    paths=page.get_drawings()
    for p in paths:p.pop('seqno',None)
    return paths

def remove_exact_text_object(doc,page,old):
    """Remove one pure-prose BT/ET object without rewriting other operators.

    The locator lines have one font and hex-encoded glyph strings. Decode their
    embedded ToUnicode map and require an exact nonspace-text match. Every byte
    outside that text object is retained, avoiding redaction's numeric rounding.
    """
    fonts={f[4]:f[0] for f in page.get_fonts(full=True)}
    def mapping(name):
        xref=fonts[name];typ,value=doc.xref_get_key(xref,'ToUnicode')
        if typ!='xref':return None
        cm=doc.xref_stream(int(value.split()[0])).decode('latin1');m={}
        for section in re.findall(r'beginbfchar(.*?)endbfchar',cm,re.S):
            for a,z in re.findall(r'<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>',section):m[int(a,16)]=bytes.fromhex(z).decode('utf-16-be')
        for section in re.findall(r'beginbfrange(.*?)endbfrange',cm,re.S):
            for a,b,z in re.findall(r'<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>',section):
                for code in range(int(a,16),int(b,16)+1):m[code]=(int(z,16)+code-int(a,16)).to_bytes(len(z)//2,'big').decode('utf-16-be')
        return m
    wanted=re.sub(r'\s','',old);matches=[]
    for xref in page.get_contents():
        stream=doc.xref_stream(xref)
        for hit in re.finditer(rb'\bBT\b.*?\bET\b',stream,re.S):
            obj=hit[0];fn=re.findall(rb'/([^\s/]+)\s+[-.\d]+\s+Tf',obj)
            if len(fn)!=1 or fn[0].decode() not in fonts:continue
            cmap=mapping(fn[0].decode());text=''
            for token in re.findall(rb'<([0-9A-Fa-f]+)>',obj):
                data=bytes.fromhex(token.decode())
                if cmap is None:text+=data.decode('cp1252')
                else:
                    if len(data)%2:break
                    text+=''.join(cmap.get(int.from_bytes(data[i:i+2],'big'),'\ufffd') for i in range(0,len(data),2))
            if re.sub(r'\s','',text)==wanted:matches.append((xref,hit.start(),hit.end(),stream))
    if len(matches)!=1:raise ValueError('Expected one exact standalone locator text object, found '+str(len(matches)))
    xref,start,end,stream=matches[0]
    replacement=stream[:start]+b'BT ET'+stream[end:]
    doc.update_stream(xref,replacement)
    return {'xref':xref,'removed_object_sha256':hashlib.sha256(stream[start:end]).hexdigest(),'bytes_outside_removed_text_object_unchanged':True}

def apply_component(basis,plan):
    cid=basis['component_id'];src=ROOT/basis['path'];dst=OUT/(cid+'.pdf')
    if H.sha(src)!=basis['sha256']:raise RuntimeError('Input hash differs: '+cid)
    doc=fitz.open(src);toc=doc.get_toc(simple=False);page_count=len(doc)
    assert page_count==basis['pages']
    image_streams={xref:hashlib.sha256(doc.xref_stream(xref)).hexdigest() for p in doc for xref,*_ in p.get_images(full=True)}
    all_math=[H.math_snapshot(p) for p in doc]
    report={'component_id':cid,'input_pdf':str(src.relative_to(ROOT)),'input_sha256':H.sha(src),'applied':[],'skipped':[],'pages':[]}
    by_page={}
    for i,e in enumerate(plan['edits']):
        if e['component_id']==cid:by_page.setdefault(e['page_1based']-1,[]).append((i,e))
    for pn,items in sorted(by_page.items()):
        page=doc[pn];before=H.pix(page,2);ann=H.annotations_snapshot(doc,page);drawings=geometry(page);regions=[]
        for index,e in items:
            try:
                b=H.find_block(page,e);prepared=prepare(page,b,e)
                for p in prepared:
                    if p.get('scale',1)<.95:raise ValueError('Type size below 95% floor')
                    if any(p['rect'].intersects(q['rect']) and (p['rect']&q['rect']).get_area()>.1 for q in regions):raise ValueError('Edit regions overlap')
                for p in prepared:p['proposal_index']=index
                regions.extend(prepared)
                report['applied'].append({'proposal_index':index,'page_1based':pn+1,'kind':e['kind'],'regions':[H.rect_values(p['rect']) for p in prepared],'scales':[p.get('scale',1) for p in prepared],'new_text':e['new_text'],'reason':e['reason']})
            except (ValueError,RuntimeError) as ex:report['skipped'].append({'proposal_index':index,'page_1based':pn+1,'reason':str(ex)})
        if not regions:continue
        if all(e['old_text_exact'].startswith('Traditional monograph:') for _,e in items):
            removals=[remove_exact_text_object(doc,page,e['old_text_exact']) for _,e in items]
            report.setdefault('stream_exact_locator_removals',[]).append({'page_1based':pn+1,'removals':removals})
            page=doc.reload_page(page)
        else:
            for p in regions:page.add_redact_annot(p.get('redact_rect',p['rect']),fill=False,cross_out=False)
            page.apply_redactions(images=0,graphics=0,text=0)
        for p in regions:
            if not p['draw']:continue
            sty=p['style'];fontname='RCFinalProse'+hashlib.sha256(sty['font_path'].encode()).hexdigest()[:12]
            page.insert_font(fontname=fontname,fontfile=sty['font_path'])
            for line in p['draw']:page.insert_text(line['origin'],line['text'],fontname=fontname,fontsize=line['size'],color=sty['color'],overlay=True)
        H.restore_annotations(doc,page,ann);page=doc.reload_page(page)
        if H.math_snapshot(page)!=all_math[pn]:raise RuntimeError(f'Math glyphs/positions changed: {cid} p{pn+1}')
        if H.annotations_snapshot(doc,page)!=ann:raise RuntimeError(f'Annotation objects changed: {cid} p{pn+1}')
        if geometry(page)!=drawings:raise RuntimeError(f'Vector geometry changed: {cid} p{pn+1}')
        after=H.pix(page,2);changed=np.any(before!=after,axis=2);mask=np.zeros(changed.shape,dtype=bool)
        for p in regions:
            r=p['rect'];x0=max(0,math.floor(r.x0*2)-2);y0=max(0,math.floor(r.y0*2)-2);x1=min(mask.shape[1],math.ceil(r.x1*2)+2);y1=min(mask.shape[0],math.ceil(r.y1*2)+2);mask[y0:y1,x0:x1]=True
        outside=int(np.count_nonzero(changed&~mask))
        if outside:
            yy,xx=np.where(changed&~mask)
            raise RuntimeError(f'{outside} changed pixels outside exact regions: {cid} p{pn+1}; pixel bounds {int(xx.min())},{int(yy.min())},{int(xx.max())},{int(yy.max())}')
        report['pages'].append({'page_1based':pn+1,'regions':len(regions),'outside_changed_pixels_at_144dpi':outside,'math_unchanged':True,'annotations_unchanged':True,'vector_geometry_unchanged':True})
    if doc.get_toc(simple=False)!=toc:raise RuntimeError('Outlines changed')
    for xref,digest in image_streams.items():
        if hashlib.sha256(doc.xref_stream(xref)).hexdigest()!=digest:raise RuntimeError('Image stream changed')
    for pn,page in enumerate(doc):
        if H.math_snapshot(page)!=all_math[pn]:raise RuntimeError(f'Global math snapshot changed: {cid} p{pn+1}')
    OUT.mkdir(exist_ok=True);doc.save(dst,garbage=0,deflate=True,no_new_id=True);doc.close()
    check=fitz.open(dst)
    assert len(check)==page_count and check.get_toc(simple=False)==toc
    for pn,page in enumerate(check):
        if H.math_snapshot(page)!=all_math[pn]:raise RuntimeError(f'Saved math snapshot changed: {cid} p{pn+1}')
    report.update(output_pdf=str(dst.relative_to(ROOT)),output_sha256=H.sha(dst),page_count_preserved=page_count,all_page_math_unchanged=True,image_streams_unchanged=True,outlines_unchanged=True,proposal_sha256=H.sha(PLAN))
    return report

def main():
    plan=json.loads(PLAN.read_text());reports=[]
    for basis in plan['source_basis']:
        report=apply_component(basis,plan);reports.append(report)
        (BASE/'preserved_final_apply_report.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2)+'\n')
        print(report['component_id'],len(report['applied']),'applied',len(report['skipped']),'skipped',flush=True)
    (BASE/'preserved_final_exact_journal.json').write_text(json.dumps([dict(e,proposal_index=i) for i,e in enumerate(plan['edits'])],ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
