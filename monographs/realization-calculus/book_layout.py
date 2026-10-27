#!/usr/bin/env python3
"""Build the ordered book map and canonical routes for duplicate visual plates."""
from pathlib import Path
import json,re,unicodedata
import fitz
from render_book_matter import render_glossary

ROOT=Path(__file__).resolve().parent

def norm(text):
    return ''.join(c for c in unicodedata.normalize('NFKC',text).casefold() if c.isalnum())

def qualify_glossary(components):
    data=json.loads((ROOT/'editorial/book_revision/glossary.json').read_text())
    docs={};records=[]
    for term in data['terms']:
        for ref in term.get('references',term.get('refs',[])):
            cid=ref['component_id']
            if cid not in docs:docs[cid]=fitz.open(ROOT/components[cid]['path'])
            needle=norm(ref['anchor_quote'])
            hits=[i for i,p in enumerate(docs[cid]) if needle in norm(p.get_text())]
            if len(hits)!=1:
                raise ValueError(f'Glossary anchor must identify one rebuilt page: {term["term"]}: {hits}')
            old=ref['local_page'];ref['local_page']=hits[0]+1
            records.append({'term':term['term'],'component_id':cid,'previous_local_page':old,'local_page':hits[0]+1,'anchor_quote':ref['anchor_quote']})
    for doc in docs.values():doc.close()
    (ROOT/'book/glossary_resolved.json').write_text(json.dumps(data,indent=2)+'\n')
    (ROOT/'book/glossary_anchor_resolution.json').write_text(json.dumps({'status':'PASS','references':records},indent=2)+'\n')
    return render_glossary(data,ROOT/'book')

