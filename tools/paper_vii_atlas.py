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
from reader_documents import png_dimensions
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


def label_tex(text):
    """Present forced prose line breaks without changing math or matrix rows."""
    result=[]; position=0; in_math=False
    while position<len(text):
        if text.startswith(r'\\',position):
            result.append(r'\\' if in_math else r'\newline ')
            position+=2
        elif text[position]=='\\':
            result.append(text[position:position+2]); position+=2
        else:
            if text[position]=='$': in_math=not in_math
            result.append(text[position]); position+=1
    if in_math:
        raise ValueError('Unclosed drawing-label mathematics')
    return ''.join(result)


def drawing_nodes(text):
    text=expand_drawing_loops(text)
    result=[]
    pattern=r'(?:\\node|(?<!\\)\bnode)(?:\[[^\]]*\])?(?:\s+\([a-z]+\))?(?:\s+at\s+\(([-+\d.]+),([-+\d.]+)\))?\s*\{'
    for match in re.finditer(pattern,text):
        value,end=group(text,match.end()-1)
        if not text[end:].lstrip().startswith((';','(')):
            raise ValueError('Unsupported Paper VII drawing label tail')
        result.append(dict(text=label_tex(value),source_text=value,
                           position=[coordinate(match[1]),coordinate(match[2])] if match[1] else None,
                           line=text.count('\n',0,match.start())+1))
    if len(result)!=len(re.findall(r'(?:\\node|(?<!\\)\bnode)\b',text)):
        raise ValueError('Unsupported Paper VII drawing label')
    if [m for n in result for m in original_math(n['text'])]!=original_math(label_tex(text)):
        raise ValueError('Mathematics outside the Paper VII label transcript')
    return result


def coordinate(text):
    terms=re.findall(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)',text)
    if ''.join(terms)!=text:
        raise ValueError('Unsupported drawing coordinate')
    return sum(map(float,terms))


def expand_drawing_loops(text):
    """Expand only the two literal finite label loops in the frozen drawings."""
    from readable_chapters import split_cells
    while (match:=re.search(r'\\foreach\s+([^{}]+?)\s+in\s*\{',text)):
        variables=match[1].strip().split('/')
        if variables not in ([r'\x',r'\t'],[r'\x',r'\h',r'\t']):
            raise ValueError('Review the drawing loop variables')
        values,end=group(text,match.end()-1)
        while text[end].isspace():end+=1
        body,stop=group(text,end)
        if '\n' in text[match.start():stop]:
            raise ValueError('Review multiline drawing loop source anchors')
        items=split_cells(values,',')
        if len(items)!=3:
            raise ValueError('Review the drawing loop inventory')
        expanded=[]
        for item in items:
            bindings=split_cells(item,'/')
            if len(bindings)!=len(variables):
                raise ValueError('Irregular drawing loop values')
            rendered=body
            for variable,value in zip(variables,bindings):
                value=value.strip()
                if value.startswith('{'):
                    value,tail=group(value,0)
                    if tail!=len(bindings[variables.index(variable)].strip()):
                        raise ValueError('Unsupported drawing loop value')
                if not re.fullmatch(r'[\d./]+',value):
                    raise ValueError('Review nonliteral drawing loop value')
                rendered=re.sub(re.escape(variable)+r'\b',lambda m:value,rendered)
            expanded.append(rendered)
        text=text[:match.start()]+' '.join(expanded)+text[stop:]
    if r'\foreach' in text:
        raise ValueError('Unsupported drawing loop')
    return text


def reading_aids(name,nodes,source):
    """Group the original gridded labels into tables; keep all other labels."""
    cells=[]
    for match in re.finditer(r'\\path\[draw=black!30,[^\]]*\]\s*\(([-\d.]+),([-\d.]+)\) rectangle \(([-\d.]+),([-\d.]+)\)',source):
        x0,y0,x1,y1=map(float,match.groups())
        center=[(x0+x1)/2,(y0+y1)/2]
        found=[i for i,n in enumerate(nodes) if n['position'] and all(abs(a-b)<1e-5 for a,b in zip(n['position'],center))]
        if len(found)==1:
            cells.append(dict(x0=x0,y0=y0,x1=x1,y1=y1,index=found[0]))
    groups=[]
    while cells:
        component=[cells.pop(0)]; changed=True
        while changed:
            changed=False
            for cell in cells[:]:
                if any(abs(cell['x1']-cell['x0']-(other['x1']-other['x0']))<1e-5
                       and abs(cell['y1']-cell['y0']-(other['y1']-other['y0']))<1e-5
                       and ((abs(cell['x0']-other['x0'])<1e-5 and min(abs(cell['y0']-other['y1']),abs(cell['y1']-other['y0']))<1e-5)
                            or (abs(cell['y0']-other['y0'])<1e-5 and min(abs(cell['x0']-other['x1']),abs(cell['x1']-other['x0']))<1e-5))
                       for other in component):
                    component.append(cell);cells.remove(cell);changed=True
        columns=sorted({c['x0'] for c in component}); rows=sorted({c['y0'] for c in component},reverse=True)
        if len(component)>1 and len(component)==len(columns)*len(rows):
            groups.append([[next(c['index'] for c in component if c['x0']==x and c['y0']==y) for x in columns] for y in rows])
    lookup={index:(number,rows) for number,rows in enumerate(groups,1) for row in rows for index in row}
    seen=set();blocks=[]
    for index in range(len(nodes)):
        if index in lookup:
            number,rows=lookup[index]
            if number in seen:continue
            seen.add(number)
            blocks.append(dict(kind='table',caption='Matrix '+str(number)+' · rows top to bottom, columns left to right',
                               headers=['Row / column']+['Column '+str(i+1) for i in range(len(rows[0]))],
                               rows=[['Row '+str(i+1)]+row for i,row in enumerate(rows)]))
        elif blocks and blocks[-1]['kind']=='text':
            blocks[-1]['nodes'].append(index)
        else:
            blocks.append(dict(kind='text',nodes=[index]))
    return dict(**FIGURES[name],blocks=blocks)


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


def neighbours(reader, plate):
    number,page = plate['number'],plate['url']
    selected = reader.paper_vii_atlas['plates']
    routes = []
    if number>1:
        previous = selected[number-2]
        routes.append(('Previous: V'+str(number-1)+' · '+previous['title'],previous['url']))
    routes.append(('All 40 atlas plates',INDEX))
    if number<40:
        following = selected[number]
        label = ('Next: ' if number<HTML_COUNT else 'Continue in the PDF: ')+'V'+str(number+1)+' · '+following['title']
        routes.append((label,following['url']))
    return '<nav class="chapter-neighbours" aria-label="Neighbouring atlas plates">'+''.join(
        '<a href="'+reader.site.rel(target,page)+'">'+html.escape(label)+'</a>'
        for label,target in routes)+'</nav>'


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
        body += '<p><a href="'+reader.viewer_url(pdf,page,'page='+str(number+117))+'">Original plate in the monograph PDF</a> · <a href="'+reader.resolve(SOURCE,page,'L'+str(plate['line']))+'">Original atlas source</a></p>'
        body += '<p>All 40 plates are available in HTML. Evidence notes retain the source edition’s scope.</p>'
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
        body += '</article>'+neighbours(reader,plate)
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
