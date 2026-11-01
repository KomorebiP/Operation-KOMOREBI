"""One reading sequence and accessible chapter controls for every HTML edition."""
import html
import json
import posixpath
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

RECORD = 'documents/reading-navigation.json'


def entries(config):
    result = [dict(url=c['url'], title=c['title']) for c in config['chapters']]
    bibliography = config.get('bib_page')
    if bibliography and bibliography not in {c['url'] for c in result}:
        result.append(dict(url=bibliography, title='Bibliography'))
    if not result or len(result) != len({c['url'] for c in result}):
        raise ValueError('Reading sequence must contain unique pages')
    return result


def neighbours(config, page):
    sequence = entries(config)
    position = next((i for i,c in enumerate(sequence) if c['url']==page), None)
    if position is None: raise ValueError('Page is outside its reading sequence: '+page)
    previous = sequence[position-1] if position else dict(url=config['index'], title='Full contents')
    if position+1<len(sequence): following = sequence[position+1]
    elif config.get('partial'):
        following = dict(url=config['index']+'#source-continuations', title='Continue in the full manuscript')
    else: following = dict(url=config['index'], title='Return to full contents')
    return sequence, position, previous, following


def navigation(config, page, placement='top'):
    if placement not in {'top','bottom'}: raise ValueError('Unknown reading-navigation placement')
    sequence, position, previous, following = neighbours(config,page)
    e = html.escape
    def relative(target):
        path,sep,fragment = target.partition('#')
        return e(posixpath.relpath(path,posixpath.dirname(page))+ (sep+fragment if sep else ''),quote=True)
    def step(target, direction, label):
        relation = ('prev' if direction=='previous' else 'next') if target in sequence else 'contents'
        return ('<a class="reading-step reading-'+direction+'" rel="'+relation+'" href="'+relative(target['url'])+'" aria-label="'+e(label+' '+target['title'],quote=True)+'">'
                '<span class="reading-step-label">'+label+'</span><span class="reading-step-title">'+e(target['title'])+'</span></a>')
    body = '<nav class="reading-navigation" aria-label="Chapter and part navigation ('+placement+')" data-reading-work="'+e(config['work'],quote=True)+'" data-reading-position="'+str(position+1)+'" data-reading-total="'+str(len(sequence))+'" data-reading-placement="'+placement+'">'
    body += '<div class="reading-position"><span>'+e(config['label'])+'</span><span>'+str(position+1)+' of '+str(len(sequence))+'</span></div>'
    body += '<div class="reading-steps">'+step(previous,'previous','← Previous' if position else '← Contents')
    body += step(following,'next','Next →' if position+1<len(sequence) else ('Continue reading →' if config.get('partial') else 'Contents →'))+'</div>'
    body += '<details class="reading-menu"><summary>Chapters &amp; parts</summary><div class="reading-menu-panel"><p><a rel="contents" href="'+relative(config['index'])+'">Full contents</a></p><ol>'
    for i,entry in enumerate(sequence):
        current = ' aria-current="page"' if i==position else ''
        body += '<li><a data-reading-entry="'+str(i+1)+'" href="'+relative(entry['url'])+'"'+current+'><span class="reading-entry-number" aria-hidden="true">'+str(i+1)+'</span><span>'+e(entry['title'])+'</span></a></li>'
    body += '</ol></div></details></nav>'
    return body


def outline(contents):
    return '<details class="reading-outline"><summary>On this page</summary>'+contents+'</details>'


def chapter_layout(body,extra_tools=''):
    """Move complete section navigation beside the unmodified chapter article.

    Track nested tags so a statement-index disclosure cannot truncate the outline.
    Pages without an outline retain their existing structure.
    """
    class Parts(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=False)
            self.lines=[0]+[i+1 for i,c in enumerate(body) if c=='\n']
            self.active=[];self.parts={}
        def source_position(self):
            line,column=self.getpos()
            return self.lines[line-1]+column
        def handle_starttag(self,tag,attrs):
            for part in self.active:
                if part['tag']==tag:part['depth']+=1
            attrs=dict(attrs);classes=attrs.get('class','').split()
            name = ('outline' if tag=='details' and 'reading-outline' in classes else
                    'resources' if tag=='details' and 'reading-resources' in classes else
                    'start' if tag=='p' and 'reading-start' in classes else
                    'article' if tag=='article' and attrs.get('id')=='chapter-text' else None)
            if name:self.active.append(dict(name=name,tag=tag,start=self.source_position(),depth=1))
        def handle_endtag(self,tag):
            for part in self.active[:]:
                if part['tag']!=tag:continue
                part['depth']-=1
                if not part['depth']:
                    self.parts[part['name']]=(part['start'],body.index('>',self.source_position())+1)
                    self.active.remove(part)
    parser=Parts();parser.feed(body)
    parts=parser.parts
    if not {'outline','article'}<=parts.keys():return body
    def text(name):
        start,end=parts[name]
        return body[start:end]
    article_start,article_end=parts['article']
    # Only rearrange controls that precede this article.
    controls=[name for name in ('outline','resources','start') if name in parts]
    if any(parts[name][1]>article_start for name in controls):return body
    prefix=body[:article_start]
    for name in sorted(controls,key=lambda n:parts[n][0],reverse=True):
        start,end=parts[name];prefix=prefix[:start]+prefix[end:]
    contents=text('outline').replace('<summary>On this page</summary>',
        '<summary>Contents<span class="reading-current-section" aria-hidden="true"></span></summary>',1)
    toolbar='<div class="chapter-toolbar">'+''.join(text(name) for name in ('start','resources') if name in parts)+'</div>'
    tools='<div class="chapter-sidebar-tools">'+extra_tools+'</div>' if extra_tools else ''
    layout=('<div class="chapter-layout"><aside class="chapter-sidebar'+(' has-reading-tools' if tools else '')+'" aria-label="Section navigation">'+tools+contents+
            '</aside><div class="chapter-reading">'+text('article')+'</div></div>')
    return prefix+toolbar+layout+body[article_end:]


