"""All 27 Paper XII visual plates, with current manuscript labels and source scope."""
import json
from pathlib import Path
import re
from types import SimpleNamespace
from paper_xii_reading import BOOK,prepare_book
from readable_chapters import HEADINGS,PANELS,KIND_NAMES,render_table
from worked_visual_atlas import WorkedAtlas,AtlasChapter
from paper_xii_atlas_descriptions import FIGURES
from paper_xii_atlas_drawings import drawing_nodes

SPEC=json.loads(Path(__file__).with_name('paper_xii_atlas_sources.json').read_bytes())
TABLE_AIDS={(r['plate'],r['id']):r['aid'] for r in SPEC['table_aids']}


def resolve_aliases(text):
    return re.sub(r'\\href\{(p12-route:visual-\d+)\}\{([^{}]+)\}',lambda m:r'\hyperref['+SPEC['aliases'][m[1]]+']{'+m[2]+'}',text)


class PaperXIIAtlas(WorkedAtlas):
    def drawing_nodes(self,source,name):return drawing_nodes(source,name)

    def render_drawing(self,figure,chapter,reader):
        markup=super().render_drawing(figure,chapter,reader)
        prefix='drawing-'+figure['receipt']['name']+'-'
        return re.sub(r'\b(id|aria-labelledby|aria-describedby)="([^"]+)"',lambda m:m[1]+'="'+' '.join(prefix+part for part in m[2].split())+'"',markup)

    def drawing_tex(self,text):
        def inline(match):
            name='inline_nilpotent_slice' if 'reduced slice' in match[0] else 'inline_packet_occupancy' if r'$V=T$' in match[0] else None
            if name is None:raise ValueError('Review new Paper XII inline drawing')
            return r'\vfig{'+name+'}'+'\n'*match[0].count('\n')
        text=re.sub(r'\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}',inline,text,flags=re.S)
        return super().drawing_tex(text)

    def prepare(self,reader):
        self.add_node_labels(reader.readable_books[self.work]['chapters'])
        return super().prepare(reader)

    def add_node_labels(self,chapters):
        labels=chapters[0][2].labels
        for _,_,chapter in chapters:
            for node in chapter.nodes:
                if node['number'] and not node['labels']:labels['@'+node['kind']+':'+node['number']]=dict(node,url=chapter.url)
        return labels

    def read_plates(self,read):
        wrapper=read(self.DEFINITIONS).decode('utf-8-sig').split(r'\begin{document}',1)[1]
        if re.findall(r'\\input\{([^{}]+)\}',wrapper)!=['source/pages.tex']:raise ValueError('Review Paper XII visual input graph')
        selected=super().read_plates(read)
        for plate,check in zip(selected,SPEC['pdf_page_checks'],strict=True):
            if {k:plate[k] for k in ('number','title','category','locator','line','end_line')}!=check:raise ValueError('Changed Paper XII visual metadata')
            plate['locator']=resolve_aliases(plate['locator'])
        return selected

    def atlas_tex(self,text):
        text=self.drawing_tex(resolve_aliases(text)).replace(r'\captiontext{',r'\platecaption{')
        mask=lambda m:''.join('\n' if c=='\n' else ' ' for c in m[0])
        text=re.sub(r'\\(?:sffamily|bfseries|centering|footnotesize|scriptsize)\b|\\begin\{minipage\}\[[ct]\]\{\.(?:44|47|48|49|51|52)\\linewidth\}|\\end\{minipage\}',mask,text)
        text=re.sub(r'\\vspace\{4pt\}',mask,text)
        text=text.replace(r'\textbullet','•')
        # A source callout containing a whole table becomes a semantic table,
        # rather than a nested print box. All cell wording is retained.
        text=re.sub(r'\\begin\{insight\}(.*?)\\end\{insight\}',lambda m:m[1] if r'\begin{tabular' in m[1] else m[0],text,flags=re.S)
        text=text.replace(r'\begin{insight}',r'\begin{readerroadmap}[title={Source reading note}]').replace(r'\end{insight}',r'\end{readerroadmap}')
        text=text.replace(r'\begin{tabularx}{\linewidth}',r'\begin{tabularx}{\textwidth}')
        text=re.sub(r'\\\\\[(?:2|3|4|5|6)pt\]',lambda m:r'\\'+' '*(len(m[0])-2),text)
        return super().atlas_tex(text)

    def chapter_for(self,plate,macros):
        chapter=super().chapter_for(plate,macros);chapter.allow_prose_groups=True;return chapter

    def render_atlas_table(self,node,chapter,aid):
        markup=super().render_atlas_table(node,chapter,aid)
        if '' in aid['headers']:
            label='Invariant' if aid['caption'].startswith('V7:') else 'Measurement' if aid['caption'].startswith('V13:') else None
            if label is None:raise ValueError('Review a new empty Paper XII table corner')
            if markup.count('<th scope="col"></th>')!=1:raise ValueError('Changed Paper XII table corner')
            markup=markup.replace('<th scope="col"></th>','<th scope="col">'+label+'</th>')
        return markup

    def manuscript_chapters(self,read,macros):
        reader=SimpleNamespace(records={},claims_by_source={},site=SimpleNamespace(root=Path(__file__).resolve().parents[1],read_source=lambda record:read(record['repository_path'])))
        reader.add=lambda path,*args:reader.records.setdefault(path,dict(repository_path=path))
        reader.resolve=lambda path,page,anchor=None:path+('#'+anchor if anchor else '')
        chapters=prepare_book(reader,self.BOOK)['chapters'];self.add_node_labels(chapters);return chapters

    def reference_keys(self,plate):return SPEC['references'][str(plate['number'])]

    def reference_map(self,chapters):
        return {key:(chapter,node) for _,_,chapter in chapters for key,node in chapter.labels.items() if node.get('url')==chapter.url}

    def reference_route(self,key,reference):
        chapter,node=reference
        return ('Section' if node['kind'] in HEADINGS else KIND_NAMES.get(node['kind'],node['kind'].capitalize()))+' '+node['number'],chapter.url+'#'+node['id']

    def edition_checks(self):
        return dict(numbered_plates=27,drawings=23,inline_drawings=2,retained_unused_artwork=['support_rotated'],pdf_page_offset=1,pdf_page_checks=SPEC['pdf_page_checks'],manuscript_targets='Current manuscript labels, independently reconstructed by the Paper XII reader',inherited_checks='Retained evidence only; not rerun for this conversion')

    def edition_note(self):
        return '<p>The guide contains 27 plates and 23 drawings: 21 from separate drawing files and two embedded directly in the page source. The unused rotated-support sketch is retained in the source archive. The final claim-delta and evidence pages preserve the distinction between the revised contract and the historical original wording.</p>'

    def verify_index_introduction(self,root,documents,pages,report,read,macros):
        import posixpath
        from reader_documents import ReadingDocuments,png_dimensions
        from reader_atlas import transcript_order
        records={r['repository_path']:r for r in documents['files']}
        resolver=SimpleNamespace(records=records,site=SimpleNamespace(rel=lambda target,page:posixpath.relpath(target,posixpath.dirname(page))))
        resolver.viewer_url=lambda *args:ReadingDocuments.viewer_url(resolver,*args)
        resolver.resolve=lambda *args:ReadingDocuments.resolve(resolver,*args)
        selected=self.read_plates(read);manuscript=self.manuscript_chapters(read,macros);labels=manuscript[0][2].labels
        for plate in selected:
            assert len(pages[plate['url']].ids)==len(set(pages[plate['url']].ids)),('Duplicate Paper XII passage or figure IDs',plate['number'])
            chapter=self.chapter_for(plate,macros);chapter.labels=labels;chapter.url=plate['url'];chapter.included_sources={}
            chapter.command_links={'pagerefV':{str(p['number']):(p['url'],'Visual '+str(p['number'])) for p in selected}}
            markup=(root/plate['url']).read_text(encoding='utf-8')
            assert chapter.inline(plate['locator']) in markup
            for node in chapter.nodes:
                if node['kind']=='text' or node['kind'] in PANELS:assert chapter.paragraphs(node['body']) in markup,('Changed Paper XII visual wording',plate['number'],node['id'])
                elif node['kind'] in {'table','tabular','tabularx'}:assert self.render_atlas_table(node,chapter,self.TABLE_AIDS[(plate['number'],node['id'])]) in markup
                elif node['kind'] in HEADINGS:assert '<h2 id="'+node['id']+'">'+chapter.inline(node['title'])+'</h2>' in markup
                elif node['kind']=='figure':
                    record=report['figures'][node['body']];nodes=record['nodes'];info=record['reading_aid'];width,height=png_dimensions((root/record['image']).read_bytes())
                    figure=dict(receipt=record,nodes=nodes,description=info,order=transcript_order(info,nodes),width=width,height=height)
                    assert self.render_drawing(figure,chapter,resolver) in markup,('Changed Paper XII drawing transcript',node['body'])
            assert 'p12-route:' not in markup


ATLAS=PaperXIIAtlas('paper-xii',SPEC,FIGURES,TABLE_AIDS)
prepare=ATLAS.prepare
render=ATLAS.render
verify=ATLAS.verify
