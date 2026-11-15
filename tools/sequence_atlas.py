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
            source=source, work_ids=[] if kind == 'fibonacci' else ['monographs-special-functions'],
            tags=tags, status='Known reference sequence', oeis=oeis, cap=cap))
    for i, entry in enumerate(entries, 1):
        entry.update(id=f'KSEQ-{i:06d}', offset=0, terms=list(map(str, terms(entry))),
            verification='Exact implementation checks; linked sources retain their recorded proof scope.',
            novelty='No originality claim is made for this entry or its formulas.')
    return entries


def e(value):
    return html.escape(str(value), quote=True)


def entry_body(entry, prefix=''):
    identifier = entry['id']
    matches = entry.get('matches', [])
    match_html = ''.join('<li><a href="https://oeis.org/'+e(m['id'])+'">'+e(m['id'])+'</a> — '+e(m['name'])+
        ' ('+str(m['matched_terms'])+' matching terms; excerpt position '+str(m['position'])+')</li>' for m in matches)
    source = entry['source'] if entry['source'].startswith('https:') else prefix+entry['source']
    return ('<p class="sa-label">'+e(identifier)+' · '+e(entry['status'])+'</p>'
        '<p class="sa-formula">'+e(entry['formula'])+'</p><p>'+e(entry['recurrence'])+'</p>'
        '<p>'+e(entry['explanation'])+'</p><p>Index starts at 0. '+e(entry['novelty'])+'</p>'
        '<p class="sa-terms">'+e(', '.join(entry['terms'][:12]))+'…</p>'
        '<p><a href="'+e(source)+'">Read the definition and derivation</a>'
        +(' · <a href="https://oeis.org/'+entry['oeis']+'">Reference '+entry['oeis']+'</a>' if entry['oeis'] else '')+'</p>'
        + ('<details><summary>OEIS snapshot matches</summary><p>Finite contiguous matches in the recorded snapshot; matching terms alone do not prove sequence identity. Positions count from zero within the exported excerpt, not the sequence’s mathematical offset.</p><ul>'+match_html+'</ul></details>' if matches else
           '<p class="sa-note">No six-term match recorded in the loaded reference snapshot. This is not evidence of novelty.</p>'))


