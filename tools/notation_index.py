"""Source-bound mathematical notation, with meanings kept local to each work.

This is a reference index, not a TeX compiler or a mathematical proof audit.
It records every detected mathematical passage and symbol without interpreting
an occurrence as a definition. Original source positions remain authoritative.
"""
from __future__ import annotations
import bisect
import collections
import hashlib
import html
import json
from pathlib import PurePosixPath
import re
import unicodedata

VERSION = 1
TEXT_SUFFIXES = {'.tex', '.md', '.txt'}
GREEK = dict(zip(
    'alpha beta gamma delta epsilon varepsilon zeta eta theta vartheta iota kappa lambda mu nu xi pi varpi rho varrho sigma varsigma tau upsilon phi varphi chi psi omega Gamma Delta Theta Lambda Xi Pi Sigma Upsilon Phi Psi Omega'.split(),
    'α β γ δ ϵ ε ζ η θ ϑ ι κ λ μ ν ξ π ϖ ρ ϱ σ ς τ υ ϕ φ χ ψ ω Γ Δ Θ Λ Ξ Π Σ Υ Φ Ψ Ω'.split()))
GLYPHS = {**GREEK, 'in':'∈', 'notin':'∉', 'subset':'⊂', 'subseteq':'⊆', 'supseteq':'⊇',
    'to':'→', 'mapsto':'↦', 'longmapsto':'⟼', 'longrightarrow':'⟶', 'leftarrow':'←', 'leftrightarrow':'↔',
    'Rightarrow':'⇒', 'Leftrightarrow':'⇔', 'le':'≤', 'leq':'≤', 'ge':'≥', 'geq':'≥',
    'ne':'≠', 'neq':'≠', 'equiv':'≡', 'cong':'≅', 'simeq':'≃', 'sim':'∼', 'approx':'≈',
    'infty':'∞', 'partial':'∂', 'nabla':'∇', 'sum':'∑', 'prod':'∏', 'int':'∫',
    'oplus':'⊕', 'bigoplus':'⊕', 'otimes':'⊗', 'bigotimes':'⊗', 'cup':'∪', 'cap':'∩',
    'bigcup':'⋃', 'bigcap':'⋂', 'emptyset':'∅', 'varnothing':'∅', 'forall':'∀', 'exists':'∃',
    'circ':'∘', 'times':'×', 'cdot':'·', 'pm':'±', 'mp':'∓', 'perp':'⊥', 'ell':'ℓ',
    'hbar':'ℏ', 'dagger':'†', 'star':'⋆', 'ast':'∗', 'langle':'⟨', 'rangle':'⟩', 'Bbbk':'𝕜',
    'twoheadrightarrow':'↠', 'hookrightarrow':'↪', 'setminus':'∖', 'smallsetminus':'∖',
    'ldots':'…', 'cdots':'⋯', 'dots':'…'}
FORMATS = {'mathbb', 'mathcal', 'mathfrak', 'mathbf', 'mathrm', 'mathsf', 'mathtt', 'boldsymbol', 'bm', 'operatorname'}
ACCENTS = {'hat', 'widehat', 'tilde', 'widetilde', 'bar', 'overline', 'underline', 'vec', 'dot', 'ddot'}
STRUCTURAL = {'frac', 'dfrac', 'tfrac', 'sqrt', 'binom', 'dbinom', 'tbinom', 'left', 'right',
    'big', 'Big', 'bigg', 'Bigg', 'bigl', 'bigr', 'Bigl', 'Bigr', 'biggl', 'biggr',
    'begin', 'end', 'label', 'tag', 'nonumber', 'notag', 'limits', 'nolimits', 'displaystyle',
    'textstyle', 'scriptstyle', 'scriptscriptstyle', 'quad', 'qquad', 'hspace', 'vspace',
    'phantom', 'vphantom', 'hphantom', 'overbrace', 'underbrace', 'substack', 'color', 'textcolor', 'boxed'}
TEXT_COMMANDS = {'text', 'textrm', 'textsf', 'texttt', 'textnormal', 'textbf', 'emph', 'mbox', 'ref', 'eqref', 'cite', 'url', 'href'}
MATH = re.compile(
    r'\$\$(?P<dollars>.*?)\$\$|'
    r'\\\[(?P<display>.*?)\\\]|\\\((?P<inline>.*?)\\\)|'
    r'\$(?!\$)(?P<single>.*?)\$|'
    r'\\begin\{(?P<env>equation\*?|align\*?|alignat\*?|gather\*?|multline\*?|eqnarray\*?|displaymath|math)\}'
    r'(?P<environment>.*?)\\end\{(?P=env)\}', re.S)


def blank(text):
    return ''.join('\n' if c == '\n' else ' ' for c in text)


