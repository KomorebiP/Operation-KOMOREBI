"""Source-bound HTML edition of Paper VI's complete 42-plate visual atlas."""
import html
import json
import posixpath
import re
from html.parser import HTMLParser

from paper_vi_reading import BOOK
from paper_vi_atlas_descriptions import FIGURES
from reader_atlas import (atlas_tex as original_atlas_tex, digest, expected_math,
                          render_drawing as original_render_drawing, transcript_order)
from reader_drawing_transcripts import drawing_nodes,matrix_label_blocks
from readable_chapters import (Chapter, HEADINGS, MATH_PATTERN, PANELS, clean_tex,
                               group, manuscript_macros, original_math,
                               passage_links, plain_math, presentation_tex,
                               reading_options, render_table)
from reading_navigation import atlas_config, navigation, outline, resources
from reader_documents import png_dimensions
from render_paper_vi_atlas import CROPS, PDF, PDF_SHA256

SOURCE = BOOK['base']+'atlas-pages.tex'
DEFINITIONS = BOOK['base']+'atlas-definitions.tex'
INDEX = 'read/paper-vi/atlas/index.html'
REPORT = 'documents/paper-vi-atlas.json'
RECEIPTS = 'assets/atlas/paper-vi/figures.json'
HTML_COUNT = 42
REFERENCES = {
    1: [('Section',str(n)) for n in (1,2,3,8,13)],
    2: [('Section',str(n)) for n in (2,4,6,7,12)],
    3: [('Theorem','1.2'),('Theorem','4.1')],
    4: [('Theorem','2.1'),('Corollary','2.2')],
    5: [('Theorem','5.1')],
    6: [('Theorem','3.1'),('Theorem','3.3'),('Theorem','5.2')],
    7: [('Theorem','6.1')],
    8: [('Theorem','6.2')],
    9: [('Theorem','7.1'),('Theorem','7.2'),('Theorem','7.3')],
    10: [('Theorem','8.2')],
    11: [('Theorem','8.1'),('Theorem','8.4'),('Corollary','8.6')],
    12: [('Theorem','7.1'),('Theorem','9.1')],
    13: [('Proposition','9.3')],
    14: [('Example','9.2')],
    15: [('Theorem','10.1')],
    16: [('Theorem','10.3'),('Corollary','10.4')],
    17: [('Theorem','10.2')],
    18: [('Theorem','11.1')],
    19: [('Theorem','11.1'),('Theorem','11.2')],
    20: [('Theorem','12.1')],
    21: [('Theorem','13.1')],
    22: [('Theorem','13.2')],
    23: [('Theorem','13.2'),('Section','15')],
    24: [('Theorem','14.1')],
    25: [('Theorem','15.1')],
    26: [('Proposition','9.3'),('Theorem','5.1'),('Theorem','8.2')],
    27: [('Corollary','10.5'),('Section','17')],
    28: [],
    29: [('Theorem','E2.8'),('Corollary','E2.9')],
    30: [('Theorem','E4.8'),('Example','E4.10')],
    31: [('Theorem','E4.5'),('Corollary','E4.7')],
    32: [('Theorem','E5.3'),('Corollary','E5.4')],
    33: [('Theorem','E7.1'),('Corollary','E7.2'),('Corollary','E7.4'),('Corollary','E7.5')],
    34: [('Theorem','E9.3')],
    35: [('Theorem','E9.8'),('Corollary','E9.9')],
    36: [('Theorem','E10.1'),('Theorem','E10.2')],
    37: [('Theorem','E15.1'),('Corollary','E15.2')],
    38: [('Theorem','E15.6')],
    39: [('Corollary','E15.4'),('Corollary','E15.5')],
    40: [('Proposition','E16.4'),('Theorem','E16.5')],
    41: [('Theorem','E3.4'),('Theorem','15.1')],
    42: [],
}
TABLE_AIDS = {
    (1,'L14'): dict(caption='Questions and worked routes through the atlas',
                   headers=['Question','Worked route','Pages'],row_header_column=0),
    (2,'L26'): dict(caption='Conventions for transfer operators',
                   headers=['Object','Exact meaning','What to check'],row_header_column=0),
    (28,'L648'): dict(caption='Evidence layers and their stated limits',
                     headers=['Evidence','What is checked here','What it does not establish'],row_header_column=0),
}


def reading_aids(name,nodes,source):
    info=FIGURES[name]
    return info if info['blocks'] else dict(**{k:v for k,v in info.items() if k!='blocks'},
                                           blocks=matrix_label_blocks(nodes,source))


