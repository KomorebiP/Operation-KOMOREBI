"""Consistent reading chrome around unchanged manuscript articles."""
import html
from html.parser import HTMLParser
import posixpath
import re


def take_block(source, tag, class_name):
    """Extract one generated wrapper while preserving its nested markup exactly."""
    class Block(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=False)
            self.lines=[0]+[i+1 for i,c in enumerate(source) if c=='\n']
            self.start=self.end=None
            self.depth=0
        def position(self):
            line,column=self.getpos()
            return self.lines[line-1]+column
        def handle_starttag(self, name, attrs):
            if name!=tag or self.end is not None:return
            if self.depth:self.depth+=1
            elif class_name in dict(attrs).get('class','').split():
                self.start=self.position();self.depth=1
        def handle_endtag(self, name):
            if name!=tag or not self.depth:return
            self.depth-=1
            if not self.depth:self.end=source.index('>',self.position())+1
    parser=Block();parser.feed(source)
    if parser.end is None:return source,''
    return source[:parser.start]+source[parser.end:],source[parser.start:parser.end]


def heading_text(markup):
    class Text(HTMLParser):
        def __init__(self):
            super().__init__();self.parts=[]
        def handle_data(self,data):self.parts.append(data)
    parser=Text();parser.feed(markup)
    return ' '.join(''.join(parser.parts).split())


def has_statement_finder(config):
    return bool(re.fullmatch(r'paper-[ivx]+',config['work']) or config.get('statement_navigation'))


def edition(path):
    from readable_chapters import BOOKS,statement_directory_url
    match=re.fullmatch(r'read/([a-z0-9-]+)/[^/]+\.html',path)
    if not match or match[1] not in BOOKS:return None
    config=BOOKS[match[1]]
    pages={config['index'],*[c['url'] for c in config['chapters']]}
    if config.get('bib_page'):pages.add(config['bib_page'])
    if has_statement_finder(config):pages.add(statement_directory_url(config))
    return config if path in pages else None


def standardize(body,path):
    """Move only generated heading and action wrappers, leaving the article intact."""
    library=path=='read/index.html'
    config=dict(label='HTML reading editions',index=path,work='library') if library else edition(path)
    if not config:return body
    from readable_chapters import statement_directory_url
    article=body.find('<article id="chapter-text"')
    limit=article if article>=0 else len(body)
    heading=re.search(r'<h1\b[^>]*>.*?</h1>',body[:limit],re.S)
    if not heading:return body
    before=body[:heading.start()];after=body[heading.end():]
    eyebrow=re.search(r'<p class="eyebrow">.*?</p>\s*$',before,re.S)
    if eyebrow:before=before[:eyebrow.start()]
    before,reader_controls=take_block(before,'div','reading-collection-nav')
    title=heading[0]
    prefix=html.escape(config['label'])+': '
    title=re.sub(r'(<h1\b[^>]*>)'+re.escape(prefix),r'\1',title,count=1)
    if path==config.get('bib_page'):
        title=re.sub(r'(<h1\b[^>]*>).*?(</h1>)',r'\1References\2',title,flags=re.S)
    context=('' if library else 'Contents' if path==config['index'] else 'Statements and proofs' if path==statement_directory_url(config)
             else 'References' if path==config.get('bib_page') else 'Reading edition')
    actions=[]
    # Both wrappers are generated before the manuscript article and contain no
    # nested wrappers of their own tag. Never select controls inside a passage.
    front_end=after.find('<article id="chapter-text"')
    front_end=front_end if front_end>=0 else len(after)
    front,tail=after[:front_end],after[front_end:]
    first_heading=re.match(r'<article id="chapter-text"[^>]*>\s*(<h2\b[^>]*>.*?</h2>)',tail,re.S)
    first_title=heading_text(first_heading[1]) if first_heading else ''
    if first_title and heading_text(title)==first_title:
        front=front.replace('<div class="chapter-reading">','<div class="chapter-reading has-repeated-title">',1)
    for pattern in (r'<div class="reading-save"[^>]*>.*?</div>',r'<p class="side-launch">.*?</p>'):
        match=re.search(pattern,front,re.S)
        if match:actions.append(match[0]);front=front[:match.start()]+front[match.end():]
    if reader_controls:
        primary=[];tools=[reader_controls]
        for action in actions:
            if action.startswith('<p class="side-launch">'):
                tools.append(action);continue
            saved=re.search(r'<a\b[^>]*\bdata-saved-reading-link\b[^>]*>.*?</a>',action,re.S)
            if saved:
                tools.append('<p class="reading-tools-saved">'+saved[0]+'</p>')
                action=action[:saved.start()]+action[saved.end():]
            primary.append(action)
        primary.append('<details class="reading-page-tools"><summary>Reading tools</summary>'
                       '<div class="reading-page-tools-panel">'+''.join(tools)+'</div></details>')
        actions=primary
    target=html.escape(posixpath.relpath(config['index'],posixpath.dirname(path)),quote=True)
    header=('<header class="reading-page-header"><p class="eyebrow"><a href="'+target+'">'+html.escape(config['label'])+
            '</a>'+('<span aria-hidden="true"> · </span><span>'+context+'</span>' if context else '')+'</p>'+title+
            ('<div class="reading-actions">'+''.join(actions)+'</div>' if actions else '')+'</header>')
    return before+header+front+tail
