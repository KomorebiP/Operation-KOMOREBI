"""Source-linked integer sequence catalogue and progressively enhanced explorer.

All term values are serialized as decimal strings. The catalogue records published
definitions, not claims of sequence novelty or additional formal verification.
"""
from __future__ import annotations

from functools import lru_cache
import hashlib
import html
import json
import re
from math import comb, factorial
from pathlib import Path
from sequence_formula_catalogue import formula_block, formula_variants
from sequence_atlas_reference import REFERENCES, KINDS, reference_terms, program, connections
from sequence_atlas_reading import reading_metadata, reading_block
from sequence_atlas_study import study_block
from sequence_atlas_index import connection_graph, connection_block, directory_block, index_csv

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'collection/demonstrations/SEQUENCE_SHAPES.html'


@lru_cache(maxsize=None)
def reciprocal(N, power, count):
    base = [1]
    for n in range(1, count):
        base.append(sum((-1)**(k+1)*comb(N*n, N*k)*base[n-k] for k in range(1, n+1)))
    result = [1]+[0]*(count-1)
    for _ in range(power):
        result = [sum(comb(N*n, N*k)*result[k]*base[n-k] for k in range(n+1)) for n in range(count)]
    return tuple(result)


def terms(entry, count=64):
    kind = entry['kind']
    if kind in KINDS:
        return reference_terms(kind,count)
    if kind == 'reciprocal':
        return list(reciprocal(entry['N'], entry['power'], count))
    if kind == 'euler':
        return [(-1)**n*x for n, x in enumerate(reciprocal(2, 1, count))]
    if kind == 'factorial':
        return [factorial(n) for n in range(count)]
    if kind == 'fibonacci':
        values, a, b = [], 0, 1
        for _ in range(count):
            values.append(a)
            a, b = b, a+b
        return values
    if kind not in ('bell','fubini'):
        raise ValueError('Unknown sequence definition')
    row, result = [1], []
    for n in range(count):
        result.append(sum(x*(factorial(k) if kind == 'fubini' else 1) for k, x in enumerate(row)))
        row = [0]+[k*(row[k] if k < len(row) else 0)+row[k-1] for k in range(1, n+2)]
    return result


def catalogue():
    entries = []
    for N in range(2, 9):
        for power in range(1, 4):
            entries.append(dict(kind='reciprocal', N=N, power=power,
                title=('Secant numbers' if (N, power) == (2, 1) else f'Reciprocal family N={N}, r={power}'),
                formula=f'D_{N}(t)^(-{power}) = sum a(n) t^({N}n)/({N}n)!, D_{N}(t) = sum (-1)^q t^({N}q)/({N}q)!',
                recurrence='For r=1: a(0)=1; a(n)=sum_{k=1}^n (-1)^(k+1) binom(Nn,Nk) a(n-k). Higher powers use factorial-weighted convolution.',
                explanation=f'The compressed index n corresponds to ordinary degree {N}n. This is the published Paper IV reciprocal family with power {power}.',
                source=SOURCE+'#reciprocal-growth', work_ids=['paper-iv'],
                tags=['reciprocal', 'Paper IV', f'N={N}', f'r={power}', 'generating function'],
                status='Known reference sequence' if (N, power) == (2, 1) else 'Published family · novelty unassessed',
                oeis='A000364' if (N, power) == (2, 1) else None, cap=64))
    for kind, title, formula, recurrence, source, tags, oeis, cap in [
        ('bell', 'Bell numbers', 'B(n) = sum_{k=0}^n S(n,k)', 'S(0,0)=1; S(n,k)=k S(n-1,k)+S(n-1,k-1), with zero values outside the triangle.', 'collection/demonstrations/STIRLING_BELL_FUBINI.html', ['partitions', 'Stirling', 'counting'], 'A000110', 128),
        ('fubini', 'Fubini / ordered Bell numbers', 'F(n) = sum_{k=0}^n k! S(n,k); sum F(n)t^n/n! = 1/(2-exp(t))', 'S(0,0)=1; S(n,k)=k S(n-1,k)+S(n-1,k-1). Weight each row by k! and sum.', SOURCE+'#factorial-weights', ['partitions', 'ordered', 'Stirling', 'factorial'], 'A000670', 128),
        ('factorial', 'Factorials', 'a(n) = n!', 'a(0)=1; a(n)=n a(n-1).', 'collection/demonstrations/FACTORIAL_LANES.html', ['factorial', 'growth', 'benchmark'], 'A000142', 256),
        ('fibonacci', 'Fibonacci numbers', 'F(0)=0, F(1)=1; F(n)=F(n-1)+F(n-2)', 'Two-term recurrence starting at index zero.', 'https://oeis.org/A000045', ['recurrence', 'Fibonacci', 'benchmark'], 'A000045', 1000),
        ('euler', 'Signed even Euler numbers', 'a(n) = E_(2n) = (-1)^n A_2^[1](n)', 'Multiply the secant coefficient at compressed index n by (-1)^n.', 'collection/demonstrations/EULER_PACKETS.html', ['Euler', 'signed', 'secant', 'Paper IV'], None, 64),
    ]:
        entries.append(dict(kind=kind, title=title, formula=formula, recurrence=recurrence,
            explanation='A classical reference sequence. The linked source gives its definition and mathematical context.',
            source=source, work_ids=['paper-iv'] if kind == 'euler' else [] if kind == 'fibonacci' else ['monographs-special-functions'],
            tags=tags, status='Known reference sequence', oeis=oeis, cap=cap))
    for kind,title,formula,recurrence,tags,oeis,example in REFERENCES:
        entries.append(dict(kind=kind,title=title,formula=formula,recurrence=recurrence,tags=tags,oeis=oeis,example=example,
            explanation='A classical reference sequence, indexed here from n=0. The linked OEIS entry records further interpretations and references.',
            source='https://oeis.org/'+oeis,work_ids=[],status='Known reference sequence',cap=512))
    for i, entry in enumerate(entries, 1):
        entry.update(id=f'KSEQ-{i:06d}', offset=0, terms=list(map(str, terms(entry))),
            verification='Exact implementation checks; linked sources retain their recorded proof scope.',
            novelty='No originality claim is made for this entry or its formulas.')
        if entry['kind']=='reciprocal':
            N,r=entry['N'],entry['power'];B=comb(2*N,N)
            entry['example']=f'At compressed n=1 the coefficient is {r}. At n=2, the factorial-weighted convolution gives {r}*({B}-1)+{comb(r,2)}*{B}={entry["terms"][2]}. These indices correspond to ordinary degrees {N} and {2*N}.'
        elif entry['kind'] in ('bell','fubini','factorial','fibonacci','euler'):
            entry['example']={'bell':'For a three-element set, there is one partition into one block, three into two blocks, and one into three blocks: B(3)=1+3+1=5.',
                'fubini':'For three elements, weighting Stirling counts by the number of block orders gives F(3)=1!*1+2!*3+3!*1=13.',
                'factorial':'At n=5, a(5)=5*4*3*2*1=120. The empty product gives a(0)=1.',
                'fibonacci':'F(6)=F(5)+F(4)=5+3=8, with F(0)=0 and F(1)=1.',
                'euler':'At compressed n=1, E_2=(-1)^1*1=-1; at n=2, E_4=(-1)^2*5=5. The ordinary Euler index is 2n.'}[entry['kind']]
        entry['python']=program(entry)
        entry.setdefault('example','The first three indexed values are '+', '.join(f'a({n})={v}' for n,v in enumerate(entry['terms'][:3]))+'. Use the program below to reproduce them from the definition.')
    for entry in entries:
        entry['connections']=connections(entry,entries)
        entry['reading']=reading_metadata(entry)
    return entries