def masked_source(text, suffix):
    """Mask comments and executable/code examples without moving line numbers."""
    if suffix == '.tex':
        text = re.sub(r'\\begin\{(lstlisting|verbatim\*?|minted|comment)\}.*?\\end\{\1\}', lambda m: blank(m[0]), text, flags=re.S)
        text = re.sub(r'\\verb\*?([^\w\s])(.*?)\1', lambda m: blank(m[0]), text)
        chars = list(text)
        for match in re.finditer('%', text):
            before = match.start()-1
            while before >= 0 and text[before] == '\\': before -= 1
            if (match.start()-before-1) % 2: continue
            end = text.find('\n', match.start())
            end = len(text) if end < 0 else end
            chars[match.start():end] = ' '*(end-match.start())
        text = ''.join(chars)
        start = text.find(r'\begin{document}')
        if start >= 0: text = blank(text[:start])+text[start:]
    else:
        text = re.sub(r'<!--.*?-->', lambda m: blank(m[0]), text, flags=re.S)
        def fence(match):
            if match['language'].strip().lower() in {'math', 'latex', 'tex'}:
                # Preserve the source offsets. The formula scan handles this
                # body separately so bare math fences need no synthetic $ signs.
                return match[0]
            return blank(match[0])
        text = re.sub(r'(?m)^(?P<fence>`{3,}|~{3,})(?P<language>[^\n]*)\n.*?^(?P=fence)[ \t]*$', fence, text, flags=re.S)
        text = re.sub(r'(?<!`)`[^`\n]+`(?!`)', lambda m: blank(m[0]), text)
    return text


def passages(text, suffix):
    clean = masked_source(text, suffix)
    chars=list(clean)
    for match in re.finditer(r'\$',clean):
        before=match.start()-1
        while before>=0 and clean[before]=='\\':before-=1
        if (match.start()-before-1)%2:chars[match.start()]=' '
    clean=''.join(chars)
    fences = []
    if suffix != '.tex':
        for match in re.finditer(r'(?m)^(`{3,}|~{3,})(?:math|latex|tex)[ \t]*\n(.*?)^\1[ \t]*$', clean, re.S):
            fences.append((match.start(2), match.end(2), match[2]))
        for start, end, _ in fences:
            clean = clean[:start]+blank(clean[start:end])+clean[end:]
    found = list(fences)
    for match in MATH.finditer(clean):
        name = next(name for name in ('dollars','display','inline','single','environment') if match[name] is not None)
        found.append((match.start(name), match.end(name), match[name]))
    return sorted(found)


def group(text, offset, opening='{', closing='}'):
    if offset >= len(text) or text[offset] != opening: return None
    depth, pos = 1, offset+1
    while pos < len(text):
        if text[pos] == '\\': pos += 2; continue
        if text[pos] == opening: depth += 1
        elif text[pos] == closing: depth -= 1
        if not depth: return text[offset:pos+1], pos+1
        pos += 1
    return None


def atom(text, pos):
    if pos >= len(text): return None
    if text[pos] == '{': return group(text, pos)
    if text[pos] == '\\':
        match = re.match(r'\\(?:[A-Za-z]+|.)', text[pos:])
        return (match[0], pos+len(match[0])) if match else None
    return text[pos], pos+1


def symbol_tokens(expression):
    """Literal atoms and decorated forms. Never equate two authors' meanings."""
    tokens = set()
    def scan(text):
        pos = 0
        while pos < len(text):
            start = pos
            if text[pos] == '\\':
                item = atom(text, pos)
                if not item: pos += 1; continue
                base, pos = item
                command = base[1:]
                if command in TEXT_COMMANDS | {'begin','end','label','tag','color'}:
                    while pos < len(text) and text[pos].isspace(): pos += 1
                    body = group(text, pos)
                    if body: pos = body[1]
                    continue
                if command in FORMATS | ACCENTS:
                    while pos < len(text) and text[pos].isspace(): pos += 1
                    body = atom(text, pos)
                    if body:
                        base += body[0]; pos = body[1]
                    else: continue
                elif command in STRUCTURAL or not command.isalpha():
                    continue
            elif text[pos].isalpha() or text[pos] in '∈∉⊂⊆⊕⊗∪∩∅∀∃∂∇∞≤≥≠≡≈→↦∘±+*=|':
                base = text[pos]; pos += 1
            else:
                pos += 1; continue
            tokens.add(base)
            decorated = base
            while pos < len(text):
                saved = pos
                while pos < len(text) and text[pos].isspace(): pos += 1
                if pos >= len(text): break
                if text[pos] in "'′":
                    decorated += text[pos]; pos += 1; continue
                if text[pos] not in '_^': pos = saved; break
                op = text[pos]; pos += 1
                while pos < len(text) and text[pos].isspace(): pos += 1
                body = atom(text, pos)
                if not body: break
                decorated += op+body[0]; pos = body[1]
                scan(body[0][1:-1] if body[0].startswith('{') else body[0])
            tokens.add(decorated)
    scan(expression)
    return sorted(t for t in tokens if t.strip())


