"""Source-preserving HTML for the 171-lesson Special Functions visual guide.

The original guide concerns the eight-paper series. Links to the current
monograph are explicitly related reading, not claims of theorem correspondence.
"""
import hashlib
import html
import json
from pathlib import Path
import posixpath
import re

from readable_chapters import (Chapter, HEADINGS, clean_tex, group,
                               navigation_title, original_math, render_table)

WORK = 'monographs-special-functions'
BASE = 'monographs/special-functions/expanded_visual/'
MAIN = BASE + 'main.tex'
PDF = 'monographs/special-functions/books/Expanded_Visual_Guide.pdf'
INDEX = 'read/' + WORK + '/atlas/index.html'
REPORT = 'documents/special-functions-atlas.json'
RECEIPTS = 'assets/atlas/' + WORK + '/figures.json'
SPEC_FILE = Path(__file__).with_name('special_functions_atlas_sources.json')
COUNT = 171


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def lesson_url(number):
    return INDEX.replace('index.html', 'l' + str(number).zfill(3) + '.html')


def _arguments(text, start, count):
    values, positions = [], []
    for _ in range(count):
        while start < len(text) and text[start].isspace():
            start += 1
        positions.append(start)
        value, start = group(text, start)
        values.append(value)
    return values, positions, start


def source_specs(load):
    """Walk every authored body input, rejecting unconsumed body material."""
    main = load(MAIN)
    body_start = main.index(r'\begin{document}') + len(r'\begin{document}')
    body_end = main.index(r'\end{document}')
    main_body = main[body_start:body_end]
    inputs = list(re.finditer(r'\\input\{([^{}]+)\}', main_body))
    if not inputs:
        raise ValueError('Special Functions visual guide has no body inputs')
    result, included = [], set()
    current_group = None

    def walk(name):
        nonlocal current_group
        name = name if name.endswith('.tex') else name + '.tex'
        path = BASE + name
        if path in included:
            raise ValueError('Repeated Special Functions visual input: ' + path)
        included.add(path)
        raw = load(path)
        text = clean_tex(raw)
        if name == 'addition_sources.tex':
            result.append(dict(kind='notes', source=path, title='Sequence, channel, and tap conventions',
                               url=INDEX.replace('index.html', 'conventions.html'),
                               line=1, end_line=len(raw.splitlines()), body=raw))
            return
        position = 0
        for match in re.finditer(r'\\(input|lesson|startvolume)\{', text):
            if match.start() < position:
                continue
            if text[position:match.start()].strip():
                raise ValueError('Unselected Special Functions visual prose: ' + path)
            command = match[1]
            args, positions, end = _arguments(text, match.end()-1,
                                               dict(input=1, lesson=8, startvolume=2)[command])
            if command == 'input':
                walk(args[0])
            elif command == 'startvolume':
                current_group = ': '.join(args)
            else:
                number = len([item for item in result if item['kind'] == 'lesson']) + 1
                tag, title, figure, equation, description, example, takeaway, scope = args
                if original_math(tag + title + figure):
                    raise ValueError('Review mathematics in visual lesson metadata')
                if not re.fullmatch(r'[A-Za-z0-9_]+', figure):
                    raise ValueError('Unexpected Special Functions figure name')
                result.append(dict(kind='lesson', number=number, tag=tag, title=title,
                    group=current_group, figure=figure, source=path, url=lesson_url(number),
                    line=text.count('\n', 0, match.start())+1,
                    end_line=text.count('\n', 0, end)+1,
                    field_lines=[text.count('\n', 0, p)+1 for p in positions],
                    equation=equation, description=description, example=example,
                    takeaway=takeaway, scope=scope))
            position = end
        if text[position:].strip():
            raise ValueError('Unselected Special Functions visual tail: ' + path)

    for match in inputs:
        walk(match[1])
    orientation_start = main.index(r'{\LARGE\bfseries How to use this guide\par}')
    orientation_end = main.index(r'\clearpage', orientation_start)
    notes_start = main.index(r'{\LARGE\bfseries Notation and source map\par}')
    def section(start, end, title, slug):
        return dict(kind='notes', source=MAIN, title=title,
                    url=INDEX.replace('index.html', slug+'.html'),
                    line=main.count('\n',0,start)+1, end_line=main.count('\n',0,end)+1,
                    body='\n'*main.count('\n',0,start)+main[start:end])
    result.insert(0, section(orientation_start,orientation_end,'How to use this guide','orientation'))
    result.append(section(notes_start,body_end,'Notation and source map','notation'))
    if [m for p in result if p['source']==MAIN for m in original_math(p['body'])] != original_math(main_body):
        raise ValueError('Unselected mathematics in Special Functions visual front/back matter')
    lessons = [item for item in result if item['kind']=='lesson']
    if len(lessons) != COUNT or len({item['figure'] for item in lessons}) != COUNT:
        raise ValueError('Review changed Special Functions visual lesson inventory')
    return result, sorted(included | {MAIN, BASE+'guide_macros.tex', BASE+'atlas-design.tex'})


