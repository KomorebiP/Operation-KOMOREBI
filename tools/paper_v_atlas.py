"""Source-bound HTML edition of Paper V's complete 40-plate visual atlas."""
import html
import json
import posixpath
import re
from html.parser import HTMLParser

from paper_v_chapters import BOOK
from paper_v_atlas_descriptions import FIGURES
from reader_atlas import (atlas_tex as original_atlas_tex, digest, expected_math,
                          render_drawing as original_render_drawing, transcript_order)
from paper_v_atlas_drawings import drawing_nodes
from reader_drawing_transcripts import matrix_label_blocks
from readable_chapters import (Chapter, HEADINGS, MATH_PATTERN, PANELS, clean_tex,
                               group, manuscript_macros, original_math,
                               passage_links, plain_math, presentation_tex,
                               reading_options, render_table)
from reading_navigation import atlas_config, navigation, outline, resources, visual_title, visual_backlink, visual_position, visual_contents, visual_search_terms, visual_search_preview
from reader_documents import png_dimensions
from render_paper_v_atlas import CROPS, PDF, PDF_SHA256


def drawing_source(name):
    return BOOK['base']+'visual_graphics/'+name+('.pdf' if name=='annals_gibbs_comparison' else '.tex')

SOURCE = BOOK['base']+'atlas-pages.tex'
DEFINITIONS = BOOK['base']+'atlas-definitions.tex'
INDEX = 'read/paper-v/atlas/index.html'
REPORT = 'documents/paper-v-atlas.json'
RECEIPTS = 'assets/atlas/paper-v/figures.json'
HTML_COUNT = 40
TABLE_AIDS = {
    (2,'L19'): dict(caption='Objects and conventions in the atlas',
        headers=['Object','Literal meaning','What it is not'],row_header_column=0),
    (11,'L183'): dict(caption='Discarded energy by coefficient budget',
        headers=[r'kept coefficients $k$','1','2','4','8','12','16'],row_header_column=0),
    (17,'L297'): dict(caption='Exact error norms for the translated interval',
        headers=['error measure',r'$L^1$ norm',r'squared $L^2$ norm',r'$L^\infty$ norm'],row_header_column=0),
    (22,'L409'): dict(caption='Four reflection coefficients and exact impedances',
        headers=[r'$\Gamma$',r'$1/2$',r'$i/2$',r'$-1/2$',r'$-i/2$'],row_header_column=0),
    (26,'L487'): dict(caption='Evidence layers and their limits',
        headers=['Structure','What is established in the original worked layer'],row_header_column=0),
    (27,'L509'): dict(caption='Representations and conditional recovery',
        headers=['Transition','Additional input','Resulting control'],row_header_column=0),
}
REFERENCE_PATTERN = re.compile(r'(Section|Definition|Theorem|Proposition|Corollary|Remark|Lemma|Example|Locator) ([A-Z]?\d+(?:\.\d+)?|D)')


def reference_keys(plate):
    keys = REFERENCE_PATTERN.findall(plate['locator'])
    # The print concordance uses Locator 5 for the notation appendix (C),
    # and Locator D for the formalization/reproducibility appendix.
    keys=[('Section',{'5':'C','D':'D'}[number]) if kind=='Locator' else (kind,number)
          for kind,number in keys]
    if not keys:
        raise ValueError('Paper V plate has no manuscript references')
    return keys



def reading_aids(name,nodes,source):
    info=FIGURES[name]
    return info if info['blocks'] else dict(**{k:v for k,v in info.items() if k!='blocks'},
                                           blocks=matrix_label_blocks(nodes,source))


def drawing_tex(text):
    text=re.sub(r'\\vfig\[[^\]]+\]', lambda m:r'\vfig', text)
    text=text.replace(r'\begin{center}\includegraphics[width=.78\linewidth]{visual_graphics/annals_gibbs_comparison.pdf}\end{center}',r'\vfig{annals_gibbs_comparison}')
    return text


def atlas_tex(text):
    text=drawing_tex(text)
    text=re.sub(r'\\endgroup\b|\\vspace\{[\d.]+pt\}',lambda m:' '*len(m[0]),text)
    return original_atlas_tex(text)


