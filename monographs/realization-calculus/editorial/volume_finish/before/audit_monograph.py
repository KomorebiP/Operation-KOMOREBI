#!/usr/bin/env python3
"""Independent structural/content audit of the assembled core monograph.

Read-only with respect to PDFs and assembler source. This verifies publication
assembly, not mathematical correctness or a fresh formal replay.
"""
from pathlib import Path
import argparse
import collections
import hashlib
import json
import re
import sys
import unicodedata
from urllib.parse import unquote, urlsplit, parse_qs

import fitz

ROOT = Path(__file__).resolve().parent
TOL = 0.75


def sha(path):
    with open(path, 'rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def normalized(text):
    text = unicodedata.normalize('NFKC', text)
    return ''.join(c for c in text if not c.isspace() and c not in '\u00ad\u200b\ufeff')


def subsequence(needle, haystack):
    """Ignore only inserted material; never reorder the source characters."""
    j = 0
    for c in haystack:
        if j < len(needle) and c == needle[j]:
            j += 1
    return j == len(needle)


def transform_rect(box, transform):
    scale, tx, ty = transform
    r = fitz.Rect(box)
    return fitz.Rect(r.x0 * scale + tx, r.y0 * scale + ty,
                     r.x1 * scale + tx, r.y1 * scale + ty)


def within(box, page, tol=TOL):
    r, p = fitz.Rect(box), fitz.Rect(page)
    return r.x0 >= p.x0-tol and r.y0 >= p.y0-tol and r.x1 <= p.x1+tol and r.y1 <= p.y1+tol


def spans(page):
    result = []
    for block in page.get_text('dict')['blocks']:
        if block.get('type') != 0:
            continue
        for line in block.get('lines', []):
            for span in line.get('spans', []):
                if span.get('text', '').strip():
                    result.append(span)
    return result


def annotation_xrefs(doc, page):
    kind, value = doc.xref_get_key(page.xref, 'Annots')
    if kind == 'xref':
        ref = int(value.split()[0])
        value = doc.xref_object(ref, compressed=True)
    return [int(x) for x in re.findall(r'(\d+)\s+\d+\s+R', value)] if kind != 'null' else []


def inspect_action(doc, xref):
    kind, value = doc.xref_get_key(xref, 'A')
    if kind == 'xref':
        action = int(value.split()[0])
        prefix = ''
    elif kind == 'dict':
        action = xref
        prefix = 'A/'
    else:
        return None
    def get(key):
        return doc.xref_get_key(action, prefix + key)
    return get



def resolve_page(components, leaves, cid, raw):
    """Independent redirect walk. Return the selected page or explicit leaf."""
    seen=set();redirected=False
    while True:
        if (cid,raw) in seen:raise ValueError('Redirect cycle')
        seen.add((cid,raw))
        if cid not in components:raise ValueError('Unknown target component '+cid)
        c=components[cid]
        if not isinstance(raw,int) or not 0<=raw<c['pages']:raise ValueError('Target raw page out of range')
        if str(raw) in c['book_pages']:
            return {'book_index':c['book_pages'][str(raw)],'component_id':cid,'source_page':raw,'redirected':redirected}
        r=c.get('redirects',{}).get(str(raw))
        if r is None:raise ValueError('Omitted page has no explicit redirect')
        redirected=True
        if 'leaf_id' in r:
            if r['leaf_id'] not in leaves:raise ValueError('Unknown redirect leaf')
            return {'book_index':leaves[r['leaf_id']]['book_index'],'leaf_id':r['leaf_id'],'redirected':True}
        cid,raw=r['component_id'],r['source_page']


def expected_transform(source, index, front_count, comp=None, raw=None):
    folio=index-front_count+1
    preserved=bool(comp and (comp['build_kind']=='preserved_pdf' or any(a<=raw+1<=b for a,b in comp.get('preserved_page_spans',[]))))
    if preserved and not comp.get('display_normalized',False):
        scale=min(564/source.rect.width,686/source.rect.height)
        return [scale,24+(564-source.rect.width*scale)/2,55+(686-source.rect.height*scale)/2]
    return [1.0,6.0 if folio%2 else -6.0,0.0]


def serial(value):
    if isinstance(value,dict):return {str(k):serial(v) for k,v in value.items()}
    if isinstance(value,(list,tuple,fitz.Rect,fitz.Point)):return [serial(v) for v in value]
    return value


def transform_point(point, transform):
    return [point[0]*transform[0]+transform[1],point[1]*transform[0]+transform[2]]


def clamp_point(point):
    return [max(0,min(612,point[0])),max(0,min(792,point[1]))]



def audit_navigation(root, spec, docs, book, page_map, error, stats):
    """Authenticate emitted records against actual source links and PDF actions."""
    components={c['id']:c for p in spec['parts'] for c in p['components']}
    leaves={l['id']:l for l in spec['leaves']}
    names={cid:doc.resolve_names() for cid,doc in docs.items()}
    aliases={}
    for cid,c in components.items():
        for name in [Path(c['path']).name,Path(c['baseline_path']).name]+c.get('aliases',[]):
            aliases[Path(unquote(name).replace('\\','/')).name]=cid
    records=json.loads((root/'book/resolved_link_map.json').read_text())
    actual={i:[l for l in page.get_links() if l['kind'] in (fitz.LINK_GOTO,fitz.LINK_URI)] for i,page in enumerate(book)}
    used=collections.defaultdict(set)
    def near(a,b,tol=.06):return len(a)==len(b) and max((abs(x-y) for x,y in zip(a,b)),default=0)<=tol
    def named(cid,name):
        dest=names[cid].get(name)
        if not dest or not 0<=dest.get('page',-1)<len(docs[cid]):raise ValueError('Missing source named destination '+str(name))
        raw=dest['page'];xy=dest.get('to',(0,docs[cid][raw].rect.height))
        return raw,[xy[0],docs[cid][raw].rect.height-xy[1]]
    def internal(cid,raw,point):
        route=resolve_page(components,leaves,cid,raw)
        target=route['book_index']
        if route['redirected']:point=[0,0]
        else:point=clamp_point(transform_point(point,page_map[target]['transform']))
        return {'kind':'internal','target':target,'point':point}
    def source_destination(cid,link):
        k=link['kind'];raw=link.get('page',-1);point=link.get('to',(0,0))
        if k in (fitz.LINK_GOTO,fitz.LINK_NAMED) and raw>=0:
            if k==fitz.LINK_NAMED:
                if link.get('nameddest'):raw,point=named(cid,link['nameddest'])
                else:point=[point[0],docs[cid][raw].rect.height-point[1]]
            return internal(cid,raw,point)
        if k==fitz.LINK_NAMED and link.get('nameddest'):
            raw,point=named(cid,link['nameddest']);return internal(cid,raw,point)
        uri=link.get('uri','') if k==fitz.LINK_URI else link.get('file','')
        if k==fitz.LINK_URI and urlsplit(uri).scheme.lower() in ('http','https','mailto'):
            return {'kind':'uri','uri':uri}
        filename,_,fragment=unquote(uri).replace('\\','/').partition('#')
        target_cid=aliases.get(Path(filename).name);fragment=parse_qs(fragment)
        if target_cid:
            name=(fragment.get('nameddest') or [None])[0]
            numeric=not name and not isinstance(link.get('to'),str)
            if 'page' in fragment:raw=int(fragment['page'][0])-1
            if numeric and raw>=0 and components[cid]['numeric_remotes_edition']=='frozen':
                return {'kind':'original','attachment':Path(components[target_cid]['baseline_path']).name,'page':raw+1}
            point=[0,0]
            if name or isinstance(link.get('to'),str):raw,point=named(target_cid,name or link['to'])
            if raw>=0:return internal(target_cid,raw,point)
        if k==fitz.LINK_NONE:return {'kind':'empty'}
        raise ValueError('Cannot resolve source link independently')
    source_actual=collections.Counter();source_declared=collections.Counter()
    def source_key(cid,raw,link):
        clean={k:v for k,v in link.items() if k not in ('component_id','source_page')}
        return (cid,raw,json.dumps(serial(clean),sort_keys=True,ensure_ascii=False))
    for cid,c in components.items():
        for raw in c['keep_pages']:
            for link in docs[cid][raw].get_links():source_actual[source_key(cid,raw,link)]+=1
    internal_records=uri_records=0
    for r in records:
        kind=r['kind'];original=r.get('original',{})
        if 'component_id' in original and 'source_page' in original and kind in ('source','external_uri','original_pdf_reference','empty_source_link'):
            cid,raw=original['component_id'],original['source_page']
            source_declared[source_key(cid,raw,original)]+=1
            source_index=components[cid]['book_pages'].get(str(raw))
            if source_index!=r['book_page']-1:error('resolved_source_origin',record=r)
            try:
                expected=source_destination(cid,original)
                if expected['kind']=='internal':
                    if r.get('target_book_index')!=expected['target'] or not near(r.get('target_point',[]),expected['point']):error('source_link_semantic_target',record=r,expected=expected)
                elif expected['kind']=='original':
                    if r.get('attachment')!=expected['attachment'] or r.get('target_page')!=expected['page']:error('source_original_reference_target',record=r,expected=expected)
                elif expected['kind']=='uri':
                    if r.get('uri')!=expected['uri']:error('source_uri_target',record=r,expected=expected)
                elif kind!='empty_source_link':error('source_empty_link_kind',record=r)
            except (KeyError,ValueError,IndexError) as exc:error('source_link_semantic_resolution',record=r,reason=str(exc))
        if 'target_book_index' in r:
            src=r['source_book_index'];target=r['target_book_index'];box=r['rect'];point=r['target_point']
            matching=[j for j,l in enumerate(actual.get(src,[])) if j not in used[src] and l['kind']==fitz.LINK_GOTO and l.get('page')==target and near(list(l['from']),box) and near(list(l.get('to',(0,0))),point)]
            if not matching:error('declared_internal_link_missing_in_pdf',record=r)
            else:used[src].add(matching[0]);internal_records+=1
        elif kind=='external_uri':
            src=r['source_book_index']
            matching=[j for j,l in enumerate(actual.get(src,[])) if j not in used[src] and l['kind']==fitz.LINK_URI and l.get('uri')==r['uri'] and near(list(l['from']),r['rect'])]
            if not matching:error('declared_uri_link_missing_in_pdf',record=r)
            else:used[src].add(matching[0]);uri_records+=1
    if source_actual!=source_declared:
        error('source_link_record_membership',source_links=sum(source_actual.values()),recorded_links=sum(source_declared.values()),missing_count=sum((source_actual-source_declared).values()),extra_count=sum((source_declared-source_actual).values()))
    for src,links in actual.items():
        for j,l in enumerate(links):
            if j not in used[src]:error('unrecorded_pdf_link',book_page=src+1,link=serial(l))
    glossary_links=json.loads((root/'book/glossary_links.json').read_text())
    declared_glossary=[r for r in records if r['kind'] in ('glossary_reference','glossary_related_links')]
    if len(declared_glossary)!=len(glossary_links):error('glossary_link_count',expected=len(glossary_links),actual=len(declared_glossary))
    for link in glossary_links:
        src=spec['glossary']['index_start']+link['page']
        box=list(transform_rect(link['rect'],page_map[src]['transform']))
        try:
            if link['kind']=='glossary_reference':
                cid=link['component_id'];raw=int(link['local_page'])-1
                dest=internal(cid,raw,[0,0])
                quote=link.get('anchor_quote')
                if quote:
                    simplify=lambda x:''.join(c for c in unicodedata.normalize('NFKC',x).casefold() if c.isalnum())
                    if simplify(quote) not in simplify(docs[cid][raw].get_text()):error('glossary_anchor_not_on_source_page',component=cid,source_page=raw+1,quote=quote)
            else:
                target=spec['glossary']['index_start']+link['target_glossary_page']
                dest={'target':target,'point':clamp_point(transform_point(link['target_point'],page_map[target]['transform']))}
            matches=[r for r in declared_glossary if r['source_book_index']==src and r['target_book_index']==dest['target'] and near(r['rect'],box) and near(r['target_point'],dest['point'])]
            if not matches:error('glossary_link_semantic_target',source=link,expected=dest)
        except (KeyError,ValueError,IndexError) as exc:error('glossary_link_resolution',source=link,reason=str(exc))
    stats['source_link_semantics_checked']=sum(source_actual.values())
    stats['resolved_internal_records_checked']=internal_records
    stats['resolved_uri_records_checked']=uri_records
    stats['glossary_link_semantics_checked']=len(glossary_links)


def audit(root=ROOT):
    spec_path = root/'book/build_spec.json'
    map_path = root/'book/page_map.json'
    pdf_path = root/'output/Realization_Calculus.pdf'
    for path in (spec_path, map_path, pdf_path):
        if not path.is_file():
            raise FileNotFoundError('Required final input absent: ' + str(path))
    spec = json.loads(spec_path.read_text())
    page_map = json.loads(map_path.read_text())['pages']
    page_map = {int(k): v for k, v in page_map.items()}
    parts = spec['parts']
    components = [c for p in parts for c in p['components']]
    comp_by_id = {c['id']: c for c in components}
    book = fitz.open(pdf_path)
    errors, warnings = [], []
    stats = collections.Counter()
    def error(code, **detail):
        errors.append({'code': code, **detail})
    def warn(code, **detail):
        warnings.append({'code': code, **detail})
    if len(parts) != 12:
        error('part_count', actual=len(parts), expected=12)
    if len(components) != 41 or len(comp_by_id) != 41:
        error('component_count_or_unique_ids', actual=len(components), unique=len(comp_by_id), expected=41)
    leaves = {l['id']: l for l in spec['leaves']}
    if len(leaves) != len(spec['leaves']):error('duplicate_leaf_ids')
    if spec['front_pages'] != 10:error('preliminary_page_count', actual=spec['front_pages'], expected=10)
    expected_count = spec['front_pages'] + len(leaves) + sum(len(c['keep_pages']) for c in components) + spec['glossary']['pages']
    if len(book) != expected_count:
        error('page_count', actual=len(book), expected=expected_count)
    expected_map_keys = set(range(spec['front_pages'], len(book)))
    if set(page_map) != expected_map_keys:
        error('page_map_membership', missing=sorted(expected_map_keys-set(page_map)), extra=sorted(set(page_map)-expected_map_keys))

    # Independently authenticate all attachment bytes against baseline files.
    attachments = {}
    embedded_names = book.embfile_names()
    expected_names = [Path(c['baseline_path']).name for c in components]
    if len(set(expected_names)) != len(expected_names):
        error('duplicate_expected_attachment_name')
    if set(embedded_names) != set(expected_names) or len(embedded_names) != 41:
        error('embedded_attachment_membership', expected=sorted(expected_names), actual=sorted(embedded_names))
    attachment_checks = []
    for comp in components:
        baseline = root/comp['baseline_path']
        name = baseline.name
        row = {'component': comp['id'], 'name': name, 'expected_sha256': comp['baseline_sha256']}
        if not baseline.is_file():
            error('baseline_file_missing', component=comp['id'], path=str(baseline))
            row['passed'] = False
            attachment_checks.append(row)
            continue
        baseline_sha = sha(baseline)
        row['baseline_sha256'] = baseline_sha
        with fitz.open(baseline) as original:
            baseline_pages = len(original)
        row['baseline_pages'] = baseline_pages
        if baseline_sha != comp['baseline_sha256']:
            error('baseline_hash_mismatch', component=comp['id'])
        if baseline_pages != comp['baseline_pages']:
            error('baseline_page_count_mismatch', component=comp['id'], actual=baseline_pages, expected=comp['baseline_pages'])
        attachments[name] = baseline_pages
        if name in embedded_names:
            blob = book.embfile_get(name)
            embedded_sha = hashlib.sha256(blob).hexdigest()
            row['embedded_sha256'] = embedded_sha
            row['embedded_bytes'] = len(blob)
            row['passed'] = embedded_sha == baseline_sha == comp['baseline_sha256']
            if not row['passed']:
                error('embedded_attachment_hash_mismatch', component=comp['id'], name=name)
        else:
            row['passed'] = False
        attachment_checks.append(row)

    docs = {}
    component_checks = []
    source_occurrences = collections.Counter()
    leaf_occurrences = collections.Counter()
    sequence_records = {}
    expected_index = spec['front_pages']
    glossary_occurrences = 0
    for comp in components:
        cid = comp['id']; path = root/comp['path']
        keep = comp['keep_pages']; mapped = comp['book_pages']
        if len(keep) != len(set(keep)) or any(not isinstance(p,int) or not 0 <= p < comp['pages'] for p in keep):
            error('selected_source_page_set', component=cid, keep_pages=keep)
        if set(map(int,mapped)) != set(keep):
            error('selected_page_map_membership', component=cid)
        if keep and comp.get('index_start') != min(mapped.values()):
            error('component_start', component=cid, actual=comp.get('index_start'), expected=min(mapped.values()))
        if not keep and comp.get('index_start') is not None:
            error('empty_component_start', component=cid, index_start=comp.get('index_start'))
        missing_redirects = set(range(comp['pages'])) - set(keep) - set(map(int,comp.get('redirects',{})))
        if missing_redirects:
            error('omitted_pages_without_explicit_redirect', component=cid, source_indexes=sorted(missing_redirects))
        for raw in comp.get('redirects',{}):
            try:resolve_page(comp_by_id, leaves, cid, int(raw))
            except (KeyError,ValueError) as exc:error('invalid_explicit_redirect', component=cid, source_index=int(raw), reason=str(exc))
        if not path.is_file():
            error('component_file_missing', component=cid, path=str(path));continue
        source = docs[cid] = fitz.open(path)
        source_sha = sha(path)
        ok = source_sha == comp['sha256'] and len(source) == comp['pages']
        if not ok:
            error('component_source_identity', component=cid, actual_sha256=source_sha, actual_pages=len(source), expected_sha256=comp['sha256'], expected_pages=comp['pages'])
        for sp in keep:
            index = mapped[str(sp)]; rec = page_map.get(index,{})
            if rec.get('kind') != 'component' or rec.get('component') != cid or rec.get('source_page') != sp+1 or rec.get('source_index') != sp or rec.get('paper') != comp['paper'] or rec.get('divider'):
                error('component_page_mapping', component=cid, source_page=sp+1, source_index=sp, book_page=index+1, map_record=rec)
        component_checks.append({'component':cid,'source_sha256':source_sha,'source_pages':len(source),'mapped_pages':len(keep),'first_book_page':min(mapped.values())+1 if mapped else None,'last_book_page':max(mapped.values())+1 if mapped else None,'source_identity_passed':ok})
    for entry in spec['sequence']:
        if entry['book_index'] != expected_index:
            error('sequence_start', entry=entry, expected=expected_index)
        if entry['kind'] == 'leaf':
            lid=entry['id'];leaf=leaves[lid];leaf_occurrences[lid]+=1
            if leaf['book_index'] != expected_index:error('leaf_index',leaf_id=lid,actual=leaf['book_index'],expected=expected_index)
            rec=page_map.get(expected_index,{})
            if rec.get('kind')!='leaf' or rec.get('leaf_id')!=lid or not rec.get('divider') or rec.get('component') is not None:
                error('leaf_map',leaf_id=lid,book_page=expected_index+1,record=rec)
            sequence_records[expected_index]={'kind':'leaf','leaf_id':lid}
            expected_index+=1
        elif entry['kind'] == 'component':
            cid=entry['component_id'];comp=comp_by_id[cid]
            for sp in entry.get('source_pages',comp['keep_pages']):
                source_occurrences[(cid,sp)]+=1
                if sp not in comp['keep_pages'] or comp['book_pages'].get(str(sp))!=expected_index:
                    error('sequence_source_page_map',component=cid,source_index=sp,book_index=expected_index)
                sequence_records[expected_index]={'kind':'component','component':cid,'source_index':sp}
                expected_index+=1
        elif entry['kind'] == 'glossary':
            glossary_occurrences+=1
            if entry['book_index']!=spec['glossary']['index_start'] or entry['pages']!=spec['glossary']['pages']:
                error('glossary_sequence_spec',entry=entry,spec=spec['glossary'])
            for sp in range(entry['pages']):
                rec=page_map.get(expected_index,{})
                if rec.get('kind')!='glossary' or rec.get('source_page')!=sp+1 or rec.get('source_index')!=sp or rec.get('component') is not None or rec.get('divider'):
                    error('glossary_page_map',source_index=sp,book_page=expected_index+1,record=rec)
                sequence_records[expected_index]={'kind':'glossary','source_index':sp}
                expected_index+=1
        else:error('unknown_sequence_kind',entry=entry)
    expected_source=collections.Counter({(c['id'],sp):1 for c in components for sp in c['keep_pages']})
    if source_occurrences!=expected_source:
        error('selected_pages_not_exactly_once',missing=[list(k) for k in (expected_source-source_occurrences)],extra=[list(k) for k in (source_occurrences-expected_source)])
    if leaf_occurrences!=collections.Counter({lid:1 for lid in leaves}):error('leaves_not_exactly_once',actual=dict(leaf_occurrences))
    if glossary_occurrences!=1:error('glossary_not_exactly_once',actual=glossary_occurrences)
    if expected_index!=len(book):error('sequence_total',mapped=expected_index,actual=len(book))
    chapter_leaves=[l for l in leaves.values() if l['kind']=='chapter']
    if len(chapter_leaves)!=12:error('chapter_leaf_count',actual=len(chapter_leaves))
    for part in parts:
        matching=[l for l in chapter_leaves if l.get('paper')==part['paper']]
        if len(matching)!=1 or matching[0]['book_index']!=part['divider_index']:
            error('chapter_divider_map',paper=part['paper'],divider_index=part['divider_index'])
    units={u['id']:u for u in spec['reading_units']}
    if len(units)!=26:error('reading_unit_count',actual=len(units),expected=26)
    for uid,unit in units.items():
        leaf=leaves[unit['leaf_id']]
        indexes=[leaf['book_index']]
        for cid in unit['component_ids']:
            if cid not in comp_by_id:error('reading_unit_unknown_component',unit_id=uid,component=cid);continue
            comp=comp_by_id[cid]
            indexes.extend(comp['book_pages'].values())
            if comp['keep_pages'] and comp.get('unit_id')!=uid:error('component_unit_assignment',unit_id=uid,component=cid,actual=comp.get('unit_id'))
        if min(indexes)!=unit['index_start'] or max(indexes)!=unit['index_end'] or set(indexes)!=set(range(unit['index_start'],unit['index_end']+1)):
            error('reading_unit_inclusive_range',unit_id=uid,range=[unit['index_start'],unit['index_end']],actual=[min(indexes),max(indexes)],count=len(set(indexes)))
        if not 0<=unit['contents_page']<spec['front_pages']:error('reading_unit_contents_page',unit_id=uid,actual=unit['contents_page'])
    for leaf in leaves.values():
        if leaf['folio']!=leaf['book_index']-spec['front_pages']+1:error('leaf_printed_folio',leaf_id=leaf['id'],actual=leaf['folio'])
    expected_order=['chapter']*12+['studies_division']+['study']*2+['formal_division']+['formal_companion']*12+['glossary']
    actual_order=[leaves[e['id']]['kind'] for e in spec['sequence'] if e['kind']=='leaf']
    if actual_order!=expected_order:error('reader_division_order',actual=actual_order,expected=expected_order)
    editorial_docs={'front':fitz.open(root/'book/frontmatter.pdf'),'leaf':fitz.open(root/'book/leaves.pdf'),'glossary':fitz.open(root/spec['glossary']['path'])}
    if len(editorial_docs['front'])!=spec['front_pages']:error('front_source_page_count')
    if len(editorial_docs['leaf'])!=len(leaves):error('leaf_source_page_count')
    if len(editorial_docs['glossary'])!=spec['glossary']['pages']:error('glossary_source_page_count')
    leaf_source_pages={l['id']:i for i,l in enumerate(spec['leaves'])}
    stats['selected_source_pages']=sum(len(c['keep_pages']) for c in components)
    stats['raw_source_pages']=sum(c['pages'] for c in components)
    stats['editorial_leaves']=len(leaves)
    stats['glossary_pages']=spec['glossary']['pages']

    # Bounds and page destinations are checked from the actual finished PDF.
    toc = book.get_toc(simple=False)
    for j, item in enumerate(toc):
        if len(item) < 3 or not isinstance(item[2], int) or not 1 <= item[2] <= len(book):
            error('bookmark_destination', bookmark_index=j, value=str(item))
        if j and item[0] > toc[j-1][0]+1:
            error('bookmark_hierarchy_jump', bookmark_index=j, value=str(item))
    expected_overrides=[]
    for comp in components:
        for title,replacement in comp.get('bookmark_overrides',{}).items():
            raw=int(replacement['source_page'] if isinstance(replacement,dict) else replacement)
            original_entries=[x for x in docs[comp['id']].get_toc() if x[1]==title]
            if not original_entries:error('bookmark_override_source_title',component=comp['id'],title=title)
            for original in original_entries:
                target=comp['book_pages'].get(str(raw))
                row={'component_id':comp['id'],'title':title,'original_source_index':original[2]-1,
                     'override_source_index':raw,'book_index':target,'book_page':target+1 if target is not None else None}
                expected_overrides.append(row)
                if target is None or not any(x[1]==title and x[2]==target+1 for x in toc):
                    error('bookmark_override_final_target',record=row)
    override_path=root/'book/bookmark_target_overrides.json'
    actual_overrides=json.loads(override_path.read_text()) if override_path.is_file() else []
    if collections.Counter(json.dumps(x,sort_keys=True) for x in expected_overrides)!=collections.Counter(json.dumps(x,sort_keys=True) for x in actual_overrides):error('bookmark_override_records',expected=expected_overrides,actual=actual_overrides)
    stats['bookmark_overrides_checked']=len(expected_overrides)
    stats['bookmarks'] = len(toc)
    page_xrefs = {book.page_xref(i): i for i in range(len(book))}
    embedded_actions, page_checks = [], []
    for index, page in enumerate(book):
        if abs(page.rect.width-612) > .02 or abs(page.rect.height-792) > .02:
            error('page_size', page=index+1, rect=list(page.rect))
        stats['pages_checked'] += 1
        text = page.get_text('text', sort=False)
        if not text.strip():
            error('empty_page_text', page=index+1)
        record = page_map.get(index, {})
        cid = record.get('component')
        row = {'book_page': index+1, 'page_size': [page.rect.width, page.rect.height], 'characters': len(text), 'component': cid}
        inherited_outside = []
        source_spans = []
        source=None; source_kind=record.get('kind','front' if index<spec['front_pages'] else 'unknown')
        if cid and cid in docs:
            sp=record['source_index'];source=docs[cid][sp]
            predicted_transform=expected_transform(source,index,spec['front_pages'],comp_by_id[cid],sp)
            transform=record.get('transform')
        elif source_kind=='glossary':
            sp=record['source_index'];source=editorial_docs['glossary'][sp]
            predicted_transform=expected_transform(source,index,spec['front_pages']);transform=record.get('transform')
        elif source_kind=='leaf':
            sp=leaf_source_pages[record['leaf_id']];source=editorial_docs['leaf'][sp]
            predicted_transform=transform=[1.0,0.0,0.0]
        elif source_kind=='front':
            sp=index;source=editorial_docs['front'][sp]
            predicted_transform=transform=[1.0,0.0,0.0]
        row['kind']=source_kind
        if source is not None:
            if not isinstance(transform,list) or len(transform)!=3 or transform[0]<=0:
                error('invalid_transform',page=index+1,transform=transform);continue
            if max(abs(x-y) for x,y in zip(transform,predicted_transform))>.0001:
                error('unexpected_transform',page=index+1,actual=transform,expected=predicted_transform)
            source_text = source.get_text('text', sort=False)
            sn, bn = normalized(source_text), normalized(text)
            if not sn:
                error('empty_component_page_text', component=cid, source_page=sp+1, book_page=index+1)
            exact_block = sn in bn
            ordered = exact_block or subsequence(sn, bn)
            row.update({'source_page': sp+1, 'source_characters_normalized': len(sn), 'source_text_is_contiguous': exact_block, 'source_text_is_ordered_subsequence': ordered, 'preserved_pdf_page': bool(record.get('preserved_pdf_page'))})
            stats['component_pages_checked' if cid else 'editorial_pages_checked'] += 1
            stats['contiguous_text_matches' if exact_block else 'ordered_text_matches' if ordered else 'text_mismatches'] += 1
            if not ordered:
                error('source_text_not_preserved', component=cid, source_page=sp+1, book_page=index+1, source_characters=len(sn), book_characters=len(bn))
            source_spans = spans(source)
            for ss in source_spans:
                target = transform_rect(ss['bbox'], transform)
                source_inside = within(ss['bbox'], source.rect)
                if not source_inside:
                    inherited_outside.append({'source_bbox': list(ss['bbox']), 'text': ss['text'][:120]})
                elif not within(target, page.rect):
                    error('assembly_text_crop', component=cid, source_page=sp+1, book_page=index+1, source_bbox=list(ss['bbox']), transformed_bbox=list(target), text=ss['text'][:120])
            if inherited_outside:
                warn('source_component_text_bounds', component=cid, source_page=sp+1, book_page=index+1, spans=inherited_outside, meaning='Present in the input component before final PDF assembly; not introduced by the assembler.')
            if record.get('preserved_pdf_page') and not record.get('display_normalized'):
                target_page = transform_rect(source.rect, transform)
                if not within(target_page, page.rect):
                    error('preserved_page_geometry_crop', component=cid, source_page=sp+1, book_page=index+1, target_rect=list(target_page))
                else:
                    stats['full_preserved_page_frames_within_output'] += 1
            # Imported vector operations precede editorial furniture. Compare
            # every source operation's kind and transformed bbox independently.
            sb, bb = source.get_bboxlog(), page.get_bboxlog()
            geom_ok = len(bb) >= len(sb)
            max_delta = 0.0
            if geom_ok:
                for a, b in zip(sb, bb):
                    if a[0] != b[0]:
                        geom_ok = False
                        break
                    if not fitz.Rect(a[1]).is_valid and max(abs(v) for v in a[1]) > 1e9:
                        if a[1] != b[1]:
                            geom_ok = False
                            break
                        stats['unchanged_empty_path_sentinels'] += 1
                        continue
                    if fitz.Rect(a[1]).is_empty:
                        stats['transformed_valid_degenerate_paths'] += 1
                    predicted = transform_rect(a[1], transform)
                    delta = max(abs(x-y) for x,y in zip(predicted,b[1]))
                    max_delta = max(max_delta, delta)
                    if delta > TOL:
                        geom_ok = False
                        break
            row.update({'source_graphic_operations': len(sb), 'source_graphic_prefix_matches': geom_ok, 'graphic_bbox_max_delta_pt': round(max_delta,6)})
            if geom_ok:
                stats['graphic_geometry_matches'] += 1
            else:
                error('graphic_bbox_prefix_difference', component=cid, source_page=sp+1, book_page=index+1, source_ops=len(sb), output_ops=len(bb), max_delta_pt=max_delta, meaning='Material unexplained operation-kind/count or transformed geometry mismatch; source text and preserved-page frame checks are independent.')
        if index>=spec['front_pages']:
            expected_folio=str(index-spec['front_pages']+1)
            footer=normalized(page.get_text('text',clip=fitz.Rect(0,750,612,792)))
            if footer!=expected_folio:error('global_folio_not_unique',page=index+1,expected=expected_folio,footer=footer)
            if page.get_label()!=expected_folio:error('page_label',page=index+1,expected=expected_folio,actual=page.get_label())
        # Source bounds are distinguished from new editorial/assembly bounds.
        outside = [s for s in spans(page) if not within(s['bbox'], page.rect)]
        for s in outside:
            text_norm = normalized(s['text'])
            known_inherited = any(text_norm == normalized(a['text']) for a in inherited_outside)
            if known_inherited:
                stats['inherited_offpage_spans'] += 1
            else:
                error('output_offpage_text', page=index+1, bbox=list(s['bbox']), text=s['text'][:140])
        row['offpage_text_spans'] = len(outside)
        for link in page.get_links():
            stats['pymupdf_link_records'] += 1
            if link['kind'] == fitz.LINK_GOTO:
                stats['internal_links'] += 1
                if not 0 <= link.get('page', -1) < len(book):
                    error('internal_link_page', source_page=index+1, link=str(link))
                point = link.get('to')
                if isinstance(point, fitz.Point) and (not -TOL <= point.x <= 612+TOL or not -TOL <= point.y <= 792+TOL):
                    error('internal_link_point_outside_page', source_page=index+1, target_page=link['page']+1, point=list(point), meaning='Page destination is valid; the inherited destination point may lie outside the page.')
            if link.get('from') and not within(link['from'], page.rect):
                error('link_rectangle_outside_page', page=index+1, rectangle=list(link['from']))
        for xref in annotation_xrefs(book, page):
            action = inspect_action(book, xref)
            if action is None:
                continue
            subtype = action('S')[1]
            stats['annotation_action_'+subtype.strip('/')] += 1
            if subtype == '/GoToE':
                nk, name = action('T/N')
                dk, dest = action('D')
                route_kind = action('T/R')[1]
                match = re.match(r'\[\s*(\d+)\s*/', dest) if dk == 'array' else None
                destpage = int(match.group(1)) if match else None
                rec = {'source_book_page': index+1, 'annotation_xref': xref, 'attachment': name, 'target_page_zero_based': destpage, 'target_relation': route_kind}
                embedded_actions.append(rec)
                if nk != 'string' or name not in attachments:
                    error('embedded_link_attachment', **rec)
                elif destpage is None or not 0 <= destpage < attachments[name]:
                    error('embedded_link_page', **rec)
                if route_kind != '/C':
                    error('embedded_link_relation', **rec)
            elif subtype == '/GoToR':
                error('remaining_external_pdf_action', page=index+1, annotation_xref=xref, target=action('F')[1])
            elif subtype == '/GoTo':
                dk, dest = action('D')
                m = re.match(r'\[\s*(\d+)\s+\d+\s+R', dest) if dk == 'array' else None
                if m and int(m.group(1)) not in page_xrefs:
                    error('internal_link_page_object', page=index+1, annotation_xref=xref, destination=dest)
        page_checks.append(row)
    stats['embedded_links_checked'] = len(embedded_actions)
    # Compare counts to emitted assembler records only after inspecting the PDF.
    record_path = root/'book/embedded_reference_links.json'
    if record_path.is_file():
        declared = json.loads(record_path.read_text())
        actual_keys = collections.Counter((r['source_book_page'],r['attachment'],r['target_page_zero_based']+1) for r in embedded_actions if r['target_page_zero_based'] is not None)
        declared_keys = collections.Counter((r['book_page'],r['attachment'],r['target_page']) for r in declared)
        if actual_keys != declared_keys:
            error('embedded_action_record_mismatch', actual_count=len(embedded_actions), declared_count=len(declared))
    audit_navigation(root,spec,docs,book,page_map,error,stats)
    summary = {
        'schema':'realization-calculus.independent-final-pdf-audit/2',
        'status':'PASS' if not errors else 'FAIL',
        'pdf':str(pdf_path.relative_to(root)), 'pdf_sha256':sha(pdf_path),
        'build_spec_sha256':sha(spec_path), 'page_map_sha256':sha(map_path),
        'scope':'Finished PDF structure, exact selected-page sequence, explicit redirects, attachment identity, source/editorial text survival, vector geometry, and source/glossary link semantics; not mathematical verification.',
        'normalization':'NFKC; remove whitespace, soft hyphen, zero-width space and BOM only. Source characters must survive as a contiguous block or ordered subsequence in extraction order.',
        'geometry_tolerance_pt':TOL,
        'audit_method_corrections': ['The first audit assumed whitespace before a destination name. Valid compact PDF arrays such as [5/Fit] are now parsed.', 'Only invalid extreme-coordinate empty-path sentinels remain unchanged and require exact source/output equality. Valid zero-area path bboxes are transformed normally; confusing those categories caused 218 warnings in the retained intermediate audit.'],
        'first_run_preserved_at':'book/audit_history/first_run/',
        'statistics':dict(stats),
        'errors':errors, 'warnings':warnings,
        'attachment_checks':attachment_checks,
        'component_checks':component_checks,
        'embedded_actions':embedded_actions,
        'page_checks':page_checks,
    }
    output = root/'book/final_pdf_audit.json'
    output.write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
    brief = {'status':summary['status'],'pages':len(book),'components':len(components),'attachments':len(embedded_names),'errors':len(errors),'warnings':len(warnings),'statistics':dict(stats),'output':str(output)}
    (root/'book/final_pdf_audit_summary.txt').write_text(json.dumps(brief,indent=2)+'\n')
    for doc in list(docs.values())+list(editorial_docs.values()):doc.close()
    book.close()
    return brief


def render_samples(root=ROOT):
    from PIL import Image, ImageOps, ImageDraw
    spec = json.loads((root/'book/build_spec.json').read_text())
    book = fitz.open(root/'output/Realization_Calculus.pdf')
    dest = root/'book/final_visual_samples';dest.mkdir(parents=True,exist_ok=True)
    selected = {}
    def add(index, reason):
        if 0 <= index < len(book):selected.setdefault(index, []).append(reason)
    for n in range(spec['front_pages']):add(n,'front matter')
    for leaf in spec['leaves']:add(leaf['book_index'],leaf['kind']+' '+str(leaf.get('paper','')))
    for part in spec['parts']:
        for comp in part['components']:
            kept=sorted(comp['keep_pages'],key=lambda raw:comp['book_pages'][str(raw)])
            if kept:
                raw=kept[min(len(kept)-1,max(0,len(kept)//2))]
                add(comp['book_pages'][str(raw)],comp['id']+' retained interior')
    glossary=spec['glossary']
    for offset in (0,glossary['pages']//2,glossary['pages']-1):add(glossary['index_start']+offset,'glossary')
    for paper in ('II','III','V','VI','VII','VIII'):
        plate=next((x for x in book.get_toc() if re.search(r'Plate\s+'+paper+r'\.',x[1],re.I)),None)
        if plate:add(plate[2]-1,'Chapter '+paper+' canonical plate')
    for stale in list(dest.glob('page_*.png'))+list(dest.glob('contact_sheet_*.png')):stale.unlink()
    rendered=[];thumbs=[]
    for index, reason in sorted(selected.items()):
        page=book[index]
        path=dest/f'page_{index+1:04d}.png'
        pix=page.get_pixmap(matrix=fitz.Matrix(1.25,1.25),alpha=False)
        pix.save(path)
        image=Image.open(path).convert('RGB')
        thumb=ImageOps.contain(image,(235,304))
        tile=Image.new('RGB',(251,338),'#e9e5e8')
        tile.paste(thumb,((251-thumb.width)//2,5))
        draw=ImageDraw.Draw(tile);draw.text((8,312),f'PDF page {index+1}: '+reason[0][:28],fill='black')
        thumbs.append(tile)
        rendered.append({'page':index+1,'reasons':reason,'image':str(path.relative_to(root))})
    sheets=[]
    for start in range(0,len(thumbs),16):
        sheet=Image.new('RGB',(4*251,4*338),'white')
        for j,tile in enumerate(thumbs[start:start+16]):sheet.paste(tile,((j%4)*251,(j//4)*338))
        path=dest/f'contact_sheet_{start//16+1:02d}.png';sheet.save(path)
        sheets.append(str(path.relative_to(root)))
    report={'sample_count':len(rendered),'selection':'All prelims and editorial opening leaves, one actual retained interior from every component with selected pages, available canonical plates, and glossary pages near the beginning, middle and end. Contact sheets are navigation aids; use individual page PNGs for close inspection.','pages':rendered,'contact_sheets':sheets,'manual_visual_review_performed_by_this_script':False}
    (dest/'sample_index.json').write_text(json.dumps(report,indent=2)+'\n')
    book.close()
    return {'sample_count':len(rendered),'contact_sheets':sheets}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--render-samples',action='store_true',help='Render the bounded selected-page visual sample after auditing.')
    parser.add_argument('--samples-only',action='store_true',help='Only create the visual samples; does not certify a structural audit.')
    args=parser.parse_args()
    result={}
    if not args.samples_only:result['audit']=audit()
    if args.render_samples or args.samples_only:result['visual_samples']=render_samples()
    print(json.dumps(result,indent=2))
    if result.get('audit',{}).get('status')=='FAIL':raise SystemExit(1)


if __name__=='__main__':main()
