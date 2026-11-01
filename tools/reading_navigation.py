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


def sequence_groups(config):
    """Keep editorial part boundaries in contents and chapter jump menus."""
    sequence = entries(config)
    starts = config.get('contents_groups', [])
    if not starts:
        starts = [dict(start=c['url'], title=c['title']) for c in config['chapters'] if c.get('kind') == 'part']
        if starts and starts[0]['start'] != sequence[0]['url']:
            starts.insert(0, dict(start=sequence[0]['url'], title='Introduction'))
    if not starts:
        return [(None, sequence)]
    positions = {entry['url']: i for i, entry in enumerate(sequence)}
    offsets = [positions[group['start']] for group in starts]
    if offsets[0] != 0 or offsets != sorted(set(offsets)):
        raise ValueError('Contents groups must cover the reading sequence in order')
    if sequence[-1]['url'] == config.get('bib_page') and offsets[-1] != len(sequence)-1:
        starts = [*starts, dict(start=sequence[-1]['url'], title='References')]
        offsets.append(len(sequence)-1)
    return [(group['title'], sequence[start:end]) for group, start, end in
            zip(starts, offsets, [*offsets[1:], len(sequence)])]


def contents_list(config, page, position=None):
    sequence = entries(config)
    positions = {entry['url']: i for i, entry in enumerate(sequence)}
    def listing(group):
        body = '<ol>'
        for entry in group:
            i = positions[entry['url']]
            current = ' aria-current="page"' if i == position else ''
            target = posixpath.relpath(entry['url'], posixpath.dirname(page))
            body += '<li><a data-reading-entry="'+str(i+1)+'" href="'+html.escape(target,quote=True)+'"'+current+'><span class="reading-entry-number" aria-hidden="true">'+str(i+1)+'</span><span>'+html.escape(entry['title'])+'</span></a></li>'
        return body+'</ol>'
    groups = sequence_groups(config)
    if groups[0][0] is None:
        return listing(sequence)
    body = '<div class="reading-contents-groups">'
    for title, group in groups:
        active = any(positions[entry['url']] == position for entry in group)
        body += '<details class="reading-contents-group"'+(' open' if active else '')+'><summary>'+html.escape(title)+' <span>('+str(len(group))+')</span></summary>'+listing(group)+'</details>'
    return body+'</div>'


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
    overview = relative('collection/works/'+config['work']+'.html')
    overview_label = config.get('overview_label', config['label'])
    context=(' data-reading-overview="'+overview+'" data-reading-index="'+relative(config['index'])+'" data-reading-label="'+e(overview_label,quote=True)+'"') if placement=='top' else ''
    body = '<nav class="reading-navigation" aria-label="Chapter and part navigation ('+placement+')" data-reading-work="'+e(config['work'],quote=True)+'" data-reading-position="'+str(position+1)+'" data-reading-total="'+str(len(sequence))+'" data-reading-placement="'+placement+'"'+context+'>'
    body += '<div class="reading-position"><span><a href="'+overview+'" aria-label="'+e(overview_label+' overview',quote=True)+'">'+e(overview_label)+'</a></span><span>'+str(position+1)+' of '+str(len(sequence))+'</span></div>'
    body += '<div class="reading-steps">'+step(previous,'previous','← Previous' if position else '← Contents')
    body += step(following,'next','Next →' if position+1<len(sequence) else ('Continue reading →' if config.get('partial') else 'Contents →'))+'</div>'
    body += '<details class="reading-menu"><summary>'+e(config.get('menu_title','Chapters & parts'))+'</summary><div class="reading-menu-panel"><p><a rel="contents" href="'+relative(config['index'])+'">'+e(config.get('index_title','Full contents'))+'</a></p>'
    body += contents_list(config,page,position)+'</div></details></nav>'
    return body


