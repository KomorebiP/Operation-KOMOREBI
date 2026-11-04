"""A visual contents page for the unchanged Quantum and Circuits reading pages."""
import hashlib
import html
import json

from quantum_reading import CHAPTERS, DATA, PREFIX, WORK

PAGE = PREFIX+'visual-guides.html'
PDF = 'monographs/quantum-and-circuits/volume/output/Realization_Calculus_Quantum_and_Circuits.pdf'
SEQUENCES = (
    ('arithmetic','Quantum arithmetic','q_visual.tex',
     'Follow selectors, Fourier coordinates, amplitudes, and measurement through the original worked diagrams.'),
    ('circuits','Circuit obstructions','c_visual.tex',
     'Explore legal circuit models, restored boundaries, cut comparisons, and the limits recorded with each example.'),
)


def sequences():
    result=[]
    for identifier,title,filename,summary in SEQUENCES:
        pages=[dict(url=c['url'],title=c['title']) for c in CHAPTERS if c['source'].endswith('/'+filename)]
        sources={c['source'] for c in CHAPTERS if c['source'].endswith('/'+filename)}
        if len(pages)!=25 or len({p['url'] for p in pages})!=25 or len(sources)!=1:
            raise ValueError('Review Quantum visual sequence: '+identifier)
        source=sources.pop()
        result.append(dict(id=identifier,title=title,summary=summary,source=source,
                           source_sha256=DATA['source_sha256'][source],pages=pages))
    return result


def is_page(page):
    return page==PAGE or any(page==p['url'] for sequence in sequences() for p in sequence['pages'])


def inventory(root,files):
    from reader_documents import png_dimensions
    from quantum_reading import BOOK
    records={r['repository_path']:r for r in files}
    if PDF not in records:raise ValueError('Missing Quantum visual reading resource: '+PDF)
    receipt=json.loads((root/'website/assets/figures/quantum-arithmetic/figures.json').read_bytes())
    figure=next(f for f in receipt['figures'] if f['image'].endswith('/q_01_primitive_roots.png'))
    raw=(root/'website'/figure['image']).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=figure['image_sha256']:raise ValueError('Changed Quantum visual preview')
    width,height=png_dimensions(raw);record=records[PDF]
    return dict(work=WORK,label='Quantum and Circuits',title=BOOK['title'],number=None,
        short_title='Quantum arithmetic and circuit diagrams',
        summary='Two complete visual sequences: 25 pages of quantum arithmetic and 25 pages of circuit obstructions.',
        units=50,unit_kind='visuals',source_unit_kind='visual pages',topics='quantum arithmetic circuits Fourier measurement gates boundaries restoration',
        preview=dict(image=figure['image'],sha256=figure['image_sha256'],width=width,height=height),
        manuscript=BOOK['index'],overview='collection/works/'+WORK+'.html',html_atlas=PAGE,
        visual_pdf=record['url'],pdf_source=PDF,pdf_sha256=record['sha256'],integrated_pdf=True,
        sequences=sequences())


def publish(reader):
    site=reader.site;e=html.escape
    body='<p class="eyebrow">Quantum and Circuits · Visual guides</p><h1>Explore the 50 visual pages</h1>'
    body+='<p>Choose either complete 25-page sequence. The linked reading pages retain the original drawings, selectable equations, source links, and recorded limits.</p>'
    body+=reader.work_routes(WORK,PAGE)
    body+='<nav class="quantum-visual-jump" aria-label="Choose a visual sequence"><a href="#arithmetic">Quantum arithmetic · 25 pages</a><a href="#circuits">Circuit obstructions · 25 pages</a></nav>'
    body+='<div class="quantum-visual-sequences">'
    for sequence in sequences():
        body+='<section id="'+sequence['id']+'"><h2>'+e(sequence['title'])+'</h2><p>'+e(sequence['summary'])+'</p><ol>'
        for page in sequence['pages']:
            body+='<li><a href="'+e(site.rel(page['url'],PAGE),quote=True)+'">'+e(page['title'])+'</a></li>'
        body+='</ol></section>'
    body+='</div><p>For a shorter suggested route, use <a href="start.html#visual">the visual introduction</a>. For definitions and proofs, return to <a href="index.html">the full volume contents</a>.</p>'
    site.page(PAGE,'Quantum and Circuits: Visual guides',body)
    site.search.append(dict(title='Quantum and Circuits / Visual guides',group='Collection',kind='Guides',visual_guide=True,
        work_ids=[WORK],url=PAGE,text='50 visual pages quantum arithmetic circuits Fourier amplitudes measurement restoration boundaries'))


def verify(pages):
    import posixpath
    assert PAGE in pages,('Missing Quantum visual contents',PAGE)
    for sequence in sequences():
        assert sequence['id'] in pages[PAGE].ids
        for page in sequence['pages']:
            assert page['url'] in pages,('Missing Quantum visual page',page['url'])
            assert posixpath.relpath(page['url'],posixpath.dirname(PAGE)) in pages[PAGE].links
    return 50
