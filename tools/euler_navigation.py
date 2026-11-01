"""A compact, complete reading guide for the extended Euler worked example."""
import html
from html.parser import HTMLParser
import re


PARTS = (
    ('Packets and exact reconstruction', 'conventions-and-coordinate-systems'),
    ('Polynomial and local coordinates', 'turn-the-reciprocal-calculation-into-parameter-polynomials'),
    ('Matrices, congruences, and residuals', 'state-the-supercongruences-and-check-an-euler-index-shift'),
    ('Polyphase and filter taps', 'change-from-series-coefficients-to-sequence-differences'),
    ('Euler and Fibonacci coordinates', 'change-euler-polynomials-to-fibonacci-coordinates'),
    ('Quartic and logarithmic coordinates', 'work-with-all-four-quartic-addresses'),
    ('Checks, downloads, and sources', 'run-the-exact-checks'),
)
TAP_SECTION = 'split-an-fir-filter-into-polyphase-taps'


def headings(markup):
    class Headings(HTMLParser):
        def __init__(self):
            super().__init__(); self.current = None; self.items = []
        def handle_starttag(self, tag, attrs):
            if tag == 'h2':
                self.current = [dict(attrs).get('id'), []]
        def handle_data(self, data):
            if self.current is not None:
                self.current[1].append(data)
        def handle_endtag(self, tag):
            if tag == 'h2' and self.current is not None:
                identifier, text = self.current
                if not identifier:
                    raise ValueError('An Euler section is missing its anchor')
                self.items.append((identifier, ' '.join(''.join(text).split())))
                self.current = None
    parser = Headings(); parser.feed(markup)
    if len(parser.items) != len({identifier for identifier, _ in parser.items}):
        raise ValueError('Euler section anchors must be unique')
    return parser.items


def decorate(markup):
    sections = headings(markup)
    ids = [identifier for identifier, _ in sections]
    required = [start for _, start in PARTS]+[TAP_SECTION]
    if any(identifier not in ids for identifier in required):
        raise ValueError('An Euler reading-guide destination is missing')
    starts = [ids.index(start) for _, start in PARTS]
    if starts[0] != 0 or starts != sorted(set(starts)):
        raise ValueError('Euler reading parts must follow the manuscript order')
    e = html.escape
    groups = []
    for index, ((title, start), first, last) in enumerate(zip(PARTS, starts, starts[1:]+[len(ids)])):
        items = sections[first:last]
        links = ''.join('<li><a href="#'+e(identifier, quote=True)+'">'+e(label)+'</a></li>' for identifier, label in items)
        groups.append('<details class="euler-part-menu"><summary><span class="euler-part-number" aria-hidden="true">'+str(index+1).zfill(2)+
                      '</span><span>'+e(title)+'</span><small>'+str(len(items))+' sections</small></summary><ol>'+links+'</ol></details>')
    guide = ('<nav class="euler-reading-guide" id="euler-reading-guide" aria-label="Euler example reading guide">'
             '<div class="euler-shortcuts"><a href="#'+PARTS[0][1]+'">Read from the beginning <span aria-hidden="true">↓</span></a>'
             '<a href="#'+TAP_SECTION+'">Polyphase / tap example</a><a href="#run-the-exact-checks">Checks &amp; downloads</a></div>'
             '<details class="euler-contents"><summary>Browse the seven parts <span>'+str(len(ids))+' sections</span></summary>'
             '<div class="euler-parts">'+''.join(groups)+'</div></details></nav>')
    for index in range(len(PARTS)-1, -1, -1):
        title, start = PARTS[index]
        label = '<p class="euler-part-label">Part '+str(index+1)+' <span aria-hidden="true">/</span> '+e(title)+'</p>'
        before = ''
        if index:
            before = part_navigation(index-1)
        pattern = r'(<h2\s+id="'+re.escape(start)+r'"[^>]*>)'
        markup, count = re.subn(pattern, lambda match: before+label+match[1], markup, count=1)
        if count != 1:
            raise ValueError('Cannot place an Euler part boundary: '+start)
    # Keep the date line before the guide; its native disclosure is closed initially.
    date = re.search(r'<p><strong>.*?</strong></p>', markup, re.S)
    if date:
        byline = date[0].replace('<p>', '<p class="euler-byline">', 1)
        markup = markup[:date.start()]+byline+guide+markup[date.end():]
    else:
        markup = guide+markup
    return markup+part_navigation(len(PARTS)-1)


def part_navigation(index):
    e = html.escape
    links = []
    if index:
        title, target = PARTS[index-1]
        links.append('<a href="#'+target+'"><small>← Previous part</small><span>'+e(title)+'</span></a>')
    links.append('<a class="euler-guide-return" href="#euler-reading-guide">Reading guide ↑</a>')
    if index+1 < len(PARTS):
        title, target = PARTS[index+1]
        links.append('<a class="euler-next-part" href="#'+target+'"><small>Next part →</small><span>'+e(title)+'</span></a>')
    return '<nav class="euler-part-navigation" aria-label="Navigation after part '+str(index+1)+'">'+''.join(links)+'</nav>'