def atlas_tex(text):
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
    image=html.escape(reader.site.rel(figure['receipt']['image'],chapter.url),quote=True)
    label=html.escape('Open full-size drawing: '+figure['description']['alt'],quote=True)
    return re.sub(r'<img\b[^>]*>',lambda m:'<a href="'+image+'" aria-label="'+label+'">'+m[0]+'</a>',body,count=1)


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
    macros = atlas_macros(main,definitions.decode('utf-8-sig'))
    selected = plates(raw.decode('utf-8-sig'))
    receipts = json.loads((reader.site.root/'website'/RECEIPTS).read_bytes())
    if receipts['source_pdf'] != PDF or receipts['source_pdf_sha256'] != PDF_SHA256:
        raise ValueError('Unexpected Paper VI drawing PDF binding')
    figures = {}
    if len(receipts['figures'])!=40:
        raise ValueError('Paper VI needs all 40 atlas drawings')
    crops={name:(number,bounds) for name,number,bounds in CROPS}
    for record in receipts['figures']:
        name = record['name']
        if name not in FIGURES or record['source'] != BOOK['base']+'visual_graphics/'+name+'.tex':
            raise ValueError('Unexpected Paper VI drawing source')
        number,bounds=crops[name]
        if (record['image']!='assets/atlas/paper-vi/'+name+'.png' or record['plate']!=number
                or record['pdf_page']!=number+2 or record['crop_pdf_points']!=bounds):
            raise ValueError('Paper VI drawing crop or image path changed')
        reader.add(record['source'])
        source = reader.site.read_source(reader.records[record['source']])
        image = (reader.site.root/'website'/record['image']).read_bytes()
        if digest(source) != record['source_sha256'] or digest(image) != record['image_sha256']:
            raise ValueError('Review changed Paper VI drawing '+name)
        nodes = drawing_nodes(source.decode('utf-8-sig'))
        width,height = png_dimensions(image)
        info=reading_aids(name,nodes,source.decode('utf-8-sig'))
        figures[name] = dict(receipt=record,nodes=nodes,description=info,
                             order=transcript_order(info,nodes),width=width,height=height)
    used = [name for p in selected[:HTML_COUNT] for name in re.findall(r'\\vfig\{([^{}]+)\}',p['body'])]
    if sorted(used) != sorted(FIGURES) or set(figures) != set(FIGURES):
        raise ValueError('Paper VI atlas drawing coverage changed')
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


def neighbours(reader, plate, placement='top'):
    config = atlas_config('paper-vi', 'Paper VI', INDEX, reader.paper_vi_atlas['plates'])
    return navigation(config, plate['url'], placement)


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
        body += '<nav class="document-routes" aria-label="Manuscript passages illustrated on this plate">'+''.join(
            '<a href="'+site.rel(target,page)+'">'+e(label)+'</a>' for label,target in atlas['references'][number])+'</nav>'
        if number in (28,42):
            body += '<p><a href="'+site.rel('collection/works/paper-vi.html#evidence',page)+'">Recorded evidence for Paper VI</a></p>'
        tools = '<p><a href="'+reader.viewer_url(pdf,page,'page='+str(number+2))+'">Original plate in the visual guide PDF</a> · <a href="'+reader.resolve(SOURCE,page,'L'+str(plate['line']))+'">Original atlas source</a></p>'
        tools += reading_options('Show each passage’s permalink and source line. Manuscript links and plate navigation remain visible.')
        body += resources(tools)+'<p class="reading-start"><a href="#chapter-text">Start reading</a></p>'
        toc = '<nav class="chapter-contents" aria-label="Plate contents"><h2 id="contents">On this plate</h2><ul>'
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
        body += '</article>'+neighbours(reader,plate,'bottom')
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
    report = dict(collection_revision=site.revision,source=SOURCE,source_sha256=atlas['source_sha256'],definitions=DEFINITIONS,
                  definitions_sha256=atlas['definitions_sha256'],macro_source=BOOK['main'],macros=atlas['macros'],
                  source_pdf=PDF,source_pdf_sha256=PDF_SHA256,index=INDEX,total_plates=42,html_plates=reports,
                  figures={name:dict(**f['receipt'],nodes=f['nodes'],node_order=f['order'],reading_aid=f['description']) for name,f in atlas['figures'].items()},
                  manuscript_references=atlas['references'],new_proof_review=False,new_lean_execution=False,
                  new_mathematical_example_execution=False,new_tex_build=False)
    site.write(REPORT,json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    body = '<p class="eyebrow">Paper VI · Visual atlas</p><h1>Explore the 42 atlas plates</h1>'
    body += '<p>Read all 42 worked plates with their original drawings, selectable equations, descriptions, and label transcripts. Each mathematical plate links to the manuscript passages it illustrates; the two evidence guides retain their source edition’s scope.</p>'+reader.work_routes('paper-vi',INDEX)
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
    macros = atlas_macros(read(BOOK['main']).decode('utf-8-sig'),definitions.decode('utf-8-sig'))
    assert report['macros']==macros
    assert report['collection_revision']==documents['source_revision']
    assert not any(report[k] for k in ('new_proof_review','new_lean_execution','new_mathematical_example_execution','new_tex_build'))
    selected = plates(source.decode('utf-8-sig'))
    assert report['total_plates']==len(selected)==42 and len(report['html_plates'])==HTML_COUNT
    figures = {}
    for name,record in report['figures'].items():
        nodes = drawing_nodes(read(record['source']).decode('utf-8-sig'))
        assert digest(read(record['source']))==record['source_sha256']
        assert digest((root/record['image']).read_bytes())==record['image_sha256']
        info=reading_aids(name,nodes,read(record['source']).decode('utf-8-sig'))
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
    returns=0
    for plate in selected:
        targets=report['manuscript_references'][str(plate['number'])]
        assert len(targets)==len(REFERENCES[plate['number']])
        for label,target in targets:
            chapter,anchor=target.split('#')
            assert anchor in pages[chapter].ids
            assert posixpath.relpath(target,posixpath.dirname(plate['url'])) in pages[plate['url']].links
            assert posixpath.relpath(plate['url'],posixpath.dirname(chapter)) in pages[chapter].links
            returns+=1
    return dict(total_plates=42,html_plates=HTML_COUNT,drawings=len(figures),
                transcribed_labels=sum(len(f['nodes']) for f in figures.values()),math_expressions=count,return_links=returns)
