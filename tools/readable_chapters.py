"""A deliberately bounded, source-preserving TeX reading pilot for Paper II.

Unknown prose commands or environments stop the build. Mathematics remains TeX
for MathJax, with only literal zero-argument macros from the manuscript expanded.
This is presentation tooling, not a mathematical review or a general TeX engine.
"""
import hashlib
import html
import json
import re

BASE = 'papers/paper-ii/current/editable/traditional/'
SOURCE = BASE+'chapters/02_coordinates.tex'
MAIN = BASE+'Paper_II_Traditional_Final.tex'
BIB = BASE+'Paper_II_Traditional_Final.bbl'
PAGE = 'read/paper-ii/refinement-and-residue-coordinates.html'
TITLE = 'Paper II: Refinement and residue coordinates'
NUMBERED = {'definition', 'theorem', 'proposition', 'lemma', 'corollary', 'remark', 'example'}
PANELS = {'keyidea': 'The central idea', 'interpretation': 'How to read the result'}
MACROS = {'Pcal', 'Qcal', 'Rcal', 'Acal', 'Scal', 'cA', 'cS', 'End', 'id', 'bbk'}
# Search aliases describe notation, not new equivalences between mathematical claims.
SYMBOLS = {'alpha': 'α', 'beta': 'β', 'gamma': 'γ', 'rho': 'ρ', 'omega': 'ω',
           'eta': 'η', 'delta': 'δ', 'ell': 'ℓ', 'sum': 'sum', 'bigoplus': 'direct sum',
           'oplus': 'direct sum', 'subseteq': 'subset', 'in': 'in', 'longrightarrow': 'maps to',
           'to': 'maps to', 'leftarrow': 'from', 'circ': 'composition', 'equiv': 'congruent',
           'ne': 'not equal', 'le': 'less than or equal', 'leq': 'less than or equal',
           'geq': 'greater than or equal', 'pmod': 'modulo', 'bmod': 'modulo'}


def clean_tex(text):
    # Retain newlines for exact links to the unchanged source file.
    return re.sub(r'(?<!\\)%[^\n]*', '', text)


def group(text, start, opening='{', closing='}'):
    if start >= len(text) or text[start] != opening:
        raise ValueError('Expected '+opening+' at '+str(start))
    depth = 1
    i = start+1
    while i < len(text):
        if text[i] == '\\':
            i += 2
            continue
        if text[i] == opening: depth += 1
        if text[i] == closing: depth -= 1
        if not depth: return text[start+1:i], i+1
        i += 1
    raise ValueError('Unclosed group')


def manuscript_macros(main):
    result = {}
    for m in re.finditer(r'\\(newcommand|providecommand)\{\\([A-Za-z]+)\}', main):
        if m[2] not in MACROS or m[2] in result: continue
        value, _ = group(main, m.end())
        if '#' in value: raise ValueError('Argument macro is outside the reading pilot')
        result[m[2]] = value
    if set(result) != MACROS: raise ValueError('Missing manuscript macro definitions')
    return result


def expand_math(tex, macros):
    for _ in range(10):
        expanded = re.sub(r'\\([A-Za-z]+)', lambda m: '{'+macros[m[1]]+'}' if m[1] in macros else m[0], tex)
        if expanded == tex: return tex
        tex = expanded
    raise ValueError('Recursive manuscript macro')


def plain_math(tex):
    names = []
    def replace(m):
        name = m[1]
        if name in SYMBOLS:
            names.append(name)
            return ' '+SYMBOLS[name]+' '
        return ' '+({'Pcal':'P','Qcal':'Q','Rcal':'R','Acal':'A','Scal':'S',
                     'cA':'A','cS':'S','bbk':'k','End':'End','id':'id'}.get(name, name))+' '
    text = re.sub(r'\\([A-Za-z]+)', replace, tex)
    return re.sub(r'\s+', ' ', re.sub(r'[{}_^\\]', ' ', text)).strip(), ' '.join(names)