def macro_definitions(text):
    text=re.sub(r'(?<!\\)%[^\n]*','',text)
    definitions = {};conflicts=set()
    def add(name,value):
        if name in definitions and definitions[name]!=value:conflicts.add(name)
        definitions[name]=value
    for match in re.finditer(r'\\(?:newcommand|renewcommand|providecommand)\*?\s*(?:\{\\([A-Za-z]+)\}|\\([A-Za-z]+))\s*', text):
        body = group(text, match.end())
        if body and '#' not in body[0]: add(match[1] or match[2],body[0][1:-1])
    for match in re.finditer(r'\\DeclareMathOperator\*?\s*\{\\([A-Za-z]+)\}\s*',text):
        body = group(text, match.end())
        if body: add(match[1],r'\operatorname'+body[0])
    return {k:v for k,v in definitions.items() if k not in conflicts}


def expand(tex, macros):
    original=tex
    for _ in range(12):
        new = re.sub(r'\\([A-Za-z]+)', lambda m: '{'+macros[m[1]]+'}' if m[1] in macros else m[0], tex)
        if new == tex: return new
        if len(new)>20000:return original
        tex = new
    return original


def plain(tex):
    """A search/display aid, never a replacement for the exact TeX spelling."""
    tex = re.sub(r'\\mathbb\s*\{([RNCQZFH])\}',lambda m:dict(R='ℝ',N='ℕ',C='ℂ',Q='ℚ',Z='ℤ',F='𝔽',H='ℍ')[m[1]],tex)
    tex = re.sub(r'\\(?:quad|qquad)\b',' ',tex)
    tex = re.sub(r'\\(?:left|right|big|Big|bigg|Bigg|bigl|bigr|Bigl|Bigr|biggl|biggr|boxed)\b','',tex)
    pieces=re.split(r'(\\(?:[A-Za-z]+|[\s\S]))',tex)
    for number,piece in enumerate(pieces):
        if number%2:
            command=piece[1:]
            pieces[number]=(GLYPHS.get(command, '' if command in FORMATS | TEXT_COMMANDS else command)
                            if command.isalpha() else command if command in '{}%&#_$' else ' ')
        else:pieces[number]=piece.replace('{','').replace('}','')
    return re.sub(r'\s+', ' ', ''.join(pieces)).strip()


def preview_commands(text):
    """Remove known layout/metadata arguments, retaining named section content."""
    omitted={'Needspace','needspace','RecordID','label','index','vspace','hspace','addvspace'}
    headings={'part','chapter','section','subsection','subsubsection','paragraph','subparagraph'}
    spacing={'protect','phantomsection','noindent','smallskip','medskip','bigskip','clearpage','newpage','par','newline','pagebreak','nopagebreak'}
    chunks=[];position=0
    for match in re.finditer(r'\\([A-Za-z]+)\*?\s*',text):
        command=match[1]
        if match.start()<position or command not in omitted|headings|spacing:continue
        end=match.end()
        if command in headings|{'pagebreak','nopagebreak'}:
            option=group(text,end,'[',']')
            if option:
                end=option[1]
                while end<len(text) and text[end].isspace():end+=1
        replacement=' '
        if command not in spacing:
            body=group(text,end)
            if not body:continue
            end=body[1]
            if command in headings:
                title=preview_commands(body[0][1:-1]).strip()
                replacement=title+(' ' if title.endswith(('.',':','!','?')) else '. ')
        chunks.extend((text[position:match.start()],replacement));position=end
    chunks.append(text[position:])
    return ''.join(chunks)


def context_for(text, start, end):
    boundaries=[text.rfind(token,0,start) for token in ('\n\n','\\\\')]
    left = max([0,text.rfind(r'\item[',0,start)]+[p+2 for p in boundaries if p>=0])
    right_candidates = [p for p in (text.find('\n\n',end),text.find('\\\\',end)) if p >= 0]
    right = min(right_candidates) if right_candidates else min(len(text),end+500)
    left = max(left, start-400)
    right = min(right, end+700)
    raw = text[left:right].strip()
    if len(raw)>1100: raw=raw[:1100]+'…'
    before = text[max(0,start-4000):start]
    table = before.rfind(r'\begin{longtable}') > before.rfind(r'\end{longtable}') or before.rfind(r'\begin{tabular') > before.rfind(r'\end{tabular')
    # Only explicit symbol/meaning headers establish a notation table.
    table = table and bool(re.search(r'(?i)(symbol|notation).*?&.*?(meaning|convention|name|description)',before,re.S))
    if table: kind='notation-table'
    elif before.rfind(r'\begin{definition}') > before.rfind(r'\end{definition}') and r'\begin{definition}' in before: kind='definition-passage'
    elif re.search(r'(?i)\b(denotes?|we write|we define|is defined|write .*? for)\b',raw): kind='introduction-passage'
    else: kind='use'
    return raw,kind


