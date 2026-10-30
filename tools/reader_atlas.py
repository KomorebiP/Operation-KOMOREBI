"""Source-bound HTML edition of Paper IV's 26 visual-atlas plates."""
import hashlib
import html
import json
import posixpath
import re
from html.parser import HTMLParser

from readable_chapters import (Chapter, FOURTH_BASE, HEADINGS, PANELS, MATH_PATTERN,
                               expand_math, group, manuscript_macros, original_math,
                               passage_links, plain_math, reading_options, render_table)
from paper_iv_atlas_descriptions import FIGURES
from reader_documents import png_dimensions

SOURCE=FOURTH_BASE+'atlas-pages.tex'
DEFINITIONS=FOURTH_BASE+'atlas-definitions.tex'
INDEX='read/paper-iv/atlas/index.html'
RECEIPTS='assets/atlas/paper-iv/figures.json'
REPORT='documents/paper-iv-atlas.json'
REFERENCE_PATTERN=re.compile(r'(Section|Definition|Theorem|Proposition|Corollary|Example) (\d+(?:\.\d+)?) \(p\. (\d+)\)')


def digest(raw): return hashlib.sha256(raw).hexdigest()
def plate_url(number): return 'read/paper-iv/atlas/v'+str(number).zfill(2)+'.html'


def plates(text):
    starts=list(re.finditer(r'\\vpage\{',text))
    if not starts or text[:starts[0].start()].strip(): raise ValueError('Unsupported atlas preamble')
    result=[]
    for i,match in enumerate(starts):
        end=match.end()-1; values=[]
        for _ in range(4):
            value,end=group(text,end); values.append(value)
        number,title,category,locator=values
        stop=starts[i+1].start() if i+1<len(starts) else len(text)
        if number!=str(i+1): raise ValueError('Atlas plate numbering changed')
        if original_math(text[match.start():end]): raise ValueError('Review mathematics in atlas metadata')
        result.append(dict(number=i+1,title=title,category=category,locator=locator,
                           line=text.count('\n',0,match.start())+1,end_line=text.count('\n',0,stop),
                           body='\n'*text.count('\n',0,end)+text[end:stop],url=plate_url(i+1)))
    if len(result)!=26: raise ValueError('Review the changed atlas plate inventory')
    return result


def drawing_nodes(text):
    nodes=[]
    for match in re.finditer(r'\\node(?:\[[^\]]*\])?\s+at\s+\(([^)]+)\)\s*\{',text):
        value,end=group(text,match.end()-1)
        if not text[end:].lstrip().startswith(';'): raise ValueError('Unsupported drawing label tail')
        nodes.append(dict(text=value,line=text.count('\n',0,match.start())+1))
    if len(nodes)!=len(re.findall(r'\\node\b',text)): raise ValueError('Unsupported drawing node')
    if [m for n in nodes for m in original_math(n['text'])]!=original_math(text):
        raise ValueError('Mathematics outside the drawing label transcript')
    return nodes


def transcript_order(description, nodes):
    order=[]
    for block in description['blocks']:
        if block['kind']=='text': cells=block['nodes']
        elif block['kind']=='table':
            if not block['rows'] or any(len(r)!=len(block['headers']) for r in block['rows']):
                raise ValueError('Irregular atlas table')
            cells=[block['caption']]+block['headers']+[c for row in block['rows'] for c in row]
        else: raise ValueError('Unsupported atlas reading block')
        order.extend(c for c in cells if isinstance(c,int))
    if sorted(order)!=list(range(len(nodes))): raise ValueError('Every drawing label must be transcribed exactly once')
    if not description['alt'] or not description['description']: raise ValueError('Drawing description is missing')
    return order


def atlas_tex(text):
    # Presentation wrappers only; preserve line numbers and all original prose.
    for command,replacement,closing in (
        ('head',r'\section*{','}'),
        ('takeaway',r'\begin{readerroadmap}[title={Read this as}]',r'\end{readerroadmap}'),
        ('platecaption',r'\begin{readerroadmap}[title={Evidence note from the source edition}]',r'\end{readerroadmap}'),
        ('vfig',r'\begin{figure}',r'\end{figure}')):
        while (match:=re.search(r'\\'+command+r'\{',text)):
            value,end=group(text,match.end()-1)
            text=text[:match.start()]+replacement+value+closing+text[end:]
    text=re.sub(r'\\par\b',lambda m:' '*len(m[0]),text)
    text=text.replace(r'{\small',' '*len(r'{\small')).replace(r'\end{tabularx}}',r'\end{tabularx} ')
    return text


