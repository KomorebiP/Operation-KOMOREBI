"""Consistent reading chrome around unchanged manuscript articles."""
import html
import posixpath
import re


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
    for pattern in (r'<div class="reading-save"[^>]*>.*?</div>',r'<p class="side-launch">.*?</p>'):
        match=re.search(pattern,front,re.S)
        if match:actions.append(match[0]);front=front[:match.start()]+front[match.end():]
    target=html.escape(posixpath.relpath(config['index'],posixpath.dirname(path)),quote=True)
    header=('<header class="reading-page-header"><p class="eyebrow"><a href="'+target+'">'+html.escape(config['label'])+
            '</a>'+('<span aria-hidden="true"> · </span><span>'+context+'</span>' if context else '')+'</p>'+title+
            ('<div class="reading-actions">'+''.join(actions)+'</div>' if actions else '')+'</header>')
    return before+header+front+tail