def atlas_macros(main,definitions):
    macros=manuscript_macros(main+'\n'+definitions,BOOK['required_macros'])
    for match in re.finditer(r'\\providecommand\{\\(mat|diagmat)\}\[1\]\{',definitions):
        if match[1] not in macros:
            macros[match[1]]=dict(arguments=1,body=group(definitions,match.end()-1)[0])
    return macros


def render_drawing(figure,chapter,reader):
    body=original_render_drawing(figure,chapter,reader)
    if not figure['nodes']:
        body=body.replace('A text description and its labels follow.','A text description follows.')
    image=html.escape(reader.site.rel(figure['receipt']['image'],chapter.url),quote=True)
    label=html.escape('Open full-size drawing: '+figure['description']['alt'],quote=True)
    return re.sub(r'<img\b[^>]*>',lambda m:'<a href="'+image+'" aria-label="'+label+'">'+m[0]+'</a>',body,count=1)


def plate_url(number):
    return 'read/paper-v/atlas/v'+str(number).zfill(2)+'.html'


def plates(source):
    starts = list(re.finditer(r'\\vpage\{',source))
    if not starts or presentation_tex(clean_tex(source[:starts[0].start()])).strip():
        raise ValueError('Unexpected Paper V atlas preamble')
    result = []
    for i, match in enumerate(starts):
        end = match.end()-1
        values = []
        for _ in range(4):
            value,end = group(source,end)
            values.append(value)
        number,title,category,locator = values
        if number != str(i+1) or original_math(source[match.start():end]):
            raise ValueError('Review Paper V atlas numbering or metadata')
        stop = starts[i+1].start() if i+1<len(starts) else len(source)
        result.append(dict(number=i+1,title=title,category=category,locator=locator,
                           line=source.count('\n',0,match.start())+1,
                           end_line=source.count('\n',0,stop),
                           body='\n'*source.count('\n',0,end)+source[end:stop],
                           url=plate_url(i+1) if i<HTML_COUNT else INDEX+'#v'+str(i+1).zfill(2)))
    if len(result) != 40:
        raise ValueError('Review the changed Paper V atlas inventory')
    return result


class AtlasChapter(Chapter):
    def inline(self, text):
        # TikZ label line breaks are prose presentation. Keep matrix row
        # separators and every other token inside mathematical expressions.
        parts = []
        pos = 0
        for match in MATH_PATTERN.finditer(text):
            parts.extend([text[pos:match.start()].replace(r'\\',r'\newline '),match[0]])
            pos = match.end()
        parts.append(text[pos:].replace(r'\\',r'\newline '))
        return super().inline(''.join(parts))


def prepare(reader):
    for path in (SOURCE,DEFINITIONS,PDF):
        reader.add(path)
    raw = reader.site.read_source(reader.records[SOURCE])
    definitions = reader.site.read_source(reader.records[DEFINITIONS])
    if digest(reader.site.read_source(reader.records[PDF])) != PDF_SHA256:
        raise ValueError('Paper V atlas PDF differs from the frozen guide')
    main = reader.readable_books['paper-v']['main']
    macros = atlas_macros(main,definitions.decode('utf-8-sig'))
    selected = plates(raw.decode('utf-8-sig'))
    receipts = json.loads((reader.site.root/'website'/RECEIPTS).read_bytes())
    if receipts['source_pdf'] != PDF or receipts['source_pdf_sha256'] != PDF_SHA256:
        raise ValueError('Unexpected Paper V drawing PDF binding')
    figures = {}
    if len(receipts['figures'])!=37:
        raise ValueError('Paper V needs all 37 atlas drawings')
    crops={name:(number,bounds) for name,number,bounds in CROPS}
    for record in receipts['figures']:
        name = record['name']
        if name not in FIGURES or record['source'] != drawing_source(name):
            raise ValueError('Unexpected Paper V drawing source')
        number,bounds=crops[name]
        if (record['image']!='assets/atlas/paper-v/'+name+'.png' or record['plate']!=number
                or record['pdf_page']!=number+3 or record['crop_pdf_points']!=bounds):
            raise ValueError('Paper V drawing crop or image path changed')
        reader.add(record['source'])
        source = reader.site.read_source(reader.records[record['source']])
        image = (reader.site.root/'website'/record['image']).read_bytes()
        if digest(source) != record['source_sha256'] or digest(image) != record['image_sha256']:
            raise ValueError('Review changed Paper V drawing '+name)
        nodes = [] if name=='annals_gibbs_comparison' else drawing_nodes(source.decode('utf-8-sig'))
        width,height = png_dimensions(image)
        info=reading_aids(name,nodes,'' if name=='annals_gibbs_comparison' else source.decode('utf-8-sig'))
        figures[name] = dict(receipt=record,nodes=nodes,description=info,
                             order=transcript_order(info,nodes),width=width,height=height)
    used = [name for p in selected[:HTML_COUNT] for name in re.findall(r'\\vfig\{([^{}]+)\}',drawing_tex(p['body']))]
    if sorted(used) != sorted(FIGURES) or set(figures) != set(FIGURES):
        raise ValueError('Paper V atlas drawing coverage changed')
    references = {}
    for _,_,chapter in reader.readable_books['paper-v']['chapters']:
        for node in chapter.nodes:
            if node['number']:
                references[(node['kind'].capitalize(),node['number'])] = (chapter,node)
    resolved = {}
    for plate in selected[:HTML_COUNT]:
        resolved[plate['number']] = []
        for key in reference_keys(plate):
            if key not in references:
                raise ValueError('Paper V atlas manuscript reference no longer resolves: '+str(key))
            chapter,node = references[key]
            target = chapter.url+'#'+node['id']
            resolved[plate['number']].append((' '.join(key),target))
            chapter.related_readings.setdefault(node['id'],[]).append(
                (visual_backlink(plate),plate['url']))
    reader.paper_v_atlas = dict(plates=selected,figures=figures,macros=macros,
                                 references=resolved,source_sha256=digest(raw),
                                 definitions_sha256=digest(definitions))


