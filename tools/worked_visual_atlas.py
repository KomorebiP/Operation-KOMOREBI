"""Source-bound HTML editions of worked visual guides."""
import html
import json
import posixpath
import re
from html.parser import HTMLParser
from readable_chapters import BOOKS
from reader_atlas import atlas_tex as original_atlas_tex, digest, expected_math, render_drawing as original_render_drawing, transcript_order
from readable_chapters import Chapter, HEADINGS, MATH_PATTERN, PANELS, clean_tex, group, manuscript_macros, original_math, passage_links, plain_math, presentation_tex, reading_options, render_table, chapter_text
from reading_navigation import atlas_config, navigation, outline, resources, visual_title, visual_backlink, visual_position, visual_contents, visual_search_terms, visual_search_preview
from reader_documents import png_dimensions
from worked_atlas_drawings import drawing_nodes

class AtlasChapter(Chapter):

    def inline(self, text):
        text=re.sub(r'\\input\{([^{}]+)\}',lambda m:self.included_sources[m[1]]['text'],text)
        while (match:=re.search(r'\\mbox\{',text)):
            value,end=group(text,match.end()-1)
            text=text[:match.start()]+value+text[end:]
        parts = []
        pos = 0
        for match in MATH_PATTERN.finditer(text):
            parts.extend([text[pos:match.start()].replace('\\\\', '\\newline '), match[0]])
            pos = match.end()
        parts.append(text[pos:].replace('\\\\', '\\newline '))
        return re.sub(' data-reference-preview="[^"]*"', '', super().inline(''.join(parts)))

