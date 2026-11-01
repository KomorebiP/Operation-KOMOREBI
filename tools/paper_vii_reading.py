"""Explicit source selection and original-PDF figures for Paper VII."""
import html
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
for i,(name,slug,title,part) in enumerate(PARTS):
    CHAPTERS.append(dict(source=BASE+'parts/'+name, url='read/paper-vii/'+slug+'.html', title=title,
                         work='paper-vii', part=part, reset_part=i in (0,1,2),
                         figure_base=BASE+('assets/core/' if i==0 else 'assets/strengthened/')))
BOOK = dict(work='paper-vii', label='Paper VII', base=BASE, main=MAIN, bib=BASE+'references.bib',
            index='read/paper-vii/index.html', bib_page='read/paper-vii/references.html',
            title='Quantum Seeds and Effective Dynamics', chapters=CHAPTERS, main_chapters=9,
            part_numbering=True, figure_pdfs=True,
            main_inputs=['monograph_examples.tex']+['parts/'+p[0] for p in PARTS]+['monograph_atlas.tex'],
            pdf_inputs={'monograph_atlas.tex':'Read the worked visual atlas in the original PDF'})


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


def prepare_figures(reader, spec, chapter):
    for node in chapter.nodes:
        if node['kind']=='figure':
            for name,caption in figure_items(node['body']):
                record=reader.add(figure_path(spec,name),'Paper VII figure: '+posixpath.basename(name))
                if not record:
                    raise ValueError('Missing receipt-bound Paper VII figure '+name)
                record['figure']=True


def render_figure(reader, spec, chapter, node, links):
    from readable_chapters import passage_links
    result='<figure id="'+node['id']+'" class="original-pdf-figure">'
    for name,caption in figure_items(node['body']):
        record=reader.records[figure_path(spec,name)]
        viewer=html.escape(reader.viewer_url(record,spec['url']),quote=True)
        title='Paper VII figure: '+posixpath.basename(name)
        result+='<figcaption>'+chapter.inline(caption)+'</figcaption>'
        result+='<p><a href="'+viewer+'">Open original figure (PDF)</a></p>'
        result+='<details><summary>View figure here</summary><iframe class="pdf-reader" loading="lazy" title="'+html.escape(title,quote=True)+'" src="'+viewer+'"></iframe></details>'
    return result+passage_links(links)+'</figure>'