def context_text(raw,macros=None):
    raw = preview_commands(raw)
    raw = re.sub(r'\\(?:ref|eqref|cref|Cref|autoref|cite|citep|citet|Depends)\*?(?:\[[^\]]*\])?\{[^{}]*\}', '[source reference]', raw)
    if macros:raw=expand(raw,macros)
    raw = re.sub(r'\\(?:toprule|midrule|bottomrule|endhead|endfirsthead|hline)\b', '', raw)
    raw = re.sub(r'\\(?:begin|end)\{[^{}]*\}', '', raw)
    # Consume escaped pairs together so literal dollars/ampersands survive.
    raw = re.sub(r'\\.|[$&]',lambda m:'' if m[0] in {'$',r'\(',r'\)',r'\[',r'\]'} else ' · ' if m[0]=='&' else m[0],raw)
    return plain(raw).strip()


def index_document(text, suffix):
    offsets=[-1]+[m.start() for m in re.finditer('\n',text)]
    result=[]
    for start,end,expression in passages(text,suffix):
        raw,kind=context_for(text,start,end)
        result.append(dict(line=bisect.bisect_left(offsets,start),start=start,end=end,expression=text[start:end],
                           context=raw,kind=kind,symbols=symbol_tokens(expression)))
    return result


def prepare_sources(reader):
    """Add declared manuscript entrypoints before following their includes."""
    config=json.loads((reader.site.root/'manifests/notation-sources.json').read_bytes())
    roots={c['id']:c['destination'] for c in reader.site.registry['components']}
    reader.notation_roots={}
    for work, paths in config['additional_entrypoints'].items():
        for path in paths:
            full=roots[work]+'/'+path
            if not reader.add(full): raise ValueError('Missing notation source: '+full)
            reader.notation_roots[full]=full


KINDS = {'notation-table':'Notation table', 'definition-passage':'Definition passage',
         'introduction-passage':'Introduction passage', 'use':'Use in source'}
RANK = {kind:n for n,kind in enumerate(KINDS)}
SAFE_COMMANDS = set(GLYPHS) | FORMATS | ACCENTS | STRUCTURAL | TEXT_COMMANDS | set(
    'sin cos tan cot sec csc sinh cosh tanh log ln exp lim limsup liminf sup inf max min '
    'det dim ker hom Pr gcd lcm mod bmod pmod coloneqq colon iff imath jmath '
    'lvert rvert lVert rVert vert Vert ldots cdots vdots ddots setminus smallsetminus '
    'top bot prime bullet triangle square Box land lor neg wedge vee bigwedge bigvee '
    'hookrightarrow twoheadrightarrow rightarrow leftleftharpoons rightharpoonup '
    'mathscr mathrm mathit mathnormal Re Im arg degree deg'.split())


def display_math(tex, macros):
    expanded = expand(tex, macros)
    commands = set(re.findall(r'\\([A-Za-z]+)', expanded))
    # Keep unfamiliar and parameterized macros exact rather than inventing an
    # expansion. No URLs, HTML commands or user-defined TeX are executed.
    forbidden = {'href','url','begin','end','label','ref','eqref','cite','color','textcolor'}
    if len(expanded)>500 or commands-SAFE_COMMANDS or commands & forbidden:
        return None
    return expanded


def aliases(tex, macros):
    names = ' '.join(re.findall(r'\\([A-Za-z]+)',tex))
    value = expand(tex,macros)
    return ' '.join(dict.fromkeys(x for x in [plain(tex),plain(value),names,
                         ' '.join(re.findall(r'\\([A-Za-z]+)',value))] if x))


def symbol_id(tex):
    return 'symbol-'+hashlib.sha256(tex.encode()).hexdigest()[:16]


def source_url(source, line):
    return source.get('source_url',source['url'])+'#L'+str(line)


