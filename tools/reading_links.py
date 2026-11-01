"""Figure access and citation return routes derived from rendered reading pages."""
from collections import Counter
from html.parser import HTMLParser
import html
import posixpath
import re
from urllib.parse import unquote, urlsplit

VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}


class ReadingMarkup(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.lines = [0]+[i+1 for i,c in enumerate(text) if c=='\n']
        self.stack=[];self.citations=[];self.references={};self.figures=[]
        self.feed(text)

    def source_offset(self):
        line,column=self.getpos()
        return self.lines[line-1]+column

    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if tag=='a' and attrs.get('href') and any(a.get('id')=='chapter-text' for _,a in self.stack):
            anchor=next((a['id'] for _,a in reversed(self.stack) if re.fullmatch(r'L\d+',a.get('id',''))),'chapter-text')
            self.citations.append((attrs['href'],anchor))
        if tag=='img':
            figure=next((a for t,a in reversed(self.stack) if t=='figure'),None)
            if figure is not None:figure['_images'].append(attrs)
        if tag=='figure':attrs['_images']=[]
        if tag not in VOID:self.stack.append((tag,attrs))

    def handle_endtag(self, tag):
        index=next((i for i in range(len(self.stack)-1,-1,-1) if self.stack[i][0]==tag),None)
        if index is None:return
        _,attrs=self.stack[index]
        if tag=='section' and attrs.get('id','').startswith('ref-'):
            if attrs['id'] in self.references:raise ValueError('Duplicate bibliography reference')
            self.references[attrs['id']]=self.source_offset()
        if tag=='figure' and attrs['_images']:self.figures.append((self.source_offset(),attrs['_images']))
        del self.stack[index:]


def figure_controls(body):
    if '<figure' not in body:return body
    insertions=[]
    for offset, images in ReadingMarkup(body).figures:
        controls='<p class="reading-figure-actions">'
        for i,image in enumerate(images,1):
            source=image.get('src','');parts=urlsplit(source)
            if not parts.path or parts.scheme or parts.netloc:continue
            label='View full-size '+('figure' if len(images)==1 else 'image '+str(i))+' (new tab)'
            description=image.get('alt','').strip()
            name=label+(': '+description if description else '')
            controls+='<a href="'+html.escape(source,quote=True)+'" target="_blank" rel="noopener" aria-label="'+html.escape(name,quote=True)+'">'+label+'</a>'
        if '</a>' in controls:insertions.append((offset,controls+'</p>'))
    for offset,markup in reversed(insertions):body=body[:offset]+markup+body[offset:]
    return body


def citation_routes(load, config):
    routes={}
    for chapter in config['chapters']:
        page=chapter['url']
        if page==config['bib_page']:continue
        for href,anchor in ReadingMarkup(load(page)).citations:
            parts=urlsplit(href)
            if parts.scheme or parts.netloc or parts.query:continue
            target=posixpath.normpath(posixpath.join(posixpath.dirname(page),unquote(parts.path))) if parts.path else page
            fragment=unquote(parts.fragment)
            if target!=config['bib_page'] or not fragment.startswith('ref-'):continue
            route=dict(url=page+'#'+anchor,title=chapter['title'])
            uses=routes.setdefault(fragment,[])
            if route not in uses:uses.append(route)
    return routes


def return_links(uses, page):
    counts=Counter(use['title'] for use in uses);positions=Counter()
    count=len(uses)
    body='<details class="reference-uses"><summary>Cited in this paper ('+str(count)+' '+('passage' if count==1 else 'passages')+')</summary><ul>'
    for use in uses:
        positions[use['title']]+=1
        label=use['title']+(' · passage '+str(positions[use['title']]) if counts[use['title']]>1 else '')
        path,fragment=use['url'].split('#',1)
        target=posixpath.relpath(path,posixpath.dirname(page))+'#'+fragment
        body+='<li><a href="'+html.escape(target,quote=True)+'">'+html.escape(label)+'</a></li>'
    return body+'</ul></details>'


def add_reference_routes(reader, book):
    config=book['config']
    if not re.fullmatch(r'paper-[ivx]+',config['work']):return
    site=reader.site;page=config['bib_page']
    load=lambda path:(site.output/path).read_text(encoding='utf-8')
    routes=citation_routes(load,config)
    markup=load(page);references=ReadingMarkup(markup).references
    unknown=set(routes)-set(references)
    if unknown:raise ValueError('Citation has no bibliography entry: '+str(sorted(unknown)))
    for offset,links in sorted(((references[key],return_links(uses,page)) for key,uses in routes.items()),reverse=True):
        markup=markup[:offset]+links+markup[offset:]
    site.write(page,markup)


def verify(root, pages):
    import json
    sequences=json.loads((root/'documents/reading-navigation.json').read_bytes())
    books=references=passages=figures=0
    load=lambda path:(root/path).read_text(encoding='utf-8')
    for work,record in sequences.items():
        if not re.fullmatch(r'paper-[ivx]+',work):continue
        page='read/'+work+'/references.html'
        config=dict(chapters=record['entries'],bib_page=page)
        routes=citation_routes(load,config)
        for chapter in config['chapters']:
            if chapter['url']==page:continue
            text=load(chapter['url'])
            expected=sum(any(image.get('src') and not urlsplit(image['src']).scheme and not urlsplit(image['src']).netloc for image in images)
                         for _,images in ReadingMarkup(text).figures)
            assert text.count('class="reading-figure-actions"')==expected,('Missing full-size figure access',chapter['url'])
            figures+=expected
        markup=load(page);entries=ReadingMarkup(markup).references
        assert set(routes)<=set(entries),('Missing bibliography reference',work)
        assert markup.count('class="reference-uses"')==len(routes),('Incorrect citation return groups',work)
        for key,uses in routes.items():
            links=return_links(uses,page)
            assert markup[:entries[key]].endswith(links),('Citation returns in the wrong entry',work,key)
            for use in uses:
                path,fragment=use['url'].split('#',1)
                assert fragment in pages[path].ids,('Missing citation passage',use)
            passages+=len(uses)
        books+=1;references+=len(entries)
    return dict(papers=books,references=references,citing_passages=passages,figure_controls=figures)
