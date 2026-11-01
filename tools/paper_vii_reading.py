"""Source-preserving topic chapters and inline original figures for Paper VII."""
import hashlib
import html
import json
import posixpath
import re

BASE = 'papers/paper-vii/current/editable/traditional/'
MAIN = BASE+'Paper_VII_Traditional_Final.tex'
PARTS = [
    ('01_finite_core.tex', 'finite-quantum-seeds', 'I. Finite quantum seed calculus', 1),
    ('02_strengthened.tex', 'effective-dynamics-and-towers', 'II. Effective dynamics and refinement towers', 2),
    ('03_supplement_01.tex', 'exact-packets-and-resolvents', 'III. Exact packets, symmetry and resolvents', 3),
    ('03_supplement_02.tex', 'basis-refinement-and-connections', 'III. Bases, refinement, connections and channels', 3),
    ('03_supplement_03.tex', 'orbits-and-character-projectors', 'III. Orbits, Schmidt rank and character projectors', 3),
    ('03_supplement_04.tex', 'leakage-curvature-and-recovery', 'III. Leakage, curvature and syndrome recovery', 3),
    ('03_supplement_05.tex', 'finite-error-correction', 'III. Finite error correction and recovery', 3),
    ('03_supplement_06.tex', 'range-bundles-and-curvature', 'III. Range bundles, connections and curvature', 3),
    ('04_alternative_derivations.tex', 'alternative-derivations', 'III. Alternative derivations', 3),
]
CHAPTERS = [dict(source=MAIN, url='read/paper-vii/orientation.html', title='Reading orientation',
                 work='paper-vii', start_line=145, end_line=210),
            dict(source=BASE+'monograph_examples.tex', url='read/paper-vii/three-finite-models.html',
                 title='Three exact finite models', work='paper-vii', part=1, reset_part=True)]
CORE_SOURCE=BASE+'parts/01_finite_core.tex'
FULL_CORE='read/paper-vii/finite-quantum-seeds.html'
FIGURE_MANIFEST='website/paper-vii-figures.json'
CORE_TOPICS=[
    (1,'quantum-seeds','The quantum seed realization'),
    (74,'seed-rank','Quantum seed rank and cyclicity'),
    (184,'symmetry-packets','Cyclic symmetry packets'),
    (273,'circuits-and-bell-states','Quantum circuits as packet paths'),
    (365,'hamiltonians-and-leakage','Symmetry-resolved Hamiltonians and leakage'),
    (464,'moving-packets','Moving packets, connections, and curvature'),
    (670,'measurements','Measurements and quantum channels'),
    (718,'quantum-channels','Kraus transfer'),
    (790,'error-correction','Quantum error correction as obstruction-packet annihilation'),
    (892,'effective-dynamics','Exact effective dynamics'),
    (998,'finite-geometry','Finite quantum geometry'),
    (1113,'spectral-dimension','Spectral dimension and continuum diagnostics'),
    (1196,'constraints-and-continuum','Constraint packets and the quantum-spacetime boundary'),
    (1260,'numerical-certificates','Numerical certificates'),
    (1306,'core-conclusion','Conclusion'),
]
CORE_CHAPTERS=[dict(source=CORE_SOURCE,url='read/paper-vii/'+slug+'.html',title=title,
                    work='paper-vii',part=1,reset_part=i==0,start_line=start,
                    end_line=CORE_TOPICS[i+1][0]-1 if i+1<len(CORE_TOPICS) else 1332,
                    figure_base=BASE+'assets/core/')
               for i,(start,slug,title) in enumerate(CORE_TOPICS)]
CHAPTERS+=CORE_CHAPTERS
for i,(name,slug,title,part) in enumerate(PARTS[1:],1):
    CHAPTERS.append(dict(source=BASE+'parts/'+name,url='read/paper-vii/'+slug+'.html',title=title,
                         work='paper-vii',part=part,reset_part=i in (1,2),
                         figure_base=BASE+'assets/strengthened/'))
BOOK = dict(work='paper-vii', label='Paper VII', base=BASE, main=MAIN, bib=BASE+'references.bib',
            index='read/paper-vii/index.html', bib_page='read/paper-vii/references.html',
            title='Quantum Seeds and Effective Dynamics', chapters=CHAPTERS, main_chapters=23,
            part_numbering=True, figure_pdfs=True,
            collected_parts=[dict(url=FULL_CORE,title='Read all of Part I on one page')],
            reading_introduction='Read Part I in short topic chapters, then continue through effective dynamics and the supplementary developments.',
            atlas_index='read/paper-vii/atlas/index.html',atlas_link_text='Explore all 40 worked atlas plates in HTML',
            reading_note='All 38 manuscript figures appear inline. The 40 worked atlas plates also have HTML pages with original drawings, selectable labels, and manuscript links. The HTML preserves the source wording, mathematics, and recorded limits; it adds no proof assessment.',
            main_inputs=['monograph_examples.tex']+['parts/'+p[0] for p in PARTS]+['monograph_atlas.tex'],
            html_inputs={'monograph_atlas.tex':dict(url='read/paper-vii/atlas/index.html',title='Read the 40 worked atlas plates in HTML',note='')})


