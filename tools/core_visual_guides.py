"""One source-derived directory of visual reading routes for the core sequence."""
import html
import json
import re

INDEX='read/visual-guides.html'
REPORT='documents/core-visual-guides.json'


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
        result.append(dict(work=work,label=config['label'],title=config['title'],
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
    body='<p class="eyebrow">The twelve core papers</p><h1>Visual guides and worked atlases</h1>'
    body+='<p>Choose a visual route into each paper. '+str(count)+' complete atlases have HTML plates with original drawings and selectable mathematics. Every paper also retains its original visual material in an on-site PDF.</p>'
    body+='<p><a href="index.html">Reading library</a> · <a href="'+site.rel('documents.html',INDEX)+'">All papers and PDFs</a></p><div class="work-list">'
    for row in rows:
        body+='<section class="work" id="'+row['work']+'"><p class="eyebrow">'+row['label']+'</p><h2>'+html.escape(row['title'])+'</h2>'
        body+='<p>'+('Complete visual atlas in HTML.' if row['html_atlas'] else 'Visual atlas available in the PDF.')+'</p>'
        body+='<nav aria-label="'+row['label']+' visual reading routes">'
        if row['html_atlas']:
            body+='<a class="button" href="'+site.rel(row['html_atlas'],INDEX)+'">Read the HTML atlas</a>'
        body+='<a href="'+site.rel(row['visual_pdf'],INDEX)+'">'+('Monograph with visual atlas (PDF)' if row['integrated_pdf'] else 'Visual guide (PDF)')+'</a>'
        body+='<a href="'+site.rel(row['manuscript'],INDEX)+'">Manuscript contents</a><a href="'+site.rel(row['overview'],INDEX)+'">Work and evidence</a></nav></section>'
    body+='</div><p>The guides retain the evidence and hypotheses of their source editions. A reading conversion adds no proof review or Lean execution.</p>'
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
    assert {r['work'] for r in rows}<=pages[INDEX].ids
    import posixpath
    for row in rows:
        targets=[row['visual_pdf'],row['manuscript'],row['overview']]
        if row['html_atlas']:targets.append(row['html_atlas'])
        for target in targets:
            assert target in pages
            assert posixpath.relpath(target,posixpath.dirname(INDEX)) in pages[INDEX].links
    return dict(guides=len(rows),html_atlases=sum(bool(r['html_atlas']) for r in rows))