class Chapter:
    def __init__(self, text, macros, section_offset=0):
        self.text = clean_tex(text)
        self.macros = macros
        self.math = []
        self.labels = {}
        self.nodes = []
        self.references = []
        self.section = section_offset
        self.subsection = self.counter = 0
        self.parse()

    def line(self, pos): return self.text.count('\n', 0, pos)+1

    def parse(self):
        text = self.text
        pos = 0
        while pos < len(text):
            if text[pos].isspace():
                pos += 1
                continue
            start = pos
            heading = re.match(r'\\(section|subsection)\{', text[pos:])
            env = re.match(r'\\begin\{([a-z]+)\}', text[pos:])
            if heading:
                title, pos = group(text, pos+heading.end()-1)
                if heading[1] == 'section':
                    self.section += 1
                    self.subsection = self.counter = 0
                    number = str(self.section)
                else:
                    self.subsection += 1
                    number = str(self.section)+'.'+str(self.subsection)
                node = dict(kind=heading[1], title=title, number=number, body='')
            elif env:
                kind = env[1]
                if kind not in NUMBERED | set(PANELS) | {'proof', 'figure'}:
                    raise ValueError('Unsupported reading environment: '+kind)
                pos += env.end()
                title = ''
                if text[pos:pos+1] == '[': title, pos = group(text, pos, '[', ']')
                end_tag = '\\end{'+kind+'}'
                end = text.find(end_tag, pos)
                if end < 0: raise ValueError('Unclosed '+kind)
                body = text[pos:end]
                pos = end+len(end_tag)
                number = ''
                if kind in NUMBERED:
                    self.counter += 1
                    number = str(self.section)+'.'+str(self.counter)
                node = dict(kind=kind, title=title, number=number, body=body)
            else:
                match = re.search(r'\\(?:section|subsection)\{|\\begin\{(?:'+
                                  '|'.join(sorted(NUMBERED | set(PANELS) | {'proof','figure'}))+r')\}', text[pos:])
                pos = pos+match.start() if match else len(text)
                node = dict(kind='text', title='', number='', body=text[start:pos])
            # Labels immediately after headings belong to those headings.
            if heading:
                while (m := re.match(r'\s*\\label\{([^{}]+)\}', text[pos:])):
                    node['body'] += m[0]
                    pos += m.end()
            labels = re.findall(r'\\label\{([^{}]+)\}', node['body'])
            node.update(line=self.line(start), end_line=self.line(pos), id='L'+str(self.line(start)), labels=labels)
            for label in labels:
                if label in self.labels: raise ValueError('Duplicate chapter label '+label)
                self.labels[label] = node
            self.nodes.append(node)
        # Discover all references before rendering so unknown references fail closed.
        for node in self.nodes:
            for keys in re.findall(r'\\(?:c|C|eq)?ref\{([^{}]+)\}', node['body']):
                for key in keys.split(','):
                    if key not in self.labels: raise ValueError('Unresolved chapter reference: '+key)

    def inline(self, text):
        out = []
        pos = 0
        while pos < len(text):
            if text[pos] == '$' or text.startswith('\\[', pos):
                display = text.startswith('\\[', pos)
                opening, closing = ('\\[','\\]') if display else ('$','$')
                end = text.find(closing, pos+len(opening))
                if end < 0: raise ValueError('Unclosed math')
                tex = text[pos+len(opening):end]
                self.math.append(tex)
                tag = 'div' if display else 'span'
                extra = ' tabindex="0" role="group" aria-label="Displayed equation. Scroll horizontally if needed."' if display else ''
                out.append('<'+tag+' class="arithmatex"'+extra+'>'+html.escape(
                    ('\\[' if display else '\\(')+expand_math(tex,self.macros)+('\\]' if display else '\\)'))+'</'+tag+'>')
                pos = end+len(closing)
            elif text[pos] == '\\':
                m = re.match(r'\\([A-Za-z]+)', text[pos:])
                if not m: raise ValueError('Unsupported prose escape at '+text[pos:pos+40])
                name = m[1]
                pos += m.end()
                value, pos = group(text, pos)
                if name == 'label': continue
                if name in {'textbf','emph','textit'}:
                    tag = 'strong' if name == 'textbf' else 'em'
                    out.append('<'+tag+'>'+self.inline(value)+'</'+tag+'>')
                elif name in {'cref','Cref','ref','eqref'}:
                    links = []
                    for key in value.split(','):
                        node = self.labels[key]
                        label = node['kind'].capitalize()+' '+node['number']
                        links.append('<a href="#'+node['id']+'" title="'+html.escape(node['title'],quote=True)+'">'+label+'</a>')
                    out.append(', '.join(links))
                    self.references.extend(value.split(','))
                elif name == 'cite':
                    links = []
                    for key in value.split(','):
                        number, url = self.citations[key]
                        links.append('<a href="'+html.escape(url,quote=True)+'" aria-label="Reference '+str(number)+': '+html.escape(key,quote=True)+'">['+str(number)+']</a>')
                    out.append(', '.join(links))
                else: raise ValueError('Unsupported prose command: '+name)
            else:
                m = re.match(r'[^$\\]+', text[pos:])
                literal = m[0]
                if '{' in literal or '}' in literal: raise ValueError('Unparsed prose grouping')
                out.append(html.escape(re.sub(r'\s+', ' ', literal).replace('~','\u00a0')))
                pos += len(literal)
        return ''.join(out)

    def paragraphs(self, text):
        # Separate paragraphs outside math. A display splits paragraph elements,
        # but its exact mathematical source is passed unchanged to inline().
        chunks = re.split(r'(\\\[.*?\\\])', re.sub(r'\\label\{[^{}]+\}', '', text), flags=re.S)
        out = []
        for chunk in chunks:
            if chunk.startswith('\\['): out.append(self.inline(chunk))
            else:
                out.extend('<p>'+self.inline(p.strip())+'</p>' for p in re.split(r'\n\s*\n',chunk) if p.strip())
        return ''.join(out)

    def preview(self, text):
        """Return inert text/math pieces, keeping formulas intact at the excerpt boundary."""
        text = re.sub(r'\\label\{[^}]+\}', '', text).strip()
        def reference(match):
            return ', '.join(self.labels[key]['kind']+' '+self.labels[key]['number'] for key in match[1].split(','))
        text = re.sub(r'\\(?:c|C|eq)?ref\{([^}]+)\}', reference, text)
        text = re.sub(r'\\cite\{([^}]+)\}',lambda m:', '.join('['+str(self.citations[k][0])+']' for k in m[1].split(',')),text)
        parts = []
        size = 0
        for part in re.split(r'(\$.*?\$)',text,flags=re.S):
            if not part: continue
            math = part.startswith('$')
            value = expand_math(part[1:-1],self.macros) if math else re.sub(r'\s+',' ',part)
            if math and size+len(value)>400: break
            if not math and size+len(value)>400: value=value[:max(0,400-size)].rsplit(' ',1)[0]+'…'
            parts.append(dict(type='math' if math else 'text',text=value))
            size += len(value)
            if size>=400 or value.endswith('…'): break
        return parts


