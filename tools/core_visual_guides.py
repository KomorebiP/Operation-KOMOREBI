"""One source-derived directory of visual reading routes for the core sequence."""
import html
import json
import re
import hashlib
import posixpath

INDEX='read/visual-guides.html'
REPORT='documents/core-visual-guides.json'

# Editorial navigation labels; the original manuscript titles remain in the inventory.
GUIDES={
 'paper-i':('Operator systems and packet coordinates','Start with operators, their compositions, and the coordinates needed to recover them.',22,'plates','grammar_budget','operators seeds rank Fourier'),
 'paper-ii':('Refinement and integral separation','See how refinement, weighted transfer, and integral constraints fit together.',24,'plates','three_resolutions','refinement weights integral separation'),
 'paper-iii':('Nonlinear transfer and obstructions','Follow typed transfers, nonlinear packets, and the obstructions to gluing local data.',24,'plates','three_structures','nonlinear obstruction gluing'),
 'paper-iv':('Cyclic functions and spectral zeros','Explore roots of unity, cyclic analytic families, and reciprocal and spectral data.',26,'plates','three_views','analytic functions reciprocal roots unity zeros'),
 'paper-v':('Signals and multiresolution','Move between samples, packets, and multiresolution signal coordinates.',40,'plates','three_worlds','signals wavelets Haar filters polyphase'),
 'paper-vi':('Transfer semigroups and memory','Track time, transfer, and memory in finite operator models.',42,'plates','clock','semigroups time memory'),
 'paper-vii':('Quantum seeds and dynamics','Distinguish quantum seeds, finite representations, and effective dynamics.',40,'plates','three_objects','quantum dynamics states seeds'),
 'paper-viii':('Algorithms, compilation, and GPUs','Follow packet operators from exact factorizations to compiled algorithms and GPU models.',32,'plates','factored_application','algorithms compilation GPU computing'),
 'paper-ix':('Euler congruences','See normalization, divisibility gains, exact periods, and worked lifting examples.',23,'sections','normalization','Euler congruences valuations p-adic Newton lifting'),
 'paper-x':('Residual seeds and recovery','Separate residual roots, compatible branches, and occupied packets through worked examples.',30,'plates','01_three_questions','residual seeds recovery branches occupancy'),
 'paper-xi':('Tame and wild packet geometry','Follow finite packet geometry into restricted constructions and the open realization boundary.',47,'lessons','01_three_objects','Langlands tame wild Heisenberg realization'),
 'paper-xii':('Patching, support, and Hecke packets','Use explicit local models to study support, Hecke packets, and conditional completion.',27,'plates','monomial_quotient','patching support Hecke Fitting automorphic completion'),
}


def is_visual_guide(work,page):
    from readable_chapters import BOOKS
    index=BOOKS.get(work,{}).get('atlas_index')
    return bool(index and page.startswith(index.removesuffix('index.html')))


def guide_navigation(work,page,more=''):
    """Keep visual readers in the visual format when they change papers."""
    from readable_chapters import BOOKS
    e=html.escape;relative=lambda target:posixpath.relpath(target,posixpath.dirname(page))
    book=BOOKS[work];index=book['atlas_index']
    body='<nav class="work-overview-nav paper-routes visual-guide-routes" aria-label="Visual guide navigation">'
    body+='<a href="'+relative(INDEX)+'">All visual guides</a>'
    body+='<a href="'+relative(index)+'"'+(' aria-current="page"' if page==index else '')+'>Guide contents</a>'
    body+='<a href="'+relative(book['index'])+'">Read paper</a>'
    body+='<details class="visual-guide-switch"><summary>Switch guide</summary><nav aria-label="Choose a visual guide"><ul>'
    for identifier,info in GUIDES.items():
        other=BOOKS[identifier];current=' aria-current="'+('page' if page==index else 'location')+'"' if identifier==work else ''
        body+='<li><a href="'+relative(other['atlas_index'])+'"'+current+'><strong>'+e(other['label'])+'</strong><span>'+e(info[0])+'</span></a></li>'
    return body+'</ul></nav></details>'+more+'</nav>'


def inventory(root,files):
    from readable_chapters import BOOKS
    registry=json.loads((root/'manifests/browse-resources.json').read_bytes())
    records={r['repository_path']:r for r in files}
    result=[]
    for component in registry['components']:
        work=component['id']
        if not re.fullmatch(r'paper-[ivx]+',work):
            continue
        config=BOOKS[work]
        visual=next((r for r in component['resources'] if r['kind']=='visual'),None)
        # Paper I retains its atlas inside the main monograph.
        resource=visual or next(r for r in component['resources'] if r['kind']=='pdf')
        path=component['destination']+'/'+resource['path']
        if path not in records:
            raise ValueError('Missing visual reading resource: '+path)
        record=records[path]
        short,summary,units,kind,preview_name,topics=GUIDES[work]
        from reader_documents import png_dimensions
        receipt=json.loads((root/('website/assets/atlas/'+work+'/figures.json')).read_bytes())
        figure=next(f for f in receipt['figures'] if f['name']==preview_name)
        raw=(root/'website'/figure['image']).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=figure['image_sha256']:raise ValueError('Changed visual directory preview: '+work)
        width,height=png_dimensions(raw)
        result.append(dict(work=work,label=config['label'],title=config['title'],number=len(result)+1,
            short_title=short,summary=summary,units=units,unit_kind=kind,topics=topics,
            preview=dict(image=figure['image'],sha256=figure['image_sha256'],width=width,height=height),
            manuscript=config['index'],overview='collection/works/'+work+'.html',
            html_atlas=config.get('atlas_index'),
            visual_pdf=record['url'],pdf_source=path,pdf_sha256=record['sha256'],
            integrated_pdf=visual is None))
    if len(result)!=12 or len({r['work'] for r in result})!=12:
        raise ValueError('Review the core visual-guide inventory')
    return result