def e(value):
    return html.escape(str(value), quote=True)


def structured_entry(entry, graph):
    source=entry['source'] if entry['source'].startswith('https:') else '../'+entry['source']
    reference=('<p><a href="https://oeis.org/'+entry['oeis']+'">OEIS '+entry['oeis']+' — comments, bibliography, programs, and history</a></p>' if entry['oeis'] else '')
    # Keep the finite snapshot attribution and names in the existing source section.
    snapshot=entry_body(entry,'../').split('<details><summary>OEIS comparisons',1)
    snapshot_html='<details><summary>OEIS comparisons'+snapshot[1] if len(snapshot)>1 else '<p>No six-term comparison recorded in the loaded snapshot.</p>'
    return (reading_block(entry)
        +'<section id="formulas"><h2>Formulas and recurrences</h2><div class="sa-typeset arithmatex" tabindex="0" role="region" aria-label="Typeset defining formula" hidden>\\['+e(entry['reading']['tex'])+'\\]</div><details class="sa-plain-formula" open><summary>Plain text formula</summary><p id="sa-entry-formula" class="sa-formula">'+e(entry['formula'])+'</p></details><p>'+e(entry['recurrence'])+'</p><button type="button" data-copy-entry="sa-entry-formula" hidden>Copy formula</button>'+formula_block(entry)+'</section>'
        '<section id="examples"><h2>Comments and examples</h2><p>'+e(entry['example'])+'</p></section>'
        +study_block(entry)+
        '<section id="programs"><h2>Reproduce the terms</h2><p>Self-contained Python, using exact integers and the standard library. Change count to choose the finite number of terms.</p><button type="button" data-copy-entry="sa-entry-program" hidden>Copy Python program</button><pre tabindex="0" role="region" aria-label="Python reproduction program"><code id="sa-entry-program">'+e(entry['python'])+'</code></pre></section>'
        +connection_block(entry,graph)+
        '<section id="references"><h2>References and verification</h2><p><a href="'+e(source)+'">Definition and source context</a></p>'+reference+'<p>'+e(entry['verification'])+'</p><p>'+e(entry['novelty'])+'</p>'+snapshot_html+'</section>')


def entry_body(entry, prefix=''):
    identifier = entry['id']
    all_matches = entry.get('matches', [])
    matches = sorted(all_matches,key=lambda m:(m['id']!=entry.get('oeis'),-m['matched_terms'],m['id'],m['position']))[:12]
    match_html = ''.join('<li><a href="https://oeis.org/'+e(m['id'])+'">'+e(m['id'])+'</a> — '+e(m['name'])+
        ' ('+str(m['matched_terms'])+' matching terms; excerpt position '+str(m['position'])+')</li>' for m in matches)
    source = entry['source'] if entry['source'].startswith('https:') else prefix+entry['source']
    return ('<p class="sa-label">'+e(identifier)+' · '+e(entry['status'])+'</p>'
        '<p class="sa-formula">'+e(entry['formula'])+'</p><p>'+e(entry['recurrence'])+'</p>'
        '<p>'+e(entry['explanation'])+'</p><p>Index starts at 0. '+e(entry['novelty'])+'</p>'
        '<p class="sa-terms">'+e(', '.join(entry['terms'][:12]))+'…</p>'
        '<p><a href="'+e(source)+'">Read the definition and derivation</a>'
        +(' · <a href="https://oeis.org/'+entry['oeis']+'">Reference '+entry['oeis']+'</a>' if entry['oeis'] else '')+'</p>'
        + ('<details><summary>OEIS comparisons</summary><p>Finite contiguous matches in the recorded snapshot; matching terms alone do not prove sequence identity. Positions count from zero within the exported excerpt, not the sequence’s mathematical offset. Reference names are credited to <a href="https://oeis.org/">The Online Encyclopedia of Integer Sequences</a> under <a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a>.</p><ul>'+match_html+'</ul></details>' if matches else
           '<p class="sa-note">No six-term match recorded in the loaded reference snapshot. This is not evidence of novelty.</p>')
        +('<p class="sa-note">Showing '+str(len(matches))+' of '+str(len(all_matches))+' finite snapshot hits. The catalogue JSON retains all recorded comparisons.</p>' if len(all_matches)>12 else ''))


