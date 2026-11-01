"""Opening HTML plates of Paper VI's retained 42-plate visual atlas."""
import html
import json
import re
from html.parser import HTMLParser

from paper_vi_reading import BOOK
from paper_vi_atlas_descriptions import FIGURES
from reader_atlas import (atlas_tex, digest, drawing_nodes, expected_math,
                          render_drawing, transcript_order)
from readable_chapters import (Chapter, HEADINGS, MATH_PATTERN, PANELS, clean_tex,
                               group, manuscript_macros, original_math,
                               passage_links, plain_math, presentation_tex,
                               reading_options, render_table)
from reader_documents import png_dimensions
from render_paper_vi_atlas import PDF, PDF_SHA256

SOURCE = BOOK['base']+'atlas-pages.tex'
DEFINITIONS = BOOK['base']+'atlas-definitions.tex'
INDEX = 'read/paper-vi/atlas/index.html'
REPORT = 'documents/paper-vi-atlas.json'
RECEIPTS = 'assets/atlas/paper-vi/figures.json'
HTML_COUNT = 6
REFERENCES = {
    1: [('Section',str(n)) for n in (1,2,3,8,13)],
    2: [('Section',str(n)) for n in (2,4,6,7,12)],
    3: [('Theorem','1.2'),('Theorem','4.1')],
    4: [('Theorem','2.1'),('Corollary','2.2')],
    5: [('Theorem','5.1')],
    6: [('Theorem','3.1'),('Theorem','3.3'),('Theorem','5.2')],
}
TABLE_AIDS = {
    (1,'L14'): dict(caption='Questions and worked routes through the atlas',
                   headers=['Question','Worked route','Pages'],row_header_column=0),
    (2,'L26'): dict(caption='Conventions for transfer operators',
                   headers=['Object','Exact meaning','What to check'],row_header_column=0),
}


def plate_url(number):
    return 'read/paper-vi/atlas/v'+str(number).zfill(2)+'.html'


def plates(source):
    starts = list(re.finditer(r'\\vpage\{',source))
    if not starts or presentation_tex(clean_tex(source[:starts[0].start()])).strip():
        raise ValueError('Unexpected Paper VI atlas preamble')
    result = []
    for i, match in enumerate(starts):
        end = match.end()-1
        values = []
        for _ in range(4):
            value,end = group(source,end)
            values.append(value)
        number,title,category,locator = values
        if number != str(i+1) or original_math(source[match.start():end]):
            raise ValueError('Review Paper VI atlas numbering or metadata')
        stop = starts[i+1].start() if i+1<len(starts) else len(source)
        result.append(dict(number=i+1,title=title,category=category,locator=locator,
                           line=source.count('\n',0,match.start())+1,
                           end_line=source.count('\n',0,stop),
                           body='\n'*source.count('\n',0,end)+source[end:stop],
                           url=plate_url(i+1) if i<HTML_COUNT else INDEX+'#v'+str(i+1).zfill(2)))
    if len(result) != 42:
        raise ValueError('Review the changed Paper VI atlas inventory')
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
        raise ValueError('Paper VI atlas PDF differs from the frozen guide')
    main = reader.readable_books['paper-vi']['main']
    macros = manuscript_macros(main+'\n'+definitions.decode('utf-8-sig'),BOOK['required_macros'])
    selected = plates(raw.decode('utf-8-sig'))
    receipts = json.loads((reader.site.root/'website'/RECEIPTS).read_bytes())
    if receipts['source_pdf'] != PDF or receipts['source_pdf_sha256'] != PDF_SHA256:
        raise ValueError('Unexpected Paper VI drawing PDF binding')
    figures = {}
    for record in receipts['figures']:
        name = record['name']
        if name not in FIGURES or record['source'] != BOOK['base']+'visual_graphics/'+name+'.tex':
            raise ValueError('Unexpected Paper VI drawing source')
        reader.add(record['source'])
        source = reader.site.read_source(reader.records[record['source']])
        image = (reader.site.root/'website'/record['image']).read_bytes()
        if digest(source) != record['source_sha256'] or digest(image) != record['image_sha256']:
            raise ValueError('Review changed Paper VI drawing '+name)
        nodes = drawing_nodes(source.decode('utf-8-sig'))
        width,height = png_dimensions(image)
        figures[name] = dict(receipt=record,nodes=nodes,description=FIGURES[name],
                             order=transcript_order(FIGURES[name],nodes),width=width,height=height)
    used = [name for p in selected[:HTML_COUNT] for name in re.findall(r'\\vfig\{([^{}]+)\}',p['body'])]
    if sorted(used) != sorted(FIGURES) or set(figures) != set(FIGURES):
        raise ValueError('Paper VI opening-plate drawing coverage changed')
    references = {}
    for _,_,chapter in reader.readable_books['paper-vi']['chapters']:
        for node in chapter.nodes:
            if node['number']:
                references[(node['kind'].capitalize(),node['number'])] = (chapter,node)
    resolved = {}
    for plate in selected[:HTML_COUNT]:
        resolved[plate['number']] = []
        for key in REFERENCES[plate['number']]:
            if key not in references:
                raise ValueError('Paper VI atlas manuscript reference no longer resolves: '+str(key))
            chapter,node = references[key]
            target = chapter.url+'#'+node['id']
            resolved[plate['number']].append((' '.join(key),target))
            chapter.related_readings.setdefault(node['id'],[]).append(
                ('Atlas V'+str(plate['number'])+': '+plate['title'],plate['url']))
    reader.paper_vi_atlas = dict(plates=selected,figures=figures,macros=macros,
                                 references=resolved,source_sha256=digest(raw),
                                 definitions_sha256=digest(definitions))


