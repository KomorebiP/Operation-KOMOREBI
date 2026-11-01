"""Source-bound editorial notes alongside unchanged manuscript transcripts."""
import hashlib
import html
import json
import posixpath
import re

MANIFEST='manifests/reader-proofreading-2026-11-01.json'
REPORT='documents/reader-proofreading.json'


def validate(data, read, passage):
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
            lines=sources[anchor['path']];line=anchor['line']
            if type(line) is not int or line<1 or line>len(lines) or lines[line-1]!=anchor['expected']:
                raise ValueError('Review proofreading source passage: '+identifier)
        if note['placement']!='abstract':
            if passage(note['source']['path'],int(note['placement'].removeprefix('L')))!=note['page']+'#'+note['placement']:
                raise ValueError('Proofreading note is outside its source chapter')
        for reference in note['references']:
            if passage(reference['path'],reference['line'])!=reference['target']:
                raise ValueError('Review proofreading reference target: '+identifier)
    return data


def prepare(reader):
    from reader_guidance import reading_passage_url
    path=reader.site.root/MANIFEST
    reader.proofreading_notes=[];reader.rendered_proofreading_notes=[]
    if not path.is_file():return
    data=json.loads(path.read_bytes())
    read=lambda path:reader.site.read_source(reader.records[path])
    reader.proofreading_record=validate(data,read,lambda path,line:reading_passage_url(reader,path,line))
    reader.proofreading_notes=data['notes']


def render(reader,page,placement):
    e=html.escape;body=''
    for note in getattr(reader,'proofreading_notes',[]):
        if (note['page'],note['placement'])!=(page,placement):continue
        identifier=note['id']
        body+='<aside class="proofreading-note" id="proofreading-'+identifier+'" data-proofreading-note="'+identifier+'" aria-label="Editorial reading note">'
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


def verify(root,documents,pages):
    data=json.loads((root/REPORT).read_bytes())
    assert data['collection_revision']==documents['source_revision']
    sources={row['repository_path']:row for row in documents['files']}
    # Passage bindings are checked again against the generated chapter reports.
    books=json.loads((root/'documents/readable-chapters.json').read_bytes())
    def passage(path,line):
        for row in books:
            if row['source']!=path:continue
            node=next((n for n in reversed(row['nodes']) if n['line']<=line<=n['end_line']),None)
            if node:return row['url']+'#'+node['id']
    validate(data,lambda path:(root/sources[path]['file_url']).read_bytes(),passage)
    for note in data['notes']:
        text=(root/note['page']).read_text(encoding='utf-8')
        assert text.count('data-proofreading-note="'+note['id']+'"')==1
        assert html.escape(note['text']) in text
        for reference in note['references']:
            path,anchor=reference['target'].split('#')
            assert anchor in pages[path].ids
            target=posixpath.relpath(path,posixpath.dirname(note['page']))+'#'+anchor
            assert target in pages[note['page']].links
    return dict(notes=len(data['notes']),reviewed_sources=len(data['sources']),mathematical_token_changes=0)