def search_section(entries):
    topics=sorted({tag for entry in entries for tag in entry['tags'] if not tag.startswith(('N=','r='))},key=str.casefold)
    body = '''<section id="find" aria-labelledby="sa-find-title"><h2 id="sa-find-title" tabindex="-1">Find your next sequence</h2>
<p>'''+str(len(entries))+''' source-linked entries. Start with a name, a formula, an identifier, or the numbers themselves.</p>
<div id="sa-search-controls" hidden><form id="sa-search-form" role="search" aria-label="Search the sequence catalogue">
<label for="sa-query">Search sequences and formulas</label><p id="sa-query-summary" class="sa-sr-only">Combine words, or enter comma-separated terms. Use ? for an unknown term. Open Search help for field syntax.</p><div class="sa-query-row"><input id="sa-query" type="search" autocomplete="off" placeholder='Try ordered bell, n:4 r:2, or 1, ?, 69' maxlength="20000" aria-controls="sa-results" aria-describedby="sa-query-summary sa-search-status"><button type="submit">Search</button><button type="button" id="sa-clear-search">Clear</button></div>
<details class="sa-search-refine"><summary>Refine by topic, type, and matching</summary><div class="sa-search-filters"><label for="sa-filter">Entry type<select id="sa-filter"><option value="all">All entries</option><option value="reference">Known reference sequences</option><option value="family">Published reciprocal families</option><option value="saved">Saved entries</option></select></label>
<label for="sa-topic">Topic<select id="sa-topic"><option value="">All topics</option>'''+''.join('<option>'+e(tag)+'</option>' for tag in topics)+'''</select></label>
<label for="sa-match">Term matching<select id="sa-match"><option value="any">Anywhere in recorded terms</option><option value="start">Starting at index 0</option></select></label>
<label for="sa-sort">Sort results<select id="sa-sort"><option value="relevance">Best match</option><option value="name">Name</option><option value="id">Identifier</option></select></label></div></details></form>
<div class="sa-search-examples" aria-label="Example searches"><span>Try:</span><button type="button" data-search-example="n:4 r:2">n:4 r:2</button><button type="button" data-search-example='name:"ordered bell"'>ordered Bell</button><button type="button" data-search-example="1, ?, 69">1, ?, 69</button><button type="button" data-search-example="-tag:benchmark">without benchmarks</button></div>
<div class="sa-search-actions"><button type="button" id="sa-share-search">Copy search link</button><a href="#catalogue">Browse entry details</a><button type="button" id="sa-show-saved" aria-controls="sa-results" aria-pressed="false"><span id="sa-saved-count">Saved entries</span></button></div></div>
<p id="sa-search-error" class="sa-error" role="alert" hidden></p><p id="sa-search-status" role="status" aria-live="polite" aria-atomic="true">'''+str(len(entries))+''' entries. Browse the complete catalogue below without JavaScript.</p>
<p><a id="sa-archive-search" href="sequence-archive.html#records">Search the 90 research archive records →</a> · definitions, exact offsets, review stages, and modular plots</p>
<div id="sa-search-results" hidden><h3 id="sa-results-title" tabindex="-1">Search results</h3><ol id="sa-results" class="sa-results"></ol><div id="sa-empty" hidden><p>No catalogue entries match this search. Try fewer words, another topic, or a shorter term pattern.</p><div id="sa-suggestions"></div></div><button type="button" id="sa-more-results" hidden>Show more results</button></div>
<details class="sa-search-help"><summary>Search help and examples</summary><div id="sa-query-help"><p>Words are combined with AND: <code>bell factorial</code> finds entries containing both. Quotes keep a phrase together. Use <code>|</code> for alternatives and a leading minus to exclude a word or field.</p>
<dl><dt><code>name:"ordered bell"</code></dt><dd>Search entry names.</dd><dt><code>n:4 r:2</code></dt><dd>Select reciprocal spacing N and power r.</dd><dt><code>formula:convolution</code></dt><dd>Search definitions and recurrences.</dd><dt><code>tag:partitions -name:fubini</code></dt><dd>Combine a topic with an exclusion.</dd><dt><code>id:KSEQ-7 | oeis:A000364</code></dt><dd>Find a local identifier or recorded OEIS reference.</dd><dt><code>1, ?, 69</code></dt><dd>Match consecutive integer terms, allowing one unknown value. Match locations are shown in the results.</dd></dl>
<p>Term searches cover the first 64 stored terms of each entry. Text suggestions correct spelling only; integer matching stays exact. Saved entries are stored in this browser; a saved-filter link uses the recipient’s own saved list. This field syntax is inspired by <a href="https://oeis.org/hints.html">OEIS search hints</a>; it searches the Komorebi catalogue. Press Ctrl+/ (Command+/ on Mac) outside an input to focus search, or Arrow Down in the search field to reach its results.</p></div></details></section>'''
    help_match=re.search(r'<details class="sa-search-help">.*?</details>',body,re.S)
    help_html=help_match[0]
    body=body[:help_match.start()]+body[help_match.end():]
    return body.replace('<p id="sa-search-error"',help_html+'<p id="sa-search-error"',1)