def metadata():
    return json.loads(SPEC_FILE.read_text(encoding='utf-8'))


def sequence():
    return [dict(url=p['url'], title=p['title']) for p in metadata()['pages']]


def config():
    pages = metadata()['pages']
    groups, previous = [], None
    for p in pages:
        title = p.get('group') if p['kind']=='lesson' else p['title']
        if title != previous:
            groups.append(dict(start=p['url'], title=title))
            previous = title
    return dict(work=WORK, label='Special Functions visual guide', overview_label='Special Functions',
                index=INDEX, chapters=sequence(), menu_title='Lessons', index_title='All lessons',
                contents_groups=groups, menu_current_group_only=True, footer_index_only=True)


def normalize_notes(raw):
    """Remove only known print wrappers, retaining all authored prose and math."""
    from special_functions_reading import mask
    text = re.sub(r'\{\\LARGE\\bfseries ([^{}]+)\\par\}', r'\\section*{\1}', raw)
    text = clean_tex(text)
    text = re.sub(r'\\pdfbookmark\[0\]\{[^{}]+\}\{[^{}]+\}', lambda m:mask(m[0]), text)
    text = re.sub(r'\\(?:clearpage|par)\b|\\vspace\{[\d.]+in\}', lambda m:mask(m[0]), text)
    text = re.sub(r'\\\\\[[\d.]+in\]', lambda m:r'\\'+' '*(len(m[0])-2), text)
    if original_math(text) != original_math(raw) or text.count('\n') != raw.count('\n'):
        raise ValueError('Special Functions visual note normalization changed source')
    return text


def expected_math(spec):
    if spec['kind']=='notes':
        return original_math(spec['body'])
    return [spec['equation']] + [m for key in ('description','example','takeaway','scope')
                                for m in original_math(spec[key])]


def validate_source(read):
    data = metadata()
    for path, sha in data['inputs'].items():
        if digest(read(path)) != sha:
            raise ValueError('Review changed Special Functions visual source: '+path)
    pages, sources = source_specs(lambda p:read(p).decode('utf-8-sig'))
    descriptors = [{k:v for k,v in p.items() if k not in {'body','equation','description','example','takeaway','scope'}} for p in pages]
    if descriptors != data['pages']:
        raise ValueError('Review changed Special Functions visual source ranges')
    if sources != data['text_sources']:
        raise ValueError('Review changed Special Functions visual input coverage')
    return data, pages