def atlas_config(work, label, index, plates):
    return dict(work=work,label=label+' atlas',overview_label=label,index=index,
                chapters=[dict(url=p['url'],title='V'+str(p['number'])+' · '+p['title']) for p in plates],
                menu_title='Atlas plates',index_title='All '+str(len(plates))+' atlas plates')


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
            self.active=[];self.parts={};self.reading=None;self.reading_depth=0;self.steps={}
        def source_position(self):
            line,column=self.getpos()
            return self.lines[line-1]+column
        def handle_starttag(self,tag,attrs):
            for part in self.active:
                if part['tag']==tag:part['depth']+=1
            attrs=dict(attrs);classes=attrs.get('class','').split()
            if tag=='nav' and self.reading_depth:self.reading_depth+=1
            if tag=='nav' and attrs.get('data-reading-placement')=='top':
                self.reading=attrs;self.reading_depth=1;self.steps={}
            if tag=='a' and self.reading_depth:
                for direction in ('previous','next'):
                    if 'reading-'+direction in classes:self.steps[direction]=attrs
            name = ('outline' if tag=='details' and 'reading-outline' in classes else
                    'resources' if tag=='details' and 'reading-resources' in classes else
                    'start' if tag=='p' and 'reading-start' in classes else
                    'article' if tag=='article' and attrs.get('id')=='chapter-text' else None)
            if name:self.active.append(dict(name=name,tag=tag,start=self.source_position(),depth=1))
        def handle_endtag(self,tag):
            if tag=='nav' and self.reading_depth:self.reading_depth-=1
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
    reading=parser.reading;returns=''
    if reading and set(parser.steps)=={'previous','next'} and all(reading.get(key) for key in ('data-reading-overview','data-reading-index','data-reading-label')):
        e=html.escape
        def neighbour(direction):
            link=parser.steps[direction]
            label=('← Contents' if link.get('rel')=='contents' else '← Previous') if direction=='previous' else ('Continue →' if link['aria-label'].startswith('Continue reading') else 'Contents →' if link.get('rel')=='contents' else 'Next →')
            return '<a class="reading-return-'+direction+'" href="'+e(link['href'],quote=True)+'" aria-label="'+e(link['aria-label'],quote=True)+'">'+label+'</a>'
        returns=('<nav class="reading-return" aria-label="Keep reading">'+neighbour('previous')+
                 '<a class="reading-work-overview" href="'+e(reading['data-reading-overview'],quote=True)+'" aria-label="'+e(reading['data-reading-label']+' overview',quote=True)+'">Work overview</a>'
                 '<a class="reading-full-contents" href="'+e(reading['data-reading-index'],quote=True)+'">Full contents</a>'+neighbour('next')+'</nav>')
    layout=('<div class="chapter-layout"><aside class="chapter-sidebar'+(' has-reading-tools' if tools else '')+'" aria-label="Section navigation">'+tools+contents+
            returns+'</aside><div class="chapter-reading">'+text('article')+'</div></div>')
    return prefix+toolbar+layout+body[article_end:]


def resources(contents):
    return '<details class="reading-resources"><summary>PDF, source &amp; reading options</summary><div>'+contents+'</div></details>'


def work_links(reader, work, page, exclude=('Read chapters',)):
    """Group secondary routes and omit the chapter link already in the reading bar."""
    targets=[(label,url) for label,url in reader.work_route_targets(work) if label not in exclude]
    groups=[('Read and explore',{'Read chapters','Read PDF','Original PDF','Revised edition','Monograph PDF','Visual atlas','Diagram descriptions','Worked examples','Notation'}),
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
        super().__init__();self.controls=[];self.returns=[];self.has_sidebar=False;self.current=None;self.feed(text)
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='aside' and 'chapter-sidebar' in attrs.get('class','').split():self.has_sidebar=True
        if tag=='nav' and 'data-reading-work' in attrs:
            self.current=dict(attrs=attrs,links=[]);self.controls.append(self.current)
        elif tag=='nav' and 'reading-return' in attrs.get('class','').split():
            self.current=dict(attrs=attrs,links=[]);self.returns.append(self.current)
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
        elif config.get('custom_reader') == 'paper_ix':
            from paper_ix_reading import source_specs as paper_ix_specs
            config['chapters']=paper_ix_specs(load)
        elif config.get('custom_reader') == 'paper_x':
            from paper_x_reading import source_specs as paper_x_specs
            config['chapters']=paper_x_specs(load)
        elif config.get('custom_reader') == 'paper_xi':
            from paper_xi_reading import source_specs as paper_xi_specs
            config['chapters']=paper_xi_specs(load)
        elif config.get('custom_reader') == 'paper_xii':
            from paper_xii_reading import source_specs as paper_xii_specs
            config['chapters']=paper_xii_specs(load)
        elif config.get('custom_reader'):
            config['chapters']=source_specs(load)
        sequence=entries(config)
        assert records[work]==dict(index=config['index'],label=config['label'],partial=bool(config.get('partial')),entries=sequence)
        for entry in sequence:
            page=entry['url'];_,position,previous,following=neighbours(config,page)
            assert page in pages, ('Missing reading page',page)
            parsed=Navigation((root/page).read_text(encoding='utf-8'));controls=parsed.controls
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
            assert len(parsed.returns)==int(parsed.has_sidebar),('Missing or duplicate reading return links',page)
            if parsed.returns:
                assert [target(a) for a in parsed.returns[0]['links']]==[previous['url'],'collection/works/'+work+'.html',config['index'],following['url']],('Wrong reading return destination',page)
            count+=1
    return dict(editions=len(records),reading_pages=count,navigation_controls=2*count)