def refine_body(body, entries):
    body=body.replace('<nav aria-label="Atlas sections">','<nav aria-label="Atlas sections"><a href="#find">Find a sequence</a>')
    body=re.sub(r'<div id="sa-search-controls".*?</div>\s*<p id="sa-search-status".*?</p>', '', body, flags=re.S)
    body=body.replace('<section id="explorer"',search_section(entries)+discovery_section(entries)+'<section id="explorer"',1)
    body=re.sub(r'<nav aria-label="Atlas sections">.*?</nav>','<nav class="sa-mode-nav" aria-label="Atlas sections"><a href="#find" data-atlas-mode="find">Browse</a><a href="#discover" data-atlas-mode="discover">Discover</a><a href="#explorer" data-atlas-mode="explorer">Plot</a><a href="#catalogue" data-atlas-mode="catalogue">All entries</a><a href="#reference" data-atlas-mode="reference">About</a></nav>',body,flags=re.S)
    body=body.replace('<a href="#explorer">Plot explorer</a>','<a href="#discover">Discover connections</a><a href="#explorer">Plot explorer</a>')
    body=body.replace('<div id="sa-workspace" hidden>', '''<div id="sa-workspace" hidden><div class="sa-presets" role="group" aria-label="Load an investigation"><span>Start with a question:</span><button type="button" data-investigation="fibonacci">Fibonacci residues</button><button type="button" data-investigation="euler">Euler sign changes</button><button type="button" data-investigation="powers">Compare reciprocal powers</button><button type="button" data-investigation="partitions">Ordering partitions</button></div><p id="sa-investigation" class="sa-note"></p>''')
    body=body.replace('<option value="pairs">Successive-term pairs</option>','<option value="pairs">Successive-term pairs</option><option value="mod-pairs">Successive residues (a(n), a(n+1)) mod m</option>')
    body=body.replace('<option value="difference">First differences</option>','<option value="difference">First differences</option><option value="second-difference">Second differences</option>')
    body=body.replace('<option value="raw">Original terms</option>','<option value="raw">Original terms</option><option value="alternating">Alternating signs</option><option value="absolute">Absolute values</option><option value="binomial">Binomial transform</option><option value="inverse-binomial">Inverse binomial transform</option>')
    body=body.replace('<p id="sa-error" role="alert" hidden>', '<p id="sa-error" class="sa-error" role="alert" hidden>')
    body=body.replace('<p id="sa-summary" role="status" aria-live="polite">', '<p id="sa-action-status" role="status" aria-live="polite" aria-atomic="true"></p><p id="sa-summary" role="status" aria-live="polite" aria-atomic="true">')
    body=body.replace('<p id="sa-current-formula" class="sa-formula"></p>', '''<p id="sa-current-formula" class="sa-formula"></p><p id="sa-entry-links"></p>
<div class="sa-window-tools" role="group" aria-label="Move or resize the sample window"><button id="sa-previous-window" type="button">← Previous window</button><button id="sa-next-window" type="button">Next window →</button><button id="sa-fewer" type="button">Fewer terms</button><button id="sa-more" type="button">More terms</button><button id="sa-table-open" type="button">Read exact values</button></div>''')
    body=body.replace('<div id="sa-plot"></div>', '<p id="sa-plot-help" class="sa-note">Tab to the graph; arrows move between marks. Home/End jump, and Enter or Space reads a value. Inspection pauses animation. Use the exact table for another view.</p><div id="sa-plot" aria-describedby="sa-plot-help"></div>')
    body=body.replace('<p id="sa-inspect" class="sa-inspect">Focus a plot point with Tab, or select it, to read its exact value. Lines connect discrete samples.</p>', '''<div class="sa-point-tools" role="group" aria-label="Inspect plot marks"><button id="sa-previous-point" type="button">Previous mark</button><button id="sa-next-point" type="button">Next mark</button></div><p id="sa-inspect" class="sa-inspect">Focus or select a mark to read its exact value. Lines connect discrete samples.</p><p id="sa-point-announcement" class="sa-sr-only" role="status" aria-live="polite" aria-atomic="true"></p>
<div class="sa-window-tools" role="group" aria-label="Use the displayed values"><button id="sa-copy-values" type="button">Copy displayed values</button><button id="sa-search-values" type="button">Search displayed integers</button><a id="sa-oeis-terms" href="https://oeis.org/">Look up integers in OEIS</a></div>''')
    body=body.replace('<details><summary>Exact values and plotted coordinates</summary><div class="table-scroll"', '<details id="sa-table-detail"><summary>Exact values and plotted coordinates</summary><div id="sa-values-region" class="table-scroll"')
    exports=re.search(r'<button id="sa-csv".*?</button><button id="sa-svg".*?</button><button id="sa-png".*?</button>',body,re.S)
    if exports:
        controls=exports[0]+'<button id="sa-json" type="button">Export view JSON</button>'
        body=body[:exports.start()]+body[exports.end():]
        body=body.replace('<details id="sa-table-detail">','<details id="sa-export-options" class="sa-export-options"><summary>Export data and figures</summary><div class="sa-toolbar">'+controls+'</div></details><details id="sa-table-detail">')
    body=body.replace('Loading the interactive explorer. The full catalogue is available below.','The full catalogue is available below. JavaScript adds interactive search and plotting.')
    return body


def discovery_section(entries):
    topics=['elementary','polynomial','combinatorics','partitions','recurrence','reciprocal','signed','binomial']
    browse=''.join('<a href="?topic='+tag+'#find">'+e(tag)+' <span>('+str(sum(tag in x['tags'] for x in entries))+')</span></a>' for tag in topics)
    return ('<nav class="sa-topic-index" aria-label="Browse sequence topics">'+browse+'</nav>'
        '<section id="discover" aria-labelledby="sa-discovery-title"><h2 id="sa-discovery-title" tabindex="-1">What could these terms be?</h2><p>Look beyond a literal match. Try differences, sums, sign changes, binomial transforms, and shifted input against this catalogue.</p>'
        '<div id="sa-discovery-controls" hidden><form id="sa-discovery-form"><label for="sa-discovery-input">Your consecutive integer terms</label><textarea id="sa-discovery-input" rows="3" maxlength="20000" aria-describedby="sa-discovery-help" placeholder="0, 1, 4, 9, 16, 25, 36, 49"></textarea><p id="sa-discovery-help" class="sa-note">6–64 integers; a tested transform must leave at least six terms. All available transformed input terms must match consecutively within the 64 stored catalogue terms.</p>'
        '<label class="sa-check" for="sa-discovery-both"><input id="sa-discovery-both" type="checkbox"> Also compare transformed catalogue terms</label><div class="sa-toolbar"><button type="submit">Find connections</button><button type="button" id="sa-discovery-example">Try square numbers</button><button type="button" id="sa-discovery-share">Copy discovery link</button><button type="button" id="sa-random-entry">Random entry</button><button type="button" id="sa-discovery-export" hidden>Download discovery JSON</button></div></form><label id="sa-discovery-copy-fallback" for="sa-discovery-copy-text" hidden>Discovery link<textarea id="sa-discovery-copy-text" readonly></textarea></label><p id="sa-discovery-error" class="sa-error" role="alert" hidden></p><p id="sa-discovery-status" role="status" aria-live="polite" aria-atomic="true"></p><ol id="sa-discovery-results" class="sa-results"></ol><details><summary>Which transformations are tested?</summary><ul><li>Original terms; omit the first one or two input terms.</li><li>First and second differences; partial sums.</li><li>Alternating signs and absolute values.</li><li>Binomial and inverse binomial transforms of the input.</li></ul><p>With the optional comparison enabled, catalogue terms also use differences, sums, and sign transforms. Initial undefined differences are skipped, with their indices reported. Binomial transforms start at index zero.</p></details></div>'
        '<p class="sa-note">Inspired by the <a href="https://oeis.org/wiki/Sequence_transforms">OEIS transform toolbox</a>. Matches are finite suggestions, not sequence identities or evidence of novelty. This tool searches '+str(len(entries))+' local entries; <a id="sa-discovery-oeis" href="https://oeis.org/">open OEIS</a> for a broader search. Pasted terms stay in this browser unless you copy or open a link containing them.</p></section>')