def extract_work(site, work):
    reader=site.reader
    records=sorted((r for r in reader.records.values() if r['work']==work and
                    PurePosixPath(r['path']).suffix.lower() in TEXT_SUFFIXES),key=lambda r:r['repository_path'])
    sources=[]; passages_all=[]; symbols=collections.defaultdict(list)
    spellings=collections.defaultdict(set); displays={}
    texts={r['repository_path']:site.read_source(r).decode('utf-8-sig') for r in records}
    for number,record in enumerate(records):
        path=record['repository_path'];text=texts[path]
        main=reader.notation_roots.get(path) or reader.manuscript_roots.get(work)
        macros=macro_definitions(texts.get(main,''))
        macros.update(macro_definitions(text))
        found=index_document(text,PurePosixPath(path).suffix.lower())
        sources.append({k:record[k] for k in ('repository_path','file_url','url','sha256','git_blob_sha1','size')})
        if 'source_url' in record: sources[-1]['source_url']=record['source_url']
        sources[-1]['passages']=len(found)
        sources[-1]['macros']=macros
        alias_cache={};display_cache={}
        for item in found:
            terms=item.pop('symbols');item['source']=number
            index=len(passages_all);passages_all.append(item)
            for tex in terms:
                symbols[tex].append(index)
                if tex not in alias_cache:
                    alias_cache[tex]=aliases(tex,macros)
                    display_cache[tex]=display_math(tex,macros)
                spellings[tex].add(alias_cache[tex])
                rendered=display_cache[tex]
                # A macro can change meaning even within one work. Render only
                # when all encountered source contexts agree on the expansion.
                if tex in displays and displays[tex]!=rendered: displays[tex]=None
                else: displays[tex]=rendered
    entries=[]
    for tex,occurrences in sorted(symbols.items(),key=lambda x:(plain(x[0]).casefold(),x[0])):
        ranked=sorted(occurrences,key=lambda i:(RANK[passages_all[i]['kind']],i))
        entries.append(dict(id=symbol_id(tex),tex=tex,aliases=' '.join(sorted(spellings[tex])),
                            display=displays.get(tex),kind=passages_all[ranked[0]]['kind'],
                            occurrences=ranked))
    pdfs=[{k:r[k] for k in ('repository_path','url','sha256')} for r in reader.records.values() if r['work']==work and r['format']=='pdf']
    entries.sort(key=lambda item:(RANK[item['kind']],plain(item['tex']).casefold(),item['tex']))
    return dict(version=VERSION,work=work,title=site.components[work]['title'],source_revision=site.revision,
                sources=sources,pdfs=pdfs,passages=passages_all,entries=entries)


def preview_occurrences(data,entry):
    """Prefer distinct source contexts, retaining every occurrence in the data."""
    seen=set();result=[]
    for number in entry['occurrences']:
        item=data['passages'][number]
        key=(item['source'],item['context'])
        if key in seen:continue
        seen.add(key);result.append(number)
        if len(result)==1:break
    return result


def table_preview(context,macros):
    """Read a table's own symbol/name/meaning cells without defining its atoms."""
    clean=context
    for start,end,_ in reversed(passages(context,'.tex')):
        clean=clean[:start]+blank(clean[start:end])+clean[end:]
    breaks=[m.start() for m in re.finditer(r'(?<!\\)&',clean)]
    if not breaks:return None
    bounds=[-1,*breaks,len(context)]
    cells=[context[a+1:b].strip() for a,b in zip(bounds,bounds[1:])]
    math=passages(cells[0],'.tex')
    if not math or len(cells) not in (2,3):return None
    symbol=', '.join(item[2].strip() for item in math)
    label=context_text(cells[1],macros) if len(cells)==3 else ''
    meaning=context_text(cells[-1],macros)
    if len(label)>100 or len(symbol)>300:return None
    return dict(tex=symbol,display=display_math(symbol,macros),label=label,meaning=meaning[:450])


def symbol_names(tex,display):
    # Whole-symbol aliases rank above words which merely occur in its context.
    return sorted({s for s in (tex,plain(tex),plain(display) if display else '',
                              re.sub(r'\\(?=[A-Za-z])','',tex)) if s})


def reader_index(search,work):
    """A compact, work-local slice of the existing context-aware search index."""
    entries=[entry for entry in search['entries'] if entry['work']==work]
    identifiers=sorted({entry['context'] for entry in entries})
    positions={identifier:number for number,identifier in enumerate(identifiers)}
    return dict(version=2,source_revision=search['source_revision'],
                works=[row for row in search['works'] if row['id']==work],
                contexts=[search['contexts'][identifier] for identifier in identifiers],
                entries=[{**entry,'context':positions[entry['context']]} for entry in entries])