def neighbours(reader, plate):
    number,page = plate['number'],plate['url']
    selected = reader.paper_vi_atlas['plates']
    routes = []
    if number>1:
        previous = selected[number-2]
        routes.append(('Previous: V'+str(number-1)+' · '+previous['title'],previous['url']))
    routes.append(('All 42 atlas plates',INDEX))
    if number<42:
        following = selected[number]
        label = ('Next: ' if number<HTML_COUNT else 'Continue in the PDF: ')+'V'+str(number+1)+' · '+following['title']
        routes.append((label,following['url']))
    return '<nav class="chapter-neighbours" aria-label="Neighbouring atlas plates">'+''.join(
        '<a href="'+reader.site.rel(target,page)+'">'+html.escape(label)+'</a>'
        for label,target in routes)+'</nav>'


def render(reader):
    site,atlas = reader.site,reader.paper_vi_atlas
    e = html.escape
    pdf = reader.records[PDF]
    reports = []
    aided = set()
    for plate in atlas['plates'][:HTML_COUNT]:
        number,page = plate['number'],plate['url']
        title = 'Paper VI atlas / V'+str(number)+': '+plate['title']
        chapter = AtlasChapter(atlas_tex(plate['body']),atlas['macros'])
        chapter.url = page
        chapter.command_links = {'pagerefV':{str(p['number']):(p['url'],'V'+str(p['number'])) for p in atlas['plates']}}
        body = '<p class="eyebrow">Paper VI visual atlas · V'+str(number)+' · '+e(plate['category'])+'</p><h1>'+e(plate['title'])+'</h1>'
        body += '<p>'+e(plate['locator'])+'</p>'+reader.work_routes('paper-vi',page)+neighbours(reader,plate)
        body += '<p><a href="'+reader.viewer_url(pdf,page,'page='+str(number+2))+'">Original plate in the visual guide PDF</a> · <a href="'+reader.resolve(SOURCE,page,'L'+str(plate['line']))+'">Original atlas source</a></p>'
        body += '<p>V1–V6 are available in HTML. The complete 42-plate atlas remains in the PDF. Evidence notes retain the source edition’s scope.</p>'
        body += '<nav class="document-routes" aria-label="Manuscript passages illustrated on this plate">'+''.join(
            '<a href="'+site.rel(target,page)+'">'+e(label)+'</a>' for label,target in atlas['references'][number])+'</nav>'
        body += reading_options('Show each passage’s permalink and source line. Manuscript links and plate navigation remain visible.')
        body += '<nav class="chapter-contents" aria-label="Plate contents"><h2 id="contents">On this plate</h2><ul>'
        for node in chapter.nodes:
            if node['kind'] in HEADINGS or node['kind']=='figure':
                body += '<li><a href="#'+node['id']+'">'+e(node['title'] if node['kind'] in HEADINGS else 'Drawing and text description')+'</a></li>'
        body += '</ul></nav><article id="chapter-text" class="readable-chapter atlas-plate" aria-label="'+e(title,quote=True)+'">'
        for node in chapter.nodes:
            kind,identifier = node['kind'],node['id']
            links = '<a href="#'+identifier+'">Permalink</a> · <a href="'+reader.resolve(SOURCE,page,'L'+str(node['line']))+'">Source line '+str(node['line'])+'</a>'
            if kind in HEADINGS:
                body += '<h2 id="'+identifier+'">'+chapter.inline(node['title'])+'</h2>'+passage_links(links)
            elif kind=='figure':
                body += '<div id="'+identifier+'">'+render_drawing(atlas['figures'][node['body']],chapter,reader)+'</div>'
            elif kind in {'table','tabularx'}:
                key = (number,identifier)
                if key not in TABLE_AIDS:
                    raise ValueError('Review the Paper VI atlas table '+str(key))
                aided.add(key)
                body += '<section id="'+identifier+'">'+render_table(node,chapter,TABLE_AIDS[key])+passage_links(links)+'</section>'
            elif kind=='text' or kind in PANELS:
                body += '<section id="'+identifier+'" class="reading-block '+kind+'">'
                if kind in PANELS:
                    body += '<h3>'+chapter.inline(node['title'] or PANELS[kind])+'</h3>'
                body += chapter.paragraphs(node['body'])+passage_links(links)+'</section>'
            else:
                raise ValueError('Unsupported Paper VI atlas block: '+kind)
        body += '</article>'+neighbours(reader,plate)
        body += '<details class="document-provenance"><summary>Source and conversion record</summary><p>The original atlas wording, equations and drawing labels are retained. Drawings are views of the frozen visual-guide PDF. Text descriptions and table headings are added reading aids. This conversion does not rebuild TeX, rerun the examples, audit proofs or compile Lean.</p><p><a href="'+site.rel(REPORT,page)+'">Conversion checks and source hashes</a></p></details>'
        expected = expected_math(plate,atlas['figures'])
        if chapter.math != expected:
            raise ValueError('Paper VI atlas mathematics differ on V'+str(number))
        site.page(page,title,body)
        site.search.append(dict(title=title,group='Collection',kind='Papers and source',work_ids=['paper-vi'],
                                url=page,text=plain_math(plate['body'])[0]+' '+plate['title']))
        reports.append(dict(number=number,url=page,start_line=plate['line'],end_line=plate['end_line'],
                            math_expressions=len(expected),math_sequence_sha256=digest(json.dumps(expected,ensure_ascii=False).encode()),
                            nodes=[{k:n[k] for k in ('kind','id','line','end_line')} for n in chapter.nodes]))
    if aided != set(TABLE_AIDS):
        raise ValueError('Paper VI atlas table coverage differs')
    report = dict(source=SOURCE,source_sha256=atlas['source_sha256'],definitions=DEFINITIONS,
                  definitions_sha256=atlas['definitions_sha256'],macro_source=BOOK['main'],macros=atlas['macros'],
                  source_pdf=PDF,source_pdf_sha256=PDF_SHA256,index=INDEX,total_plates=42,html_plates=reports,
                  figures={name:dict(**f['receipt'],nodes=f['nodes'],node_order=f['order']) for name,f in atlas['figures'].items()},
                  manuscript_references=atlas['references'],new_proof_review=False,new_lean_execution=False,
                  new_mathematical_example_execution=False,new_tex_build=False)
    site.write(REPORT,json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    body = '<p class="eyebrow">Paper VI · Visual atlas</p><h1>Explore the 42 atlas plates</h1>'
    body += '<p>The first six plates have HTML reading pages with drawings, selectable equations, descriptions and tables. All 42 plates can be opened at their exact pages in the complete visual guide.</p>'+reader.work_routes('paper-vi',INDEX)
    body += '<nav class="chapter-contents" aria-label="Atlas plates"><h2>Choose a plate</h2><ol>'
    for plate in atlas['plates']:
        number = plate['number']
        body += '<li id="v'+str(number).zfill(2)+'"><strong>V'+str(number)+': '+e(plate['title'])+'</strong><p>'
        if number<=HTML_COUNT:
            body += '<a href="'+site.rel(plate['url'],INDEX)+'">Read V'+str(number)+' in HTML</a> · '
        body += '<a href="'+reader.viewer_url(pdf,INDEX,'page='+str(number+2))+'">Open V'+str(number)+' in the PDF</a></p></li>'
    body += '</ol></nav><p><a href="'+reader.resolve(SOURCE,INDEX)+'">Complete selectable atlas source</a> · <a href="'+site.rel(REPORT,INDEX)+'">Conversion records</a></p>'
    site.page(INDEX,'Paper VI visual atlas',body)
    site.search.append(dict(title='Paper VI / Visual atlas',group='Collection',kind='Papers and source',work_ids=['paper-vi'],
                            url=INDEX,text=' '.join(p['title'] for p in atlas['plates'])))


def verify(root, documents, pages):
    from check_reader_site import check_png_image_sizes
    report = json.loads((root/REPORT).read_bytes())
    records = {r['repository_path']:r for r in documents['files']}
    read = lambda path:(root/records[path]['file_url']).read_bytes()
    source,definitions = read(SOURCE),read(DEFINITIONS)
    assert digest(source)==report['source_sha256'] and digest(definitions)==report['definitions_sha256']
    assert report['source_pdf']==PDF and digest(read(PDF))==report['source_pdf_sha256']==PDF_SHA256
    macros = manuscript_macros(read(BOOK['main']).decode('utf-8-sig')+'\n'+definitions.decode('utf-8-sig'),BOOK['required_macros'])
    assert report['macros']==macros
    assert not any(report[k] for k in ('new_proof_review','new_lean_execution','new_mathematical_example_execution','new_tex_build'))
    selected = plates(source.decode('utf-8-sig'))
    assert report['total_plates']==len(selected)==42 and len(report['html_plates'])==HTML_COUNT
    figures = {}
    for name,record in report['figures'].items():
        nodes = drawing_nodes(read(record['source']).decode('utf-8-sig'))
        assert digest(read(record['source']))==record['source_sha256']
        assert digest((root/record['image']).read_bytes())==record['image_sha256']
        assert record['nodes']==nodes and record['node_order']==transcript_order(FIGURES[name],nodes)
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
        expected=expected_math(plate,figures)
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
    assert all('v'+str(n).zfill(2) in pages[INDEX].ids for n in range(1,43))
    return dict(total_plates=42,html_plates=HTML_COUNT,drawings=len(figures),
                transcribed_labels=sum(len(f['nodes']) for f in figures.values()),math_expressions=count)
