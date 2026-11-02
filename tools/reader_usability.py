"""Shared reading controls that retain manuscript text and mathematics."""
import html
import posixpath
import re


def enhance(body, page):
    from readable_chapters import BOOKS,statement_directory_url
    from reading_navigation import Navigation
    from reader_display import edition,has_statement_finder
    config=edition(page)
    if not config:return body,False
    work=config['work']
    is_index = page == config['index']
    is_directory = page == statement_directory_url(config)
    if not is_index and not is_directory and 'id="chapter-text"' not in body:
        return body, False
    from reading_links import figure_controls
    body=figure_controls(body)
    e = html.escape
    def relative(target):
        return e(posixpath.relpath(target, posixpath.dirname(page)), quote=True)
    controls = '<div class="reading-collection-nav"><a href="'+relative('read/index.html')+'">Reading library</a>'
    if is_directory:controls+='<a href="'+relative(config['index'])+'">Contents</a>'
    elif has_statement_finder(config):controls+='<a href="'+relative(statement_directory_url(config))+'">Find statements</a>'
    controls+='<details class="reading-paper-menu"><summary>Switch work</summary><nav aria-label="Reading editions">'
    for group,core in [('Core papers',True),('Books and monographs',False)]:
        controls+='<section><h2>'+group+'</h2><ul>'
        for identifier,book in BOOKS.items():
            if bool(re.fullmatch(r'paper-[ivx]+',identifier))!=core:continue
            current = ' aria-current="'+('page' if is_index or is_directory else 'location')+'"' if identifier == work else ''
            target=statement_directory_url(book) if is_directory and has_statement_finder(book) else book['index']
            controls+='<li><a href="'+relative(target)+'"'+current+'><strong>'+e(book['label'])+'</strong><span>'+e(book['title'])+'</span></a></li>'
        controls+='</ul></section>'
    controls+='</nav></details>'
    if not is_index and not is_directory:
        controls += ('<details class="reading-display" hidden><summary>Text settings</summary>'
                     '<div><label for="reading-text-size">Text size</label>'
                     '<select id="reading-text-size"><option value="default">Standard</option>'
                     '<option value="large">Large</option><option value="larger">Extra large</option></select>'
                     '<label for="reading-text-font">Text font</label><select id="reading-text-font">'
                     '<option value="default">Sans serif</option><option value="serif">Serif</option></select>'
                     '<p>Saved in this browser for reading chapters. Browser zoom also works.</p>'
                     '<button type="button" class="reading-display-reset">Reset text settings</button></div></details>')
    controls += '</div>'
    parsed = Navigation(body);navigation = parsed.controls
    if navigation and 'class="chapter-sidebar' in body and not parsed.returns:
        links = navigation[0]['links']
        previous = next(link for link in links if 'reading-previous' in link.get('class', '').split())
        following = next(link for link in links if 'reading-next' in link.get('class', '').split())
        shortcut = '<nav class="reading-shortcuts" aria-label="Keep reading">'
        for link, label in ((previous, '← Contents' if previous.get('rel')=='contents' else '← Previous'),
                            (dict(href=posixpath.relpath(config['index'],posixpath.dirname(page)),
                                  **{'aria-label': 'All chapters in '+config['label']}), 'Chapters'),
                            (following, 'Contents →' if following.get('rel')=='contents' else 'Next →')):
            shortcut += '<a href="'+e(link['href'],quote=True)+'" aria-label="'+e(link['aria-label'],quote=True)+'">'+label+'</a>'
        shortcut += '</nav>'
        body = re.sub(r'(<aside\b[^>]*class="chapter-sidebar\b.*?)(</aside>)',
                      lambda m:m[1]+shortcut+m[2],body,count=1,flags=re.S)
    return controls+body, True