def figure_items(body):
    """Parse only the single-image and paired-minipage forms in this edition."""
    from readable_chapters import group
    body=re.sub(r'\\centering\b|\\hfill\b|\\begin\{minipage\}\[t\]\{0\.48\\textwidth\}|\\end\{minipage\}', '',body)
    items=[]
    while body.strip():
        body=body.lstrip()
        match=re.match(r'\\includegraphics\[width=(?:[0-9.]+)?\\textwidth\]\{([^{}]+\.pdf)\}\s*\\(?:captionof\{figure\}|caption)\{',body)
        if not match: raise ValueError('Unsupported Paper VII figure: '+body[:100])
        caption,end=group(body,match.end()-1)
        body=body[end:]
        labels=re.match(r'(?:\s*\\label\{[^{}]+\})*',body)
        body=body[labels.end():]
        items.append((match[1],caption))
    if not items: raise ValueError('Empty Paper VII figure')
    return items


def figure_path(spec, name):
    return posixpath.normpath((BASE if '/' in name else spec.get('figure_base',BASE))+name)


def validate_core_ranges(text):
    lines=text.splitlines()
    if len(lines)!=1332:raise ValueError('Review Paper VII core source boundaries')
    for i,spec in enumerate(CORE_CHAPTERS):
        if i and CORE_CHAPTERS[i-1]['end_line']+1!=spec['start_line']:
            raise ValueError('Paper VII topic ranges have a gap or overlap')
        kind='subsection' if spec['start_line']==718 else 'section'
        if not lines[spec['start_line']-1].startswith('\\'+kind+'{'+spec['title']+'}'):
            raise ValueError('Review Paper VII topic heading '+spec['title'])


def assets(reader):
    if hasattr(reader,'paper_vii_assets'):return reader.paper_vii_assets
    from build_reader_site import safe_path
    from reader_documents import png_dimensions
    report=json.loads((reader.site.root/FIGURE_MANIFEST).read_bytes())
    found={}
    for item in report['figures']:
        source=item['source']
        if not source.startswith(BASE) or source in found or not item['image'].startswith('assets/figures/paper-vii/'):
            raise ValueError('Unexpected Paper VII figure path')
        record=reader.add(source)
        if not record or hashlib.sha256(reader.site.read_source(record)).hexdigest()!=item['source_sha256']:
            raise ValueError('Paper VII figure PDF differs: '+source)
        raw=(reader.site.root/'website'/safe_path(item['image'])).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=item['image_sha256'] or png_dimensions(raw)!=(item['width'],item['height']):
            raise ValueError('Paper VII figure image differs: '+source)
        if not item.get('alt') or not item.get('description'):
            raise ValueError('Missing Paper VII figure description: '+source)
        record.update(figure=True,figure_source=True)
        found[source]=item
    if len(found)!=38:raise ValueError('Paper VII needs all 38 manuscript figures')
    reader.paper_vii_assets=found
    reader.paper_vii_figure_usage=[]
    return found


def prepare_figures(reader, spec, chapter):
    figures=assets(reader)
    if spec['url']==CHAPTERS[0]['url']:
        reader.paper_vii_figure_usage=[]
    if spec['source']==CORE_SOURCE and spec.get('reset_part'):
        validate_core_ranges(reader.site.read_source(reader.records[CORE_SOURCE]).decode('utf-8-sig'))
    for node in chapter.nodes:
        if node['kind']=='figure':
            for name,caption in figure_items(node['body']):
                path=figure_path(spec,name)
                if path not in figures or caption!=figures[path]['caption']:
                    raise ValueError('Review Paper VII figure caption: '+name)
                reader.paper_vii_figure_usage.append(path)
    if spec['url']==CHAPTERS[-1]['url']:
        if len(reader.paper_vii_figure_usage)!=38 or set(reader.paper_vii_figure_usage)!=set(figures):
            raise ValueError('Every Paper VII figure must appear exactly once')


