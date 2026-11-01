"""Source-bound HTML edition of Paper VII's retained 40-plate visual atlas."""
import html
import json
import posixpath
import re
from html.parser import HTMLParser

from paper_vii_reading import BOOK
from paper_vii_atlas_descriptions import FIGURES
from reader_atlas import (atlas_tex as original_atlas_tex, digest,
                          render_drawing, transcript_order)
from readable_chapters import (Chapter, HEADINGS, MATH_PATTERN, PANELS, clean_tex,
                               group, manuscript_macros, original_math,
                               passage_links, plain_math, presentation_tex,
                               reading_options, render_table)
from reading_navigation import atlas_config, navigation, outline, resources
from reader_documents import png_dimensions
from reader_drawing_transcripts import (label_tex,drawing_nodes,coordinate,
                                        expand_drawing_loops,matrix_label_blocks)
from render_paper_vii_atlas import CROPS, PDF, PDF_SHA256

SOURCE = BOOK['base']+'monograph_atlas.tex'
DEFINITIONS = BOOK['base']+'atlas_definitions.tex'
INDEX = 'read/paper-vii/atlas/index.html'
REPORT = 'documents/paper-vii-atlas.json'
RECEIPTS = 'assets/atlas/paper-vii/figures.json'
HTML_COUNT = 40
TABLE_AIDS = {
    (2,'L22'): dict(caption='Types and conventions used in the atlas',
                   headers=['Symbol','Object','What it records'],row_header_column=0),
    (28,'L516'): dict(caption='Evidence layers and their limits',
                    headers=['Evidence','What it supports','What it does not supply'],row_header_column=0),
}
REFERENCE_PATTERN = re.compile(r'(Section|Definition|Theorem|Proposition|Corollary|Example|Classical input) (II\.\d+(?:\.\d+)?)')
EXTENDED = {'s3','polar','choi','gram','defect','stability','memory_positive',
            'transfer_ground','heat_limits','constraint_image','tower_tail','trace_topology'}


def drawing_source(name):
    if name not in FIGURES:
        raise ValueError('Unknown Paper VII drawing '+name)
    return BOOK['base']+('visual_graphics_extended/' if name in EXTENDED else 'visual_graphics/')+name+'.tex'


def atlas_macros(main,definitions):
    macros=manuscript_macros(main+'\n'+definitions,BOOK.get('required_macros'))
    for match in re.finditer(r'\\renewcommand\{\\(AA)\}\{',definitions):
        macros[match[1]]=group(definitions,match.end()-1)[0]
    for match in re.finditer(r'\\providecommand\{\\(mat|diagmat)\}\[1\]\{',definitions):
        if match[1] not in macros:
            macros[match[1]]=dict(arguments=1,body=group(definitions,match.end()-1)[0])
    return macros


def reading_aids(name,nodes,source):
    return dict(**FIGURES[name],blocks=matrix_label_blocks(nodes,source))


def atlas_tex(text):
    text=re.sub(r'\\xfig\{',lambda m:r'\vfig{',text)
    text=re.sub(r'\\endgroup\b',lambda m:' '*len(m[0]),text)
    text=re.sub(r'\\vspace\{[\d.]+pt\}',lambda m:' '*len(m[0]),text)
    return original_atlas_tex(text)


def expected_math(plate,figures):
    result=[];position=0
    for match in re.finditer(r'\\(?:vfig|xfig)\{([^{}]+)\}',plate['body']):
        result.extend(original_math(plate['body'][position:match.start()]))
        figure=figures[match[1]]
        result.extend(m for index in figure['order'] for m in original_math(figure['nodes'][index]['text']))
        position=match.end()
    return result+original_math(plate['body'][position:])


def reference_keys(plate):
    keys = [(kind.replace(' input',''),number) for kind,number in REFERENCE_PATTERN.findall(plate['locator'])]
    # V18 retains the older "Classical input" wording. The same numbered
    # Kraus/Choi statement is a Standard fact in the current manuscript.
    keys=[('Standardfact',number) if (kind,number)==('Classical','II.7.7') else (kind,number)
          for kind,number in keys]
    if not keys:
        raise ValueError('Paper VII plate has no declared manuscript reference')
    return keys



def plate_url(number):
    return 'read/paper-vii/atlas/v'+str(number).zfill(2)+'.html'