def build(site):
    entries = catalogue()
    graph = connection_graph(entries)
    site.write('assets/sequence-atlas-connections.json',json.dumps(graph,ensure_ascii=False,indent=2)+'\n')
    site.write('assets/sequence-atlas-index.csv',index_csv(entries,graph))
    snapshot_path = site.root/'manifests/sequence-atlas-oeis.json'
    snapshot = json.loads(snapshot_path.read_text(encoding='utf-8')) if snapshot_path.exists() else None
    if snapshot:
        for entry in entries:
            entry['matches'] = snapshot['matches'].get(entry['id'], [])
    data = dict(schema=1, entries=[dict(entry,formulas=formula_variants(entry)) for entry in entries], snapshot=snapshot,
        scope='Search covers the curated Komorebi catalogue. OEIS comparisons are finite comparisons, not originality or identity proofs.')
    raw = json.dumps(data, ensure_ascii=False, separators=(',', ':'))+'\n'
    site.write('assets/sequence-atlas-data.json', raw)
    theme=(site.root/'website/assets/sequence-reading-theme.mjs').read_text(encoding='utf-8')
    theme=theme.replace("'./sequence-research-ui.mjs'","'./sequence-research-ui.mjs?v="+hashlib.sha256((site.root/'website/assets/sequence-research-ui.mjs').read_bytes()).hexdigest()[:12]+"'")
    version = lambda name: hashlib.sha256(theme.encode('utf-8') if name=='sequence-reading-theme.mjs' else (site.root/'website/assets'/name).read_bytes()).hexdigest()[:12]
    css = '<link rel="stylesheet" href="assets/sequence-atlas.css?v='+version('sequence-atlas.css')+'">'
    cards = ''.join('<article class="sa-card" data-sequence="'+x['id']+'"><p class="sa-label">'+x['id']+'</p><h3><a href="sequences/'+x['id']+'.html">'+e(x['title'])+'</a></h3>'
        +'<p class="sa-terms">'+e(', '.join(x['terms'][:8]))+'…</p><details class="sa-card-detail"><summary>Formula, sources, and reference matches</summary>'+entry_body(x)+'</details><div class="sa-card-actions"><button type="button" data-load="'+x['id']+'" hidden>Explore this sequence</button><button type="button" data-save-sequence="'+x['id']+'" aria-pressed="false" hidden>Save entry</button></div></article>' for x in entries)
    options = ''.join('<option value="'+x['id']+'">'+e(x['title'])+'</option>' for x in entries)
    snapshot_note = ('OEIS reference data downloaded '+e(snapshot['retrieved_at'][:10])+'; '+str(snapshot['sequence_count'])+' exported sequences scanned.' if snapshot else
        'OEIS reference data is unavailable. Reference links remain available; catalogue search is local.')
    body = css+'''<div class="sequence-atlas" id="sequence-atlas">
<header class="sa-intro"><p class="sa-label">Komorebi / sequences and formulas</p><h1>Curated sequence generators</h1>
<p>Generate terms and explore transforms for 38 curated sequences. This tool extends their stored prefixes within its stated limits. <a href="sequence-library.html">Search all sequence records in the complete library</a> for every family, formula, and stored-data plot.</p>
<nav aria-label="Atlas sections"><a href="#explorer">Plot explorer</a><a href="#catalogue">Sequence catalogue</a><a href="sequence-archive.html">Research archive · 90 records</a><a href="#reference">Sources and scope</a></nav></header>
<noscript><p class="notice">The catalogue, formulas, term tables, and CSV downloads work without JavaScript. Enable JavaScript for interactive plots and filtering.</p></noscript>
<section id="explorer" aria-labelledby="explorer-title"><h2 id="explorer-title" tabindex="-1">Plot explorer</h2>
<div id="sa-workspace" hidden><div class="sa-controls">
<label>Sequence<select id="sa-sequence">'''+options+'''<option value="custom">Pasted integer sequence</option></select></label>
<label>Compare with<select id="sa-compare"><option value="">No comparison</option>'''+options+'''</select></label>
<label>View<select id="sa-view"><option value="standard">Sequence values</option><option value="mod">Values modulo m</option><option value="grid">Residue grid (n mod m, a(n) mod m)</option><option value="frequency">Residue frequencies</option><option value="pairs">Successive-term pairs</option></select></label>
<label>Transform<select id="sa-transform"><option value="raw">Original terms</option><option value="difference">First differences</option><option value="sum">Partial sums</option><option value="ratio">Successive ratios</option><option value="average">Running averages</option></select></label>
<label>Scale<select id="sa-scale"><option value="linear">Linear</option><option value="log">Log10 (positive values)</option><option value="signed-log">Signed log10(1 + |value|)</option></select></label>
<label>Marks<select id="sa-marks"><option value="points">Points</option><option value="line">Lines and points</option><option value="bars">Bars</option></select></label>
<label>First index<input id="sa-start" type="number" min="0" max="999" step="1" value="0"></label>
<label>Terms shown<input id="sa-count" type="number" min="2" max="1000" step="1" value="32"></label>
<label>Modulus m<input id="sa-modulus" type="number" min="2" max="128" step="1" value="7"></label>
<label>Color points<select id="sa-color"><option value="series">By sequence</option><option value="value">By a(n) mod m</option><option value="index">By n mod m</option></select></label>
<label>Reciprocal spacing N<select id="sa-N">'''+''.join(f'<option>{n}</option>' for n in range(2,9))+'''</select></label>
<label>Reciprocal power r<select id="sa-power"><option>1</option><option>2</option><option>3</option></select></label>
</div><div id="sa-custom-panel" hidden><label for="sa-custom">Paste integer terms (commas or spaces)</label><textarea id="sa-custom" rows="3" maxlength="20000" placeholder="0, 1, 1, 2, 3, 5, 8, 13"></textarea><p class="sa-note">Up to 1,000 terms, 300 digits per term, and 20,000 characters. Pasted data starts at index 0 and is labelled unreviewed.</p></div>
<div class="sa-toolbar"><button id="sa-animate" type="button" aria-pressed="false">Animate modulus</button><button id="sa-reset" type="button">Reset view</button><button id="sa-share" type="button">Copy view link</button><button id="sa-csv" type="button">Export exact CSV</button><button id="sa-svg" type="button">Export SVG</button><button id="sa-png" type="button">Export PNG</button></div>
<p id="sa-error" role="alert" hidden></p><label id="sa-share-fallback" hidden>View link<input id="sa-share-link" readonly></label>
<p id="sa-summary" role="status" aria-live="polite"></p><p id="sa-current-formula" class="sa-formula"></p>
<figure class="sa-figure"><div id="sa-plot"></div><figcaption id="sa-caption"></figcaption></figure>
<p id="sa-inspect" class="sa-inspect">Focus a plot point with Tab, or select it, to read its exact value. Lines connect discrete samples.</p>
<p id="sa-period" class="sa-note"></p><p id="sa-window" class="sa-note"></p>
<details><summary>Exact values and plotted coordinates</summary><div class="table-scroll" tabindex="0" role="region" aria-label="Exact sequence values"><table><caption id="sa-table-caption">Displayed samples</caption><thead><tr><th scope="col">Sequence</th><th scope="col">n</th><th scope="col">a(n)</th><th scope="col">Transformed value</th><th scope="col">Residue</th><th scope="col">Plot x</th><th scope="col">Plot y</th></tr></thead><tbody id="sa-values"></tbody></table></div></details>
</div><p id="sa-loading">Loading the interactive explorer. The full catalogue is available below.</p></section>
'''+directory_block(entries,graph,cards)+'''
<section id="reference"><h2>Sources, scope, and reuse</h2><p>'''+snapshot_note+'''</p>
<p>These entries organize existing published definitions and classical benchmarks. Formula novelty and sequence novelty require separate review. A finite match does not prove identity; an absent match does not establish novelty. Period suggestions and residue frequencies describe the selected finite window.</p>
<p>Integer terms, differences, sums, and residues are exact. Ratios and averages are exact fractions. Plot coordinates use floating-point approximations; logarithmic views omit nonpositive values. Modular views use the integer transform before any plotting approximation, and are unavailable for fraction-valued transforms.</p>
<p>OEIS reference names and matching excerpts are credited to <a href="https://oeis.org/">The Online Encyclopedia of Integer Sequences</a> and the OEIS Foundation, under <a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a>. Matching and presentation are our adaptations. Each reference links to its OEIS entry. This atlas is an independent Komorebi project.</p>
<p><a href="assets/sequence-atlas-data.json">Download catalogue and reference data details</a> · <a href="https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/docs/SEQUENCE_ATLAS.md">Sources and reproduction</a> · <a href="collection/demonstrations/SEQUENCE_SHAPES.html">Sequence derivations and Python experiments</a></p>
</section></div>'''
    body=refine_body(body,entries)
    body=body.replace('<figure class="sa-figure">','<div id="sa-plot-presets" class="sp-preset-bar" role="group" aria-label="Plot view presets"></div><p class="sa-note">View presets keep your sequence and index window. Appearance settings are shared across the sequence library.</p><div id="sa-plot-options"></div><figure class="sa-figure">')
    body='<link rel="stylesheet" href="assets/sequence-plot-options.css?v='+version('sequence-plot-options.css')+'">'+body
    discovery_script=(site.root/'website/assets/sequence-atlas-discovery.mjs').read_text(encoding='utf-8')
    for dependency in ('sequence-atlas-core.mjs','sequence-atlas-search.mjs'):
        discovery_script=discovery_script.replace("'./"+dependency+"'","'./"+dependency+'?v='+version(dependency)+"'")
    directory_script=(site.root/'website/assets/sequence-atlas-directory.mjs').read_text(encoding='utf-8').replace("'./sequence-atlas-search.mjs'", "'./sequence-atlas-search.mjs?v="+version('sequence-atlas-search.mjs')+"'")
    site.write('assets/sequence-atlas-directory.mjs',directory_script)
    script = (site.root/'website/assets/sequence-atlas.js').read_text(encoding='utf-8')
    script = script.replace("'./sequence-atlas-core.mjs'", "'./sequence-atlas-core.mjs?v="+version('sequence-atlas-core.mjs')+"'")
    script = script.replace("'./sequence-atlas-data.json'", "'./sequence-atlas-data.json?v="+hashlib.sha256(raw.encode()).hexdigest()[:12]+"'")
    script=script.replace("'./sequence-atlas-discovery.mjs'","'./sequence-atlas-discovery.mjs?v="+hashlib.sha256(discovery_script.encode()).hexdigest()[:12]+"'")
    for name in ('sequence-atlas-search.mjs','sequence-atlas-saved.mjs','sequence-atlas-interface.mjs','sequence-plot-options.mjs','sequence-research-ui.mjs','sequence-reading-theme.mjs'):
        script=script.replace("'./"+name+"'", "'./"+name+'?v='+version(name)+"'")
    script=script.replace("'./sequence-atlas-directory.mjs'", "'./sequence-atlas-directory.mjs?v="+hashlib.sha256(directory_script.encode()).hexdigest()[:12]+"'")
    site.write('assets/sequence-atlas.js', script)
    entry_script=(site.root/'website/assets/sequence-atlas-entry.js').read_text(encoding='utf-8')
    study_core=(site.root/'website/assets/sequence-atlas-study.mjs').read_text(encoding='utf-8').replace("'./sequence-atlas-core.mjs'", "'./sequence-atlas-core.mjs?v="+version('sequence-atlas-core.mjs')+"'")
    study_script=(site.root/'website/assets/sequence-atlas-study.js').read_text(encoding='utf-8').replace("'./sequence-atlas-study.mjs'", "'./sequence-atlas-study.mjs?v="+hashlib.sha256(study_core.encode()).hexdigest()[:12]+"'")
    site.write('assets/sequence-atlas-study.mjs',study_core)
    site.write('assets/sequence-atlas-study.js',study_script)
    entry_script=entry_script.replace("'./sequence-atlas-study.js'", "'./sequence-atlas-study.js?v="+hashlib.sha256(study_script.encode()).hexdigest()[:12]+"'")
    for dependency in ('math-display.mjs','sequence-atlas-saved.mjs','sequence-atlas-core.mjs','sequence-research-ui.mjs','sequence-reading-theme.mjs'):
        entry_script=entry_script.replace("'./"+dependency+"'","'./"+dependency+'?v='+version(dependency)+"'")
    site.write('assets/sequence-atlas-entry.js',entry_script)
    for name in ('math-display.mjs','math-display.css','sequence-navigation.mjs','sequence-redirect.mjs','sequence-atlas-core.mjs', 'sequence-atlas.css','sequence-atlas-search.mjs','sequence-atlas-saved.mjs','sequence-atlas-discovery.mjs','sequence-atlas-interface.mjs','sequence-plot-options.mjs','sequence-plot-options.css','sequence-research-ui.mjs','sequence-reading-theme.mjs','sequence-reading.css'):
        content=(site.root/'website/assets'/name).read_text(encoding='utf-8')
        if name=='sequence-atlas-discovery.mjs':
            content=discovery_script
        elif name=='sequence-reading-theme.mjs':
            content=theme
        site.write('assets/'+name,content)
    # Retain visible wrapping labels and explicit associations for the site audit.
    body = re.sub(r'<label>([^<]*)<(select|input)([^>]*\bid="([^"]+)")', r'<label for="\4">\1<\2\3', body)
    body = body.replace('<label id="sa-share-fallback" hidden>', '<label id="sa-share-fallback" for="sa-share-link" hidden>')
    controls = re.search(r'<div class="sa-controls">(.*?)</div>', body, re.S)
    labels = re.findall(r'<label\b.*?</label>', controls[1], re.S)
    primary = ['sa-sequence', 'sa-view', 'sa-modulus', 'sa-count']
    chosen = [next(label for label in labels if f'for="{key}"' in label) for key in primary]
    advanced = [label for label in labels if label not in chosen]
    body = body[:controls.start()]+('<div class="sa-controls">'+''.join(chosen)+'</div>'
        '<details class="sa-advanced"><summary>Compare sequences, transform values, and adjust the plot</summary>'
        '<div class="sa-controls">'+''.join(advanced)+'</div></details>')+body[controls.end():]
    body += '<script type="module" src="assets/sequence-atlas.js?v='+hashlib.sha256(script.encode()).hexdigest()[:12]+'"></script>'
    body='<link rel="stylesheet" href="assets/sequence-library.css?v='+version('sequence-library.css')+'">'+body+'<link rel="stylesheet" href="assets/sequence-reading.css?v='+version('sequence-reading.css')+'">'
    body=body.replace('<nav class="sa-mode-nav"','<p class="sa-library-link"><a href="sequence-library.html">Search the full sequence and formula library →</a> · formula families, equivalent representations, and OEIS reference matching</p><nav class="sa-mode-nav"',1)
    site.page('sequence-explorer.html', 'Curated sequence generators', body)
    redirect=(site.root/'website/assets/sequence-redirect.mjs').read_text(encoding='utf-8').replace("'./sequence-navigation.mjs'","'./sequence-navigation.mjs?v="+version('sequence-navigation.mjs')+"'")
    site.write('assets/sequence-redirect.mjs',redirect)
    destinations=[('find','sequence-library.html#library-search','Search the sequence library'),('catalogue','sequence-library/index.html','Complete index'),('saved','sequence-library.html?saved=only#library-search','Saved entries'),('explorer','sequence-explorer.html#explorer','Curated sequence generators'),('discover','sequence-explorer.html#discover','Discover connections'),('connections','sequence-explorer.html#discover','Explore sequence relationships'),('reference','sequence-library.html#oeis','Compare with OEIS')]
    handoff='<nav aria-label="Sequence tools"><ul>'+''.join('<li id="'+key+'"><a href="'+e(target)+'">'+label+'</a></li>' for key,target,label in destinations)+'</ul></nav>'
    site.page('sequences.html','Sequence library','<h1>Sequence library</h1><p>Search the complete library of sequence records, formulas, and exact data.</p>'+handoff+'<script type="module" src="assets/sequence-redirect.mjs?v='+hashlib.sha256(redirect.encode()).hexdigest()[:12]+'"></script>')
    site.search.append(dict(title='Curated sequence generators', group='Collection', kind='Examples', work_ids=['paper-iv','monographs-special-functions'], url='sequence-explorer.html', text='Integer sequence formula catalogue exact modular plotting residues recurrence generating function OEIS comparison differences ratios partial sums'))
    for entry in entries:
        identifier = entry['id']
        csv = 'n,a_n\n'+''.join(f'{n},{value}\n' for n, value in enumerate(entry['terms']))
        site.write('sequences/'+identifier+'.csv', csv)
        site.write('sequences/'+identifier+'.txt','# '+identifier+' '+entry['title']+'\n# Stored terms only; index starts at 0.\n'+''.join(f'{n} {value}\n' for n,value in enumerate(entry['terms'])))
        public_base='https://komorebip.github.io/Operation-KOMOREBI/'
        export=dict(entry,public_url=public_base+'sequences/'+identifier+'.html',source_url=entry['source'] if entry['source'].startswith('https:') else public_base+entry['source'],oeis_reference=dict(license='CC-BY-SA-4.0',attribution='The Online Encyclopedia of Integer Sequences, OEIS Foundation Inc.',source='https://oeis.org/',snapshot_retrieved_at=snapshot['retrieved_at'] if snapshot else None))
        site.write('sequences/'+identifier+'.json',json.dumps(export,ensure_ascii=False,indent=2)+'\n')
        rows = ''.join('<tr id="n-'+str(n)+'" tabindex="-1"><th scope="row">'+str(n)+'</th><td>'+value+'</td></tr>' for n, value in enumerate(entry['terms']))
        at=entries.index(entry)
        neighbours=('<a rel="prev" href="'+entries[at-1]['id']+'.html">← '+e(entries[at-1]['title'])+'</a>' if at else '')+('<a rel="next" href="'+entries[at+1]['id']+'.html">'+e(entries[at+1]['title'])+' →</a>' if at+1<len(entries) else '')
        related_score=lambda x:3*(x['kind']==entry['kind'])+4*(x.get('N') is not None and x.get('N')==entry.get('N'))+len(set(x['tags'])&set(entry['tags']))
        related=sorted((x for x in entries if x['id']!=identifier and related_score(x)>0),key=lambda x:(-related_score(x),x['id']))[:3]
        content = ('<link rel="stylesheet" href="../assets/sequence-atlas.css?v='+version('sequence-atlas.css')+'">'
            '<article class="sequence-atlas sa-entry" data-entry-id="'+identifier+'" data-index-kind="'+entry['reading']['index_kind']+'" data-index-factor="'+str(entry['reading']['index_factor'])+'" data-index-label="'+entry['reading']['index_label']+'"><header class="sa-record-header"><a class="sa-back" href="../sequence-library.html#library-search">← Sequence library</a><form class="sa-record-search" hidden action="../sequence-library.html#library-search" role="search" aria-label="Search the sequence catalogue"><label for="sa-record-query" class="sa-sr-only">Sequence name, identifier or terms</label><input id="sa-record-query" name="q" type="search" placeholder="Find another sequence"><button type="submit">Search</button></form><p class="sa-record-id">'+identifier+' <span>'+e(entry['status'])+'</span></p><h1>'+e(entry['title'])+'</h1>'
            '<div class="sa-entry-actions"><a class="sa-primary-link" href="../sequence-explorer.html?sequence='+identifier+'#explorer">Plot this sequence</a><a href="#analysis">Study exact terms</a><button type="button" data-save-sequence="'+identifier+'" aria-pressed="false" hidden>Save entry</button><button id="sa-entry-copy" type="button" hidden>Copy the first 12 terms</button><button id="sa-entry-link" type="button" hidden>Copy link</button></div><p id="sa-entry-status" role="status" aria-live="polite"></p><label id="sa-entry-copy-fallback" for="sa-entry-copy-text" hidden>Text to copy<textarea id="sa-entry-copy-text" readonly></textarea></label></header>'
            '<div class="sa-record-data"><span class="sa-field-label">DATA</span><p class="sa-terms">'+e(', '.join(entry['terms'][:8]))+'…</p><a href="#data">All 64 terms ↓</a></div>'
            '<div class="sa-record-layout"><nav class="sa-entry-outline" aria-label="Entry sections"><span>In this entry</span><a href="#definition">Definition &amp; indexing</a><a href="#formulas">Formulas</a><a href="#examples">Examples</a><a href="#analysis">Study &amp; transforms</a><a href="#programs">Programs</a><a href="#connections">Connections</a><a href="#references">References</a><a href="#data">Exact data</a><a href="#sa-related-title">Related entries</a></nav><div class="sa-record-main">'
            +structured_entry(entry,graph)+'<section id="data"><h2>Exact data and downloads</h2><p><a href="../sequence-explorer.html?seq='+identifier+'#explorer">Open in plot explorer</a> · <a download href="'+identifier+'.csv">Download exact CSV</a></p>'
            '<p><a href="../sequence-explorer.html?sequence='+identifier+'&amp;view=mod#explorer">Explore residues</a> · <a download href="'+identifier+'.txt">Download indexed text (b-file style)</a> · <a download href="'+identifier+'.json">Download entry JSON</a></p>'
            '<div class="table-scroll" tabindex="0" role="region" aria-label="Exact terms"><table><caption>Exact terms, indices 0–63</caption><thead><tr><th scope="col">n</th><th scope="col">a(n)</th></tr></thead><tbody>'+rows+'</tbody></table></div>'
            '</section><section aria-labelledby="sa-related-title"><h2 id="sa-related-title">Related entries</h2><ul>'+''.join('<li><a href="'+x['id']+'.html">'+e(x['title'])+'</a> · '+x['id']+'</li>' for x in related)+'</ul></section>'
            '<nav class="sa-neighbours" aria-label="Previous and next sequence">'+neighbours+'</nav></div></div></article>'
            '<script type="module" src="../assets/sequence-atlas-entry.js?v='+hashlib.sha256(entry_script.encode()).hexdigest()[:12]+'"></script>')
        from sequence_research_notes import entry_details
        content=content.replace('<section id="analysis"',entry_details(entry)+'<section id="analysis"',1)
        site.page('sequences/'+identifier+'.html', entry['title']+' · '+identifier, '<link rel="stylesheet" href="../assets/sequence-library.css?v='+version('sequence-library.css')+'">'+content+'<link rel="stylesheet" href="../assets/sequence-reading.css?v='+version('sequence-reading.css')+'">')
        site.search.append(dict(title=entry['title']+' · '+identifier, group='Collection', kind='Examples', work_ids=entry['work_ids'], url='sequences/'+identifier+'.html', text=entry['formula']+' '+entry['recurrence']+' '+', '.join(entry['terms'][:8])))
    from sequence_archive import build as build_archive
    archive=build_archive(site,entries)
    from sequence_library import build as build_library
    library=build_library(site,entries)
    return dict(entries=len(entries), snapshot=bool(snapshot), archive=archive, library=library)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--id')
    args = parser.parse_args()
    values = catalogue()
    if args.id:
        values = [x for x in values if x['id'] == args.id]
        if not values:
            parser.error('Unknown sequence identifier')
    print(json.dumps(values, indent=2))