def reviewed_x_plate_pairs(comps,main_doc,visual_doc,exact_pairs):
    """Retain authenticated X duplicate routes after bounded book prose edits.

    This exception is confined to the thirty X atlas copies already identified
    by the prior book. It requires the exact prior display inputs and current
    hash-bound preservation reports, then independently compares every plate's
    mathematics, images, vector paths, links and text outside reviewed regions.
    """
    import hashlib
    from book_component_adapter import outside_text
    from rebrand_components import _snapshot,_vector_difference
    from volume_finish_adapter import native_math,compare_math
    def sha(path):
        with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
    review=ROOT/'editorial/volume_finish'
    baseline=json.loads((review/'baseline_build_spec.json').read_text())
    prior={c['id']:c for part in baseline['parts'] for c in part['components']}
    old={};reports={};changes={};identities={}
    current={'X_traditional':main_doc,'X_visual':visual_doc}
    try:
        for cid in current:
            c=comps[cid];base=prior[cid]
            path=review/'before/x_visual_pair_inputs'/(cid+'.pdf')
            if sha(path)!=base['sha256']:raise ValueError('Prior X display input identity changed: '+cid)
            old[cid]=fitz.open(path)
            report=json.loads((review/'component_reports'/(cid+'.json')).read_text())
            if (report['status']!='PASS' or report['component_id']!=cid
                or report['input_sha256']!=base['sha256']
                or report['output_sha256']!=sha(ROOT/c['path'])
                or report['output_sha256']!=c['sha256']
                or report['input_pages']!=base['pages']
                or report['output_pages']!=base['pages']
                or len(old[cid])!=base['pages'] or len(current[cid])!=base['pages']):
                raise ValueError('X preservation report is not bound to the exact display inputs: '+cid)
            reports[cid]=report;changes[cid]={r['page_1based']-1:r for r in report['prose_pages']}
            if len(changes[cid])!=len(report['prose_pages']):raise ValueError('Duplicate X prose page record')
            identities[cid]={'prior_input':str(path.relative_to(ROOT)),
                'prior_sha256':base['sha256'],'current_sha256':report['output_sha256'],
                'preservation_report':str((review/'component_reports'/(cid+'.json')).relative_to(ROOT))}
        pairs={int(raw):r['source_page'] for raw,r in prior['X_visual']['redirects'].items()
               if r.get('component_id')=='X_traditional'}
        if (len(pairs)!=30 or sorted(pairs)!=list(range(3,33))
            or sorted(pairs.values())!=list(range(prior['X_traditional']['atlas_start'],prior['X_traditional']['atlas_start']+30))
            or len(set(pairs.values()))!=30):
            raise ValueError('Prior X atlas pairing structure is not the reviewed thirty-page range')
        if any(bp not in pairs or pairs[bp]!=ap for bp,ap in exact_pairs.items()):
            raise ValueError('Current X exact matches disagree with the authenticated prior pairing')
        rows=[]
        for bp,ap in sorted(pairs.items()):
            if bp not in comps['X_visual']['keep_pages'] or ap not in comps['X_traditional']['keep_pages']:
                raise ValueError('An authenticated X atlas page is no longer selected')
            # The preserved prior pair must be an exact page-level copy, including
            # glyph positions and fonts, rather than merely similar prose.
            if old['X_traditional'][ap].get_text('rawdict')!=old['X_visual'][bp].get_text('rawdict'):
                raise ValueError('Prior X plate text/glyph structure is not identical')
            a,b=_snapshot(old['X_traditional'][ap]),_snapshot(old['X_visual'][bp])
            if a['images']!=b['images']:raise ValueError('Prior X plate images differ')
            _vector_difference(a['drawings'],b['drawings'])
            checked=[]
            for cid,raw in [('X_traditional',ap),('X_visual',bp)]:
                before,after=old[cid][raw],current[cid][raw]
                change=changes[cid].get(raw)
                boxes=[]
                if change:
                    if (not change['mathematical_glyphs_unchanged'] or not change['outside_text_unchanged']
                        or not change['annotations_unchanged'] or change['changed_pixels_outside_regions']!=0
                        or change.get('reviewed_native_image_edge_resampling_pixels',0)!=0
                        or change['max_math_glyph_geometry_serialization_delta_pt']>.0002):
                        raise ValueError('X plate prose preservation evidence failed')
                    boxes=[fitz.Rect(box) for box in change['regions']]
                if outside_text(before,boxes)!=outside_text(after,boxes):
                    raise ValueError('X plate differs outside the reviewed prose regions')
                sa,sb=_snapshot(before),_snapshot(after)
                if sa['images']!=sb['images'] or sa['links']!=sb['links'] or before.rect!=after.rect:
                    raise ValueError('X plate image, annotation or page geometry changed')
                vector_delta=_vector_difference(sa['drawings'],sb['drawings'])
                math_delta=compare_math(native_math(before),native_math(after))
                checked.append({'component_id':cid,'source_page':raw+1,'reviewed_prose_regions':len(boxes),
                    'outside_text_identical':True,'mathematics_preserved':True,'images_and_links_identical':True,
                    'max_math_geometry_serialization_delta_pt':math_delta,'max_vector_serialization_delta_pt':vector_delta})
            exact=norm(main_doc[ap].get_text())==norm(visual_doc[bp].get_text())
            if not exact and not any(changes[cid].get(raw) for cid,raw in [('X_traditional',ap),('X_visual',bp)]):
                raise ValueError('X duplicate text differs without an authorized prose edit')
            rows.append({'visual_source_page':bp+1,'canonical_source_page':ap+1,
                         'current_normalized_text_identical':exact,'page_preservation_checks':checked})
        report={'status':'PASS','scope':'Thirty X duplicate atlas routes only. Prior exact copies are authenticated; current differences are confined to hash-bound reviewed book prose regions.',
                'identities':identities,'pair_count':len(rows),
                'current_exact_pairs':sum(r['current_normalized_text_identical'] for r in rows),
                'reviewed_prose_pairs':sum(not r['current_normalized_text_identical'] for r in rows),'pairs':rows}
        (ROOT/'book/x_visual_pair_validation.json').write_text(json.dumps(report,indent=2)+'\n')
        return pairs
    finally:
        for doc in old.values():doc.close()


