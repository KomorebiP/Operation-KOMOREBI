"""Minimal dependency-free renderer for mathematical Markdown reading notes.

Author: Komorebi P.
Escapes source content and renders only headings, paragraphs, lists,
links, code, and explicit TeX delimiters. Production and preview builds
use the same renderer and need no extra Python packages.
"""
from html import escape
import re

KERNEL_EXAMPLE_COUNT = 32


def _inline(raw):
    holders=[]

    def reserve(markup):
        key="READERINLINEPLACEHOLDER"+str(len(holders))+"END"
        holders.append((key,markup))
        return key

    def link(match):
        href=match[2]
        if href=='POLYNOMIAL_HANKEL_STRUCTURE.md':
            href=('https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/'
                  'research/sequence-closed-forms/POLYNOMIAL_HANKEL_STRUCTURE.md')
        if not (href.startswith('https://') or href.startswith('http://')):
            return escape(match[0])
        return reserve('<a href="'+escape(href,quote=True)+'">'+escape(match[1])+'</a>')

    source=re.sub(r'\[([^\]\n]+)\]\(([^)\s]+)\)',link,raw)
    source=re.sub(r'\x60([^\x60\n]+)\x60',
                  lambda m:reserve('<code>'+escape(m[1])+'</code>'),source)
    source=re.sub(r'\\\((.+?)\\\)',
                  lambda m:reserve('<span class="arithmatex">'+escape(m[0])+'</span>'),source)
    source=escape(source)
    source=re.sub(r'\*\*([^*\n]+)\*\*',r'<strong>\1</strong>',source)
    for key,markup in holders:
        source=source.replace(key,markup)
    return source


def mathematical_reading_fragment(source, *, include_outline=False):
    """Convert a versioned math Markdown source into safe HTML article content.

    The first h1 is omitted because the site page already supplies its h1.
    """
    result=[]
    outline=[]
    paragraph=[]
    bullets=[]
    in_math=False
    math=[]
    in_code=False
    code=[]
    code_lang=''
    tick=chr(96)

    def flush_paragraph():
        if paragraph:
            result.append('<p>'+_inline(' '.join(paragraph).strip())+'</p>')
            paragraph.clear()

    def flush_bullets():
        if bullets:
            result.append('<ul>'+''.join('<li>'+_inline(x)+'</li>'
                                       for x in bullets)+'</ul>')
            bullets.clear()

    def flush_code():
        result.append('<pre class="sl-math-proof-code" tabindex="0" role="region" '
                      'aria-label="Scrollable code example"><code'+(
            ' class="language-'+escape(code_lang,quote=True)+'"' if code_lang else ''
        )+'>'+escape('\n'.join(code))+'</code></pre>')
        code.clear()

    h1_skipped=False
    used_ids=set()
    for line in source.splitlines():
        stripped=line.strip()
        if in_math:
            math.append(line)
            if stripped==r'\]':
                result.append('<div class="arithmatex sl-math-display" tabindex="0" '
                              'role="region" aria-label="Displayed mathematical equation">'
                              +escape('\n'.join(math))+'</div>')
                math=[]
                in_math=False
            continue
        if in_code:
            if stripped.startswith(tick*3):
                flush_code()
                in_code=False
            else:
                code.append(line)
            continue
        if stripped==r'\[':
            flush_paragraph();flush_bullets()
            math=[line];in_math=True
            continue
        if stripped.startswith(tick*3):
            flush_paragraph();flush_bullets()
            in_code=True;code_lang=stripped[3:].strip()[:32]
            continue
        if not stripped:
            flush_paragraph();flush_bullets()
            continue
        match=re.match(r'^(#{1,6})\s+(.*?)\s*$',stripped)
        if match:
            flush_paragraph();flush_bullets()
            level=min(4,max(2,len(match[1])))
            if len(match[1])==1 and not h1_skipped:
                h1_skipped=True
                continue
            name=re.sub(r'[^a-z0-9]+','-',match[2].lower()).strip('-')[:80]
            name='math-proof-'+(name or 'section')
            base=name;i=2
            while name in used_ids:
                name=base+'-'+str(i);i+=1
            used_ids.add(name)
            result.append(f'<h{level} id="{name}">'+_inline(match[2])+f'</h{level}>')
            if level<=3:
                outline.append('<li'+(' class="sl-proof-subsection"' if level==3 else '')+
                               '><a href="#'+name+'">'+_inline(match[2])+'</a></li>')
            continue
        if stripped.startswith('- '):
            flush_paragraph()
            bullets.append(stripped[2:])
            continue
        flush_bullets()
        paragraph.append(stripped)
    if in_math:
        raise ValueError('Unclosed TeX display in mathematical source')
    if in_code:
        raise ValueError('Unclosed fenced code block in mathematical source')
    flush_paragraph();flush_bullets()
    if include_outline and outline:
        result.insert(0,'<details class="sl-proof-outline"><summary>On this page</summary>'
                        '<nav aria-label="Proof sections"><ul>'+''.join(outline)+
                        '</ul></nav></details>')
    return '\n'.join(result)