def plates(source):
    starts = list(re.finditer(r'\\vpage\{',source))
    if not starts or digest(source[:starts[0].start()].encode()) != 'a5b1467406baf413953be7f500023eb3a77e661d85116a33175d29aa3bad7de3':
        raise ValueError('Unexpected Paper VII atlas preamble')
    result = []
    for i, match in enumerate(starts):
        end = match.end()-1
        values = []
        for _ in range(4):
            value,end = group(source,end)
            values.append(value)
        number,title,category,locator = values
        if number != str(i+1) or original_math(source[match.start():end]):
            raise ValueError('Review Paper VII atlas numbering or metadata')
        stop = starts[i+1].start() if i+1<len(starts) else len(source)
        result.append(dict(number=i+1,title=title,category=category,locator=locator,
                           line=source.count('\n',0,match.start())+1,
                           end_line=source.count('\n',0,stop),
                           body='\n'*source.count('\n',0,end)+source[end:stop],
                           url=plate_url(i+1) if i<HTML_COUNT else INDEX+'#v'+str(i+1).zfill(2)))
    if len(result) != 40:
        raise ValueError('Review the changed Paper VII atlas inventory')
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
        raise ValueError('Paper VII atlas PDF differs from the frozen guide')
    main = reader.readable_books['paper-vii']['main']
    macros = atlas_macros(main,definitions.decode('utf-8-sig'))
    selected = plates(raw.decode('utf-8-sig'))
    receipts = json.loads((reader.site.root/'website'/RECEIPTS).read_bytes())
    if receipts['source_pdf'] != PDF or receipts['source_pdf_sha256'] != PDF_SHA256:
        raise ValueError('Unexpected Paper VII drawing PDF binding')
    figures = {}
    if len(receipts['figures'])!=38:
        raise ValueError('Paper VII needs exactly 38 atlas drawings')
    crops={name:(number,bounds) for name,number,bounds in CROPS}
    for record in receipts['figures']:
        name = record['name']
        if name not in FIGURES or record['source'] != drawing_source(name):
            raise ValueError('Unexpected Paper VII drawing source')
        number,bounds=crops[name]
        if (record['image']!='assets/atlas/paper-vii/'+name+'.png'
                or record['plate']!=number or record['pdf_page']!=number+117
                or record['crop_pdf_points']!=bounds):
            raise ValueError('Paper VII drawing crop or image path changed')
        reader.add(record['source'])
        source = reader.site.read_source(reader.records[record['source']])
        image = (reader.site.root/'website'/record['image']).read_bytes()
        if digest(source) != record['source_sha256'] or digest(image) != record['image_sha256']:
            raise ValueError('Review changed Paper VII drawing '+name)
        nodes = drawing_nodes(source.decode('utf-8-sig'))
        width,height = png_dimensions(image)
        figures[name] = dict(receipt=record,nodes=nodes,description=reading_aids(name,nodes,source.decode('utf-8-sig')),
                             order=transcript_order(reading_aids(name,nodes,source.decode('utf-8-sig')),nodes),width=width,height=height)
    used = [name for p in selected[:HTML_COUNT] for name in re.findall(r'\\(?:vfig|xfig)\{([^{}]+)\}',p['body'])]
    if sorted(used) != sorted(FIGURES) or set(figures) != set(FIGURES):
        raise ValueError('Paper VII opening-plate drawing coverage changed')
    references = {}
    for _,_,chapter in reader.readable_books['paper-vii']['chapters']:
        for node in chapter.nodes:
            if node['number']:
                references[(node['kind'].capitalize(),node['number'])] = (chapter,node)
    resolved = {}
    for plate in selected[:HTML_COUNT]:
        resolved[plate['number']] = []
        for key in reference_keys(plate):
            if key not in references:
                raise ValueError('Paper VII atlas manuscript reference no longer resolves: '+str(key))
            chapter,node = references[key]
            target = chapter.url+'#'+node['id']
            resolved[plate['number']].append((' '.join(key).replace('Standardfact','Standard fact'),target))
            chapter.related_readings.setdefault(node['id'],[]).append(
                ('Atlas V'+str(plate['number'])+': '+plate['title'],plate['url']))
    reader.paper_vii_atlas = dict(plates=selected,figures=figures,macros=macros,
                                 references=resolved,source_sha256=digest(raw),
                                 definitions_sha256=digest(definitions))


def neighbours(reader, plate, placement='top'):
    config = atlas_config('paper-vii', 'Paper VII', INDEX, reader.paper_vii_atlas['plates'])
    return navigation(config, plate['url'], placement)