def prepare(reader):
    if WORK not in getattr(reader,'readable_books',{}):
        return
    for path in metadata()['inputs']:
        if not reader.add(path):
            raise ValueError('Missing receipt-bound Special Functions visual source: '+path)
    read = lambda p:reader.site.read_source(reader.owned[p])
    data, pages = validate_source(read)
    receipts=json.loads((reader.site.root/'website'/RECEIPTS).read_bytes())
    figures={r['name']:r for r in receipts['figures']}
    if set(figures)!={p['figure'] for p in pages if p['kind']=='lesson'}:
        raise ValueError('Special Functions visual figure coverage differs')
    if digest((reader.site.root/'website'/RECEIPTS).read_bytes())!=data['figure_receipts_sha256']:
        raise ValueError('Review changed Special Functions figure receipts')
    for name,record in figures.items():
        if (record['source']!=BASE+'figures/'+name+'.png' or
                record['pdf_source']!=BASE+'figures/'+name+'.pdf' or
                record['image']!='assets/atlas/'+WORK+'/'+name+'.webp'):
            raise ValueError('Unexpected Special Functions visual figure paths')
        for key,hashkey in [('source','source_sha256'),('pdf_source','pdf_sha256')]:
            if digest(read(record[key]))!=record[hashkey]:
                raise ValueError('Changed Special Functions original figure: '+record[key])
        if digest((reader.site.root/'website'/record['image']).read_bytes())!=record['image_sha256']:
            raise ValueError('Changed Special Functions browser figure: '+record['image'])
    reader.special_functions_atlas = dict(data=data,pages=pages,figures=figures)


def related_routes(spec):
    """Editorial topic links, without substituting an unverified claim mapping."""
    base = 'read/'+WORK+'/'
    tag = spec.get('tag','').upper().split(' / ',1)[0]
    if tag in {'FOUNDATIONS','PAPER I','SEQUENCES','POLYPHASE','TAPS','BRIDGE','OPERATOR','CAPSTONE'}:
        return [('Sequences and polyphase',base+'sequences-and-polyphase.html'),
                ('Exact sequences and polyphase proofs',base+'sequence-full.html')]
    if tag == 'PAPER II':
        return [('Arithmetic at complex depth',base+'arithmetic-depth.html'),
                ('Arithmetic inverse and character proofs',base+'arithmetic-full.html')]
    if tag == 'PAPER III':
        return [('Spectral functions of zero orbits',base+'orbit-spectra.html'),
                ('Orbit continuation and shift proofs',base+'spectral-full.html')]
    return [('Special Functions monograph',base+'index.html'),
            ('Proof architecture',base+'proof-map.html')]


def _source_link(reader,spec,page,line):
    return '<a href="'+html.escape(reader.resolve(spec['source'],page,'L'+str(line)),quote=True)+'">Source line '+str(line)+'</a>'


def _note_body(spec, reader):
    chapter = Chapter(normalize_notes(spec['body']),{},check_refs=False)
    chapter.url = spec['url']
    result = ''
    for node in chapter.nodes:
        if node['kind'] in HEADINGS:
            # The page already displays the source heading as its H1.
            if node['title'] != spec['title']:
                result += '<h2 id="'+node['id']+'">'+chapter.inline(node['title'])+'</h2>'
        elif node['kind']=='tabular':
            headers={'How to use this guide':['Route','What to follow'],
                     'Sequence, channel, and tap conventions':['Convention','How to read the new lessons'],
                     'Notation and source map':['Notation','Meaning in this guide']}[spec['title']]
            aid=dict(caption=spec['title'],headers=headers,row_header_column=0)
            result += '<section id="'+node['id']+'">'+render_table(node,chapter,aid)+'</section>'
        elif node['kind']=='text':
            result += '<section id="'+node['id']+'">'+chapter.paragraphs(node['body'])+'</section>'
        else:
            raise ValueError('Unsupported Special Functions visual note block: '+node['kind'])
    return result, chapter