def build(site):
    e=html.escape
    config=json.loads((site.root/'manifests/notation-sources.json').read_bytes())
    all_entries=[];works=[];contexts=[];context_ids={};search_entries=[]
    totals=collections.Counter()
    script_hash=hashlib.sha256((site.root/'website/assets/notation.js').read_bytes()).hexdigest()[:12]
    def script(page):
        search_hash=hashlib.sha256((site.root/'website/assets/notation-search.js').read_bytes()).hexdigest()[:12]
        return '<script defer src="'+site.rel('assets/notation-search.js',page)+'?v='+search_hash+'"></script><script defer src="'+site.rel('assets/notation.js',page)+'?v='+script_hash+'"></script>'
    for component in site.registry['components']:
        work=component['id'];data=extract_work(site,work)
        page='notation/'+work+'.html';data_url='notation/data/'+work+'.json'
        site.write(data_url,json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
        count=len(data['entries']);npass=len(data['passages'])
        row=dict(id=work,title=data['title'],url=page,data_url=data_url,sources=len(data['sources']),
                 passages=npass,symbols=count,pdfs=len(data['pdfs']),
                 data_sha256=hashlib.sha256((site.output/data_url).read_bytes()).hexdigest())
        row['short_title']=data['title'].split(':',1)[0] if work.startswith('paper-') else data['title']
        works.append(row)
        totals.update({k:row[k] for k in ('sources','passages','symbols')})
        body='<p class="eyebrow">Notation by work</p><h1>'+e(data['title'])+'</h1>'
        body+='<p><a href="../notation.html">All notation</a> · <a href="../collection/GLOSSARY.html">Glossary</a> · <a href="#coverage">Source coverage</a></p>'
        body+=site.reader.work_routes(work,page)
        body+='<p>'+str(count)+' symbol spellings in '+str(npass)+' mathematical passages across '+str(len(data['sources']))+' selected source files. Subscripts and superscripts have their own entries alongside their base symbols.</p>'
        body+='<p>The same symbol can have several meanings here. A passage classified as a definition may define another part of its expression. Read the linked context before assigning a meaning.</p>'
        if count:
            body+='<form class="notation-filter" data-notation-work="'+e(work)+'" data-source="data/'+work+'.json"><label for="notation-query">Find a symbol, TeX spelling or word in a source excerpt</label><input id="notation-query" name="q" type="search" placeholder="For example: alpha, \\Phi, packet"><label for="notation-kind">Passage type</label><select id="notation-kind"><option value="">All passages</option>'+''.join('<option value="'+k+'">'+v+'</option>' for k,v in KINDS.items())+'</select><button type="submit">Find notation</button><button type="reset">Clear</button></form><p id="notation-status" role="status" aria-live="polite">All '+str(count)+' entries are available below.</p><div id="notation-entries">'
        introduction=body
        entry_blocks=[]
        for entry in data['entries']:
            body=''
            sample=preview_occurrences(data,entry)
            excerpts=[context_text(data['passages'][i]['context'],data['sources'][data['passages'][i]['source']]['macros']) for i in sample]
            search=' '.join([entry['tex'],entry['aliases'],*excerpts])
            url=page+'#'+entry['id']
            item=dict(work=work,url=url,tex=entry['tex'],aliases=entry['aliases'],display=entry['display'],
                      kind=entry['kind'],excerpt=excerpts[0][:350],count=len(entry['occurrences']))
            all_entries.append(item)
            primary=data['passages'][sample[0]];source=data['sources'][primary['source']]
            key=(work,source['repository_path'],primary['context'])
            if key not in context_ids:
                from reader_guidance import reading_passage_url
                context_ids[key]=len(contexts)
                contexts.append(dict(work=work,excerpt=excerpts[0][:450],source_url=source_url(source,primary['line']),
                    reading_url=reading_passage_url(site.reader,source['repository_path'],primary['line']) or source_url(source,primary['line']),
                    source_label=PurePosixPath(source['repository_path']).name+', line '+str(primary['line']),
                    table=table_preview(primary['context'],source['macros']) if primary['kind']=='notation-table' else None))
            search_entries.append({k:v for k,v in item.items() if k!='excerpt'} |
                                  dict(context=context_ids[key],names=symbol_names(entry['tex'],entry['display'])))
            body+='<details class="notation-entry" id="'+entry['id']+'" data-kind="'+entry['kind']+'" data-search="'+e(search,quote=True)+'"><summary><code>'+e(entry['tex'])+'</code><span>'+KINDS[entry['kind']]+' · '+str(len(entry['occurrences']))+' passages</span></summary>'
            if entry['display']:
                body+='<p class="notation-display" data-math="'+e(entry['display'],quote=True)+'"></p>'
            body+='<p class="notation-aliases">Search aliases: '+e(entry['aliases'])+'</p>'
            body+='<p><a href="#'+entry['id']+'">Link to this entry</a> · <button type="button" class="notation-copy" data-copy="'+e(entry['tex'],quote=True)+'">Copy TeX</button></p><ul class="notation-passages">'
            for number in sample:
                p=data['passages'][number];source=data['sources'][p['source']]
                excerpt=context_text(p['context'],source['macros'])
                body+='<li><p><strong>'+KINDS[p['kind']]+'</strong> · <a href="'+site.rel(source_url(source,p['line']),page)+'">'+e(PurePosixPath(source['repository_path']).name)+', line '+str(p['line'])+'</a></p><p class="notation-excerpt">'+e(excerpt[:500]+('…' if len(excerpt)>500 else ''))+'</p><details><summary>Exact mathematical passage</summary><pre><code>'+e(p['expression'])+'</code></pre></details></li>'
            body+='</ul><button type="button" class="notation-occurrences" data-symbol="'+entry['id']+'" hidden>List all '+str(len(entry['occurrences']))+' source passages</button><div class="notation-all"></div></details>'
            entry_blocks.append(body)
        body=introduction+''.join(entry_blocks)
        if count:body+='</div><button id="notation-more" type="button" hidden>Show more entries</button><noscript><p>All entries are listed. Use your browser’s Find command to search. The JSON download contains every detected source occurrence.</p></noscript>'
        else:body+='<aside class="notice"><h2>No delimited mathematics found</h2><p>The selected text files did not yield mathematical notation. This does not mean that the work contains no symbols. Read the documents below, including any PDFs, for notation outside the text scan.</p></aside>'
        body+='<section id="coverage"><h2>Source coverage</h2><p>Automatic extraction covers TeX and Markdown math delimiters and common equation environments in these selected files. It does not interpret diagrams, images, PDF text, program identifiers, or historical archives. Occurrences are navigation aids, not a proof review.</p><p><a href="'+site.rel(data_url,page)+'" download>Download all entries, passages and source checksums (JSON)</a> · <a href="../notation.html#coverage">Collection coverage</a></p><ul>'
        for source in data['sources']:
            body+='<li><a href="'+site.rel(source.get('source_url',source['url']),page)+'">'+e(source['repository_path'])+'</a> · '+str(source['passages'])+' mathematical passages</li>'
        body+='</ul>'
        if data['pdfs']:
            body+='<details><summary>PDF reading editions ('+str(len(data['pdfs']))+')</summary><p>The text index does not extract PDF glyphs. Check the reading edition for notation in figures, tables and PDF-only material.</p><ul>'+''.join('<li><a href="'+site.rel(p['url'],page)+'">'+e(PurePosixPath(p['repository_path']).name)+'</a></li>' for p in data['pdfs'])+'</ul></details>'
        body+='</section>'+script(page)
        site.page(page,'Notation: '+data['title'],body)
        site.search.append(dict(title='Notation: '+data['title'],group='Collection',kind='Notation',url=page,
                                work_ids=[work],text='Symbols definitions notation TeX '+data['title']+' '+' '.join(x['tex']+' '+x['aliases'] for x in data['entries'])))
    manifest=dict(version=VERSION,source_revision=site.revision,scope=config['scope'],totals=dict(totals),works=works,entries=all_entries)
    site.write('notation/index.json',json.dumps(manifest,ensure_ascii=False,separators=(',',':'))+'\n')
    search=dict(version=2,source_revision=site.revision,works=works,contexts=contexts,entries=search_entries)
    site.write('notation/search.json',json.dumps(search,ensure_ascii=False,separators=(',',':'))+'\n')
    for work in works:
        site.write('notation/reader/'+work['id']+'.json',json.dumps(reader_index(search,work['id']),ensure_ascii=False,separators=(',',':'))+'\n')
    body='<div class="notation-heading"><p class="eyebrow">Across the collection</p><h1>Notation index</h1><p>Find a symbol and read it in context.</p><p class="notation-links"><a href="collection/GLOSSARY.html">Glossary</a> · <a href="#works">Browse by work</a> · <a href="#coverage">Coverage</a></p></div>'
    options='<option value="">All works</option>'
    for label,core in [('Core papers',True),('Books and other works',False)]:
        options+='<optgroup label="'+label+'">'+''.join('<option value="'+w['id']+'">'+e(w['short_title'])+'</option>' for w in works if w['id'].startswith('paper-')==core)+'</optgroup>'
    body+='<form id="notation-search" class="notation-search-clean" data-index="notation/search.json?v='+site.revision+'"><div class="notation-query-row"><div><label for="notation-query">Symbol, name or phrase</label><input id="notation-query" name="q" type="search" autocomplete="off" placeholder="α, alpha, packet…" aria-describedby="notation-help"></div><button type="submit">Search</button></div><div class="notation-controls"><div class="notation-work-control"><label for="notation-work">Work</label><select id="notation-work">'+options+'</select></div><details id="notation-options"><summary>More options</summary><label for="notation-kind">Passage type</label><select id="notation-kind"><option value="">All passages</option>'+''.join('<option value="'+k+'">'+v+'</option>' for k,v in KINDS.items())+'</select><label for="notation-exact"><input id="notation-exact" type="checkbox" name="exact"> Exact TeX spelling and case</label></details><button type="reset" class="notation-clear">Clear</button></div><p id="notation-help">Try <button type="button" class="notation-example" data-query="alpha">alpha</button>, <button type="button" class="notation-example" data-query="P_\\alpha">P_α</button> or <button type="button" class="notation-example" data-query="packet">packet</button>. Repeated passages are grouped together.</p></form><p id="notation-status" role="status" aria-live="polite">Enter a symbol or choose a work.</p><ol id="notation-results"></ol><button type="button" id="notation-more" hidden>Show more results</button><noscript><p>Search needs JavaScript. Every work index below remains readable without it.</p></noscript>'
    body+='<details id="works" class="notation-browse"><summary>Browse all '+str(len(works))+' works</summary><div class="notation-work-list">'+''.join('<article><h3><a href="'+w['url']+'">'+e(w['title'])+'</a></h3><p>'+str(w['symbols'])+' spellings · '+str(w['sources'])+' text sources'+(' · Manual notation pass needed' if not w['symbols'] else '')+'</p></article>' for w in works)+'</div></details>'
    body+='<details id="coverage" class="notation-browse"><summary>Coverage and how to read the results</summary><p>'+f'{totals["symbols"]:,}'+' spellings across '+str(len(works))+' works, from '+f'{totals["passages"]:,}'+' mathematical passages.</p><p>Exact symbol matches come first. Results that share a source passage are grouped within their work. Open the matching entries to follow each spelling individually. A notation table is quoted as a whole row, so letters mentioned in that row do not acquire the row’s definition.</p><p>'+e(config['scope'])+'</p><p>PDF glyphs, illustrations, unusual TeX syntax and notation outside math delimiters still need manual coverage. Each work lists the files scanned. Source passages remain authoritative and existing confidence assessments are unchanged.</p><p><a download href="notation/index.json">Download the full index (JSON)</a> · <a href="collection/NOTATION_INDEX.html">How the index is maintained</a></p></details>'+script('notation.html')
    site.page('notation.html','Notation index',body)
    site.search.append(dict(title='Notation index',group='Collection',kind='Notation',work_ids=[],url='notation.html',text='Complete notation source coverage symbols Greek letters TeX mathematical definitions'))
    return dict(works=len(works),**dict(totals))


def verify(root,documents,pages):
    """Check the index against the exact published source bytes and HTML."""
    manifest=json.loads((root/'notation/index.json').read_bytes())
    build=json.loads((root/'build-info.json').read_bytes())
    assert manifest['source_revision']==build['collection_revision']
    records={r['repository_path']:r for r in documents['files']}
    expected_works={r['work'] for r in documents['files']}
    assert {w['id'] for w in manifest['works']}==expected_works
    assert {'paper-'+n for n in ('i','ii','iii','iv','v','vi','vii','viii','ix','x','xi','xii')}<=expected_works
    indexed={};totals=collections.Counter()
    for work in manifest['works']:
        raw=(root/work['data_url']).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==work['data_sha256']
        data=json.loads(raw)
        assert data['source_revision']==manifest['source_revision']
        assert data['work']==work['id']
        expected_sources={p for p,r in records.items() if r['work']==work['id'] and PurePosixPath(p).suffix.lower() in TEXT_SUFFIXES}
        assert {s['repository_path'] for s in data['sources']}==expected_sources
        source_text=[]
        for source in data['sources']:
            record=records[source['repository_path']]
            assert source['sha256']==record['sha256'] and source['git_blob_sha1']==record['git_blob_sha1']
            source_text.append((root/source['file_url']).read_bytes().decode('utf-8-sig'))
        bysource=collections.Counter()
        for p in data['passages']:
            text=source_text[p['source']]
            assert text[p['start']:p['end']]==p['expression']
            assert text.count('\n',0,p['start'])+1==p['line']
            source=data['sources'][p['source']]
            assert 'L'+str(p['line']) in pages[source.get('source_url',source['url'])].ids
            bysource[p['source']]+=1
        for n,source in enumerate(data['sources']):assert source['passages']==bysource[n]
        assert len(data['entries'])==len({e['tex'] for e in data['entries']})==work['symbols']
        for entry in data['entries']:
            assert entry['id']==symbol_id(entry['tex'])
            assert entry['id'] in pages[work['url']].ids
            assert entry['occurrences'] and len(entry['occurrences'])==len(set(entry['occurrences']))
            assert all(0<=i<len(data['passages']) for i in entry['occurrences'])
            indexed[(work['id'],entry['tex'])]=entry
        assert work['sources']==len(data['sources']) and work['passages']==len(data['passages'])
        totals.update({k:work[k] for k in ('sources','passages','symbols')})
    assert dict(totals)==manifest['totals']
    assert len(manifest['entries'])==len(indexed)
    for entry in manifest['entries']:
        source=indexed[(entry['work'],entry['tex'])]
        assert entry['url']=='notation/'+entry['work']+'.html#'+source['id']
        assert entry['count']==len(source['occurrences'])
    search=json.loads((root/'notation/search.json').read_bytes())
    assert search['version']==2 and search['source_revision']==manifest['source_revision']
    assert len(search['entries'])==len(manifest['entries'])
    assert {e['url'] for e in search['entries']}=={e['url'] for e in manifest['entries']}
    for entry in search['entries']:
        assert search['contexts'][entry['context']]['work']==entry['work']
    for context in search['contexts']:
        path,fragment=context['source_url'].split('#',1)
        assert path in pages and fragment in pages[path].ids
        path,fragment=context['reading_url'].split('#',1)
        assert path in pages and fragment in pages[path].ids
    for work in search['works']:
        compact=json.loads((root/('notation/reader/'+work['id']+'.json')).read_bytes())
        assert compact==reader_index(search,work['id']),('Reader notation index differs',work['id'])
    return dict(works=len(manifest['works']),**dict(totals))
