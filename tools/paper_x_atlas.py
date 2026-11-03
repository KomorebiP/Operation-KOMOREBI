"""Paper X's complete numbered atlas and its opening scope contract."""
import html
import json
from pathlib import Path
import re
from types import SimpleNamespace

from paper_x_atlas_descriptions import FIGURES
from paper_x_reading import BOOK,CONTINUATION,prepare_book
from readable_chapters import HEADINGS,PANELS,KIND_NAMES,original_math,manuscript_macros,passage_links,render_table
from reader_atlas import digest
from worked_atlas_drawings import drawing_nodes
from worked_visual_atlas import WorkedAtlas,AtlasChapter

SPEC=json.loads(Path(__file__).with_name('paper_x_atlas_sources.json').read_text(encoding='utf-8'))

REFERENCES={
 1:['sec:conditional-final'],2:['px:1.1','px:5.1','px:6.1','px:7.1','px:7.2','px:8.1'],
 3:['px:2.1','px:2.2','px:2.3'],4:['px:3.2'],5:['px:3.4','px:6.2'],6:['px:5.3','px:6.3'],
 7:['px:6.4','px:6.6'],8:['px:8.2','px:8.3','px:8.4'],9:['px:3.3'],10:['px:4.2'],11:['px:4.2'],
 12:['px:7.3'],13:['px:7.1'],14:['px:8.1','px:8.2'],15:['px:9.1','sec:historical-residue-continuation'],
 16:['px:9.2','px:9.3'],17:['px:9.1'],18:['px:10.1'],19:['px:10.1'],
 20:['px:8.2','px:11.1','sec:conditional-final'],21:['sec:historical-residue-continuation'],
 22:['prop:norm-character'],23:['prop:norm-character'],24:['prop:norm-character'],
 25:['sec:historical-residue-continuation'],26:['prop:residue-count'],27:['sec:historical-residue-continuation'],
 28:['px:9.1','sec:historical-residue-continuation','sec:conditional-final'],29:['px:8.4'],
 30:['sec:conditional-final','sec:historical-residue-continuation']}


def opening_fragment(source):
    start=source.index(r'\section*{The current reading contract}')
    stop=source.index(r'\setcounter{page}{1}',start)
    # The final page break belongs to print pagination, not the scope prose.
    fragment='\n'*source.count('\n',0,start)+source[start:stop]
    titles=re.findall(r'\\section\*\{([^{}]+)\}',fragment)
    if titles!=[r['title'] for r in SPEC['opening_pdf_pages']]:raise ValueError('Review Paper X opening scopes')
    match=re.search(r'\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}',fragment,re.S)
    if not match or fragment.count(r'\begin{tikzpicture}')!=1:raise ValueError('Review Paper X opening contract drawing')
    return fragment[:match.start()]+r'\vfig{opening_contract}'+'\n'*match[0].count('\n')+fragment[match.end():]