def prepare(reader):
    reader.add(SOURCE,'Paper IV visual atlas source')
    reader.add(DEFINITIONS,'Paper IV atlas notation and layout definitions')
    raw=reader.site.read_source(reader.records[SOURCE])
    defs=reader.site.read_source(reader.records[DEFINITIONS])
    main=reader.readable_books['paper-iv']['main']
    macros=manuscript_macros(main+'\n'+defs.decode('utf-8-sig'))
    selected=plates(raw.decode('utf-8-sig'))
    receipts=json.loads((reader.site.root/'website'/RECEIPTS).read_bytes())
    receipt_map={r['name']:r for r in receipts['figures']}
    if set(receipt_map)!=set(FIGURES) or len(receipts['figures'])!=24: raise ValueError('Atlas figure receipts differ from reading aids')
    figures={}
    for name,description in FIGURES.items():
        receipt=receipt_map[name]
        path=FOURTH_BASE+'visual_graphics/'+name+'.tex'
        if receipt['source']!=path or receipt['image']!='assets/atlas/paper-iv/'+name+'.png': raise ValueError('Unexpected atlas receipt path')
        reader.add(path,'Paper IV atlas drawing: '+name.replace('_',' '))
        source=reader.site.read_source(reader.records[path])
        image=(reader.site.root/'website'/receipt['image']).read_bytes()
        if digest(source)!=receipt['source_sha256'] or digest(image)!=receipt['image_sha256']:
            raise ValueError('Atlas drawing or rendered image changed: '+name)
        nodes=drawing_nodes(source.decode('utf-8-sig'))
        width,height=png_dimensions(image)
        figures[name]=dict(receipt=receipt,nodes=nodes,description=description,order=transcript_order(description,nodes),width=width,height=height)
    used=[name for p in selected for name in re.findall(r'\\vfig\{([^{}]+)\}',p['body'])]
    if sorted(used)!=sorted(FIGURES): raise ValueError('Every atlas drawing must appear once')
    references={}
    for _,_,chapter in reader.readable_books['paper-iv']['chapters']:
        for node in chapter.nodes:
            if node['number'] and node['kind']!='part':
                references[(node['kind'].capitalize(),node['number'])]=chapter.url+'#'+node['id']
    backlinks=manuscript_backlinks(selected,references)
    for _,_,chapter in reader.readable_books['paper-iv']['chapters']:
        for node in chapter.nodes:
            linked=backlinks.get(chapter.url+'#'+node['id'],[])
            chapter.related_readings[node['id']]=[('Atlas V'+str(p['number'])+': '+p['title'],p['url']) for p in linked]
    reader.atlas=dict(plates=selected,figures=figures,macros=macros,references=references,
                      backlinks=backlinks,
                      source_sha256=digest(raw),definitions_sha256=digest(defs))


def reference_matches(locator, references):
    matches=[]
    for match in REFERENCE_PATTERN.finditer(locator):
        key=(match[1],match[2])
        if key not in references: raise ValueError('Atlas reference does not resolve: '+match[0])
        matches.append((match,references[key]))
    if not matches: raise ValueError('Atlas plate has no manuscript reference')
    return matches


def manuscript_backlinks(selected, references):
    """Reverse only the manuscript references explicitly retained in each plate."""
    backlinks={}
    for plate in selected:
        for target in dict.fromkeys(target for _,target in reference_matches(plate['locator'],references)):
            backlinks.setdefault(target,[]).append({key:plate[key] for key in ('number','title','url')})
    return backlinks


def source_references(locator, references, relative):
    out=[]; pos=0
    for match,target in reference_matches(locator,references):
        out.append(html.escape(locator[pos:match.start()]))
        out.append('<a href="'+html.escape(relative(target),quote=True)+'">'+html.escape(match[0])+'</a>')
        pos=match.end()
    return ''.join(out)+html.escape(locator[pos:])


def neighbours(reader, plate):
    number=plate['number']; page=plate['url']
    routes=[]
    def neighbour(index, direction):
        adjacent=reader.atlas['plates'][index]
        return (direction+': V'+str(adjacent['number'])+' · '+adjacent['title'],adjacent['url'])
    if number>1: routes.append(neighbour(number-2,'Previous'))
    routes.append(('All 26 atlas plates',INDEX))
    if number<26: routes.append(neighbour(number,'Next'))
    return '<nav class="chapter-neighbours" aria-label="Neighbouring atlas plates">'+''.join(
        '<a href="'+reader.site.rel(url,page)+'">'+html.escape(title)+'</a>' for title,url in routes)+'</nav>'