def _lesson_body(spec, reader):
    page = spec['url']
    chapter = Chapter('',{})
    chapter.url = page
    record=reader.special_functions_atlas['figures'][spec['figure']]
    raw=(reader.site.root/'website'/record['image']).read_bytes()
    target=reader.site.output/record['image']
    target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
    reader.images[record['source']]=dict(repository_path='website/'+record['image'],
        file_url=record['image'],width=record['width'],height=record['height'],
        size=len(raw),sha256=record['image_sha256'],source=PDF,source_sha256=reader.records[PDF]['sha256'],
        original_image_source=record['source'],original_image_source_sha256=record['source_sha256'],
        git_blob_sha1=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest())
    image=reader.site.rel(record['image'],page)
    body = '<figure id="figure"><img src="'+image+'" width="'+str(record['width'])+'" height="'+str(record['height'])+'" alt="'+html.escape(spec['title'],quote=True)+'" aria-describedby="read-figure" loading="lazy"><figcaption>Original lesson figure. The source description follows below.</figcaption></figure>'
    body += '<section id="formula" aria-label="Central formula">'+chapter.paragraphs(r'\['+spec['equation']+r'\]')+'</section>'
    for key,title,identifier,argument in [('description','Read the figure','read-figure',4),
            ('example','Work an example','example',5),('takeaway','Carry forward','carry-forward',6),
            ('scope','Source and scope','source-scope',7)]:
        body += '<section id="'+identifier+'"><h2>'+title+'</h2>'+chapter.paragraphs(spec[key])
        body += '<p class="reading-passage-links"><a href="#'+identifier+'">Permalink</a> · '+_source_link(reader,spec,page,spec['field_lines'][argument])+'</p></section>'
    return body, chapter