def build(site):
    entries = catalogue()
    snapshot_path = site.root/'manifests/sequence-atlas-oeis.json'
    snapshot = json.loads(snapshot_path.read_text(encoding='utf-8')) if snapshot_path.exists() else None
    if snapshot:
        for entry in entries:
            entry['matches'] = snapshot['matches'].get(entry['id'], [])
    data = dict(schema=1, entries=entries, snapshot=snapshot,
        scope='Search covers the curated Komorebi catalogue. OEIS snapshot matches are finite comparisons, not originality or identity proofs.')
    raw = json.dumps(data, ensure_ascii=False, separators=(',', ':'))+'\n'
    site.write('assets/sequence-atlas-data.json', raw)
    version = lambda name: hashlib.sha256((site.root/'website/assets'/name).read_bytes()).hexdigest()[:12]
    css = '<link rel="stylesheet" href="assets/sequence-atlas.css?v='+version('sequence-atlas.css')+'">'
    cards = ''.join('<article class="sa-card" data-sequence="'+x['id']+'"><h3><a href="sequences/'+x['id']+'.html">'+e(x['title'])+'</a></h3>'
        +entry_body(x)+'<button type="button" data-load="'+x['id']+'" hidden>Explore this sequence</button></article>' for x in entries)
    options = ''.join('<option value="'+x['id']+'">'+e(x['title'])+'</option>' for x in entries)
    snapshot_note = ('Reference snapshot retrieved '+e(snapshot['retrieved_at'])+'; '+str(snapshot['sequence_count'])+' exported sequences scanned.' if snapshot else
        'No OEIS bulk snapshot has been loaded. Reference links remain available; catalogue search is local.')
    body = css+'''<div class="sequence-atlas" id="sequence-atlas">
<header class="sa-intro"><p class="sa-label">Komorebi / sequences and formulas</p><h1>Find a sequence.<br><em>Explore its structure.</em></h1>
<p>Follow exact integer sequences from their formulas to their plots. Compare families, change the modulus, and return to the derivations.</p>
<nav aria-label="Atlas sections"><a href="#explorer">Plot explorer</a><a href="#catalogue">Sequence catalogue</a><a href="#reference">Sources and scope</a></nav></header>
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
<section id="catalogue" aria-labelledby="catalogue-title"><h2 id="catalogue-title">Sequence catalogue</h2>
<div id="sa-search-controls" hidden><label for="sa-query">Search names, formulas, identifiers, or integer terms</label><input id="sa-query" type="search" placeholder="Try Fubini, N=4, A000364, or 1, 1, 69" maxlength="20000">
<label>Entry type<select id="sa-filter"><option value="all">All entries</option><option value="reference">Known reference sequences</option><option value="family">Published reciprocal families</option></select></label></div>
<p id="sa-search-status" role="status">'''+str(len(entries))+''' entries. Pasted-term searches compare contiguous terms in this catalogue’s recorded samples.</p>
<div class="sa-catalogue">'''+cards+'''</div></section>
<section id="reference"><h2>Sources, scope, and reuse</h2><p>'''+snapshot_note+'''</p>
<p>These entries organize existing published definitions and classical benchmarks. Formula novelty and sequence novelty require separate review. A finite match does not prove identity; an absent match does not establish novelty. Period suggestions and residue frequencies describe the selected finite window.</p>
<p>Integer terms, differences, sums, and residues are exact. Ratios and averages are exact fractions. Plot coordinates use floating-point approximations; logarithmic views omit nonpositive values. Modular views use the integer transform before any plotting approximation, and are unavailable for fraction-valued transforms.</p>
<p>OEIS reference names and matching excerpts are credited to <a href="https://oeis.org/">The Online Encyclopedia of Integer Sequences</a> and the OEIS Foundation, under <a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a>. Matching and presentation are our adaptations. Each reference links to its OEIS entry. This atlas is an independent Komorebi project.</p>
<p><a href="assets/sequence-atlas-data.json">Download catalogue JSON and snapshot metadata</a> · <a href="https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/docs/SEQUENCE_ATLAS.md">Maintenance and reproducibility</a> · <a href="collection/demonstrations/SEQUENCE_SHAPES.html">Sequence derivations and Python experiments</a></p>
</section></div>'''
    script = (site.root/'website/assets/sequence-atlas.js').read_text(encoding='utf-8')
    script = script.replace("'./sequence-atlas-core.mjs'", "'./sequence-atlas-core.mjs?v="+version('sequence-atlas-core.mjs')+"'")
    script = script.replace("'./sequence-atlas-data.json'", "'./sequence-atlas-data.json?v="+hashlib.sha256(raw.encode()).hexdigest()[:12]+"'")
    site.write('assets/sequence-atlas.js', script)
    for name in ('sequence-atlas-core.mjs', 'sequence-atlas.css'):
        site.write('assets/'+name, (site.root/'website/assets'/name).read_text(encoding='utf-8'))
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
    site.page('sequences.html', 'Sequence and Formula Atlas', body)
    site.search.append(dict(title='Sequence and Formula Atlas', group='Collection', kind='Examples', work_ids=['paper-iv','monographs-special-functions'], url='sequences.html', text='Integer sequence formula catalogue exact modular plotting residues recurrence generating function OEIS comparison differences ratios partial sums'))
    for entry in entries:
        identifier = entry['id']
        csv = 'n,a_n\n'+''.join(f'{n},{value}\n' for n, value in enumerate(entry['terms']))
        site.write('sequences/'+identifier+'.csv', csv)
        rows = ''.join('<tr><th scope="row">'+str(n)+'</th><td>'+value+'</td></tr>' for n, value in enumerate(entry['terms']))
        content = ('<link rel="stylesheet" href="../assets/sequence-atlas.css?v='+version('sequence-atlas.css')+'">'
            '<article class="sequence-atlas"><p><a href="../sequences.html">← Sequence and Formula Atlas</a></p><h1>'+e(entry['title'])+'</h1>'
            +entry_body(entry, '../')+'<p>'+e(entry['verification'])+'</p><p><a href="../sequences.html?seq='+identifier+'#explorer">Open in plot explorer</a> · <a download href="'+identifier+'.csv">Download exact CSV</a></p>'
            '<details><summary>Reproduce these integer terms in Python</summary><p>The generator is maintained in tools/sequence_atlas.py. Run from the repository root:</p>'
            '<pre><code>python -B tools/sequence_atlas.py --id '+identifier+'</code></pre></details>'
            '<div class="table-scroll" tabindex="0" role="region" aria-label="Exact terms"><table><caption>Exact terms, indices 0–63</caption><thead><tr><th scope="col">n</th><th scope="col">a(n)</th></tr></thead><tbody>'+rows+'</tbody></table></div></article>')
        site.page('sequences/'+identifier+'.html', entry['title']+' · '+identifier, content)
        site.search.append(dict(title=entry['title']+' · '+identifier, group='Collection', kind='Examples', work_ids=entry['work_ids'], url='sequences/'+identifier+'.html', text=entry['formula']+' '+entry['recurrence']+' '+', '.join(entry['terms'][:8])))
    return dict(entries=len(entries), snapshot=bool(snapshot))


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
