#!/usr/bin/env python3
"""Remove redundant reader furniture from display copies, retaining source pages.

This is a publication operation. Original inputs and mathematical content are
kept separately. Every removed text region is recorded for review.
"""
from pathlib import Path
import hashlib, json, re, os, tempfile
import fitz
from rebrand_components import _outside_text, _snapshot, _vector_difference

def outside_text(page, boxes):
    # PDF ligatures can expose zero-width continuation characters. They still
    # belong to a redacted line and must be tested by their origin rectangle.
    chars=[]
    for block in page.get_text('rawdict')['blocks']:
        for line in block.get('lines',[]):
            for span in line['spans']:
                for char in span['chars']:
                    rect=fitz.Rect(char['bbox'])
                    if rect.width==0:rect.x1=rect.x0+.001
                    if rect.height==0:rect.y1=rect.y0+.001
                    if not any(rect.intersects(box) for box in boxes):chars.append(char['c'])
    return ''.join(''.join(chars).split())


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def lines(page):
    ans=[]
    for block in page.get_text('dict')['blocks']:
        for line in block.get('lines',[]):
            ans.append({'text':''.join(s['text'] for s in line['spans']),
                        'rect':fitz.Rect(line['bbox']), 'spans':line['spans']})
    return ans


def normalize_preserved_palette(path, component_id):
    """Replace only known publication palette operands in page text streams.

    External form/image objects (including scientific plot palettes) are not
    traversed. Geometry, character content, image data and annotations stay put.
    """
    if component_id not in ('IV_visual','XI_research_progress','XI_research_atlas'):
        return {'status':'not_applicable'}
    palettes=[
        ((.129,.231,.204), '#22282C'),((.12941,.23137,.20392),'#22282C'),
        ((.129,.169,.204),'#22282C'),((.12941,.16864,.20392),'#22282C'),
        ((.184,.392,.322),'#7B4165'),((.18431,.39217,.32158),'#7B4165'),
        ((.141,.365,.376),'#7B4165'),((.14119,.36472,.37646),'#7B4165'),
        ((.337,.404,.373),'#615963'),((.33725,.40392,.37256),'#615963'),
        ((.345,.392,.420),'#615963'),
        ((.739,.806,.783),'#D9CDD7'),((.73898,.8055,.78291),'#D9CDD7'),
        ((.690,.769,.742),'#D9CDD7'),
        ((.957,.949,.914),'#F5F1F5'),((.95686,.94902,.91374),'#F5F1F5'),
        ((.97424,.98094,.9813),'#F5F1F5'),((.93333,.95294,.94902),'#F5F1F5'),
    ]
    path=Path(path);before=sha(path);doc=fitz.open(path);original=fitz.open(path)
    pattern=re.compile(rb'(?<![\d.])([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+(rg|RG)\b')
    replacements=[];seen=set()
    for page in doc:
        for xref in page.get_contents():
            if xref in seen:continue
            seen.add(xref);stream=doc.xref_stream(xref)
            def replace(match):
                color=tuple(float(match.group(i)) for i in (1,2,3))
                hit=next((new for old,new in palettes if max(abs(a-b) for a,b in zip(color,old))<.00008),None)
                if not hit:return match.group()
                rgb=[int(hit[i:i+2],16)/255 for i in (1,3,5)]
                replacements.append({'page':page.number+1,'from_rgb':color,'to_hex':hit,'operator':match.group(4).decode()})
                return (' '.join(f'{v:.7f}' for v in rgb)+' '+match.group(4).decode()).encode()
            changed=pattern.sub(replace,stream)
            if changed!=stream:doc.update_stream(xref,changed)
    def without_palette(value):
        if isinstance(value,dict):return {k:without_palette(v) for k,v in value.items() if k not in ('color','fill')}
        if isinstance(value,list):return [without_palette(v) for v in value]
        return value
    for a,b in zip(original,doc):
        if a.get_text()!=b.get_text():raise ValueError('Palette normalization changed text')
        sa,sb=_snapshot(a),_snapshot(b)
        if sa['links']!=sb['links'] or sa['images']!=sb['images']:raise ValueError('Palette normalization changed links/images')
        _vector_difference(without_palette(sa['drawings']),without_palette(sb['drawings']))
    name=path.with_suffix('.palette.pdf');doc.save(name,garbage=3,deflate=True,no_new_id=True)
    doc.close();original.close();os.replace(name,path)
    return {'status':'PASS','before_sha256':before,'after_sha256':sha(path),'replacements':replacements,
            'scope':'Known publication palette only. Text, mathematical glyphs, vector geometry, links and image data unchanged; external scientific figure objects untouched.'}