def publish(reader):
    atlas = getattr(reader,'special_functions_atlas',None)
    if atlas is None:
        return
    from reading_navigation import navigation, resources, outline, contents_list
    from core_visual_guides import guide_navigation
    site = reader.site
    reports = []
    for spec in atlas['pages']:
        page = spec['url']
        label = ('Lesson '+str(spec['number'])+' · '+spec['tag']) if spec['kind']=='lesson' else 'Expanded visual guide'
        body = '<p class="eyebrow">Special Functions · '+html.escape(label)+'</p><h1>'+html.escape(spec['title'])+'</h1>'+guide_navigation(WORK,page)+navigation(config(),page)
        body += '<p class="reading-start"><a href="#chapter-text">Start reading</a></p>'
        if spec['kind']=='lesson':
            body += outline('<nav aria-label="On this lesson"><h2>On this lesson</h2><ul>'+''.join('<li><a href="#'+i+'">'+t+'</a></li>' for i,t in [('figure','Figure'),('formula','Central formula'),('read-figure','Read the figure'),('example','Work an example'),('carry-forward','Carry forward'),('source-scope','Source and scope')])+'</ul></nav>')
        body += resources('<p>'+_source_link(reader,spec,page,spec['line'])+' · <a href="'+reader.viewer_url(reader.records[PDF],page)+'">Original visual-guide PDF</a></p>')
        article, chapter = _lesson_body(spec,reader) if spec['kind']=='lesson' else _note_body(spec,reader)
        expressions = expected_math(spec)
        if chapter.math != expressions:
            raise ValueError('Special Functions visual mathematics differs: '+spec['url'])
        body += '<article id="chapter-text" class="readable-chapter">'+article+'</article>'
        if spec['kind']=='lesson':
            body += '<aside class="reader-note"><h2>Related reading in the current monograph</h2><p>'+ ' · '.join('<a href="'+site.rel(target,page)+'">'+title+'</a>' for title,target in related_routes(spec))+'</p><p>These are topic connections. The lesson’s original source and scope note identifies the series result it uses.</p></aside>'
        body += navigation(config(),page,'bottom')
        body += '<details class="document-provenance"><summary>Source and conversion record</summary><p>The authored lesson text, equations, order, and figure are retained. Navigation and related-reading links are web additions. This conversion adds no proof review or Lean execution.</p><p><a href="'+site.rel(REPORT,page)+'">Source identities and conversion checks</a></p></details>'
        site.page(page,'Special Functions visual guide / '+spec['title'],body)
        text = ' '.join(spec.get(k,'') for k in ('tag','title','equation','description','example','takeaway','scope')) if spec['kind']=='lesson' else spec['title']+' '+spec['body']
        site.search.append(dict(title='Special Functions visual guide / '+spec['title'],group='Collection',kind='Guides',visual_guide=True,work_ids=[WORK],url=page,text=text))
        reports.append(dict(url=page,source=spec['source'],kind=spec['kind'],line=spec['line'],end_line=spec['end_line'],
                            math_expressions=len(expressions),math_sequence_sha256=digest(json.dumps(expressions,ensure_ascii=False).encode()),
                            figure=(reader.images[BASE+'figures/'+spec['figure']+'.png']['file_url'] if spec['kind']=='lesson' else None)))
    body = '<p class="eyebrow">Special Functions · Expanded visual guide</p><h1>171 visual lessons</h1><p class="lede">Follow coefficient packets, arithmetic functions, spectra, sequences, and finite operations through original figures and worked calculations.</p>'
    body += guide_navigation(WORK,INDEX)
    body += '<p>This guide accompanies the eight-paper Special Functions series. Each lesson retains its figure, central formula, reading explanation, worked example, and source-and-scope note.</p>'
    body += '<p class="reading-start"><a class="button" href="orientation.html">How to use the guide</a> <a href="l001.html">Begin with the foundations</a></p>'
    body += '<section><h2>Contracted feedback and coupled functions</h2><p>For the current monograph’s contraction families, use its separate visual chapters and the interactive laboratory.</p><p><a href="../contracted-feedback.html">Contracted feedback</a> · <a href="../coupled-coupled-visual.html">Coupled growth and inverse geometry</a> · <a href="../coupled-resolution-visual.html">Finite observation and resolution</a> · <a href="'+site.rel('special-functions-lab.html',INDEX)+'">Coupled-function lab</a></p></section>'
    body += '<nav class="chapter-contents reading-contents-index" aria-label="Special Functions visual lessons"><h2>Choose a lesson</h2>'+contents_list(config(),INDEX)+'</nav>'
    body += '<p><a href="'+reader.viewer_url(reader.records[PDF],INDEX)+'">Original 180-page PDF</a> · <a href="'+site.rel(REPORT,INDEX)+'">Conversion record</a></p>'
    site.page(INDEX,'Special Functions expanded visual guide',body)
    site.search.append(dict(title='Special Functions / Expanded visual guide',group='Collection',kind='Guides',visual_guide=True,work_ids=[WORK],url=INDEX,text='171 lessons foundations packets arithmetic spectra sequences polyphase taps operators capstone'))
    site.write(REPORT,json.dumps(dict(schema=1,index=INDEX,source_revision=site.revision,
        inputs=atlas['data']['inputs'],pages=reports,lessons=COUNT,figures=list(atlas['figures'].values()),
        math_expressions=sum(r['math_expressions'] for r in reports),
        new_tex_build=False,new_lean_execution=False,new_proof_review=False,
        original_figure_generator_executed=False),ensure_ascii=False,indent=2)+'\n')


