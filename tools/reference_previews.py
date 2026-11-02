"""Audit reference destinations and publish inert excerpts of retained passages."""
from html.parser import HTMLParser
import json
import posixpath
import re
from urllib.parse import unquote,urlsplit

VOID={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
TAGS=set('p em strong code pre div span section ul ol li dl dt dd table thead tbody tfoot tr th td caption blockquote h2 h3 h4 h5 h6 a br sub sup figcaption'.split())
SKIP={'passage-links','passage-tools','reference-uses','reading-figure-actions','reading-save-passage','statement-navigation'}
CLASSES={'arithmatex','equation-number','table-scroll','source-formal-note'}


class Node:
    def __init__(self,tag='',attrs=None,parent=None):
        self.tag=tag;self.attrs=attrs or {};self.parent=parent;self.children=[]

    def walk(self):
        yield self
        for child in self.children:
            if isinstance(child,Node):yield from child.walk()

    def text(self):
        return ''.join(child.text() if isinstance(child,Node) else child for child in self.children)


class Markup(HTMLParser):
    def __init__(self,text):
        super().__init__();self.root=Node();self.stack=[self.root];self.ids={};self.references=[]
        self.feed(text)

    def handle_starttag(self,tag,attrs):
        node=Node(tag,dict(attrs),self.stack[-1]);self.stack[-1].children.append(node)
        if 'id' in node.attrs:
            if node.attrs['id'] in self.ids:raise ValueError('Duplicate reference destination '+node.attrs['id'])
            self.ids[node.attrs['id']]=node
        if tag=='a' and 'data-reference-preview' in node.attrs:self.references.append(node)
        if tag not in VOID:self.stack.append(node)

    def handle_data(self,text):self.stack[-1].children.append(text)

    def handle_endtag(self,tag):
        position=next((i for i in range(len(self.stack)-1,0,-1) if self.stack[i].tag==tag),None)
        if position is not None:del self.stack[position:]


def destination(href,page):
    parts=urlsplit(href)
    if parts.scheme or parts.netloc:
        return href if parts.scheme in {'http','https'} else None
    path=posixpath.normpath(posixpath.join(posixpath.dirname(page),unquote(parts.path))) if parts.path else page
    if path.startswith('../') or path.startswith('/'):return None
    return path+('?' +parts.query if parts.query else '')+('#'+unquote(parts.fragment) if parts.fragment else '')


def serialize(node,page,omitted):
    if isinstance(node,str):return [node]
    classes=set(node.attrs.get('class','').split())
    if classes & SKIP or node.tag in {'script','style','button','input','select','textarea','dialog','nav'}:return []
    if node.tag=='img':
        omitted.append(True)
        return [dict(tag='p',children=[node.attrs['alt']])] if node.attrs.get('alt') else []
    children=[part for child in node.children for part in serialize(child,page,omitted)]
    if node.tag not in TAGS:return children
    tag={'h2':'h3','h3':'h4','h4':'h5','h5':'h6'}.get(node.tag,node.tag)
    part=dict(tag=tag,children=children)
    if classes & CLASSES:part['classes']=' '.join(sorted(classes & CLASSES))
    for name in ('scope','colspan','rowspan'):
        if name in node.attrs:part[name]=node.attrs[name]
    if tag=='a':
        url=destination(node.attrs.get('href',''),page)
        if not url:return children
        part['url']=url
    return [part]


def make_entry(target,page,label,context):
    formulas=[node for node in target.walk() if label in node.attrs.get('data-equation-labels','').split()]
    if len(formulas)>1:raise ValueError('Ambiguous labelled equation '+page+' '+label)
    kind='equation' if formulas else 'citation' if target.attrs.get('id','').startswith('ref-') else 'passage'
    heading=next((n for n in target.walk() if n.tag in {'h2','h3','h4','h5','h6'}),None)
    title='Referenced equation' if formulas else ' '.join(heading.text().split()) if heading else 'Referenced passage'
    omitted=[]
    if formulas:
        selected=[formulas[0]]
        siblings=formulas[0].parent.children;position=siblings.index(formulas[0])
        if position+1<len(siblings) and isinstance(siblings[position+1],Node) and 'equation-number' in siblings[position+1].attrs.get('class','').split():selected.append(siblings[position+1])
    elif target.tag in {'h2','h3','h4','h5','h6'}:
        siblings=target.parent.children;position=siblings.index(target);selected=[target]
        for sibling in siblings[position+1:]:
            if isinstance(sibling,Node) and sibling.tag in {'h2','h3','h4','h5','h6'}:break
            selected.append(sibling)
    else:selected=list(target.children)
    parts=[];size=0;excerpt=target.tag in {'h2','h3','h4','h5','h6'} and not formulas
    for node in selected:
        candidate=serialize(node,page,omitted)
        length=len(json.dumps(candidate,ensure_ascii=False))
        if length and size+length>14000:excerpt=True;break
        parts.extend(candidate);size+=length
    if not parts:excerpt=True
    return dict(title=title,context=context,kind=kind,parts=parts,excerpt=excerpt or bool(omitted))


def build(load,work,pages):
    parsed={page:Markup(load(page)) for page in pages}
    entries={};links=0
    for page,markup in parsed.items():
        for link in markup.references:
            url=destination(link.attrs['href'],page)
            parts=urlsplit(url or '')
            if not url or parts.query or not parts.fragment or parts.path not in parsed or not parts.path.startswith('read/'+work+'/'):
                raise ValueError('Reference leaves its canonical paper: '+page+' '+str(url))
            target=parsed[parts.path].ids.get(parts.fragment)
            if target is None:raise ValueError('Missing reference destination: '+page+' '+url)
            label=link.attrs['data-reference-preview'];key=url+'|'+label
            entry=make_entry(target,parts.path,label,pages[parts.path])
            entry['url']=url
            if key in entries and entries[key]!=entry:raise ValueError('Inconsistent reference excerpt '+key)
            entries[key]=entry;links+=1
    return dict(version=1,work=work,pages=pages,links=links,entries=entries)


def book_pages(book):
    from readable_chapters import navigation_title
    config=book['config'];label=config['label']
    pages={config['index']:label+' contents'}
    pages.update({spec['url']:label+' · '+navigation_title(spec['title']) for spec,_,_ in book['chapters']})
    pages[config['bib_page']]=label+' references'
    pages.update({part['url']:label+' · '+navigation_title(part['title']) for part in config.get('collected_parts',[])})
    return pages


def publish(reader,book):
    work=book['config']['work']
    if not re.fullmatch(r'paper-[ivx]+',work):return
    site=reader.site
    data=build(lambda page:(site.output/page).read_text(encoding='utf-8'),work,book_pages(book))
    site.write('documents/reference-previews/'+work+'.json',json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')


def check(data,load,work,pages):
    expected=build(load,work,pages)
    assert data==expected,('Reference preview differs from retained passages',work)


def verify(root):
    from readable_chapters import BOOKS,navigation_title
    reports=json.loads((root/'documents/readable-chapters.json').read_bytes())
    books={work:config for work,config in BOOKS.items() if re.fullmatch(r'paper-[ivx]+',work)}
    assert len(books)==12,('Missing core paper configuration',len(books))
    counts=dict(papers=0,links=0,targets=0,equations=0,citations=0,excerpts=0)
    load=lambda page:(root/page).read_text(encoding='utf-8')
    directory=root/'documents/reference-previews'
    assert {path.stem for path in directory.glob('paper-*.json')}==set(books),'Missing or unexpected reference preview indexes'
    for work,config in books.items():
        path=directory/(work+'.json');label=config['label']
        data=json.loads(path.read_bytes())
        pages={config['index']:label+' contents',config['bib_page']:label+' references'}
        for report in reports:
            page=report['url']
            if not page.startswith('read/'+work+'/'):continue
            heading=next(node for node in Markup(load(page)).root.walk() if node.tag=='h1')
            title=heading.text().removeprefix(label+': ')
            pages[page]=label+' · '+navigation_title(title)
        pages.update({part['url']:label+' · '+navigation_title(part['title']) for part in config.get('collected_parts',[])})
        check(data,load,work,pages)
        counts['papers']+=1;counts['links']+=data['links'];counts['targets']+=len(data['entries'])
        for entry in data['entries'].values():
            counts['equations']+=entry['kind']=='equation';counts['citations']+=entry['kind']=='citation';counts['excerpts']+=entry['excerpt']
    assert counts['papers']==12,('Missing core reference previews',counts['papers'])
    return counts