def adapt_component(path, component_id, preserved=False):
    path=Path(path);before=sha(path);doc=fitz.open(path);original=fitz.open(path)
    edits=[]
    override_file=Path(__file__).resolve().parent/'editorial/book_revision/frontmatter_keep_overrides.json'
    overrides={r['component_id']:r for r in json.loads(override_file.read_text())['components']}
    override=overrides[component_id]
    if override['pages']!=len(doc):raise ValueError('Reviewed front matter map is stale: '+component_id)
    dropped={p-1:'Reviewed redundant front matter or integrated verification record; see frontmatter_keep_overrides.json for exact rationale.' for p in override['exclude_pages_1based']}
    mixed={r['page_1based']-1:r for r in override['mixed_toc_regions']}
    for number,page in enumerate(doc):
        page_lines=lines(page)
        if number in mixed and number not in dropped:
            box=fitz.Rect(mixed[number]['remove_bbox'])
            edits.append({'page':number+1,'kind':'local_contents','bbox':list(box),
                          'removed_text':mixed[number]['navigation_text_exact']})
            page.add_redact_annot(box,fill=None,cross_out=False)
        if preserved and number not in dropped:
            for line in page_lines:
                box=line['rect']
                if box.y1<49 or box.y0>742:
                    edits.append({'page':number+1,'kind':'repeated_furniture','bbox':list(box),
                                  'removed_text':line['text']})
                    page.add_redact_annot(box,fill=None,cross_out=False)
            if component_id=='IV_visual':
                plate=[x for x in page_lines if 52<x['rect'].y0<78 and re.fullmatch(r'V\d+',x['text'].strip())]
                if plate:
                    row=[x for x in page_lines if abs(x['rect'].y0-plate[0]['rect'].y0)<1]
                    row.sort(key=lambda x:x['rect'].x0)
                    number_text=plate[0]['text'].strip()[1:]
                    label='PLATE IV.'+str(int(number_text))+'  /  '+' '.join(x['text'].strip() for x in row if x not in plate and x['text'].strip()!='/')
                    box=fitz.Rect(58,plate[0]['rect'].y0-.3,555,max(x['rect'].y1 for x in row)+.3)
                    edits.append({'page':number+1,'kind':'qualified_plate','bbox':list(box),'removed_text':' '.join(x['text'] for x in row),'replacement':label,'origin':[62.64,plate[0]['spans'][0]['origin'][1]],'font_size':7.8})
                    page.add_redact_annot(box,fill=None,cross_out=False)
            if component_id=='XI_research_atlas':
                for line in page_lines:
                    match=re.fullmatch(r'WORKED PLATE V(\d+)',line['text'].strip())
                    if match:
                        edits.append({'page':number+1,'kind':'qualified_plate','bbox':list(line['rect']),'removed_text':line['text'],'replacement':'PLATE XI.'+str(int(match.group(1))),'origin':list(line['spans'][0]['origin']),'font_size':8})
                        page.add_redact_annot(line['rect'],fill=None,cross_out=False)
        if any(e['page']==number+1 for e in edits):
            page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE,graphics=fitz.PDF_REDACT_LINE_ART_NONE,text=fitz.PDF_REDACT_TEXT_REMOVE)
            for edit in [e for e in edits if e['page']==number+1 and 'replacement' in e]:
                page.insert_text(fitz.Point(edit['origin']),edit['replacement'],fontname='hebo',fontsize=edit['font_size'],color=(.482,.255,.396))
    page_count=len(doc)
    if edits:
        handle,name=tempfile.mkstemp(prefix=path.stem+'_book_',suffix='.pdf',dir=path.parent);os.close(handle)
        doc.save(name,garbage=3,deflate=True,no_new_id=True);doc.close()
        check=fitz.open(name);checks=[]
        try:
            for number,page in enumerate(check):
                boxes=[fitz.Rect(e['bbox']) for e in edits if e['page']==number+1]
                if outside_text(original[number],boxes)!=outside_text(page,boxes):
                    raise ValueError(f'Unexpected noneditorial text change in {component_id} page {number+1}')
                a,b=_snapshot(original[number]),_snapshot(page)
                delta=_vector_difference(a['drawings'],b['drawings'])
                if a['images']!=b['images']:
                    raise ValueError(f'Unexpected image change in {component_id} page {number+1}')
                checks.append({'page':number+1,'noneditorial_text_identical':True,'images_identical':True,'vector_structure_preserved':True,'max_vector_reserialization_delta_pt':delta})
        except:
            check.close();Path(name).unlink(missing_ok=True);original.close();raise
        check.close();os.replace(name,path)
    else:doc.close();checks=[]
    original.close()
    return {'component_id':component_id,'before_sha256':before,'after_sha256':sha(path),
            'source_pages':page_count,'excluded_pages':[{'page':p+1,'reason':reason} for p,reason in sorted(dropped.items())],
            'keep_pages':[p for p in range(page_count) if p not in dropped],
            'text_edits':edits,'checks':checks,'scope':'Reader furniture, redundant contents and plate labels only; mathematical source untouched.'}
