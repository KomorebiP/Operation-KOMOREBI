"""Reading coverage and discovery for the complete Physics reading volume."""
import json
import posixpath

WORK='monographs-physics'
REPORT='documents/physics-reading-map.json'
GUIDE='read/'+WORK+'/start.html'


def counts():
    from physics_reading import CHAPTERS
    from physics_visual import metadata as visual
    from physics_companions import metadata as companions
    v,c=visual(),companions()
    result=dict(treatments=len(CHAPTERS),visual=len(v['pages']),verification=len(c['pages'])+len(c['scope_pages']),plates=12*len(v['atlases']))
    result['total']=sum(result[k] for k in ['treatments','visual','verification'])
    return result


def reading_summary():
    n=counts()
    return f"{n['total']} reading pages: {n['treatments']} treatments, {n['visual']} visual studies and {n['verification']} verification pages"


def destination(row):
    """Every assembled PDF entry must have a corresponding HTML destination."""
    from physics_reading import DATA,CHAPTERS
    from physics_visual import metadata as visual
    from physics_companions import metadata as companions
    match=next((t for t in DATA['treatments'] if t['main'].endswith('/'+row['stem']+'.tex')),None)
    if match:
        url=match.get('part_entries',{}).get(row['part']) or next(p['url'] for p in CHAPTERS if p['treatment']==match['id'])
        return dict(url=url,label='Read in HTML')
    data=visual();match=next((a for a in data['atlases'] if a['main'].endswith('/'+row['stem']+'.tex')),None)
    if match:return dict(url=next(p['url'] for p in data['pages'] if p['atlas']==match['id']),label='Read visual atlas in HTML')
    data=companions();match=next((c for c in data['companions'] if c['main'].endswith('/'+row['stem']+'.tex')),None)
    if match:return dict(url=next(p['url'] for p in data['pages'] if p['companion']==match['id']),label='Read verification material in HTML')
    if row['stem']=='verification_scope':return dict(url=data['scope_pages'][0]['url'],label='Read verification material in HTML')
    raise ValueError('Unmapped Physics book entry: '+row['stem']+' / '+row['part'])


def guide_paths():
    from physics_reading import BOOK,CHAPTERS,DATA
    from physics_visual import INDEX as VISUAL_INDEX
    from physics_companions import INDEX as VERIFY_INDEX,metadata
    from readable_chapters import statement_directory_url
    def step(title,url,description):return dict(title=title,url=url,description=description)
    data=metadata()
    first=[step('Work through the packet-current example','collection/PHYSICS_COLLECTION.html#packet-current','Begin with two packets and an explicit balance calculation.'),
           step('Explore the five visual atlases',VISUAL_INDEX,'Read 60 original plates with their equations, explanations and scope notes.'),
           step('Begin the foundations treatment',CHAPTERS[0]['url'],'Continue from the example into the definitions and stated hypotheses.'),
           step('Read the verification scope',data['scope_pages'][0]['url'],'Distinguish written mathematics, recorded checks and physical interpretation.')]
    study=[step(group['title'],group['start'],'Read this treatment in its retained source order.') for group in DATA['groups']]
    study+=[step('All treatment contents',BOOK['index'],'Choose among the 160 treatment pages and the original PDF destinations.'),
            step('Visual atlas contents',VISUAL_INDEX,'Read the 72 illustrated and supporting pages.'),
            step('Verification and formalization companions',VERIFY_INDEX,'Continue through the three scope pages and all five companions.')]
    evidence=[step('Verification scope and source conventions',data['scope_pages'][0]['url'],'Begin with the distinction between a mathematical statement, a source-identity check and a recorded run.'),
              step('Find a statement and written proof',statement_directory_url(BOOK),'Search the explicit statement blocks in the Physics treatments.')]
    for companion in data['companions']:
        url=next(p['url'] for p in data['pages'] if p['companion']==companion['id'])
        evidence.append(step(companion['title'],url,'Read the declarations, assumptions, retained evidence and remaining obligations for this subject.'))
    evidence.append(step('Inspect the retained Lean project','lean/'+WORK+'/index.html','Inspect selected source modules and their recorded environment; HTML publication adds no Lean execution.'))
    return first,study,evidence