def render_drawing(figure, chapter, reader):
    e=html.escape; info=figure['description']; record=figure['receipt']; nodes=figure['nodes']
    def cell(value):
        if isinstance(value,str): return e(value)
        node=nodes[value]
        return '<span id="drawing-label-'+str(value)+'">'+chapter.inline(node['text'])+'</span>'
    def passage(index):
        value=nodes[index]['text']
        sole=MATH_PATTERN.fullmatch(value.strip())
        def display(match):
            tex=next(part for part in match.groups() if part is not None)
            return r'\['+tex+r'\]' if sole or len(tex)>40 else match[0]
        # Long drawing labels get the manuscript's keyboard-scrollable display
        # treatment. The exact expression remains unchanged in the transcript.
        value=MATH_PATTERN.sub(display,value)
        return '<div id="drawing-label-'+str(index)+'">'+chapter.paragraphs(value)+'</div>'
    image=reader.site.rel(record['image'],chapter.url)
    size=' width="'+str(figure['width'])+'" height="'+str(figure['height'])+'"'
    body='<figure class="atlas-drawing"><img src="'+image+'"'+size+' alt="'+e(info['alt'],quote=True)+'" loading="lazy"><figcaption>Original drawing. A text description and its labels follow.</figcaption></figure>'
    body+='<section aria-labelledby="drawing-description"><h2 id="drawing-description">Reading the drawing</h2><p>'+e(info['description'])+'</p>'
    for block in info['blocks']:
        if block['kind']=='text':
            if block.get('title'): body+='<h3>'+e(block['title'])+'</h3>'
            if (block.get('title') or '').endswith('ticks'):
                body+='<p>'+', '.join(cell(index) for index in block['nodes'])+'</p>'
            else: body+=''.join(passage(index) for index in block['nodes'])
        else:
            # A real caption and row/column headers preserve relationships at zoom
            # and in assistive reading, without using the image's coordinates.
            caption=cell(block['caption'])
            body+='<div class="table-scroll" tabindex="0" role="region" aria-label="Drawing values. Scroll horizontally if needed."><table><caption>'+caption+'</caption><thead><tr>'
            body+=''.join('<th scope="col">'+cell(c)+'</th>' for c in block['headers'])+'</tr></thead><tbody>'
            for row in block['rows']:
                body+='<tr>'+''.join(('<th scope="row">' if i==0 else '<td>')+cell(c)+('</th>' if i==0 else '</td>') for i,c in enumerate(row))+'</tr>'
            body+='</tbody></table></div>'
    body+='<p><a href="'+image+'">Open the full-size drawing</a></p>'
    body+=passage_links('<a href="'+reader.resolve(record['source'],chapter.url)+'">Drawing source with line numbers</a>')+'</section>'
    return body


def expected_math(plate, figures):
    result=[]; pos=0
    for match in re.finditer(r'\\vfig\{([^{}]+)\}',plate['body']):
        result.extend(original_math(plate['body'][pos:match.start()]))
        figure=figures[match[1]]
        result.extend(m for index in figure['order'] for m in original_math(figure['nodes'][index]['text']))
        pos=match.end()
    return result+original_math(plate['body'][pos:])


