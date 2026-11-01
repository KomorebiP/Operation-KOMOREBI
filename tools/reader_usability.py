"""Shared reading controls that retain manuscript text and mathematics."""
import html
import posixpath
import re


def enhance(body, page):
    from readable_chapters import BOOKS
    from reading_navigation import Navigation
    match = re.fullmatch(r'read/(paper-[ivx]+)/[^/]+\.html', page)
    if not match or match[1] not in BOOKS:
        return body, False
    work = match[1]
    config = BOOKS[work]
    is_index = page == config['index']
    if not is_index and 'id="chapter-text"' not in body:
        return body, False
    from reading_links import figure_controls
    body=figure_controls(body)
    e = html.escape
    def relative(target):
        return e(posixpath.relpath(target, posixpath.dirname(page)), quote=True)
    controls = ('<div class="reading-collection-nav"><a href="'+relative('read/index.html')+'">All reading editions</a>'
                '<details class="reading-paper-menu"><summary>Switch paper</summary>'
                '<nav aria-label="Core papers"><ul>')
    for identifier, book in BOOKS.items():
        if not re.fullmatch(r'paper-[ivx]+', identifier):
            continue
        current = ' aria-current="'+('page' if is_index else 'location')+'"' if identifier == work else ''
        controls += ('<li><a href="'+relative(book['index'])+'"'+current+'><strong>'+e(book['label'])+
                     '</strong><span>'+e(book['title'])+'</span></a></li>')
    controls += '</ul></nav></details>'
    if not is_index:
        controls += ('<details class="reading-display" hidden><summary>Text settings</summary>'
                     '<div><label for="reading-text-size">Text size</label>'
                     '<select id="reading-text-size"><option value="default">Standard</option>'
                     '<option value="large">Large</option><option value="larger">Extra large</option></select>'
                     '<label for="reading-text-font">Text font</label><select id="reading-text-font">'
                     '<option value="default">Sans serif</option><option value="serif">Serif</option></select>'
                     '<p>Saved in this browser for all core-paper chapters. Browser zoom also works.</p>'
                     '<button type="button" class="reading-display-reset">Reset text settings</button></div></details>')
    controls += '</div>'
    navigation = Navigation(body).controls
    if navigation and 'class="chapter-sidebar' in body:
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
