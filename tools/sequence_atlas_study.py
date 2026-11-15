"""Exact finite study tables, also available without browser scripting."""
from fractions import Fraction
from html import escape
from math import comb, gcd

MODES = {
    'raw': ('Original terms', 'b(n) = a(n).'),
    'difference': ('First differences', 'b(n) = a(n) - a(n-1), defined for n >= 1.'),
    'second-difference': ('Second differences', 'b(n) = a(n) - 2a(n-1) + a(n-2), defined for n >= 2.'),
    'sum': ('Partial sums', 'b(n) = a(0) + ... + a(n). Sums always start at index zero.'),
    'ratio': ('Successive ratios', 'b(n) = a(n)/a(n-1). Undefined at n=0 or when a(n-1)=0.'),
    'average': ('Running averages', 'b(n) = (a(0) + ... + a(n))/(n+1). Averages always start at index zero.'),
    'alternating': ('Alternating signs', 'b(n) = (-1)^n a(n), using the original index n.'),
    'absolute': ('Absolute values', 'b(n) = |a(n)|.'),
    'binomial': ('Binomial transform', 'b(n) = sum from k=0 to n of binom(n,k) a(k).'),
    'inverse-binomial': ('Inverse binomial transform', 'b(n) = sum from k=0 to n of (-1)^(n-k) binom(n,k) a(k).'),
    'mod': ('Residues', 'b(n) is the least nonnegative residue of a(n) modulo m.'),
}


def study_model(entry, mode='raw', start=0, count=12, modulus=7):
    """Independent Fraction oracle; n is retained, never reindexed after a window."""
    raw = list(map(int, entry['terms']))
    if mode not in MODES or not 2 <= count <= 32 or not 0 <= start <= len(raw)-count or not 2 <= modulus <= 128:
        raise ValueError('Invalid study options')
    values = []
    for n, a in enumerate(raw):
        if mode == 'difference':
            value = a-raw[n-1] if n else None
        elif mode == 'second-difference':
            value = a-2*raw[n-1]+raw[n-2] if n >= 2 else None
        elif mode == 'sum':
            value = sum(raw[:n+1])
        elif mode == 'ratio':
            value = Fraction(a, raw[n-1]) if n and raw[n-1] else None
        elif mode == 'average':
            value = Fraction(sum(raw[:n+1]), n+1)
        elif mode == 'alternating':
            value = (-1)**n*a
        elif mode == 'absolute':
            value = abs(a)
        elif mode in ('binomial', 'inverse-binomial'):
            value = sum(((-1)**(n-k) if mode == 'inverse-binomial' else 1)*comb(n,k)*raw[k] for k in range(n+1))
        elif mode == 'mod':
            value = a % modulus
        else:
            value = a
        values.append(None if value is None else Fraction(value))
    sample = values[start:start+count]
    defined = [v for v in sample if v is not None]
    integers = [int(v) for v in defined if v.denominator == 1]
    common = 0
    for value in integers:
        common = gcd(common, value)
    encode = lambda value: None if value is None else str(value)
    ladder = [[sum((-1)**k*comb(order,k)*raw[n-k] for k in range(order+1)) if n >= order else None for n in range(start, start+min(count,8))] for order in range(5)]
    return dict(rows=[dict(n=n, value=encode(values[n])) for n in range(start,start+count)],
        facts=dict(defined=len(defined), undefined=count-len(defined), integers=len(integers),
            zero=sum(v == 0 for v in defined), positive=sum(v > 0 for v in defined), negative=sum(v < 0 for v in defined),
            even=sum(v % 2 == 0 for v in integers), odd=sum(v % 2 != 0 for v in integers),
            gcd=str(common) if defined and len(integers) == len(defined) else None),
        ladder=[[encode(v) for v in row] for row in ladder])


