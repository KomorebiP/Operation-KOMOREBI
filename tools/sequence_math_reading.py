"""Minimal dependency-free renderer for mathematical Markdown reading notes.

Author: Komorebi P.
Escapes source content and renders only headings, paragraphs, lists,
links, code, and explicit TeX delimiters. Production and preview builds
use the same renderer and need no extra Python packages.
"""
from html import escape
import re


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
    source=escape(source)
    source=re.sub(r'\*\*([^*\n]+)\*\*',r'<strong>\1</strong>',source)
    for key,markup in holders:
        source=source.replace(key,markup)
    return source


def mathematical_reading_fragment(source):
    """Convert a versioned math Markdown source into safe HTML article content.

    The first h1 is omitted because the site page already supplies its h1.
    """
    result=[]
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
        result.append('<pre class="sl-math-proof-code"><code'+(
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
    return '\n'.join(result)