def inventory(root, files):
    """The visual directory can call this after prepare has selected all sources."""
    rows = [r for r in files if r['repository_path']==PDF]
    if not rows:
        raise ValueError('Missing Special Functions expanded visual PDF')
    from reader_documents import png_dimensions
    preview='assets/atlas/'+WORK+'/preview.png'
    raw=(root/'website'/preview).read_bytes()
    receipt=json.loads((root/'website'/RECEIPTS).read_bytes())
    expected=next(r['source_sha256'] for r in receipt['figures'] if r['name']=='F01_coefficient_addresses')
    if digest(raw)!=expected:
        raise ValueError('Changed Special Functions visual preview')
    width,height=png_dimensions(raw)
    return dict(work=WORK,label='Special Functions',title='Special Functions expanded visual guide',number=None,
        short_title='Packets, functions, sequences, and exact examples',
        summary='171 illustrated lessons, with original figures, selectable equations, worked examples, and source scope notes.',
        units=len(sequence()),unit_kind='pages',source_unit_kind='lessons and reading notes',
        topics='special functions arithmetic spectra sequences polyphase taps operators coefficients',
        preview=dict(image=preview,sha256=expected,width=width,height=height),
        manuscript='read/'+WORK+'/index.html',overview='collection/works/'+WORK+'.html',html_atlas=INDEX,
        visual_pdf=rows[0]['url'],pdf_source=PDF,pdf_sha256=rows[0]['sha256'],integrated_pdf=False,
        sequences=[dict(id='expanded-visual-guide',title='Expanded visual guide',
            summary='The complete 171-lesson sequence with orientation and source notes.',
            source=MAIN,source_sha256=metadata()['inputs'][MAIN],pages=sequence())])


# The shared reader calls its visual publishers render(reader).
render = publish


def verify(root, documents, pages=None):
    """Re-read emitted equations/images and source bytes independently of render."""
    from html.parser import HTMLParser
    from readable_chapters import expand_math
    class MathText(HTMLParser):
        def __init__(self,markup):
            super().__init__();self.article=False;self.depth=0;self.values=[];self.feed(markup)
        def handle_starttag(self,tag,attrs):
            attrs=dict(attrs)
            if tag=='article' and attrs.get('id')=='chapter-text':self.article=True
            if not self.article:return
            if self.depth:self.depth+=1
            elif 'arithmatex' in attrs.get('class','').split():self.depth=1;self.values.append('')
        def handle_endtag(self,tag):
            if self.depth:self.depth-=1
            if tag=='article':self.article=False
        def handle_data(self,text):
            if self.article and self.depth:self.values[-1]+=text
    records={r['repository_path']:r for r in documents['files']}
    records.update({r['repository_path']:r for r in documents.get('images',[])})
    read=lambda path:(root/records[path]['file_url']).read_bytes()
    data,selected=validate_source(read)
    report=json.loads((root/REPORT).read_text(encoding='utf-8'))
    assert report['inputs']==data['inputs']
    assert [p['url'] for p in report['pages']]==[p['url'] for p in selected]
    total=0
    receipts=json.loads((Path(__file__).resolve().parents[1]/'website'/RECEIPTS).read_bytes())
    assert report['figures']==receipts['figures']
    figures={r['name']:r for r in receipts['figures']}
    for figure in figures.values():
        image=records['website/'+figure['image']]
        assert image['source']==PDF and image['source_sha256']==records[PDF]['sha256']
        assert image['original_image_source']==figure['source']
        assert image['original_image_source_sha256']==figure['source_sha256']
    for spec,row in zip(selected,report['pages']):
        markup=(root/spec['url']).read_text(encoding='utf-8')
        actual=[v[2:-2] for v in MathText(markup).values]
        expected=expected_math(spec)
        assert actual==[expand_math(v,{}) for v in expected],'Special Functions visual HTML math changed: '+spec['url']
        assert row['math_sequence_sha256']==digest(json.dumps(expected,ensure_ascii=False).encode())
        total+=len(expected)
        if spec['kind']=='lesson':
            figure=figures[spec['figure']]
            assert row['figure']==figure['image']
            assert digest((root/row['figure']).read_bytes())==figure['image_sha256'], 'Special Functions visual figure changed'
            for identifier in ('read-figure','example','carry-forward','source-scope'):
                assert 'id="'+identifier+'"' in markup or 'id='+identifier in markup
    assert report['math_expressions']==total
    return dict(lessons=COUNT,figures=COUNT,reading_pages=len(selected),math_expressions=total)