def publish(reader):
    from physics_reading import PAGE_MAP,ROOT,BOOK,CHAPTERS
    from physics_visual import REPORT as VISUAL_REPORT,INDEX as VISUAL_INDEX,metadata as visual
    from physics_companions import REPORT as COMPANION_REPORT,INDEX as COMPANION_INDEX,metadata as companions
    book=getattr(reader,'readable_books',{}).get(WORK)
    if not book:return
    site=reader.site;v,c=visual(),companions()
    rows=[dict(part=r['part'],title=r['title'],stem=r['stem'],pdf_page=r['index_start']+1,html=destination(r)['url']) for r in book['full_book']]
    main=json.loads((site.output/'documents/readable-chapters.json').read_bytes())
    math=sum(p['math_expressions'] for p in main if p['url'].startswith('read/'+WORK+'/'))
    math+=sum(json.loads((site.output/name).read_bytes())['math_expressions'] for name in [VISUAL_REPORT,COMPANION_REPORT])
    report=dict(source_revision=site.revision,counts=counts(),math_expressions=math,
        book_sha256=reader.records[ROOT+'Komorebi_Physics.pdf']['sha256'],manifest_sha256=reader.records[PAGE_MAP]['sha256'],
        indexes=[BOOK['index'],VISUAL_INDEX,COMPANION_INDEX],guide=GUIDE,entries=rows,
        html_pages=[p['url'] for p in CHAPTERS+v['pages']+c['scope_pages']+c['pages']],
        new_proof_review=False,new_lean_execution=False,scientific_computations_executed=False)
    site.write(REPORT,json.dumps(report,ensure_ascii=False,indent=2)+'\n')


def verify(root,documents,pages):
    from physics_reading import PAGE_MAP,ROOT,BOOK,CHAPTERS
    from physics_visual import metadata as visual,INDEX as VISUAL_INDEX,REPORT as VISUAL_REPORT
    from physics_companions import metadata as companions,INDEX as COMPANION_INDEX,REPORT as COMPANION_REPORT
    records={r['repository_path']:r for r in documents['files']}
    if ROOT+'Komorebi_Physics.pdf' not in records:return dict(entries=0,pages=0)
    report=json.loads((root/REPORT).read_bytes())
    manifest=json.loads((root/records[PAGE_MAP]['file_url']).read_bytes())
    assert report['source_revision']==documents['source_revision'] and not BOOK.get('partial')
    assert report['counts']==counts() and report['counts']['total']==305
    assert report['book_sha256']==records[ROOT+'Komorebi_Physics.pdf']['sha256']
    assert report['manifest_sha256']==records[PAGE_MAP]['sha256']
    expected=[dict(part=r['part'],title=r['title'],stem=r['stem'],pdf_page=r['index_start']+1,html=destination(r)['url']) for r in manifest]
    assert report['entries']==expected and len(expected)==21
    assert report['indexes']==[BOOK['index'],VISUAL_INDEX,COMPANION_INDEX] and report['guide']==GUIDE
    v,c=visual(),companions();html_pages=[p['url'] for p in CHAPTERS+v['pages']+c['scope_pages']+c['pages']]
    assert report['html_pages']==html_pages and len(html_pages)==len(set(html_pages))==305
    assert all(p in pages for p in html_pages+report['indexes'])
    for row in expected:
        assert posixpath.relpath(row['html'],posixpath.dirname(BOOK['index'])) in pages[BOOK['index']].links
    main=json.loads((root/'documents/readable-chapters.json').read_bytes())
    math=sum(p['math_expressions'] for p in main if p['url'].startswith('read/'+WORK+'/'))
    math+=sum(json.loads((root/name).read_bytes())['math_expressions'] for name in [VISUAL_REPORT,COMPANION_REPORT])
    assert report['math_expressions']==math==7571
    assert not any(report[k] for k in ['new_proof_review','new_lean_execution','scientific_computations_executed'])
    return dict(entries=len(expected),pages=len(html_pages),math_expressions=math)