def neighbours(reader, plate, placement='top'):
    config = atlas_config('paper-v', 'Paper V', INDEX, reader.paper_v_atlas['plates'])
    return navigation(config, plate['url'], placement)


def render(reader):
    site,atlas = reader.site,reader.paper_v_atlas
    e = html.escape
    pdf = reader.records[PDF]
    reports = []
    aided = set()
    for plate in atlas['plates'][:HTML_COUNT]:
        number,page = plate['number'],plate['url']
        title = visual_title('Paper V',plate)
        chapter = AtlasChapter(atlas_tex(plate['body']),atlas['macros'])
        chapter.url = page
        chapter.command_links = {'pagerefV':{str(p['number']):(p['url'],'Visual '+str(p['number'])) for p in atlas['plates']}}
        body = '<p class="eyebrow">'+visual_position('Paper V',plate['number'],HTML_COUNT)+ ' · '+e(plate['category'])+'</p><h1>'+e(plate['title'])+'</h1>'
        body += '<p>'+e(plate['locator'])+'</p>'+reader.work_routes('paper-v',page)+neighbours(reader,plate)
        body += '<nav class="document-routes" aria-label="Manuscript passages illustrated here">'+''.join(
            '<a href="'+site.rel(target,page)+'">'+e(label)+'</a>' for label,target in atlas['references'][number])+'</nav>'
        if number in (26,27,40):
            body += '<p><a href="'+site.rel('collection/works/paper-v.html#evidence',page)+'">Recorded evidence for Paper V</a></p>'
        tools = '<p><a href="'+reader.viewer_url(pdf,page,'page='+str(number+3))+'">Original plate in the visual guide PDF</a> · <a href="'+reader.resolve(SOURCE,page,'L'+str(plate['line']))+'">Original atlas source</a></p>'
        tools += reading_options('Show each passage’s permalink and source line. Manuscript links and plate navigation remain visible.')
        body += resources(tools)+'<p class="reading-start"><a href="#chapter-text">Start reading</a></p>'
        toc = '<nav class="chapter-contents" aria-label="Visual contents"><h2 id="contents">On this visual</h2><ul>'
        for node in chapter.nodes:
            if node['kind'] in HEADINGS or node['kind']=='figure':
                toc += '<li><a href="#'+node['id']+'">'+e(node['title'] if node['kind'] in HEADINGS else 'Drawing and text description')+'</a></li>'
        body += outline(toc+'</ul></nav>')+'<article id="chapter-text" class="readable-chapter atlas-plate" aria-label="'+e(title,quote=True)+'">'
        for node in chapter.nodes:
            kind,identifier = node['kind'],node['id']
            links = '<a href="#'+identifier+'">Permalink</a> · <a href="'+reader.resolve(SOURCE,page,'L'+str(node['line']))+'">Source line '+str(node['line'])+'</a>'
            if kind in HEADINGS:
                body += '<h2 id="'+identifier+'">'+chapter.inline(node['title'])+'</h2>'+passage_links(links)
            elif kind=='figure':
                body += '<div id="'+identifier+'">'+render_drawing(atlas['figures'][node['body']],chapter,reader)+'</div>'
            elif kind in {'table','tabularx','tabular'}:
                key = (number,identifier)
                if key not in TABLE_AIDS:
                    raise ValueError('Review the Paper V atlas table '+str(key))
                aided.add(key)
                body += '<section id="'+identifier+'">'+render_table(node,chapter,TABLE_AIDS[key])+passage_links(links)+'</section>'
            elif kind=='text' or kind in PANELS:
                body += '<section id="'+identifier+'" class="reading-block '+kind+'">'
                if kind in PANELS:
                    body += '<h3>'+chapter.inline(node['title'] or PANELS[kind])+'</h3>'
                body += chapter.paragraphs(node['body'])+passage_links(links)+'</section>'
            else:
                raise ValueError('Unsupported Paper V atlas block: '+kind)
        body += '</article>'+neighbours(reader,plate,'bottom')
        body += '<details class="document-provenance"><summary>Source and conversion record</summary><p>The original atlas wording, equations, and drawing labels are retained. Drawings are views of the frozen visual-guide PDF. Text descriptions and table headings are added reading aids. This conversion does not rebuild TeX, rerun the examples, audit proofs or compile Lean.</p><p><a href="'+site.rel(REPORT,page)+'">Conversion checks and source hashes</a></p></details>'
        expected = expected_math(dict(plate,body=drawing_tex(plate['body'])),atlas['figures'])
        if chapter.math != expected:
            raise ValueError('Paper V atlas mathematics differ on V'+str(number))
        site.page(page,title,body)
        site.search.append(dict(title=title,group='Collection',kind='Papers and source',visual_guide=True,work_ids=['paper-v'],
                                url=page,text=visual_search_terms(plate)+' '+plain_math(plate['body'])[0]+' '+plate['title'],**visual_search_preview(chapter,atlas['figures'])))
        reports.append(dict(number=number,url=page,start_line=plate['line'],end_line=plate['end_line'],
                            math_expressions=len(expected),math_sequence_sha256=digest(json.dumps(expected,ensure_ascii=False).encode()),
                            nodes=[{k:n[k] for k in ('kind','id','line','end_line')} for n in chapter.nodes]))
    if aided != set(TABLE_AIDS):
        raise ValueError('Paper V atlas table coverage differs')
    report = dict(collection_revision=site.revision,source=SOURCE,source_sha256=atlas['source_sha256'],definitions=DEFINITIONS,
                  definitions_sha256=atlas['definitions_sha256'],macro_source=BOOK['main'],macros=atlas['macros'],
                  source_pdf=PDF,source_pdf_sha256=PDF_SHA256,index=INDEX,total_plates=40,html_plates=reports,
                  figures={name:dict(**f['receipt'],nodes=f['nodes'],node_order=f['order'],reading_aid=f['description']) for name,f in atlas['figures'].items()},
                  manuscript_references=atlas['references'],new_proof_review=False,new_lean_execution=False,
                  new_mathematical_example_execution=False,new_tex_build=False)
    site.write(REPORT,json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    body = '<p class="eyebrow">Paper V · Visual guide</p><h1>Explore the 40 visuals</h1>'
    body += '<p>Read all 40 visuals with 37 original drawings, selectable equations, descriptions, and transcripts of the TikZ labels. Each worked example links to the manuscript passages it illustrates; evidence notes retain their source edition’s scope.</p>'+reader.work_routes('paper-v',INDEX)
    body += visual_contents(atlas['plates'],INDEX,site.rel,lambda p:reader.viewer_url(pdf,INDEX,'page='+str(p['number']+3)))
    body += '<p><a href="'+reader.resolve(SOURCE,INDEX)+'">Complete selectable atlas source</a> · <a href="'+site.rel(REPORT,INDEX)+'">Conversion records</a></p>'
    site.page(INDEX,'Paper V visual guide',body)
    site.search.append(dict(title='Paper V / Visual guide',group='Collection',kind='Papers and source',visual_guide=True,work_ids=['paper-v'],
                            url=INDEX,text=' '.join(p['title'] for p in atlas['plates'])))


def verify(root, documents, pages):
    from check_reader_site import check_png_image_sizes
    report = json.loads((root/REPORT).read_bytes())
    records = {r['repository_path']:r for r in documents['files']}
    read = lambda path:(root/records[path]['file_url']).read_bytes()
    source,definitions = read(SOURCE),read(DEFINITIONS)
    assert digest(source)==report['source_sha256'] and digest(definitions)==report['definitions_sha256']
    assert report['source_pdf']==PDF and digest(read(PDF))==report['source_pdf_sha256']==PDF_SHA256
    macros = atlas_macros(read(BOOK['main']).decode('utf-8-sig'),definitions.decode('utf-8-sig'))
    assert report['macros']==macros
    assert report['collection_revision']==documents['source_revision']
    assert not any(report[k] for k in ('new_proof_review','new_lean_execution','new_mathematical_example_execution','new_tex_build'))
    selected = plates(source.decode('utf-8-sig'))
    assert report['total_plates']==len(selected)==40 and len(report['html_plates'])==HTML_COUNT
    figures = {}
    for name,record in report['figures'].items():
        nodes = [] if name=='annals_gibbs_comparison' else drawing_nodes(read(record['source']).decode('utf-8-sig'))
        assert digest(read(record['source']))==record['source_sha256']
        assert digest((root/record['image']).read_bytes())==record['image_sha256']
        info=reading_aids(name,nodes,('' if name=='annals_gibbs_comparison' else read(record['source']).decode('utf-8-sig')))
        assert record['reading_aid']==info
        assert record['nodes']==nodes and record['node_order']==transcript_order(info,nodes)
        figures[name]=dict(nodes=nodes,order=record['node_order'])
    assert set(figures)==set(FIGURES)
    class MathText(HTMLParser):
        def __init__(self):
            super().__init__();self.depth=0;self.expressions=[]
        def handle_starttag(self,tag,attrs):
            if self.depth: self.depth+=1
            elif 'arithmatex' in dict(attrs).get('class','').split():
                self.depth=1;self.expressions.append('')
        def handle_endtag(self,tag):
            if self.depth:self.depth-=1
        def handle_data(self,data):
            if self.depth:self.expressions[-1]+=data
    count=0
    for plate,binding in zip(selected,report['html_plates']):
        expected=expected_math(dict(plate,body=drawing_tex(plate['body'])),figures)
        assert (binding['number'],binding['url'],binding['start_line'],binding['end_line'])==(plate['number'],plate['url'],plate['line'],plate['end_line'])
        assert binding['math_expressions']==len(expected)
        assert binding['math_sequence_sha256']==digest(json.dumps(expected,ensure_ascii=False).encode())
        rendered=MathText();rendered.feed((root/plate['url']).read_text(encoding='utf-8'))
        from readable_chapters import expand_math
        assert [x[2:-2] for x in rendered.expressions]==[expand_math(x,macros) for x in expected]
        check_png_image_sizes(root,plate['url'],pages[plate['url']].images)
        for node in binding['nodes']:
            assert node['id'] in pages[plate['url']].ids
            assert 'L'+str(node['line']) in pages[records[SOURCE]['url']].ids
        count+=len(expected)
    assert all('v'+str(n).zfill(2) in pages[INDEX].ids for n in range(1,HTML_COUNT+1))
    returns=0
    for plate in selected:
        targets=report['manuscript_references'][str(plate['number'])]
        assert len(targets)==len(reference_keys(plate))
        for label,target in targets:
            chapter,anchor=target.split('#')
            assert anchor in pages[chapter].ids
            assert posixpath.relpath(target,posixpath.dirname(plate['url'])) in pages[plate['url']].links
            assert posixpath.relpath(plate['url'],posixpath.dirname(chapter)) in pages[chapter].links
            returns+=1
    return dict(total_plates=40,html_plates=HTML_COUNT,drawings=len(figures),
                transcribed_labels=sum(len(f['nodes']) for f in figures.values()),math_expressions=count,return_links=returns)
