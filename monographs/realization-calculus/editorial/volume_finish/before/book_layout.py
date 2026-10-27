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
    # Paper X embeds the same 30 visual-study pages in its mathematical reader.
    # Bind by text and image identities, without assuming its final pagination.
    main,visual=comps['X_traditional'],comps['X_visual']
    a,b=fitz.open(ROOT/main['path']),fitz.open(ROOT/visual['path'])
    matches=[]
    for bp in list(visual['keep_pages']):
        bt=norm(b[bp].get_text())
        if len(bt)<250:continue
        hits=[ap for ap in main['keep_pages'] if norm(a[ap].get_text())==bt]
        if len(hits)==1:
            ap=hits[0];visual['keep_pages'].remove(bp)
            visual['redirects'][str(bp)]={'component_id':main['id'],'source_page':ap}
            matches.append(ap)
            rows.append({'chapter':'X','omitted_component':visual['id'],'omitted_page':bp+1,'canonical_component':main['id'],'canonical_page':ap+1,'evidence':'Exact normalized page text, original append-copy build provenance.'})
    if len(matches)!=30:raise ValueError(f'Expected thirty verified X plate duplicates, found {len(matches)}')
    main['atlas_start']=min(matches)
    a.close();b.close()
    (ROOT/'book/canonical_visual_routes.json').write_text(json.dumps({'routes':rows},indent=2)+'\n')

def make_layout(parts,adaptations):
    comps={c['id']:c for p in parts for c in p['components']}
    for cid,c in comps.items():
        c['keep_pages']=list(adaptations[cid]['keep_pages']);c['redirects']={};c['book_pages']={}
        c['display_normalized']=True
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
    def chunk(cid,pages):
        nonlocal cursor
        if not pages:return
        c=comps[cid];sequence.append({'kind':'component','component_id':cid,'source_pages':pages,'book_index':cursor})
        for sp in pages:
            if str(sp) in c['book_pages']:raise ValueError('A source page was selected twice')
            c['book_pages'][str(sp)]=cursor;cursor+=1
    def unit(ident,kind,title,paper,cids,contents_page,**kw):
        opening=leaf(ident,kind,title,paper,**kw)
        u={'id':ident,'kind':kind,'paper':paper,'title':title,'component_ids':cids,'leaf_id':ident,'index_start':opening['book_index'],'contents_page':contents_page}
        for cid in cids:comps[cid]['unit_id']=ident
        main=next((cid for cid in cids if comps[cid]['role']=='traditional'),None)
        visual=next((cid for cid in cids if comps[cid]['role']=='visual'),None)
        handled=set()
        if main and visual and 'atlas_start' in comps[main] and comps[visual]['keep_pages']:
            point=comps[main]['atlas_start'];keep=comps[main]['keep_pages']
            chunk(main,[p for p in keep if p<point])
            for cid in cids:
                if comps[cid]['role']=='analytic_supplement':chunk(cid,comps[cid]['keep_pages']);handled.add(cid)
            chunk(visual,comps[visual]['keep_pages']);chunk(main,[p for p in keep if p>=point]);handled|={main,visual}
        for cid in cids:
            if cid not in handled:chunk(cid,comps[cid]['keep_pages'])
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
        if positions:
            by_leaf[target_leaf]['entries'].append({'label':c['title'],'target':min(positions),'folio':min(positions)-9})
    for p in parts:
        opening=by_leaf['chapter_'+p['paper']];f=by_leaf['formal_'+p['paper']]
        opening['entries'].append({'label':'Formal companion','target':f['book_index'],'folio':f['folio']})
        if p['paper']=='XI':
            opening['entries'].append({'label':'Further arithmetic studies','target':study_div['book_index'],'folio':study_div['folio']})
    study_div['entries']=[{'label':x['title'],'target':x['book_index'],'folio':x['folio']} for x in (study1,study2)]
    formal_div['entries']=[{'label':p['paper']+'  '+p['title'],'target':by_leaf['formal_'+p['paper']]['book_index'],'folio':by_leaf['formal_'+p['paper']]['folio']} for p in parts]
    glossary_leaf['entries']=[{'label':letter,'target':glossary_start+page,'folio':glossary_start+page-9} for letter,page in glossary['letter_starts'].items()]
    result={'schema':'realization-calculus.book-spec/2','front_pages':10,'expected_total_pages':cursor,'parts':parts,'leaves':leaves,'reading_units':units,'sequence':sequence,'glossary':{'index_start':glossary_start,'pages':glossary['pages'],'path':'book/glossary.pdf'},'front_contents':{}}
    (ROOT/'book/book_layout_accounting.json').write_text(json.dumps({'source_pages':sum(c['pages'] for c in comps.values()),'selected_source_pages':sum(len(c['keep_pages']) for c in comps.values()),'editorial_leaves':len(leaves),'glossary_pages':glossary['pages'],'total_pages':cursor,'all_selected_pages_unique':all(len(c['keep_pages'])==len(c['book_pages']) for c in comps.values())},indent=2)+'\n')
    return result
