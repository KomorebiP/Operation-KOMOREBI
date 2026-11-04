"""Source-bound editorial notes alongside unchanged manuscript transcripts."""
import hashlib
import html
from html.parser import HTMLParser
import json
import posixpath
import re

MANIFEST='manifests/reader-proofreading-2026-11-01.json'
MANIFESTS=(MANIFEST,'manifests/reader-proofreading-kcos-2026-11-03.json')
REPORT='documents/reader-proofreading.json'
VOID={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}


def validate(data, read, passage, placement=None):
    if data.get('schema')!=1:raise ValueError('Unknown proofreading record schema')
    sources={}
    for row in data['sources']:
        path=row['path']
        if path in sources:raise ValueError('Duplicate proofreading source')
        raw=read(path)
        if hashlib.sha256(raw).hexdigest()!=row['sha256']:
            raise ValueError('Review stale proofreading source: '+path)
        sources[path]=raw.decode('utf-8-sig').splitlines()
    seen=set()
    for note in data['notes']:
        identifier=note['id']
        if not re.fullmatch(r'[a-z0-9-]+',identifier) or identifier in seen:
            raise ValueError('Invalid or duplicate proofreading note')
        seen.add(identifier)
        for anchor in [note['source'],*note['references']]:
            if anchor['path'] not in sources:
                raise ValueError('Missing proofreading source passage: '+identifier)
            lines=sources[anchor['path']];line=anchor['line']
            if type(line) is not int or line<1 or line>len(lines) or lines[line-1]!=anchor['expected']:
                raise ValueError('Review proofreading source passage: '+identifier)
        if placement is not None:
            if not placement(note):
                raise ValueError('Proofreading note is outside its source chapter')
        elif note['placement']!='abstract':
            anchor=re.fullmatch(r'L([1-9][0-9]*)(?:-[1-9][0-9]*)?',note['placement'])
            if not anchor or passage(note['source']['path'],int(anchor[1]))!=note['page']+'#'+note['placement']:
                raise ValueError('Proofreading note is outside its source chapter')
        for reference in note['references']:
            if passage(reference['path'],reference['line'])!=reference['target']:
                raise ValueError('Review proofreading reference target: '+identifier)
    if 'reviews' in data:
        manifests=set();reviewed_sources=set();reviewed_notes=[]
        for review in data['reviews']:
            if review['manifest'] in manifests or not re.fullmatch(r'[0-9a-f]{64}',review['manifest_sha256']):
                raise ValueError('Invalid or duplicate proofreading review')
            manifests.add(review['manifest'])
            if review['metadata'].get('schema')!=1:
                raise ValueError('Unknown proofreading review schema')
            if len(review['source_paths'])!=len(set(review['source_paths'])):
                raise ValueError('Duplicate proofreading source in review')
            reviewed_sources.update(review['source_paths'])
            reviewed_notes.extend(review['note_ids'])
        if reviewed_sources!=set(sources) or sorted(reviewed_notes)!=sorted(seen):
            raise ValueError('Proofreading review bindings differ from selected sources or notes')
    return data


def source_spans(source,node):
    return node.get('source_spans') or [dict(source=node.get('source',source),
        line=node['line'],end_line=node['end_line'])]


def placements(chapters,abstracts=None):
    result={}
    for row in chapters:
        for node in row['nodes']:
            result[(row['url'],node['id'])]={span['source'] for span in source_spans(row['source'],node)}
    for page,source in (abstracts or {}).items():result[(page,'abstract')]={source}
    return lambda note:note['source']['path'] in result.get((note['page'],note['placement']),set())


def prepare(reader):
    from reader_guidance import reading_passage_url
    reader.proofreading_notes=[];reader.rendered_proofreading_notes=[]
    reader.proofreading_record=None
    books=getattr(reader,'readable_books',{})
    selected=set(books)
    sources={};notes=[];reviews=[]
    for manifest in MANIFESTS:
        path=reader.site.root/manifest
        if not path.is_file():continue
        raw=path.read_bytes();data=json.loads(raw)
        if data.get('schema')!=1:raise ValueError('Unknown proofreading record schema')
        chosen_notes=[note for note in data['notes'] if note['work'] in selected]
        required={anchor['path'] for note in chosen_notes for anchor in [note['source'],*note['references']]}
        chosen_sources=[row for row in data['sources'] if row.get('work') in selected or row['path'] in required]
        if not chosen_notes and not chosen_sources:continue
        for row in chosen_sources:
            previous=sources.get(row['path'])
            if previous is not None and previous!=row:
                raise ValueError('Conflicting proofreading source records: '+row['path'])
            sources[row['path']]=row
        notes.extend(chosen_notes)
        reviews.append(dict(manifest=manifest,manifest_sha256=hashlib.sha256(raw).hexdigest(),
            metadata={key:value for key,value in data.items() if key not in {'sources','notes'}},
            selected_works=sorted(selected & ({row.get('work') for row in chosen_sources}|{note['work'] for note in chosen_notes})),
            source_paths=[row['path'] for row in chosen_sources],note_ids=[note['id'] for note in chosen_notes]))
    if not reviews:return
    data=dict(schema=1,reviews=reviews,sources=list(sources.values()),notes=notes)
    chapters=[dict(source=spec['source'],url=spec['url'],nodes=chapter.nodes)
        for book in books.values() for spec,_,chapter in book['chapters']]
    abstracts={book['config']['index']:book['config']['main'] for book in books.values()}
    read=lambda path:reader.site.read_source(reader.records[path])
    reader.proofreading_record=validate(data,read,lambda path,line:reading_passage_url(reader,path,line),placements(chapters,abstracts))
    reader.proofreading_notes=data['notes']