def resources(contents):
    return '<details class="reading-resources"><summary>PDF, source &amp; reading options</summary><div>'+contents+'</div></details>'


def work_links(reader, work, page):
    """Group secondary routes and omit the chapter link already in the reading bar."""
    targets=[(label,url) for label,url in reader.work_route_targets(work) if label!='Read chapters']
    groups=[('Read and explore',{'Read PDF','Original PDF','Revised edition','Monograph PDF','Visual atlas','Diagram descriptions','Worked examples','Notation'}),
            ('Proofs and implementation',{'Claims','Written proofs','Lean','Code'}),
            ('About this work',{'Paper overview','Evidence','Search this work'})]
    used=set();body='<div class="reading-resource-groups">'
    for title,labels in groups:
        selected=[(label,url) for label,url in targets if label in labels]
        used.update(label for label,url in selected)
        if selected:
            body+='<section><h3>'+title+'</h3><ul>'+''.join('<li><a href="'+html.escape(reader.site.rel(url,page),quote=True)+'">'+html.escape(label)+'</a></li>' for label,url in selected)+'</ul></section>'
    remaining=[(label,url) for label,url in targets if label not in used]
    if remaining:
        body+='<section><h3>Other resources</h3><ul>'+''.join('<li><a href="'+html.escape(reader.site.rel(url,page),quote=True)+'">'+html.escape(label)+'</a></li>' for label,url in remaining)+'</ul></section>'
    return body+'</div>'


def publish_record(site, books):
    record = {work:dict(index=c['index'],label=c['label'],partial=bool(c.get('partial')),entries=entries(c)) for work,c in books.items()}
    site.write(RECORD,json.dumps(record,ensure_ascii=False,indent=2)+'\n')


class Navigation(HTMLParser):
    def __init__(self,text):
        super().__init__();self.controls=[];self.current=None;self.feed(text)
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='nav' and 'data-reading-work' in attrs:
            self.current=dict(attrs=attrs,links=[]);self.controls.append(self.current)
        elif tag=='a' and self.current is not None:self.current['links'].append(attrs)
    def handle_endtag(self,tag):
        if tag=='nav':self.current=None


def verify(root, pages, documents):
    """Check both directions, the full jump menu and boundary pages of each book."""
    from readable_chapters import BOOKS
    from special_functions_reading import source_specs
    sources={r['repository_path']:r for r in documents['files']}
    def load(path):return (root/sources[path]['file_url']).read_text(encoding='utf-8-sig')
    records=json.loads((root/RECORD).read_bytes())
    assert set(records)==set(BOOKS), 'Reading editions missing from navigation'
    count=0
    for work,original in BOOKS.items():
        config=dict(original)
        if config.get('custom_reader') == 'proof_path':
            from proof_path_reading import source_specs as proof_path_specs
            config['chapters']=proof_path_specs(load)
        elif config.get('custom_reader'):
            config['chapters']=source_specs(load)
        sequence=entries(config)
        assert records[work]==dict(index=config['index'],label=config['label'],partial=bool(config.get('partial')),entries=sequence)
        for entry in sequence:
            page=entry['url'];_,position,previous,following=neighbours(config,page)
            assert page in pages, ('Missing reading page',page)
            controls=Navigation((root/page).read_text(encoding='utf-8')).controls
            assert len(controls)==2, ('Reading page needs top and bottom controls',page)
            assert [c['attrs']['data-reading-placement'] for c in controls]==['top','bottom']
            def target(link):
                parts=urlsplit(link['href'])
                assert not parts.scheme and not parts.netloc, 'Reading navigation must stay on site'
                return posixpath.normpath(posixpath.join(posixpath.dirname(page),unquote(parts.path)))+('#'+parts.fragment if parts.fragment else '')
            for control in controls:
                assert control['attrs']['data-reading-work']==work
                assert control['attrs']['data-reading-position']==str(position+1)
                assert control['attrs']['data-reading-total']==str(len(sequence))
                for direction,expected in [('previous',previous),('next',following)]:
                    link=[a for a in control['links'] if 'reading-'+direction in a.get('class','').split()]
                    assert len(link)==1 and target(link[0])==expected['url'], ('Wrong reading neighbour',page,direction)
                menu=[a for a in control['links'] if 'data-reading-entry' in a]
                assert [target(a) for a in menu]==[e['url'] for e in sequence], ('Incomplete reading menu',page)
                assert [i for i,a in enumerate(menu) if a.get('aria-current')=='page']==[position], ('Wrong current chapter',page)
            count+=1
    return dict(editions=len(records),reading_pages=count,navigation_controls=2*count)