def study_block(entry):
    model = study_model(entry)
    facts = model['facts']
    rows = ''.join('<tr><th scope="row">'+str(row['n'])+'</th><td>'+row['value']+'</td></tr>' for row in model['rows'])
    ladder = ''.join('<tr><th scope="row">'+('a(n)' if k == 0 else 'Difference '+str(k))+'</th>'+''.join('<td>'+('undefined' if v is None else v)+'</td>' for v in row)+'</tr>' for k,row in enumerate(model['ladder']))
    options = ''.join('<option value="'+key+'">'+escape(label)+'</option>' for key,(label,_) in MODES.items())
    return ('<section id="analysis" class="sa-study"><p class="sa-section-kicker">A closer look</p><h2>Study this sequence</h2>'
        '<p>Work with exact values, compare differences, and follow a pattern into search or a plot. Indices below are the entry’s original n; transformations act on its stored integers.</p>'
        '<form id="sa-study-form" class="sa-study-controls" hidden><label for="sa-study-transform">Show<select id="sa-study-transform">'+options+'</select></label>'
        '<label for="sa-study-start">First index<input id="sa-study-start" type="number" min="0" max="62" value="0" step="1" required></label>'
        '<label for="sa-study-count">Index positions<input id="sa-study-count" type="number" min="2" max="32" value="12" step="1" required></label>'
        '<label id="sa-study-modulus-field" for="sa-study-modulus" hidden>Modulus<input id="sa-study-modulus" type="number" min="2" max="128" value="7" step="1" required></label>'
        '<button type="submit">Apply</button></form><p id="sa-study-error" class="sa-error" role="alert" hidden></p>'
        '<p id="sa-study-rule" class="sa-study-rule">b(n) = a(n).</p><p id="sa-study-range" class="sa-note">Indices 0–11 of the 64 stored terms. Undefined values retain their index positions.</p>'
        '<dl id="sa-study-facts" class="sa-study-facts"><div><dt>Defined values</dt><dd>12 of 12</dd></div>'
        '<div><dt>Signs in this sample</dt><dd>'+str(facts['positive'])+' positive · '+str(facts['zero'])+' zero · '+str(facts['negative'])+' negative</dd></div>'
        '<div><dt>Integer parity</dt><dd>'+str(facts['even'])+' even · '+str(facts['odd'])+' odd</dd></div><div><dt>GCD of defined values</dt><dd>'+facts['gcd']+'</dd></div></dl>'
        '<div class="sa-study-actions"><a id="sa-study-plot" href="../sequences.html?sequence='+entry['id']+'&amp;view=standard&amp;count=12#explorer">Plot this window</a>'
        '<a id="sa-study-search" href="../sequences.html?q='+','.join(entry['terms'][:8])+'#find">Search these integers</a>'
        '<a id="sa-study-discover" href="../sequences.html?discover='+','.join(entry['terms'][:12])+'#discover">Discover connections</a>'
        '<button id="sa-study-copy" type="button" hidden>Copy indexed values</button><button id="sa-study-share" type="button" hidden>Copy study link</button>'
        '<button id="sa-study-csv" type="button" hidden>Download CSV</button><button id="sa-study-json" type="button" hidden>Download study JSON</button></div>'
        '<p id="sa-study-action-note" class="sa-note">Search uses the first 8 integers in this window. Discovery uses its first 12.</p>'
        '<p id="sa-study-status" role="status" aria-live="polite" aria-atomic="true"></p>'
        '<label id="sa-study-copy-fallback" for="sa-study-copy-text" hidden>Text to copy<textarea id="sa-study-copy-text" readonly></textarea></label>'
        '<div class="table-scroll sa-study-values" tabindex="0" role="region" aria-label="Exact study values"><table id="sa-study-values"><caption>Original terms, n=0–11</caption><thead><tr><th scope="col">n</th><th scope="col">b(n)</th></tr></thead><tbody>'+rows+'</tbody></table></div>'
        '<div class="sa-study-paging" hidden><button id="sa-study-previous" type="button">← Previous window</button><button id="sa-study-next" type="button">Next window →</button></div>'
        '<details class="sa-study-differences"><summary>Open the difference table</summary><p>Backward differences of the original stored integers, before the selected transform: difference k at n is the difference of order k-1 at n minus its value at n-1. The first k positions are undefined. This table shows up to eight indices of the selected window.</p>'
        '<p id="sa-study-observation" class="sa-note">A constant row in this finite table is an observation about the displayed sample.</p>'
        '<div class="table-scroll" tabindex="0" role="region" aria-label="Backward difference table"><table id="sa-study-differences"><caption>Original integers and backward differences, n=0–7</caption><thead><tr><th scope="col">Order</th>'+''.join('<th scope="col">n='+str(n)+'</th>' for n in range(8))+'</tr></thead><tbody>'+ladder+'</tbody></table></div></details>'
        '<p class="sa-note">All statistics describe this finite window. A constant difference row or a transform match does not establish an infinite identity. Inspired by the <a href="https://oeis.org/wiki/Sequence_transforms">OEIS transform toolbox</a>.</p></section>')