def readable_url(path, line=None):
    if path != SOURCE: return None
    return PAGE+('#L'+str(line) if line else '')


def prepare(reader):
    if SOURCE not in reader.records: raise ValueError('Missing Paper II pilot source')
    # The bbl is the manuscript's retained, ordered bibliography, not a new citation list.
    reader.add(BIB, 'Paper II bibliography source')


def render(reader):
    site = reader.site
    raw = site.read_source(reader.records[SOURCE])
    main = site.read_source(reader.records[MAIN]).decode('utf-8-sig')
    preceding = site.read_source(reader.records[BASE+'chapters/01_orientation.tex']).decode('utf-8-sig')
    macros = manuscript_macros(main)
    chapter = Chapter(raw.decode('utf-8-sig'), macros, len(re.findall(r'\\section\{',clean_tex(preceding))))
    bib = site.read_source(reader.records[BIB]).decode('utf-8-sig')
    chapter.citations = {m[1]:(i,reader.resolve(BIB,PAGE,'L'+str(bib.count('\n',0,m.start())+1)))
                         for i,m in enumerate(re.finditer(r'\\bibitem\{([^}]+)\}',bib),1)}
    rows = {r['statement_line']:r for r in reader.claims_by_source[SOURCE]}
    proof_rows = {r['proof_line']:r for r in rows.values() if r['proof_line']}
    e = html.escape
    headings = [n for n in chapter.nodes if n['kind'] in {'section','subsection'}]
    section_order = {n['id']:i for i,n in enumerate(headings)}
    toc = '<nav class="chapter-contents" aria-label="Chapter contents"><h2 id="contents">Contents</h2><ol>'
    toc += ''.join('<li'+(' class="subsection-entry"' if n['kind']=='subsection' else '')+'><a href="#'+n['id']+'">'+n['number']+' '+e(n['title'])+'</a></li>' for n in headings)+'</ol></nav>'
    previous = reader.resolve(BASE+'chapters/01_orientation.tex',PAGE)
    following = reader.resolve(BASE+'chapters/03_weighted.tex',PAGE)
    chapter_nav = '<nav class="chapter-neighbours" aria-label="Neighbouring manuscript chapters"><a href="'+previous+'">Previous chapter: Orientation (source)</a><a href="#contents">Chapter contents</a><a href="'+following+'">Next chapter: Weighted transfer (source)</a></nav>'
    body = '<p class="eyebrow">Readable chapter pilot</p><h1>'+TITLE+'</h1>'
    body += '<p>This reading view follows sections 3 and 4 of the retained Paper II manuscript. The wording and equations come from that source. This format does not add a proof review or extend Lean coverage.</p>'
    body += reader.work_routes('paper-ii',PAGE)+chapter_nav
    body += '<p><a href="'+reader.resolve(SOURCE,PAGE)+'">Original TeX with line links</a> · <a href="'+site.rel(reader.records[SOURCE]['file_url'],PAGE)+'" download>Download TeX</a></p>'
    body += '<p>Equations can be explored through the MathJax context menu. Long equations have their own keyboard-scrollable region. The PDF and source remain available if a formula does not display.</p>'+toc
    body += '<article class="readable-chapter" aria-label="Paper II manuscript sections 3 and 4">'
    report_nodes = []
    for node in chapter.nodes:
        kind = node['kind']
        label = (node['number']+' '+node['title']).strip() if kind in {'section','subsection'} else (kind.capitalize()+' '+node['number']+(': '+node['title'] if node['title'] else '')).strip()
        source_link = reader.resolve(SOURCE,PAGE,'L'+str(node['line']))
        links = '<a href="#'+node['id']+'">Permalink</a> · <a href="'+source_link+'">Source line '+str(node['line'])+'</a>'
        if kind in {'section','subsection'}:
            level = '2' if kind=='section' else '3'
            body += '<h'+level+' id="'+node['id']+'">'+e(label)+'</h'+level+'>'
            index = section_order[node['id']]
            links += ' · <a href="#contents">Contents</a>'
            if index: links += ' · <a href="#'+headings[index-1]['id']+'">Previous section</a>'
            if index+1<len(headings): links += ' · <a href="#'+headings[index+1]['id']+'">Next section</a>'
            body += '<nav class="passage-links" aria-label="Section navigation">'+links+'</nav>'
        elif kind=='figure':
            # Parse the complete figure grammar, rejecting any unhandled content.
            m = re.match(r'\s*\\centering\s*\\includegraphics\[width=0\.96\\textwidth\]\{([^}]+)\}\s*\\caption',node['body'])
            if not m: raise ValueError('Unsupported figure')
            caption, end = group(node['body'],m.end())
            tail = re.sub(r'\\label\{[^}]+\}','',node['body'][end:]).strip()
            if tail: raise ValueError('Unhandled figure content')
            path = BASE+'figures/'+m[1].removesuffix('.pdf')+'.png'
            image = reader.image_url(path,PAGE)
            if not image: raise ValueError('Missing receipt-bound figure '+path)
            caption_html = chapter.inline(caption)
            body += '<figure id="'+node['id']+'"><img src="'+image+'" alt="'+e(plain_math(caption.replace('$',''))[0],quote=True)+'" loading="lazy"><figcaption>'+caption_html+'</figcaption><p class="passage-links">'+links+'</p></figure>'
        else:
            row = rows.get(node['line']) or proof_rows.get(node['line'])
            if row:
                links += ' · <a href="'+site.rel('claims.html',PAGE)+'#'+row['id'].lower()+'">Claim record</a>'
                other = row['statement_line'] if kind=='proof' else row['proof_line']
                if other: links += ' · <a href="#L'+str(other)+'">'+('Back to statement' if kind=='proof' else 'Read proof')+'</a>'
            body += '<section id="'+node['id']+'" class="reading-block '+kind+'">'
            if kind!='text':
                if kind in PANELS: label = PANELS[kind]
                if kind=='proof' and row: label = 'Proof of '+row['title']
                level = '4' if any(n['kind']=='subsection' and n['line']<node['line'] and n['number'].split('.')[0]==str(chapter_section(chapter,node)) for n in headings) else '3'
                body += '<h'+level+'>'+e(label)+'</h'+level+'>'
            body += chapter.paragraphs(node['body'])
            body += '<p class="passage-links">'+links+'</p></section>'
            plain, aliases = plain_math(re.sub(r'\\label\{[^}]+\}', '',node['body']).replace('$',''))
            # A bounded verbatim mathematical excerpt, never a generated paraphrase.
            preview_match = re.search(r'\\\[(.*?)\\\]',node['body'],re.S)
            math_preview = expand_math(preview_match[1],macros).strip() if preview_match else ''
            snippet = re.split(r'\\\[',node['body'],maxsplit=1)[0]
            snippet = re.sub(r'\\label\{[^}]+\}','',snippet).strip()
            text_preview = plain_math(snippet.replace('$',''))[0]
            search_item = dict(title='Paper II / '+(label if kind!='text' else 'Passage at line '+str(node['line'])),
                               group='Collection',kind='Written proofs' if kind=='proof' else 'Papers and source',
                               work_ids=['paper-ii'],url=PAGE+'#'+node['id'],text=plain+' '+aliases,
                               preview=text_preview or plain[:240])
            if snippet: search_item['preview_parts'] = chapter.preview(snippet)
            if math_preview and len(math_preview)<900: search_item['math_preview'] = math_preview
            site.search.append(search_item)
        report_nodes.append({k:node[k] for k in ('kind','line','end_line','labels')})
    body += '</article>'+chapter_nav+reader.work_routes('paper-ii',PAGE)
    body += '<details class="document-provenance"><summary>Source and conversion record</summary><p>Source SHA-256: <code>'+reader.records[SOURCE]['sha256']+'</code></p><p>Every paragraph, statement, proof, displayed equation and figure in this chapter is processed. Unsupported prose commands stop the build. Mathematical macros are expanded from the retained manuscript definitions.</p><p><a href="'+site.rel('documents/readable-paper-ii.json',PAGE)+'">Read the conversion record</a></p></details>'
    site.page(PAGE,TITLE,body)
    # Independent count and sequence comparison catches dropped or duplicated math.
    original_math = [m[1] if m[1] is not None else m[2] for m in re.finditer(r'\$(.*?)\$|\\\[(.*?)\\\]',chapter.text,re.S)]
    if chapter.math != original_math: raise ValueError('Reading view lost or reordered mathematical expressions')
    report = dict(source=SOURCE,source_sha256=hashlib.sha256(raw).hexdigest(),url=PAGE,
                  math_expressions=len(chapter.math),math_sequence_sha256=hashlib.sha256(json.dumps(chapter.math,ensure_ascii=False).encode()).hexdigest(),
                  references=len(chapter.references),labels=len(chapter.labels),nodes=report_nodes,
                  macro_source=MAIN,macros=macros,new_proof_review=False,new_lean_execution=False)
    site.write('documents/readable-paper-ii.json',json.dumps(report,ensure_ascii=False,indent=2)+'\n')


def chapter_section(chapter,node):
    return int(next(n['number'] for n in reversed(chapter.nodes) if n['kind']=='section' and n['line']<=node['line']))