def render_figure(reader, spec, chapter, node, links):
    from readable_chapters import passage_links
    result='<div id="'+node['id']+'" class="original-figures" tabindex="-1">'
    for name,caption in figure_items(node['body']):
        source=figure_path(spec,name)
        record=reader.records[source]
        item=assets(reader)[source]
        viewer=html.escape(reader.viewer_url(record,spec['url']),quote=True)
        raw=(reader.site.root/'website'/item['image']).read_bytes()
        target=reader.site.output/item['image']
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
        reader.images[source]=dict(width=item['width'],height=item['height'],
            repository_path='website/'+item['image'],file_url=item['image'],size=len(raw),
            sha256=item['image_sha256'],git_blob_sha1=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),
            source=source,source_sha256=item['source_sha256'])
        image=html.escape(reader.site.rel(item['image'],spec['url']),quote=True)
        result+='<figure class="reading-figure"><a href="'+image+'" aria-label="Open full-size figure: '+html.escape(item['alt'],quote=True)+'">'
        result+='<img src="'+image+'" width="'+str(item['width'])+'" height="'+str(item['height'])+'" alt="'+html.escape(item['alt'],quote=True)+'" loading="lazy"></a>'
        result+='<figcaption>'+chapter.inline(caption)+'</figcaption>'
        result+='<details class="figure-description"><summary>Text description</summary><p>'+html.escape(item['description'])+'</p></details>'
        result+='<p><a href="'+viewer+'">Open original figure (PDF)</a></p>'
        result+='</figure>'
    return result+passage_links(links)+'</div>'


def render_collected_core(reader,book):
    site=reader.site
    body='<p class="eyebrow">Paper VII / Part I</p><h1>Finite quantum seed calculus</h1>'
    body+='<p>Read Part I on one page, or choose a shorter topic below. Original section numbers and source-line links are retained.</p>'
    body+='<p><a href="index.html">Full Paper VII contents</a></p><nav id="contents" aria-label="Part I topics"><h2>Contents</h2><ol>'
    body+=''.join('<li><a href="'+site.rel(c['url'],FULL_CORE)+'">'+html.escape(c['title'])+'</a></li>' for c in CORE_CHAPTERS)+'</ol></nav>'
    body+='<section id="chapter-text">'
    for spec in CORE_CHAPTERS:
        text=(site.output/spec['url']).read_text(encoding='utf-8')
        match=re.search(r'<article id="chapter-text"[^>]*>(.*?)</article>',text,re.S)
        if not match:raise ValueError('Missing Paper VII reading article')
        body+='<article class="readable-chapter">'+match[1]+'</article>'
    body+='</section><p><a href="index.html">Return to full Paper VII contents</a></p>'
    site.page(FULL_CORE,'Paper VII: Finite quantum seed calculus / complete Part I',body)
    site.write('documents/paper-vii-figures.json',json.dumps(dict(figures=list(assets(reader).values()),
               collection_revision=site.revision,core_pages=[c['url'] for c in CORE_CHAPTERS],
               collected_core=FULL_CORE,scope='Original PDF figures and source-preserving topic chapters; no new proof assessment.'),indent=2)+'\n')


def verify_site(root,pages,documents):
    from reader_documents import png_dimensions
    record=json.loads((root/'documents/paper-vii-figures.json').read_bytes())
    assert record['core_pages']==[c['url'] for c in CORE_CHAPTERS]
    assert len(record['figures'])==38
    sources={r['repository_path']:r for r in documents['files']}
    seen=[]
    for spec in CHAPTERS:
        assert spec['url'] in pages
        page=pages[spec['url']]
        assert not page.iframes, 'Paper VII figures must render inline'
        markup=(root/spec['url']).read_text(encoding='utf-8')
        assert markup.count('<summary>Text description</summary>')==len(page.images)
        for image in page.images:
            seen.append(posixpath.normpath(posixpath.join(posixpath.dirname(spec['url']),image['src'])))
            assert image['alt'] and int(image['width'])>0 and int(image['height'])>0
    assert len(seen)==38 and len(set(seen))==38
    for item in record['figures']:
        assert item['image'] in seen
        raw=(root/item['image']).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==item['image_sha256']
        assert png_dimensions(raw)==(item['width'],item['height'])
        assert sources[item['source']]['sha256']==item['source_sha256']
    assert FULL_CORE in pages
    legacy=pages[FULL_CORE]
    for spec in CORE_CHAPTERS:
        assert {identifier for identifier in pages[spec['url']].ids if re.fullmatch(r'L\d+',identifier)}<=set(legacy.ids)
    assert {'contents','chapter-text'}<=set(legacy.ids)
    assert len(legacy.ids)==len(set(legacy.ids))
    if (root/'build-info.json').is_file():
        assert record['collection_revision']==json.loads((root/'build-info.json').read_bytes())['collection_revision']
    return dict(reading_pages=len(CHAPTERS),core_topic_pages=len(CORE_CHAPTERS),inline_figures=len(seen),collected_part_pages=1)