def render(reader,page,placement):
    e=html.escape;body=''
    for note in getattr(reader,'proofreading_notes',[]):
        if (note['page'],note['placement'])!=(page,placement):continue
        identifier=note['id']
        body+='<aside class="proofreading-note" id="proofreading-'+identifier+'" data-proofreading-note="'+identifier+'" data-proofreading-placement="'+e(placement,quote=True)+'" aria-label="Editorial reading note">'
        body+='<p><strong>Editorial reading note · '+e(note['title'])+'.</strong> '+e(note['text'])+'</p><p>'
        body+=' · '.join('<a href="'+e(reader.site.rel(ref['target'],page),quote=True)+'">'+e(ref['label'])+'</a>' for ref in note['references'])
        body+=' · <a href="'+e(reader.site.rel(REPORT,page),quote=True)+'">Proofreading record</a></p></aside>'
        reader.rendered_proofreading_notes.append(identifier)
    return body


def publish(reader):
    if not getattr(reader,'proofreading_record',None):return
    if sorted(reader.rendered_proofreading_notes)!=sorted(note['id'] for note in reader.proofreading_notes):
        raise ValueError('Every proofreading note must appear exactly once')
    reader.site.write(REPORT,json.dumps(dict(reader.proofreading_record,collection_revision=reader.site.revision),ensure_ascii=False,indent=2)+'\n')


class NotePlacements(HTMLParser):
    """Check each note follows its completed authored node, inside the reader."""
    def __init__(self,text,anchors):
        super().__init__()
        self.anchors=anchors;self.previous=None;self.stack=[];self.notes=[]
        self.feed(text)

    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs);identifier=attrs.get('id');note=None
        if identifier in self.anchors:self.previous=identifier
        if 'data-proofreading-note' in attrs:
            note=dict(id=attrs['data-proofreading-note'],placement=attrs.get('data-proofreading-placement'),
                previous=self.previous,inside_anchor=any(item[1] in self.anchors for item in self.stack),
                in_article=any(item[1]=='chapter-text' for item in self.stack),text=[])
            self.notes.append(note)
        if tag not in VOID:self.stack.append((tag,identifier,note))

    def handle_endtag(self,tag):
        for index in range(len(self.stack)-1,-1,-1):
            if self.stack[index][0]==tag:
                del self.stack[index:];break

    def handle_data(self,data):
        for _,_,note in self.stack:
            if note is not None:note['text'].append(data)


def verify(root,documents,pages):
    data=json.loads((root/REPORT).read_bytes())
    assert data['collection_revision']==documents['source_revision']
    sources={row['repository_path']:row for row in documents['files']}
    # Passage bindings are checked again against the generated chapter reports.
    books=json.loads((root/'documents/readable-chapters.json').read_bytes())
    def passage(path,line):
        for row in books:
            node=next((n for n in reversed(row['nodes']) if any(span['source']==path and span['line']<=line<=span['end_line']
                for span in source_spans(row['source'],n))),None)
            if node:return row['url']+'#'+node['id']
    abstracts={note['page']:note['source']['path'] for note in data['notes'] if note['placement']=='abstract'}
    validate(data,lambda path:(root/sources[path]['file_url']).read_bytes(),passage,placements(books,abstracts))
    expected={note['id']:note['page'] for note in data['notes']}
    found={identifier:[] for identifier in expected}
    for page,parsed in pages.items():
        for identifier in parsed.ids:
            if identifier.startswith('proofreading-'):
                identifier=identifier.removeprefix('proofreading-')
                assert identifier in found,('Unrecorded proofreading note',identifier)
                found[identifier].append(page)
    assert all(found[identifier]==[page] for identifier,page in expected.items()),'Every proofreading note must appear exactly once on its recorded page'
    rendered={}
    for page in set(expected.values()):
        anchors={node['id'] for row in books if row['url']==page for node in row['nodes']}
        if page in abstracts:anchors.add('abstract')
        rendered[page]=NotePlacements((root/page).read_text(encoding='utf-8'),anchors).notes
    for note in data['notes']:
        matches=[item for item in rendered[note['page']] if item['id']==note['id']]
        assert len(matches)==1,('Duplicate or missing proofreading note',note['id'])
        item=matches[0]
        assert item['placement']==item['previous']==note['placement'] and not item['inside_anchor'],('Review proofreading note placement',note['id'])
        assert note['placement']=='abstract' or item['in_article'],('Proofreading note is outside its reading chapter',note['id'])
        assert note['text'] in ''.join(item['text']) and note['title'] in ''.join(item['text'])
        for reference in note['references']:
            path,anchor=reference['target'].split('#')
            assert anchor in pages[path].ids
            target=posixpath.relpath(path,posixpath.dirname(note['page']))+'#'+anchor
            assert target in pages[note['page']].links
    return dict(notes=len(data['notes']),reviewed_sources=len(data['sources']),reviews=len(data.get('reviews',[])),mathematical_token_changes=0)