def add_plate_redirects(comps):
    """The source-level overlap audits authorize these canonical plate routes."""
    rows=[]
    for roman,count in [('II',24),('III',24),('V',40),('VI',42),('VII',40),('VIII',32)]:
        main,visual=comps[roman+'_traditional'],comps[roman+'_visual']
        a,b=fitz.open(ROOT/main['path']),fitz.open(ROOT/visual['path'])
        an,bn=a.resolve_names(),b.resolve_names()
        first=None
        for n in range(1,count+1):
            key=('plate'+str(n)+'.1') if roman in ('II','III') else 'vpage'+str(n)
            mainkey=('v'+key if roman=='VI' else 'atlas'+key if roman in ('VII','VIII') else key)
            if mainkey not in an or key not in bn:
                raise ValueError(f'Missing reviewed plate destination {roman} {key}')
            ap,bp=an[mainkey]['page'],bn[key]['page']
            if ap not in main['keep_pages']:
                raise ValueError(f'Canonical plate was excluded: {roman} {n}')
            first=ap if first is None else min(first,ap)
            if bp in visual['keep_pages']:visual['keep_pages'].remove(bp)
            visual['redirects'][str(bp)]={'component_id':main['id'],'source_page':ap}
            rows.append({'chapter':roman,'plate':n,'omitted_component':visual['id'],'omitted_page':bp+1,'canonical_component':main['id'],'canonical_page':ap+1})
        main['atlas_start']=first
        if roman=='III':
            # The source comparison confirms that the unique visual orientation
            # retains this page's scope, three reading routes and conventions.
            orientation=first-1
            if orientation!=73:raise ValueError('III atlas orientation pagination changed; review before consolidation')
            main['keep_pages'].remove(orientation)
            main['redirects'][str(orientation)]={'component_id':visual['id'],'source_page':1}
            rows.append({'chapter':'III','omitted_component':main['id'],'omitted_page':orientation+1,
                         'canonical_component':visual['id'],'canonical_page':2,
                         'evidence':'Reviewed orientation consolidation: scope, three reading routes, and product/coordinate conventions retained; not an exact page duplicate.'})
            main['atlas_start']=orientation
        a.close();b.close()
    # Paper X embeds thirty visual-study pages in its mathematical text.
    # Prefer exact current matches. A bounded exception authenticates the prior
    # copies and every reviewed prose region if book editing changed one copy.
    main,visual=comps['X_traditional'],comps['X_visual']
    a,b=fitz.open(ROOT/main['path']),fitz.open(ROOT/visual['path'])
    try:
        pairs={}
        for bp in list(visual['keep_pages']):
            bt=norm(b[bp].get_text())
            if len(bt)<250:continue
            hits=[ap for ap in main['keep_pages'] if norm(a[ap].get_text())==bt]
            if len(hits)==1:pairs[bp]=hits[0]
        exact_count=len(pairs)
        if len(pairs)!=30:pairs=reviewed_x_plate_pairs(comps,a,b,pairs)
        if len(pairs)!=30:raise ValueError(f'Expected thirty verified X plate duplicates, found {len(pairs)}')
        for bp,ap in sorted(pairs.items()):
            visual['keep_pages'].remove(bp)
            visual['redirects'][str(bp)]={'component_id':main['id'],'source_page':ap}
            exact=norm(a[ap].get_text())==norm(b[bp].get_text())
            evidence=('Exact normalized current page text, original append-copy build provenance.' if exact else
                'Authenticated prior exact page copy with current hash-bound reviewed book prose changes; mathematics, images, vector paths, links and text outside reviewed regions preserved. See x_visual_pair_validation.json.')
            rows.append({'chapter':'X','omitted_component':visual['id'],'omitted_page':bp+1,
                         'canonical_component':main['id'],'canonical_page':ap+1,'evidence':evidence})
        main['atlas_start']=min(pairs.values())
    finally:
        a.close();b.close()
    (ROOT/'book/canonical_visual_routes.json').write_text(json.dumps({'routes':rows},indent=2)+'\n')