class WorkedAtlas:

    def __init__(self, work, spec, figures, table_aids, related_headings=None):
        self.work = work
        self.BOOK = BOOKS[work]
        self.label = self.BOOK['label']
        self.SOURCE = spec.get('source',self.BOOK['base'] + 'visual_atlas.tex')
        self.SOURCES = spec.get('sources',[self.SOURCE])
        self.EXTRAS = spec.get('extra_sources',{})
        self.DEFINITIONS = spec.get('definitions_path',self.BOOK['base'] + spec.get('definitions',''))
        self.DRAWING_BASE = spec.get('drawing_base',self.BOOK['base']+'visual_graphics/')
        self.DRAWING_SOURCES = spec.get('drawing_sources',{})
        self.PDF_PAGES = spec.get('pdf_pages',{})
        self.INDEX_DRAWINGS = spec.get('index_drawings',[])
        self.INDEX = 'read/' + work + '/atlas/index.html'
        self.REPORT = 'documents/' + work + '-atlas.json'
        self.RECEIPTS = 'assets/atlas/' + work + '/figures.json'
        self.HTML_COUNT = spec.get('plates',24)
        self.FIGURES = figures
        self.TABLE_AIDS = table_aids
        self.RELATED_HEADINGS = related_headings or {}
        self.PDF = spec['pdf']
        self.PDF_SHA256 = spec['sha256']
        self.PDF_PAGE_OFFSET = spec['offset']
        self.CROPS = spec['crops']
        self.ISOLATED_DRAWINGS = spec.get('isolate_drawings',{})

    def drawing_source(self, name):
        return self.DRAWING_SOURCES.get(name,self.DRAWING_BASE + name + '.tex')

    def drawing_pdf_page(self,name,number):return self.PDF_PAGES.get(name,number+self.PDF_PAGE_OFFSET)

    def drawing_nodes(self,source,name):
        return drawing_nodes(source)

    def read_plates(self,read):
        return self.plates(read(self.SOURCE).decode('utf-8-sig'))

    def edition_checks(self):return {}

    def edition_note(self):return ''

    def index_introduction(self,reader,atlas,chapter):return ''

    def verify_index_introduction(self,root,documents,pages,report,read,macros):pass

    def reference_keys(self, plate):
        keys = re.findall(r'(Section|Definition|Theorem|Proposition|Corollary|Remark|Lemma|Example|Formalization target) ((?:[A-Z]|\d+)(?:\.\d+)*)', plate['locator'])
        if not keys:
            keys = [('@', title) for title in self.RELATED_HEADINGS.get(plate['number'], [])]
        if not keys:
            raise ValueError('Worked atlas plate has no manuscript route')
        return keys

    def reference_map(self, chapters):
        from readable_chapters import KIND_NAMES
        references = {}
        headings = {title for titles in self.RELATED_HEADINGS.values() for title in titles}
        for _, _, chapter in chapters:
            for node in chapter.nodes:
                if node['number']:
                    kind = 'Section' if node['kind'] in HEADINGS else KIND_NAMES.get(node['kind'], node['kind'].capitalize())
                    key = (kind, node['number'])
                    if key in references:
                        raise ValueError('Ambiguous manuscript locator: ' + str(key))
                    references[key] = (chapter, node)
                if node['kind'] in HEADINGS and node['title'] in headings:
                    key = ('@', node['title'])
                    if key in references:
                        raise ValueError('Ambiguous manuscript heading: ' + str(key))
                    references[key] = (chapter, node)
        return references

    def reference_route(self, key, reference):
        chapter, node = reference
        return (key[1] if key[0] == '@' else ' '.join(key), chapter.url + '#' + node['id'])

    def reading_aids(self, name, nodes, source):
        from reader_drawing_transcripts import matrix_label_blocks
        info=self.FIGURES[name]
        return info if info.get('blocks') else dict(**{k:v for k,v in info.items() if k!='blocks'},
                                                   blocks=matrix_label_blocks(nodes,source))

    def drawing_tex(self, text):
        return re.sub('\\\\vfig\\[[^\\]]+\\]', lambda m: '\\vfig', text)

    def atlas_tex(self, text):
        return original_atlas_tex(self.drawing_tex(text).replace('\\atlasCaption{', '\\platecaption{'))

    def atlas_macros(self, main, definitions):
        return manuscript_macros(main + '\n' + definitions, self.BOOK.get('required_macros'))

    def source_macros(self,read,main,definitions):return self.atlas_macros(main,definitions)

    def manuscript_chapters(self,read,macros):
        manuscript=[];state={'number_floats':self.BOOK.get('number_floats',False)}
        for spec in self.BOOK['chapters']:
            if 'section_prefix' in spec:state.update(section=0,appendix=False,figure=0,table=0,section_prefix=spec['section_prefix'])
            state.update(spec.get('numbering_state',{}))
            raw=read(spec['source'])
            chapter=Chapter(chapter_text(raw.decode('utf-8-sig'),spec),macros,state=state,check_refs=False)
            chapter.url=spec['url']
            for node in chapter.labels.values():node['url']=chapter.url
            manuscript.append((spec,raw,chapter))
            state={key:getattr(chapter,key) for key in ('section','appendix','part','subsection','subsubsection','counter','section_prefix','figure','table','number_floats')}
        return manuscript

    def plate_math(self, plate, figures):
        return original_math(plate['category']) + original_math(plate['title']) + original_math(plate['locator']) + expected_math(dict(plate, body=self.drawing_tex(plate['body'])), figures)

    def render_atlas_table(self, node, chapter, aid):
        return render_table(node, chapter, aid)

    def render_drawing(self, figure, chapter, reader):
        body = original_render_drawing(figure, chapter, reader)
        if not figure['nodes']:
            body = body.replace('A text description and its labels follow.', 'A text description follows.')
        image = html.escape(reader.site.rel(figure['receipt']['image'], chapter.url), quote=True)
        label = html.escape('Open full-size drawing: ' + figure['description']['alt'], quote=True)
        return re.sub('<img\\b[^>]*>', lambda m: '<a href="' + image + '" aria-label="' + label + '">' + m[0] + '</a>', body, count=1)

    def plate_url(self, number):
        return 'read/'+self.work+'/atlas/v' + str(number).zfill(2) + '.html'

    def chapter_for(self,plate,macros):
        return AtlasChapter(self.atlas_tex(plate['body']),macros,check_refs=False)

    def plates(self, source, start=1, expected=None, path=None):
        starts = list(re.finditer('\\\\vpage\\{', source))
        if not starts or presentation_tex(clean_tex(source[:starts[0].start()])).strip():
            raise ValueError('Unexpected Worked atlas preamble')
        result = []
        for i, match in enumerate(starts):
            end = match.end() - 1
            values = []
            for _ in range(4):
                value, end = group(source, end)
                values.append(value)
            number, title, category, locator = values
            number_int=start+i
            if number != str(number_int):
                raise ValueError('Review Worked atlas numbering or metadata')
            stop = starts[i + 1].start() if i + 1 < len(starts) else len(source)
            result.append(dict(number=number_int, title=title, category=category, locator=locator, source=path or self.SOURCE, line=source.count('\n', 0, match.start()) + 1, end_line=source.count('\n', 0, stop), body='\n' * source.count('\n', 0, end) + source[end:stop], url=self.plate_url(number_int)))
        if len(result) != (self.HTML_COUNT if expected is None else expected):
            raise ValueError('Review the changed Worked atlas inventory')
        return result

    def prepare(self, reader):
        for path in [*self.SOURCES,*self.EXTRAS,self.DEFINITIONS,self.PDF]:
            reader.add(path)
        read=lambda path:reader.site.read_source(reader.records[path])
        for path,sha in self.EXTRAS.items():
            if digest(read(path))!=sha:raise ValueError('Changed atlas dependency: '+path)
        raw = reader.site.read_source(reader.records[self.SOURCE])
        definitions = reader.site.read_source(reader.records[self.DEFINITIONS])
        if digest(reader.site.read_source(reader.records[self.PDF])) != self.PDF_SHA256:
            raise ValueError('Worked atlas PDF differs from the frozen guide')
        main = reader.readable_books[self.work]['main']
        macros = self.source_macros(read,main,definitions.decode('utf-8-sig'))
        selected = self.read_plates(read)
        receipts = json.loads((reader.site.root / 'website' / self.RECEIPTS).read_bytes())
        if receipts['source_pdf'] != self.PDF or receipts['source_pdf_sha256'] != self.PDF_SHA256:
            raise ValueError('Unexpected Worked atlas drawing PDF binding')
        figures = {}
        if len(receipts['figures']) != len(self.FIGURES):
            raise ValueError('Worked atlas needs every declared drawing')
        crops = {name: (number, bounds) for name, number, bounds in self.CROPS}
        for record in receipts['figures']:
            name = record['name']
            if name not in self.FIGURES or record['source'] != self.drawing_source(name):
                raise ValueError('Unexpected Worked atlas drawing source')
            number, bounds = crops[name]
            if record.get('isolated_drawing_objects')!=self.ISOLATED_DRAWINGS.get(name):raise ValueError('Changed drawing object extraction')
            if record['image'] != 'assets/atlas/'+self.work+'/' + name + '.png' or record['plate'] != number or record['pdf_page'] != self.drawing_pdf_page(name,number) or (record['crop_pdf_points'] != bounds):
                raise ValueError('Worked atlas drawing crop or image path changed')
            reader.add(record['source'])
            source = reader.site.read_source(reader.records[record['source']])
            image = (reader.site.root / 'website' / record['image']).read_bytes()
            if digest(source) != record['source_sha256'] or digest(image) != record['image_sha256']:
                raise ValueError('Review changed Worked atlas drawing ' + name)
            nodes = self.drawing_nodes(source.decode('utf-8-sig'),name)
            width, height = png_dimensions(image)
            info = self.reading_aids(name, nodes, source.decode('utf-8-sig'))
            figures[name] = dict(receipt=record, nodes=nodes, description=info, order=transcript_order(info, nodes), width=width, height=height)
        used = [name for p in selected[:self.HTML_COUNT] for name in re.findall('\\\\vfig\\{([^{}]+)\\}', self.drawing_tex(p['body']))]
        if sorted(used+self.INDEX_DRAWINGS) != sorted(self.FIGURES) or set(figures) != set(self.FIGURES):
            raise ValueError('Worked atlas drawing coverage changed')
        references = self.reference_map(reader.readable_books[self.work]['chapters'])
        resolved = {}
        for plate in selected[:self.HTML_COUNT]:
            resolved[plate['number']] = []
            for key in self.reference_keys(plate):
                if key not in references:
                    raise ValueError('Worked atlas manuscript reference no longer resolves: ' + str(key))
                chapter, node = references[key]
                resolved[plate['number']].append(self.reference_route(key, (chapter, node)))
                chapter.related_readings.setdefault(node['id'], []).append((visual_backlink(plate), plate['url']))
        if not hasattr(reader, 'worked_atlases'): reader.worked_atlases = {}
        inputs = {}
        for name in re.findall(r'\\input\{([^{}]+)\}', raw.decode('utf-8-sig')):
            path = self.BOOK['base']+name
            reader.add(path)
            included = reader.site.read_source(reader.records[path])
            if original_math(included.decode('utf-8-sig')): raise ValueError('Review mathematics in included atlas source')
            inputs[name] = dict(source=path,sha256=digest(included),text=included.decode('utf-8-sig'))
        reader.worked_atlases[self.work] = dict(source_inputs={path:digest(read(path)) for path in [*self.SOURCES,*self.EXTRAS]},inputs=inputs,plates=selected, figures=figures, macros=macros, references=resolved, labels=reader.readable_books[self.work]['chapters'][0][2].labels, source_sha256=digest(raw), definitions_sha256=digest(definitions))

    def neighbours(self, reader, plate, placement='top'):
        config = atlas_config(self.work, self.label, self.INDEX, reader.worked_atlases[self.work]['plates'])
        return navigation(config, plate['url'], placement)

    def render(self, reader):
        site, atlas = (reader.site, reader.worked_atlases[self.work])
        e = html.escape
        pdf = reader.records[self.PDF]
        reports = []
        aided = set()
        for plate in atlas['plates'][:self.HTML_COUNT]:
            number, page = (plate['number'], plate['url'])
            source_path=plate['source']
            title = visual_title(self.label,plate)
            chapter = self.chapter_for(plate,atlas['macros'])
            chapter.included_sources=atlas['inputs']
            chapter.labels = atlas['labels']
            chapter.validate_references()
            chapter.url = page
            chapter.command_links = {'pagerefV': {str(p['number']): (p['url'], 'Visual ' + str(p['number'])) for p in atlas['plates']}}
            body = '<p class="eyebrow">' + visual_position(self.label,number,self.HTML_COUNT) + ' · ' + chapter.inline(plate['category']) + '</p><h1>' + chapter.inline(plate['title']) + '</h1>'
            body += '<p>' + chapter.inline(plate['locator']) + '</p>' + reader.work_routes(self.work, page) + self.neighbours(reader, plate)
            body += '<nav class="document-routes" aria-label="Manuscript passages illustrated here">' + ''.join(('<a href="' + site.rel(target, page) + '">' + e(label) + '</a>' for label, target in atlas['references'][number])) + '</nav>'
            if number == self.HTML_COUNT:
                body += '<p><a href="' + site.rel('collection/works/'+self.work+'.html#evidence', page) + '">Recorded evidence for '+self.label+'</a></p>'
            tools = '<p><a href="' + reader.viewer_url(pdf, page, 'page=' + str(number + self.PDF_PAGE_OFFSET)) + '">Original plate in the visual-guide PDF</a> · <a href="' + reader.resolve(source_path, page, 'L' + str(plate['line'])) + '">Original atlas source</a></p>'
            tools += reading_options('Show each passage’s permalink and source line. Manuscript links and plate navigation remain visible.')
            body += resources(tools) + '<p class="reading-start"><a href="#chapter-text">Start reading</a></p>'
            toc = '<nav class="chapter-contents" aria-label="Visual contents"><h2 id="contents">On this visual</h2><ul>'
            for node in chapter.nodes:
                if node['kind'] in HEADINGS or node['kind'] == 'figure':
                    toc += '<li><a href="#' + node['id'] + '">' + e(node['title'] if node['kind'] in HEADINGS else 'Drawing and text description') + '</a></li>'
            body += outline(toc + '</ul></nav>') + '<article id="chapter-text" class="readable-chapter atlas-plate" aria-label="' + e(title, quote=True) + '">'
            for node in chapter.nodes:
                kind, identifier = (node['kind'], node['id'])
                links = '<a href="#' + identifier + '">Permalink</a> · <a href="' + reader.resolve(source_path, page, 'L' + str(node['line'])) + '">Source line ' + str(node['line']) + '</a>'
                for name in re.findall(r'\\input\{([^{}]+)\}',node['body']):
                    links+=' · <a href="'+reader.resolve(atlas['inputs'][name]['source'],page)+'">Included source</a>'
                if kind in HEADINGS:
                    body += '<h2 id="' + identifier + '">' + chapter.inline(node['title']) + '</h2>' + passage_links(links)
                elif kind == 'figure':
                    body += '<div id="' + identifier + '">' + self.render_drawing(atlas['figures'][node['body']], chapter, reader) + '</div>'
                elif kind in {'table', 'tabularx', 'tabular'}:
                    key = (number, identifier)
                    if key not in self.TABLE_AIDS:
                        raise ValueError('Review the Worked atlas table ' + str(key))
                    aided.add(key)
                    body += '<section id="' + identifier + '">' + self.render_atlas_table(node, chapter, self.TABLE_AIDS[key]) + passage_links(links) + '</section>'
                elif kind == 'text' or kind in PANELS:
                    body += '<section id="' + identifier + '" class="reading-block ' + kind + '">'
                    if kind in PANELS:
                        body += '<h3>' + chapter.inline(node['title'] or PANELS[kind]) + '</h3>'
                    body += chapter.paragraphs(node['body']) + passage_links(links) + '</section>'
                else:
                    raise ValueError('Unsupported Worked atlas block: ' + kind)
            body += '</article>' + self.neighbours(reader, plate, 'bottom')
            body += '<details class="document-provenance"><summary>Source and conversion record</summary><p>The original atlas wording, equations, and drawing labels are retained. Drawings are views of the retained visual-guide PDF. Text descriptions and table headings are added reading aids. This conversion does not rebuild TeX, rerun the examples, audit proofs or compile Lean.</p>'+self.edition_note()+'<p><a href="' + site.rel(self.REPORT, page) + '">Conversion checks and source hashes</a></p></details>'
            expected = self.plate_math(plate, atlas['figures'])
            if chapter.math != expected:
                raise ValueError('Worked atlas mathematics differ on V' + str(number))
            site.page(page, title, body)
            site.search.append(dict(title=title, group='Collection', kind='Papers and source', visual_guide=True, work_ids=[self.work], url=page, text=visual_search_terms(plate)+' '+plain_math(plate['body'])[0] + ' ' + plate['title'],**visual_search_preview(chapter,atlas['figures'])))
            reports.append(dict(number=number, source=source_path, url=page, start_line=plate['line'], end_line=plate['end_line'], math_expressions=len(expected), math_sequence_sha256=digest(json.dumps(expected, ensure_ascii=False).encode()), nodes=[{k: n[k] for k in ('kind', 'id', 'line', 'end_line')} for n in chapter.nodes]))
        if aided != set(self.TABLE_AIDS):
            raise ValueError('Worked atlas table coverage differs')
        report = dict(collection_revision=site.revision, source=self.SOURCE,source_inputs=atlas['source_inputs'], source_sha256=atlas['source_sha256'], definitions=self.DEFINITIONS, definitions_sha256=atlas['definitions_sha256'], macro_source=self.BOOK['main'], macros=atlas['macros'], source_pdf=self.PDF, source_pdf_sha256=self.PDF_SHA256, index=self.INDEX, total_plates=self.HTML_COUNT, html_plates=reports, figures={name: dict(**f['receipt'], nodes=f['nodes'], node_order=f['order'], reading_aid=f['description']) for name, f in atlas['figures'].items()}, included_sources=atlas['inputs'], manuscript_references=atlas['references'], new_proof_review=False, new_lean_execution=False, new_mathematical_example_execution=False, new_tex_build=False)
        report['edition_checks']=self.edition_checks()
        site.write(self.REPORT, json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        body = '<p class="eyebrow">' + self.label + ' · Visual guide</p><h1>Explore the '+str(self.HTML_COUNT)+' visuals</h1>'
        body += '<p>Read all '+str(self.HTML_COUNT)+' visuals with '+str(len(self.FIGURES))+' original drawings, selectable equations, descriptions, and transcripts of the drawing labels. Each worked example links to the manuscript passages it illustrates; evidence notes retain their source edition’s scope.</p>' + reader.work_routes(self.work, self.INDEX)
        body += self.index_introduction(reader,atlas,chapter)
        body += visual_contents(atlas['plates'],self.INDEX,site.rel,lambda p:reader.viewer_url(pdf,self.INDEX,'page='+str(p['number']+self.PDF_PAGE_OFFSET)),chapter.inline)
        body += '<p>'+ ' · '.join('<a href="'+reader.resolve(path,self.INDEX)+'">Selectable atlas source'+(' '+str(i+1) if len(self.SOURCES)>1 else '')+'</a>' for i,path in enumerate(self.SOURCES))+' · <a href="' + site.rel(self.REPORT, self.INDEX) + '">Conversion records</a></p>'
        site.page(self.INDEX, self.label + ' visual guide', body)
        site.search.append(dict(title=self.label + ' / Visual guide', group='Collection', kind='Papers and source', visual_guide=True, work_ids=[self.work], url=self.INDEX, text=' '.join((p['title'] for p in atlas['plates']))))

    def verify(self, root, documents, pages):
        from check_reader_site import check_png_image_sizes
        report = json.loads((root / self.REPORT).read_bytes())
        assert report['edition_checks']==self.edition_checks()
        assert (report['source'],report['definitions'],report['macro_source'],report['index'])==(self.SOURCE,self.DEFINITIONS,self.BOOK['main'],self.INDEX)
        records = {r['repository_path']: r for r in documents['files']}
        read = lambda path: (root / records[path]['file_url']).read_bytes()
        source, definitions = (read(self.SOURCE), read(self.DEFINITIONS))
        assert report['source_inputs']=={path:digest(read(path)) for path in [*self.SOURCES,*self.EXTRAS]}
        for path,sha in self.EXTRAS.items():assert digest(read(path))==sha
        assert digest(source) == report['source_sha256'] and digest(definitions) == report['definitions_sha256']
        assert report['source_pdf'] == self.PDF and digest(read(self.PDF)) == report['source_pdf_sha256'] == self.PDF_SHA256
        macros = self.source_macros(read,read(self.BOOK['main']).decode('utf-8-sig'),definitions.decode('utf-8-sig'))
        assert report['macros'] == macros
        assert report['collection_revision'] == documents['source_revision']
        assert not any((report[k] for k in ('new_proof_review', 'new_lean_execution', 'new_mathematical_example_execution', 'new_tex_build')))
        assert set(report['included_sources'])==set(re.findall(r'\\input\{([^{}]+)\}',source.decode('utf-8-sig')))
        for name, inclusion in report['included_sources'].items():
            raw=read(inclusion['source'])
            assert digest(raw)==inclusion['sha256'] and raw.decode('utf-8-sig')==inclusion['text']
            assert inclusion['source']==self.BOOK['base']+name
            fragment=AtlasChapter('',macros).inline(inclusion['text']).strip()
            assert fragment in (root/self.plate_url(24)).read_text(encoding='utf-8')
        selected = self.read_plates(read)
        assert report['total_plates'] == len(selected) == self.HTML_COUNT and len(report['html_plates']) == self.HTML_COUNT
        figures = {}
        crops={name:(number,bounds) for name,number,bounds in self.CROPS}
        for name, record in report['figures'].items():
            number,bounds=crops[name]
            assert record.get('isolated_drawing_objects')==self.ISOLATED_DRAWINGS.get(name)
            assert record['source']==self.drawing_source(name)
            assert record['image']=='assets/atlas/'+self.work+'/'+name+'.png'
            assert (record['plate'],record['pdf_page'],record['crop_pdf_points'])==(number,self.drawing_pdf_page(name,number),bounds)
            nodes = self.drawing_nodes(read(record['source']).decode('utf-8-sig'),name)
            assert digest(read(record['source'])) == record['source_sha256']
            assert digest((root / record['image']).read_bytes()) == record['image_sha256']
            info = self.reading_aids(name, nodes, read(record['source']).decode('utf-8-sig'))
            assert record['reading_aid'] == info
            assert record['nodes'] == nodes and record['node_order'] == transcript_order(info, nodes)
            figures[name] = dict(nodes=nodes, order=record['node_order'])
        assert set(figures) == set(self.FIGURES)

        class MathText(HTMLParser):

            def __init__(self):
                super().__init__()
                self.depth = 0
                self.expressions = []

            def handle_starttag(self, tag, attrs):
                if self.depth:
                    self.depth += 1
                elif 'arithmatex' in dict(attrs).get('class', '').split():
                    self.depth = 1
                    self.expressions.append('')

            def handle_endtag(self, tag):
                if self.depth:
                    self.depth -= 1

            def handle_data(self, data):
                if self.depth:
                    self.expressions[-1] += data
        count = 0
        for plate, binding in zip(selected, report['html_plates']):
            expected = self.plate_math(plate, figures)
            assert (binding['number'], binding['url'], binding['start_line'], binding['end_line']) == (plate['number'], plate['url'], plate['line'], plate['end_line'])
            assert binding['source']==plate['source']
            assert binding['math_expressions'] == len(expected)
            assert binding['math_sequence_sha256'] == digest(json.dumps(expected, ensure_ascii=False).encode())
            rendered = MathText()
            rendered.feed((root / plate['url']).read_text(encoding='utf-8'))
            from readable_chapters import expand_math
            assert [x[2:-2] for x in rendered.expressions] == [expand_math(x, macros) for x in expected]
            check_png_image_sizes(root, plate['url'], pages[plate['url']].images)
            for node in binding['nodes']:
                assert node['id'] in pages[plate['url']].ids
                assert 'L' + str(node['line']) in pages[records[plate['source']]['url']].ids
            count += len(expected)
        assert all(('v' + str(n).zfill(2) in pages[self.INDEX].ids for n in range(1, self.HTML_COUNT + 1)))
        returns = 0
        manuscript = self.manuscript_chapters(read,macros)
        references = self.reference_map(manuscript)
        for plate in selected:
            targets = report['manuscript_references'][str(plate['number'])]
            assert targets == [list(self.reference_route(key, references[key])) for key in self.reference_keys(plate)]
            for label, target in targets:
                chapter, anchor = target.split('#')
                assert anchor in pages[chapter].ids
                assert posixpath.relpath(target, posixpath.dirname(plate['url'])) in pages[plate['url']].links
                assert posixpath.relpath(plate['url'], posixpath.dirname(chapter)) in pages[chapter].links
                returns += 1
        self.verify_index_introduction(root,documents,pages,report,read,macros)
        return dict(total_plates=self.HTML_COUNT, html_plates=self.HTML_COUNT, drawings=len(figures), transcribed_labels=sum((len(f['nodes']) for f in figures.values())), math_expressions=count, return_links=returns)