def render(reader):
    site,atlas = reader.site,reader.paper_vii_atlas
    e = html.escape
    pdf = reader.records[PDF]
    reports = []
    aided = set()
    for plate in atlas['plates'][:HTML_COUNT]:
        number,page = plate['number'],plate['url']
        title = 'Paper VII atlas / V'+str(number)+': '+plate['title']
        chapter = AtlasChapter(atlas_tex(plate['body']),atlas['macros'])
        chapter.url = page
        chapter.command_links = {'pagerefV':{str(p['number']):(p['url'],'V'+str(p['number'])) for p in atlas['plates']}}
        body = '<p class="eyebrow">Paper VII visual atlas · V'+str(number)+' · '+e(plate['category'])+'</p><h1>'+e(plate['title'])+'</h1>'
        body += '<p>'+e(plate['locator'])+'</p>'+reader.work_routes('paper-vii',page)+neighbours(reader,plate)
        body += '<nav class="document-routes" aria-label="Manuscript passages illustrated on this plate">'+''.join(
            '<a href="'+site.rel(target,page)+'">'+e(label)+'</a>' for label,target in atlas['references'][number])+'</nav>'
        tools = '<p><a href="'+reader.viewer_url(pdf,page,'page='+str(number+117))+'">Original plate in the monograph PDF</a> · <a href="'+reader.resolve(SOURCE,page,'L'+str(plate['line']))+'">Original atlas source</a></p>'
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
                    raise ValueError('Review the Paper VII atlas table '+str(key))
                aided.add(key)
                body += '<section id="'+identifier+'">'+render_table(node,chapter,TABLE_AIDS[key])+passage_links(links)+'</section>'
            elif kind=='text' or kind in PANELS:
                body += '<section id="'+identifier+'" class="reading-block '+kind+'">'
                if kind in PANELS:
                    body += '<h3>'+chapter.inline(node['title'] or PANELS[kind])+'</h3>'
                body += chapter.paragraphs(node['body'])+passage_links(links)+'</section>'
            else:
                raise ValueError('Unsupported Paper VII atlas block: '+kind)
        body += '</article>'+neighbours(reader,plate,'bottom')
        body += '<details class="document-provenance"><summary>Source and conversion record</summary><p>The original atlas wording, equations and drawing labels are retained. Drawings are views of the frozen monograph PDF. Text descriptions and table headings are added reading aids. This conversion does not rebuild TeX, rerun the examples, audit proofs or compile Lean.</p><p><a href="'+site.rel(REPORT,page)+'">Conversion checks and source hashes</a></p></details>'
        expected = expected_math(plate,atlas['figures'])
        if chapter.math != expected:
            raise ValueError('Paper VII atlas mathematics differ on V'+str(number))
        site.page(page,title,body)
        site.search.append(dict(title=title,group='Collection',kind='Papers and source',work_ids=['paper-vii'],
                                url=page,text=plain_math(plate['body'])[0]+' '+plate['title']))
        reports.append(dict(number=number,url=page,start_line=plate['line'],end_line=plate['end_line'],
                            math_expressions=len(expected),math_sequence_sha256=digest(json.dumps(expected,ensure_ascii=False).encode()),
                            nodes=[{k:n[k] for k in ('kind','id','line','end_line')} for n in chapter.nodes]))
    if aided != set(TABLE_AIDS):
        raise ValueError('Paper VII atlas table coverage differs')
    report = dict(collection_revision=site.revision,source=SOURCE,source_sha256=atlas['source_sha256'],definitions=DEFINITIONS,
                  definitions_sha256=atlas['definitions_sha256'],macro_source=BOOK['main'],macros=atlas['macros'],
                  source_pdf=PDF,source_pdf_sha256=PDF_SHA256,index=INDEX,total_plates=40,html_plates=reports,
                  figures={name:dict(**f['receipt'],nodes=f['nodes'],node_order=f['order'],reading_aid=f['description']) for name,f in atlas['figures'].items()},
                  manuscript_references=atlas['references'],new_proof_review=False,new_lean_execution=False,
                  new_mathematical_example_execution=False,new_tex_build=False)
    site.write(REPORT,json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    body = '<p class="eyebrow">Paper VII · Visual atlas</p><h1>Explore the 40 atlas plates</h1>'
    body += '<p>Read all 40 worked plates with their original drawings, selectable equations, text descriptions, and label transcripts. Every plate links to the manuscript passages it illustrates and to its original monograph PDF page.</p>'+reader.work_routes('paper-vii',INDEX)
    body += '<nav class="chapter-contents" aria-label="Atlas plates"><h2>Choose a plate</h2><ol>'
    for plate in atlas['plates']:
        number = plate['number']
        body += '<li id="v'+str(number).zfill(2)+'"><strong>V'+str(number)+': '+e(plate['title'])+'</strong><p>'
        if number<=HTML_COUNT:
            body += '<a href="'+site.rel(plate['url'],INDEX)+'">Read V'+str(number)+' in HTML</a> · '
        body += '<a href="'+reader.viewer_url(pdf,INDEX,'page='+str(number+117))+'">Open V'+str(number)+' in the PDF</a></p></li>'
    body += '</ol></nav><p><a href="'+reader.resolve(SOURCE,INDEX)+'">Complete selectable atlas source</a> · <a href="'+site.rel(REPORT,INDEX)+'">Conversion records</a></p>'
    site.page(INDEX,'Paper VII visual atlas',body)
    site.search.append(dict(title='Paper VII / Visual atlas',group='Collection',kind='Papers and source',work_ids=['paper-vii'],
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
        nodes = drawing_nodes(read(record['source']).decode('utf-8-sig'))
        assert digest(read(record['source']))==record['source_sha256']
        assert digest((root/record['image']).read_bytes())==record['image_sha256']
        assert record['reading_aid']==reading_aids(name,nodes,read(record['source']).decode('utf-8-sig'))
        assert record['nodes']==nodes and record['node_order']==transcript_order(reading_aids(name,nodes,read(record['source']).decode('utf-8-sig')),nodes)
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
    assert all('v'+str(n).zfill(2) in pages[INDEX].ids for n in range(1,41))
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