def make_layout(parts,adaptations):
    comps={c['id']:c for p in parts for c in p['components']}
    for cid,c in comps.items():
        c['keep_pages']=list(adaptations[cid]['keep_pages'])
        c['redirects']={};c['book_pages']={};c['page_unit_ids']={}
        c['display_normalized']=True
        refs=c.get('reference_pages',[])
        if len(refs)!=len(set(refs)) or not set(refs)<=set(c['keep_pages']):
            raise ValueError('Reference pages must be unique retained source pages: '+cid)
        if cid in ('V_traditional','VI_traditional','VII_traditional','VIII_traditional'):
            c['bookmark_overrides']={'Reading this chapter':1}
            if cid=='VIII_traditional':c['bookmark_overrides']['Three exact models before the general theory']=7
    add_plate_redirects(comps)
    glossary=qualify_glossary(comps)
    leaves=[];units=[];sequence=[];cursor=10
    def leaf(ident,kind,title,paper=None,**kw):
        nonlocal cursor
        row={'id':ident,'kind':kind,'title':title,'book_index':cursor,'folio':cursor-9,'entries':[],**kw}
        if paper:row['paper']=paper
        leaves.append(row);sequence.append({'kind':'leaf','id':ident,'book_index':cursor});cursor+=1
        return row
    def body_pages(cid):
        return [p for p in comps[cid]['keep_pages'] if p not in comps[cid].get('reference_pages',[])]
    def chunk(cid,pages,unit_id):
        nonlocal cursor
        if not pages:return
        c=comps[cid]
        sequence.append({'kind':'component','component_id':cid,'source_pages':pages,
                         'book_index':cursor,'unit_id':unit_id})
        for sp in pages:
            if str(sp) in c['book_pages']:raise ValueError('A source page was selected twice')
            c['book_pages'][str(sp)]=cursor;c['page_unit_ids'][str(sp)]=unit_id;cursor+=1
    def unit(ident,kind,title,paper,cids,contents_page,component_pages=None,**kw):
        opening=leaf(ident,kind,title,paper,**kw)
        page_selection={cid:list(component_pages[cid] if component_pages is not None else body_pages(cid)) for cid in cids}
        u={'id':ident,'kind':kind,'paper':paper,'title':title,'component_ids':cids,
           'component_pages':page_selection,'leaf_id':ident,'index_start':opening['book_index'],
           'contents_page':contents_page}
        if kind!='references':
            for cid in cids:comps[cid]['unit_id']=ident
        main=next((cid for cid in cids if comps[cid]['role']=='traditional'),None)
        visual=next((cid for cid in cids if comps[cid]['role']=='visual'),None)
        handled=set()
        if kind!='references' and main and visual and 'atlas_start' in comps[main] and page_selection[visual]:
            point=comps[main]['atlas_start'];keep=page_selection[main]
            chunk(main,[p for p in keep if p<point],ident)
            for cid in cids:
                if comps[cid]['role']=='analytic_supplement':chunk(cid,page_selection[cid],ident);handled.add(cid)
            chunk(visual,page_selection[visual],ident);chunk(main,[p for p in keep if p>=point],ident);handled|={main,visual}
        for cid in cids:
            if cid not in handled:chunk(cid,page_selection[cid],ident)
        u['index_end']=cursor-1;units.append(u)
        return opening,u
    for p in parts:
        roman=p['paper'];cids=[c['id'] for c in p['components'] if c['role'] in ('traditional','visual','analytic_supplement')]
        opening,u=unit('chapter_'+roman,'chapter',p['title'],roman,cids,5 if len(units)<6 else 6,subtitle=p.get('subtitle',''),intro=p.get('description',''),scope=p.get('boundary',''))
        p['divider_index']=opening['book_index'];p['folio']=opening['folio']
    study_div=leaf('further_studies','studies_division','Further studies',intro='The following studies develop the restricted arithmetic constructions, obstructions and remaining realization questions associated with Chapter XI.')
    study1,_=unit('study_arithmetic','study','Arithmetic realization and its obstructions','XI',['XI_research_progress'],7,intro='These studies distinguish finite packet constructions, actual arithmetic candidates, full-character occurrence and comparison for the same candidate.',scope=next(p['boundary'] for p in parts if p['paper']=='XI'))
    study2,_=unit('study_arithmetic_visual','study','Visual studies of arithmetic realization','XI',['XI_research_atlas'],7,intro='The plates give worked constructions and counterexamples, with explicit links to the corresponding arguments and their hypotheses.')
    formal_div=leaf('formal_companions','formal_division','Formal companions',intro='The formal companions connect the mathematical chapters to their Lean declarations, hypotheses, source correspondences and verification evidence. Read each statement with the coverage described by its companion.')
    for p in parts:
        roman=p['paper'];cids=([roman+'_machine_native'] if roman=='I' else [])+[roman+'_lean']
        unit('formal_'+roman,'formal_companion',p['title'],roman,cids,8,intro='The formal companion to Chapter '+roman+' explains the declared hypotheses, theorem correspondences and evidence boundaries.',return_target=p['divider_index'],return_label='Return to Chapter '+roman)
    glossary_leaf=leaf('glossary','glossary','Glossary',intro='Definitions and reading references for the recurring language of the twelve chapters. Local meanings and hypotheses remain those of the cited mathematical treatment.')
    glossary_start=cursor;sequence.append({'kind':'glossary','book_index':cursor,'pages':glossary['pages']});cursor+=glossary['pages']
    reference_div=leaf('sources_references','references_division','Sources and references',
        intro='Sources are grouped by chapter and treatment. Citation labels retain the numbering or short names used in the text. The accompanying files contain the editable material and supporting source records.')
    reference_leaves=[];seen_reference_pages=set()
    for p in parts:
        for c in p['components']:
            groups=c.get('reference_groups',[])
            if not groups and c.get('reference_pages'):
                groups=[{'id':c['id'],'title':'Chapter '+p['paper']+' '+c['title'].lower(),'pages':c['reference_pages']}]
            for g in groups:
                pages=list(g['pages'])
                if not pages:continue
                for sp in pages:
                    key=(c['id'],sp)
                    if sp not in c.get('reference_pages',[]) or key in seen_reference_pages:
                        raise ValueError('Reference group membership is not unique: '+str(key))
                    seen_reference_pages.add(key)
                ident='references_'+re.sub(r'[^A-Za-z0-9_]+','_',g['id'])
                opening,_=unit(ident,'references',g['title'],p['paper'],[c['id']],7,
                    component_pages={c['id']:pages},
                    intro='The citation labels below belong to this treatment. References in the mathematical text link to the corresponding entries.',
                    return_target=next(l['book_index'] for l in leaves if l['id']==c['unit_id']),
                    return_label='Return to '+('the arithmetic studies' if c['role']=='research_progress' else 'Chapter '+p['paper']))
                reference_leaves.append(opening)
    expected_refs={(c['id'],sp) for c in comps.values() for sp in c.get('reference_pages',[])}
    if seen_reference_pages!=expected_refs:raise ValueError('Reference groups do not cover every reference page')
    by_leaf={l['id']:l for l in leaves};by_unit={u['id']:u for u in units}
    for cid,c in comps.items():
        if cid not in ('III_release_record','IV_verification_closeout'):
            if 'unit_id' not in c:raise ValueError('Component lacks reading unit: '+cid)
            target_leaf=c['unit_id']
        else:
            target_leaf='formal_'+c['paper'];c['unit_id']=target_leaf
        for sp in range(c['pages']):
            if sp not in c['keep_pages'] and str(sp) not in c['redirects']:
                c['redirects'][str(sp)]={'leaf_id':target_leaf}
        positions=list(c['book_pages'].values());c['index_start']=min(positions) if positions else None
        c['page_start']=min(positions)-9 if positions else None;c['page_end']=max(positions)-9 if positions else None
        for uid in set(c['page_unit_ids'].values()):
            unit_positions=[c['book_pages'][sp] for sp,unit_id in c['page_unit_ids'].items() if unit_id==uid]
            by_leaf[uid]['entries'].append({'label':c['title'],'target':min(unit_positions),'folio':min(unit_positions)-9})
    for p in parts:
        opening=by_leaf['chapter_'+p['paper']];f=by_leaf['formal_'+p['paper']]
        opening['entries'].append({'label':'Formal companion','target':f['book_index'],'folio':f['folio']})
        if p['paper']=='XI':
            opening['entries'].append({'label':'Further arithmetic studies','target':study_div['book_index'],'folio':study_div['folio']})
        chapter_refs=[l for l in reference_leaves if l['paper']==p['paper']]
        if chapter_refs:opening['entries'].append({'label':'Sources and references','target':chapter_refs[0]['book_index'],'folio':chapter_refs[0]['folio']})
    study_div['entries']=[{'label':x['title'],'target':x['book_index'],'folio':x['folio']} for x in (study1,study2)]
    formal_div['entries']=[{'label':p['paper']+'  '+p['title'],'target':by_leaf['formal_'+p['paper']]['book_index'],'folio':by_leaf['formal_'+p['paper']]['folio']} for p in parts]
    glossary_leaf['entries']=[{'label':letter,'target':glossary_start+page,'folio':glossary_start+page-9} for letter,page in glossary['letter_starts'].items()]
    reference_div['entries']=[{'label':l['title'],'target':l['book_index'],'folio':l['folio']} for l in reference_leaves]
    result={'schema':'realization-calculus.book-spec/3','front_pages':10,'expected_total_pages':cursor,
            'parts':parts,'leaves':leaves,'reading_units':units,'sequence':sequence,
            'glossary':{'index_start':glossary_start,'pages':glossary['pages'],'path':'book/glossary.pdf'},
            'references':{'leaf_id':reference_div['id'],'index_start':reference_div['book_index'],
                          'groups':len(reference_leaves),'source_pages':len(expected_refs)},'front_contents':{}}
    (ROOT/'book/book_layout_accounting.json').write_text(json.dumps({'source_pages':sum(c['pages'] for c in comps.values()),'selected_source_pages':sum(len(c['keep_pages']) for c in comps.values()),'editorial_leaves':len(leaves),'glossary_pages':glossary['pages'],'reference_pages':len(expected_refs),'reference_groups':len(reference_leaves),'total_pages':cursor,'all_selected_pages_unique':all(len(c['keep_pages'])==len(c['book_pages']) for c in comps.values())},indent=2)+'\n')
    return result