def mathematical_example_gallery(source):
    """Render the source examples as native, keyboard-operable disclosures.

    Equations remain in the static HTML, including when JavaScript is disabled.
    The source heading order is checked so a missing example fails the build.
    """
    headings=list(re.finditer(r'^## Example (\d+)\. (.+)$',source,re.MULTILINE))
    if [int(item[1]) for item in headings]!=list(range(1,KERNEL_EXAMPLE_COUNT+1)):
        raise ValueError('The algebraic-kernel gallery must contain examples 1 through '+str(KERNEL_EXAMPLE_COUNT))
    groups={
        1:('kernel-classical','Classical and multistep kernels',
           'Examples 1–6 change the coefficient kernel itself.'),
        7:('kernel-dyadic','Two-position blocks',
           'Examples 7–13 develop the original family and its special parameters.'),
        14:('kernel-blocks','Larger blocks and independent weights',
            'Examples 14–20 use three, four, and five positions per block.'),
        21:('kernel-weighted','Polynomial and Fibonacci weights',
            'Examples 21–23 weight the block index beyond a single geometric factor.'),
        24:('kernel-polynomial','Higher polynomial weights',
            'Examples 24–25 use square and falling-factorial weights.'),
        26:('kernel-recurrence','Recurrence and periodic weights',
            'Examples 26–32 include Lucas and Pell numbers, periodic selection, finite support, and mixed weights.'),
    }
    parts=[
        '<section id="kernel-examples" class="sl-math-manuscript sl-kernel-gallery" '
        'aria-labelledby="kernel-examples-heading">',
        '<h2 id="kernel-examples-heading">'+str(KERNEL_EXAMPLE_COUNT)+' worked examples</h2>',
        mathematical_reading_fragment(source[:headings[0].start()]),
        '<nav class="sl-binomial-jumps" aria-label="Example groups">'
        +''.join('<a href="#'+key+'">'+title+'</a>'
                 for key,title,_ in groups.values())+'</nav>',
        '<div class="sl-example-controls" hidden>'
        '<button type="button" data-example-action="open">Expand all examples</button>'
        '<button type="button" data-example-action="close">Collapse all examples</button>'
        '</div>',
    ]
    for index,heading in enumerate(headings):
        number=int(heading[1])
        if number in groups:
            if index:
                parts.append('</section>')
            key,title,description=groups[number]
            parts.append('<section class="sl-example-group" aria-labelledby="'+key+'">'
                         '<h3 id="'+key+'">'+title+'</h3><p>'+description+'</p>')
        end=headings[index+1].start() if index+1<len(headings) else len(source)
        body=source[heading.end():end].strip()
        parts.append(
            '<details id="kernel-example-'+str(number)+'" class="sl-kernel-example">'
            '<summary><span class="sl-example-number">Example '+str(number)+'</span> '
            +_inline(heading[2])+'</summary>'
            '<div class="sl-example-body">'
            +mathematical_reading_fragment(body)
            +'<p class="sl-example-permalink"><a href="#kernel-example-'+str(number)+'">'
             'Link to this example</a></p></div></details>')
    parts.append('</section></section>')
    return '\n'.join(parts)