class PaperXAtlas(WorkedAtlas):
    def read_plates(self,read):
        wrapper=read(self.DEFINITIONS).decode('utf-8-sig')
        body=wrapper.split(r'\begin{document}',1)[1]
        if re.findall(r'\\input\{([^{}]+)\}',body)!=['source/pages.tex']:raise ValueError('Review Paper X visual input graph')
        opening_fragment(wrapper)
        return super().read_plates(read)

    def atlas_tex(self,text):
        text=text.replace(r'\captiontext{',r'\platecaption{')
        text=text.replace(r'\begin{insight}',r'\begin{readerroadmap}[title={Scope note from the source edition}]').replace(r'\end{insight}',r'\end{readerroadmap}')
        text=text.replace(r'\begin{tabularx}{\linewidth}',r'\begin{tabularx}{\textwidth}')
        return super().atlas_tex(text)

    def source_macros(self,read,main,definitions):
        return manuscript_macros(main+'\n'+read(CONTINUATION).decode('utf-8-sig')+'\n'+definitions,self.BOOK['required_macros'])

    def manuscript_chapters(self,read,macros):
        reader=SimpleNamespace(records={},claims_by_source={},site=SimpleNamespace(read_source=lambda path:read(path)))
        reader.add=lambda path:reader.records.setdefault(path,path)
        return prepare_book(reader,self.BOOK)['chapters']

    def reference_keys(self,plate):return REFERENCES[plate['number']]

    def reference_map(self,chapters):
        return {key:(chapter,node) for _,_,chapter in chapters for key,node in chapter.labels.items() if node.get('url')==chapter.url}

    def reference_route(self,key,reference):
        chapter,node=reference
        kind='Appendix' if node['kind']=='section' and node['number'].isalpha() else 'Section' if node['kind'] in HEADINGS else KIND_NAMES.get(node['kind'],node['kind'].capitalize())
        return kind+' '+node['number'],chapter.url+'#'+node['id']

    def drawing_nodes(self,source,name):
        if name=='opening_contract':
            match=re.search(r'\\begin\{tikzpicture\}[^\n]*\n(.*?)\\end\{tikzpicture\}',source,re.S)
            if not match:raise ValueError('Missing Paper X opening contract picture')
            source='\n'*source.count('\n',0,match.start(1))+match[1]
        return drawing_nodes(source)

    def edition_checks(self):
        return dict(opening_sections=SPEC['opening_pdf_pages'],opening_drawing='opening_contract',
            numbered_plates=30,pdf_page_offset=3,pdf_page_checks=SPEC['pdf_page_checks'],
            manuscript_targets='Stable source labels reconstructed with the Paper X manuscript reader',
            scope='Historical 17/20, checked conditional 20/20, and later unpromoted 19/20 contracts remain distinct')

    def edition_note(self):
        return '<p>The retained PDF has three opening pages before V1. Its two opening scope sections and their separate-output diagram are retained on the atlas contents page. The later 19/20 attempt is a different input contract from the checked conditional 20/20 release.</p>'

    def front_markup(self,reader,atlas,read):
        chapter=AtlasChapter(self.atlas_tex(opening_fragment(read(self.DEFINITIONS).decode('utf-8-sig'))),atlas['macros'])
        chapter.url=self.INDEX;chapter.included_sources={};body='<section class="atlas-opening" aria-label="Original opening scope contract">'
        for node in chapter.nodes:
            kind,identifier=node['kind'],node['id']
            links='<a href="#'+identifier+'">Permalink</a> · <a href="'+reader.resolve(self.DEFINITIONS,self.INDEX,'L'+str(node['line']))+'">Original opening source line '+str(node['line'])+'</a>'
            if kind in HEADINGS:body+='<h2 id="'+identifier+'">'+chapter.inline(node['title'])+'</h2>'+passage_links(links)
            elif kind=='figure':body+='<div id="'+identifier+'">'+self.render_drawing(atlas['figures'][node['body']],chapter,reader)+passage_links(links)+'</div>'
            elif kind=='text':body+='<section id="'+identifier+'">'+chapter.paragraphs(node['body'])+passage_links(links)+'</section>'
            else:raise ValueError('Review Paper X opening block: '+kind)
        expected=original_math(opening_fragment(read(self.DEFINITIONS).decode('utf-8-sig')))
        expected+=[m for node in atlas['figures']['opening_contract']['nodes'] for m in original_math(node['text'])]
        if chapter.math!=expected or expected:raise ValueError('Review new mathematics in the Paper X opening contract')
        return body+'</section>'

    def index_introduction(self,reader,atlas,chapter):
        return '<p>One of the 29 drawings belongs to the two opening scope sections below; the remaining 28 accompany the numbered plates.</p>'+self.front_markup(reader,atlas,lambda path:reader.site.read_source(reader.records[path]))

    def verify_index_introduction(self,root,documents,pages,report,read,macros):
        from reader_documents import png_dimensions
        from reader_atlas import transcript_order
        import posixpath
        records={r['repository_path']:r for r in documents['files']}
        record=report['figures']['opening_contract'];nodes=record['nodes'];info=record['reading_aid']
        raw=(root/record['image']).read_bytes();width,height=png_dimensions(raw)
        figure=dict(receipt=record,nodes=nodes,description=info,order=transcript_order(info,nodes),width=width,height=height)
        site=SimpleNamespace(rel=lambda target,page:posixpath.relpath(target,posixpath.dirname(page)))
        reader=SimpleNamespace(site=site,resolve=lambda path,page,anchor=None:site.rel(records[path]['url'],page)+('#'+anchor if anchor else ''))
        expected=self.front_markup(reader,dict(macros=macros,figures={'opening_contract':figure}),read)
        assert expected in (root/self.INDEX).read_text(encoding='utf-8')
        for node in nodes:assert 'L'+str(node['line']) in pages[records[self.DEFINITIONS]['url']].ids
        # Scope language and plain-text ledger cells are load-bearing here too.
        # Reconstruct every authored prose/table block, beyond the common
        # engine's independent mathematical-sequence and route checks.
        selected=self.read_plates(read)
        for plate in selected:
            chapter=AtlasChapter(self.atlas_tex(plate['body']),macros)
            chapter.url=plate['url'];chapter.included_sources={}
            chapter.command_links={'pagerefV':{str(p['number']):(p['url'],'V'+str(p['number'])) for p in selected}}
            markup=(root/plate['url']).read_text(encoding='utf-8')
            for node in chapter.nodes:
                if node['kind']=='text' or node['kind'] in PANELS:
                    assert chapter.paragraphs(node['body']) in markup,('Changed Paper X visual wording',plate['number'],node['id'])
                elif node['kind'] in {'table','tabular','tabularx'}:
                    assert render_table(node,chapter,self.TABLE_AIDS[(plate['number'],node['id'])]) in markup
                elif node['kind'] in HEADINGS:
                    assert '<h2 id="'+node['id']+'">'+chapter.inline(node['title'])+'</h2>' in markup


TABLE_AIDS={
 (2,'L15'):dict(caption='Objects and their precise contracts',headers=['Object','What it records','What it does not supply'],row_header_column=0),
 # The final evidence ledger retains the three different input contracts.
 (30,'L454'):dict(caption='Historical, checked and later scope records',headers=['Record','What it establishes'],row_header_column=0),
}
ATLAS=PaperXAtlas('paper-x',SPEC,FIGURES,TABLE_AIDS)
prepare=ATLAS.prepare
render=ATLAS.render
verify=ATLAS.verify