def render(reader):
    site=reader.site
    rows=inventory(site.root,reader.records.values())
    count=sum(bool(row['html_atlas']) for row in rows)
    body='<div class="visual-directory"><p class="eyebrow">The twelve core papers</p><h1>Visual guides</h1>'
    body+='<p class="visual-directory-intro">Choose a subject or paper. Each complete guide has original diagrams, selectable mathematics, and links back to the paper.</p>'
    body+='<form id="visual-guide-filter" class="visual-guide-filter" role="search" hidden><label for="visual-guide-query">Find a visual guide</label><div><input id="visual-guide-query" type="search" name="q" placeholder="Paper number, title, or topic" aria-controls="visual-guide-list" aria-describedby="visual-guide-count"><button type="reset">Clear</button></div></form>'
    body+='<div class="visual-directory-tools"><nav class="visual-guide-jump" aria-label="Jump to a paper">'+''.join('<a href="#'+r['work']+'" aria-label="'+r['label']+'">'+r['label'].removeprefix('Paper ')+'</a>' for r in rows)+'</nav><p id="visual-guide-count" role="status" aria-live="polite">'+str(count)+' guides</p></div>'
    body+='<p id="visual-guide-empty" hidden>No guides match. Try another subject or clear the search.</p><ol id="visual-guide-list" class="visual-guide-grid">'
    for row in rows:
        e=html.escape;identifier=row['work'];preview=row['preview']
        search=' '.join([row['label'],'Paper '+str(row['number']),row['title'],row['short_title'],row['summary'],row['topics']])
        body+='<li class="visual-guide-card" id="'+identifier+'" data-number="'+str(row['number'])+'" data-roman="'+row['label'].removeprefix('Paper ').lower()+'" data-search="'+e(search,quote=True)+'">'
        body+='<a class="visual-guide-open" href="'+site.rel(row['html_atlas'],INDEX)+'" aria-labelledby="'+identifier+'-label '+identifier+'-title" title="'+e(row['title'],quote=True)+'">'
        body+='<div class="visual-guide-preview"><img src="'+site.rel(preview['image'],INDEX)+'" width="'+str(preview['width'])+'" height="'+str(preview['height'])+'" alt="" loading="lazy" decoding="async"></div>'
        body+='<div class="visual-guide-copy"><p class="eyebrow" id="'+identifier+'-label">'+row['label']+' <span>'+str(row['units'])+' '+row['unit_kind']+'</span></p><h2 id="'+identifier+'-title">'+e(row['short_title'])+'</h2><p>'+e(row['summary'])+'</p><span class="visual-guide-action">Open visual guide <span aria-hidden="true">→</span></span></div></a>'
        body+='<nav class="visual-guide-formats" aria-label="'+row['label']+' other reading formats"><a href="'+site.rel(row['manuscript'],INDEX)+'">Read paper</a><a href="'+site.rel(row['visual_pdf'],INDEX)+'">'+('Atlas in monograph PDF' if row['integrated_pdf'] else 'Guide PDF')+'</a><a href="'+site.rel(row['overview'],INDEX)+'">About this paper</a></nav></li>'
    body+='</ol><div class="visual-directory-footer"><p>The guides retain their papers’ assumptions and recorded limits.</p><nav aria-label="Other reading collections"><a href="index.html">Reading library</a><a href="'+site.rel('documents.html',INDEX)+'">All papers and PDFs</a></nav></div></div>'
    script=site.rel('assets/visual-guides.js',INDEX)+'?v='+hashlib.sha256((site.root/'website/assets/visual-guides.js').read_bytes()).hexdigest()[:12]
    body+='<script defer src="'+script+'"></script>'
    site.page(INDEX,'Core visual guides',body)
    site.write(REPORT,json.dumps(dict(source_revision=site.revision,guides=rows),indent=2)+'\n')
    site.search.append(dict(title='Core visual guides',group='Collection',kind='Guides',url=INDEX,
        text='Visual guides and worked atlases for all twelve core papers',work_ids=[r['work'] for r in rows]))


def verify(root,documents,pages):
    record=json.loads((root/REPORT).read_bytes())
    # Recompute destinations from the maintained reading configurations and
    # receipt-owned PDF records; a stale report cannot claim a port exists.
    repository=__import__('pathlib').Path(__file__).resolve().parents[1]
    rows=inventory(repository,documents['files'])
    assert record==dict(source_revision=documents['source_revision'],guides=rows)
    assert {r['work'] for r in rows}<=set(pages[INDEX].ids)
    import posixpath
    for row in rows:
        targets=[row['visual_pdf'],row['manuscript'],row['overview']]
        if row['html_atlas']:targets.append(row['html_atlas'])
        for target in targets:
            assert target in pages
            assert posixpath.relpath(target,posixpath.dirname(INDEX)) in pages[INDEX].links
        preview=row['preview'];raw=(root/preview['image']).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==preview['sha256']
        prefix=row['html_atlas'].removesuffix('index.html')
        guide_pages=[path for path in pages if path.startswith(prefix)]
        assert len(guide_pages)==row['units']+1,('Wrong visual directory unit count',row['work'])
        for page in guide_pages:
            links=pages[page].links
            for target in [INDEX,row['manuscript'],*[r['html_atlas'] for r in rows]]:
                assert posixpath.relpath(target,posixpath.dirname(page)) in links,('Missing visual reading route',page,target)
    return dict(guides=len(rows),html_atlases=sum(bool(r['html_atlas']) for r in rows))