def render(reader):
    atlas=reader.atlas; site=reader.site; e=html.escape; reports=[]
    pdf=next(r for r in reader.records.values() if r['work']=='paper-iv' and r.get('title')=='Visual guide (PDF)')
    for plate in atlas['plates']:
        page=plate['url']; title='Paper IV atlas / V'+str(plate['number'])+': '+plate['title']
        chapter=Chapter(atlas_tex(plate['body']),atlas['macros'])
        chapter.url=page
        chapter.command_links={'pagerefV':{str(p['number']):(p['url'],'V'+str(p['number'])) for p in atlas['plates']}}
        body='<p class="eyebrow">Paper IV visual atlas · V'+str(plate['number'])+' · '+e(plate['category'])+'</p><h1>'+e(plate['title'])+'</h1>'
        body+='<p>'+source_references(plate['locator'],atlas['references'],chapter.relative)+'</p>'
        body+=neighbours(reader,plate)
        body+='<p><a href="'+site.rel('read/paper-iv/index.html',page)+'">Paper IV chapters</a> · <a href="'+reader.viewer_url(pdf,page,'page='+str(plate['number']+2))+'">Original plate in the PDF</a></p>'
        body+='<p>Evidence notes retain the source edition’s scope. <a href="v26.html">Read the evidence guide (V26).</a></p>'+reading_options('Show each passage’s permalink and original source. Manuscript links and plate navigation are always available.')
        body+='<nav class="chapter-contents" aria-label="Plate contents"><h2 id="contents">On this plate</h2><ul>'
        for node in chapter.nodes:
            if node['kind'] in HEADINGS or node['kind']=='figure':
                body+='<li><a href="#'+node['id']+'">'+e(node['title'] if node['kind'] in HEADINGS else 'Drawing and text description')+'</a></li>'
        body+='</ul></nav><article id="chapter-text" class="readable-chapter atlas-plate" aria-label="'+e(title,quote=True)+'">'
        for node in chapter.nodes:
            kind=node['kind']; label=node['title']; identifier=node['id']
            links='<a href="#'+identifier+'">Permalink</a> · <a href="'+reader.resolve(SOURCE,page,'L'+str(node['line']))+'">Source line '+str(node['line'])+'</a>'
            if kind in HEADINGS:
                body+='<h2 id="'+identifier+'">'+chapter.inline(label)+'</h2>'+passage_links(links)
            elif kind=='figure':
                body+='<div id="'+identifier+'">'+render_drawing(atlas['figures'][node['body']],chapter,reader)+'</div>'
            elif kind in {'table','tabularx'}:
                body+='<section id="'+identifier+'">'+render_table(node,chapter)+passage_links(links)+'</section>'
            elif kind=='text' or kind in PANELS:
                body+='<section id="'+identifier+'" class="reading-block '+kind+'">'
                if kind in PANELS: body+='<h3>'+chapter.inline(label or PANELS[kind])+'</h3>'
                body+=chapter.paragraphs(node['body'])+passage_links(links)+'</section>'
            else: raise ValueError('Unsupported atlas node '+kind)
        body+='</article>'+neighbours(reader,plate)
        body+='<details class="document-provenance"><summary>Source and conversion record</summary><p>The retained atlas prose and all drawing labels are preserved. Text descriptions and table headings are added reading aids. Drawing labels are read directly from the original TikZ source. This conversion does not rerun the mathematical examples or Lean.</p><p><a href="'+reader.resolve(SOURCE,page,'L'+str(plate['line']))+'">Original atlas source</a> · <a href="'+site.rel(REPORT,page)+'">Conversion checks</a></p></details>'
        expected=expected_math(plate,atlas['figures'])
        if chapter.math!=expected: raise ValueError('Atlas mathematical sequence differs on V'+str(plate['number']))
        site.page(page,title,body)
        plain=plain_math(plate['body'])[0]
        descriptions=' '.join(atlas['figures'][n]['description']['description']+' '+' '.join(v['text'] for v in atlas['figures'][n]['nodes']) for n in re.findall(r'\\vfig\{([^{}]+)\}',plate['body']))
        site.search.append(dict(title=title,group='Collection',kind='Papers and source',work_ids=['paper-iv'],url=page,text=plain+' '+plain_math(descriptions)[0]))
        reports.append(dict(number=plate['number'],url=page,start_line=plate['line'],end_line=plate['end_line'],
                            source_math_expressions=len(original_math(plate['body'])),math_expressions=len(expected),
                            math_sequence_sha256=digest(json.dumps(expected,ensure_ascii=False).encode()),
                            nodes=[{k:n[k] for k in ('kind','id','line','end_line')} for n in chapter.nodes]))
    report=dict(source=SOURCE,source_sha256=atlas['source_sha256'],definitions=DEFINITIONS,
                definitions_sha256=atlas['definitions_sha256'],macro_source=reader.readable_books['paper-iv']['config']['main'],
                macros=atlas['macros'],plates=reports,manuscript_backlinks=atlas['backlinks'],figures={name:dict(**f['receipt'],node_order=f['order'],nodes=f['nodes']) for name,f in atlas['figures'].items()},
                new_proof_review=False,new_lean_execution=False,new_mathematical_example_execution=False)
    site.write(REPORT,json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    body='<p class="eyebrow">Paper IV · Visual atlas</p><h1>Explore the 26 atlas plates</h1><p>Read the worked models with their original drawings, selectable equations, text descriptions and tables. Each plate links to the manuscript statements it illustrates.</p>'
    body+='<p><a href="'+site.rel('read/paper-iv/index.html',INDEX)+'">Paper IV chapters</a> · <a href="'+site.rel(pdf['url'],INDEX)+'">Visual guide PDF</a></p>'
    body+='<p>For algebra, follow V3–V16. For zero geometry, follow V17–V24. V25 follows one coefficient through the whole calculation, and V26 explains the evidence.</p><nav class="chapter-contents" aria-label="Atlas plates"><h2>Choose a plate</h2><ol>'
    body+=''.join('<li><a href="'+site.rel(p['url'],INDEX)+'">V'+str(p['number'])+' · '+e(p['title'])+'</a></li>' for p in atlas['plates'])
    body+='</ol></nav><p>The source’s test and release statements describe the retained atlas edition. This HTML conversion adds reading aids and does not establish new mathematical or formal verification.</p>'
    site.page(INDEX,'Paper IV visual atlas',body)
    site.search.append(dict(title='Paper IV / Visual atlas: 26 HTML plates',group='Collection',kind='Papers and source',work_ids=['paper-iv'],url=INDEX,text='Accessible atlas diagrams descriptions equations tables '+' '.join(p['title'] for p in atlas['plates'])))


def verify(root, documents, pages):
    """Re-derive displayed math from retained sources and check label coverage."""
    from check_reader_site import check_png_image_sizes
    report=json.loads((root/REPORT).read_bytes())
    records={r['repository_path']:r for r in documents['files']}
    read=lambda path:(root/records[path]['file_url']).read_bytes()
    raw=read(SOURCE); defs=read(DEFINITIONS)
    assert report['source']==SOURCE and digest(raw)==report['source_sha256']
    assert report['definitions']==DEFINITIONS and digest(defs)==report['definitions_sha256']
    macros=manuscript_macros(read(report['macro_source']).decode('utf-8-sig')+'\n'+defs.decode('utf-8-sig'))
    assert report['macros']==macros
    assert not any(report[k] for k in ('new_proof_review','new_lean_execution','new_mathematical_example_execution'))
    figures={}
    for name,record in report['figures'].items():
        source=read(record['source']); nodes=drawing_nodes(source.decode('utf-8-sig'))
        assert digest(source)==record['source_sha256'] and digest((root/record['image']).read_bytes())==record['image_sha256']
        assert record['nodes']==nodes and record['node_order']==transcript_order(FIGURES[name],nodes)
        figures[name]=dict(nodes=nodes,order=record['node_order'])
    assert set(figures)==set(FIGURES)
    class Maths(HTMLParser):
        def __init__(self): super().__init__(); self.depth=0; self.expressions=[]
        def handle_starttag(self,tag,attrs):
            if self.depth: self.depth+=1
            elif 'arithmatex' in dict(attrs).get('class','').split(): self.depth=1; self.expressions.append('')
        def handle_endtag(self,tag):
            if self.depth: self.depth-=1
        def handle_data(self,data):
            if self.depth: self.expressions[-1]+=data
    selected=plates(raw.decode('utf-8-sig'))
    assert len(report['plates'])==len(selected)==26
    linked_plates=set(); return_links=0
    for target,linked in report['manuscript_backlinks'].items():
        chapter,anchor=target.split('#')
        assert anchor in pages[chapter].ids
        assert len(linked)==len({p['number'] for p in linked})
        for plate in linked:
            original=selected[plate['number']-1]
            assert all(plate[k]==original[k] for k in ('number','title','url'))
            assert posixpath.relpath(plate['url'],posixpath.dirname(chapter)) in pages[chapter].links
            assert posixpath.relpath(target,posixpath.dirname(plate['url'])) in pages[plate['url']].links
            linked_plates.add(plate['number']); return_links+=1
    assert linked_plates==set(range(1,27))
    count=0
    for plate,record in zip(selected,report['plates']):
        check_png_image_sizes(root,plate['url'],pages[plate['url']].images)
        assert record['number']==plate['number'] and record['url']==plate['url']
        assert (record['start_line'],record['end_line'])==(plate['line'],plate['end_line'])
        expected=expected_math(plate,figures)
        assert record['source_math_expressions']==len(original_math(plate['body']))
        assert record['math_expressions']==len(expected) and record['math_sequence_sha256']==digest(json.dumps(expected,ensure_ascii=False).encode())
        parsed=Maths(); parsed.feed((root/plate['url']).read_text(encoding='utf-8'))
        assert [m[2:-2] for m in parsed.expressions]==[expand_math(m,macros) for m in expected],plate['url']
        for node in record['nodes']:
            assert node['id'] in pages[plate['url']].ids
            assert 'L'+str(node['line']) in pages[records[SOURCE]['url']].ids
        count+=len(expected)
    return dict(plates=26,drawings=24,math_expressions=count,
                manuscript_targets=len(report['manuscript_backlinks']),return_links=return_links)
