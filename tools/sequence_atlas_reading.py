"""Reading metadata and index maps; the catalogue generators remain authoritative."""
from fractions import Fraction
from math import factorial
from html import escape

# Definition, meaning of n, displayed formula, symbol guide.
DEFINITIONS = {
    'bell': ('The number of ways to partition an n-element labelled set into nonempty, unordered blocks.', 'n is the number of elements in the set. Blocks are not ordered.', r'B_n=\sum_{k=0}^{n}S(n,k)', 'S(n,k) counts partitions into exactly k nonempty blocks. The empty set has one partition, so B(0)=1.'),
    'fubini': ('The number of partitions of an n-element labelled set when the blocks themselves are ordered.', 'n is the number of elements, not the number of blocks.', r'F_n=\sum_{k=0}^{n}k!\,S(n,k)', 'S(n,k) counts partitions into k blocks; k! orders those blocks. This distinguishes ordered Bell numbers from Bell numbers.'),
    'factorial': ('The product of the integers from 1 through n, with the empty product equal to 1.', 'n is the number of factors; equivalently, the number of distinct objects being permuted.', r'a(n)=n!=\prod_{k=1}^{n}k,\qquad a(0)=1', 'The factorial symbol ! denotes a product. There are n! linear orders of n distinct objects.'),
    'fibonacci': ('The sequence determined by initial values 0 and 1, adding the two previous values at each step.', 'n is the recurrence index, beginning with F(0)=0.', r'F_0=0,\quad F_1=1,\quad F_n=F_{n-1}+F_{n-2}\ (n\ge2)', 'The recurrence is used only from n=2 onward. Both initial values are part of the definition.'),
    'euler': ('The even-index Euler numbers with their signs retained: 1, -1, 5, -61, and so on.', 'n selects the even Euler index 2n. The term a(3) is E_6, not E_3.', r'a(n)=E_{2n}=(-1)^n A_2^{[1]}(n)', 'A_2^[1](n) is the positive secant coefficient in the reciprocal family. Multiplication by (-1)^n restores the alternating Euler signs.'),
    'naturals': ('The nonnegative integers in increasing order, including zero.', 'n is both the position index and the value of the term.', r'a(n)=n', 'The first value is zero because of this definition, not merely because the offset is zero.'),
    'odd': ('The positive odd integers in increasing order.', 'n=0 selects 1; each increment of n adds 2 to the value.', r'a(n)=2n+1', 'The local sequence starts at n=0 even though its first value is 1.'),
    'triangular': ('The sum of the integers from 1 through n: the number of dots in a triangular arrangement with n rows.', 'n is the number of rows. Zero rows contribute zero dots.', r'T_n=\sum_{k=1}^{n}k=\frac{n(n+1)}{2}', 'The sum is empty at n=0. Its first differences, beginning at n=1, are 1, 2, 3, ... .'),
    'square': ('The number of positions in an n by n square array.', 'n is the side length of the square array; n=0 gives the empty array.', r'a(n)=n^2', 'Adjacent differences are 2n-1 for n>=1. The values themselves remain indexed from zero.'),
    'cube': ('The number of positions in an n by n by n cubic array.', 'n is the side length. Zero side length gives zero positions.', r'a(n)=n^3', 'This is the cube of the index, not a recurrence index shifted by one.'),
    'power-two': ('Successive nonnegative integer powers of 2.', 'n is the exponent. The zeroth power is 1.', r'a(n)=2^n', 'Each new value is twice the previous value. The initial value is a(0)=1.'),
    'power-three': ('Successive nonnegative integer powers of 3.', 'n is the exponent. The zeroth power is 1.', r'a(n)=3^n', 'Each new value is three times the previous value. The initial value is a(0)=1.'),
    'catalan': ('The number of balanced parenthesis strings with n matching pairs, equivalently binom(2n,n)/(n+1).', 'n is the number of matching pairs. C(0)=1 counts the empty string.', r'C_n=\frac{1}{n+1}\binom{2n}{n}', 'The binomial symbol counts choices of n objects from 2n. The division by n+1 is part of the definition.'),
    'central-binomial': ('The number of ways to choose n objects from a set of 2n distinct objects.', 'n is the size of the chosen subset; the containing set has size 2n.', r'a(n)=\binom{2n}{n}=\frac{(2n)!}{(n!)^2}', 'At n=0 there is one choice: the empty subset. The term at n is (n+1) times the Catalan term at the same index.'),
    'partition': ('The number of unordered sums of positive integers whose total is n.', 'n is the integer being partitioned. Reordering the summands does not create a new partition.', r'\sum_{n\ge0}p(n)x^n=\prod_{k\ge1}\frac{1}{1-x^k}', 'The empty sum is the unique partition of zero. These partition numbers count different objects from partitions of a labelled set (Bell numbers).'),
    'lucas': ('The Fibonacci recurrence with initial values 2 and 1 instead of 0 and 1.', 'n is the recurrence index. L(0)=2 and L(1)=1 are both required.', r'L_0=2,\quad L_1=1,\quad L_n=L_{n-1}+L_{n-2}\ (n\ge2)', 'Identical recurrence rules can define different sequences when the initial values differ.'),
    'pell': ('The sequence starting 0, 1 in which the next value is twice the previous value plus the value before that.', 'n is the recurrence index, beginning with P(0)=0.', r'P_0=0,\quad P_1=1,\quad P_n=2P_{n-1}+P_{n-2}\ (n\ge2)', 'The coefficient 2 distinguishes the Pell recurrence from the Fibonacci recurrence.'),
}

def reading_metadata(entry):
    kind=entry['kind']
    if kind=='reciprocal':
        N,r=entry['N'],entry['power']
        definition=f'Take the reciprocal of the alternating factorial series with spacing {N}, raise it to power {r}, and multiply each retained coefficient by the factorial of its ordinary degree.'
        meaning=f'n is a compressed coefficient index. It selects ordinary degree {N}n; N={N} and r={r} are fixed for this entry.'
        tex=(r'\begin{gathered}D_{NN}(t)=\sum_{q\ge0}(-1)^q\frac{t^{NN q}}{(NN q)!},\\a(n)=(NN n)!\,[t^{NN n}]D_{NN}(t)^{-RR}\end{gathered}').replace('NN',str(N)).replace('RR',str(r))
        guide=f'[t^k] means the ordinary coefficient of t^k. Multiplication by k! gives the stored factorial-weighted value. Here k={N}n; r={r} is a power, not another sequence index. The variable t is formal; q is a summation index.'
        index_kind,index_label,factor='factorial','Ordinary degree',N
        normalization=f'Divide a(n) by ({N}n)! to recover the ordinary coefficient at degree {N}n. The stored integer includes this factorial weight.'
    else:
        definition,meaning,tex,guide=DEFINITIONS[kind]
        index_kind,index_label,factor=('euler','Euler index',2) if kind=='euler' else ('direct','Sequence index',1)
        normalization='The stored value is the signed Euler number E_(2n), with no additional factorial division.' if kind=='euler' else 'The displayed a(n) is the value defined above; no factorial weighting or index shift is applied.'
    samples=[]
    for n,value in enumerate(entry['terms'][:6]):
        row=dict(n=n,source_index=factor*n,value=value)
        if index_kind=='factorial': row['ordinary_coefficient']=str(Fraction(int(value),factorial(factor*n)))
        samples.append(row)
    return dict(definition=definition,index_meaning=meaning,tex=tex,symbols=guide,index_kind=index_kind,index_label=index_label,index_factor=factor,
        domain='n = 0, 1, 2, ...',normalization=normalization,offset=entry['offset'],stored_range=[0,len(entry['terms'])-1],
        initial_values=[dict(n=n,value=v) for n,v in enumerate(entry['terms'][:3])],samples=samples)

def reading_block(entry):
    m=entry['reading'];e=lambda value:escape(str(value),quote=True)
    source_column=m['index_kind']!='direct'
    headings='<th scope="col">n</th>'+('<th scope="col">'+e(m['index_label'])+'</th>' if source_column else '')+'<th scope="col">a(n)</th>'+('<th scope="col">Ordinary coefficient</th>' if m['index_kind']=='factorial' else '')
    rows=''.join('<tr><th scope="row"><a href="#n-'+str(row['n'])+'">'+str(row['n'])+'</a></th>'+('<td>'+str(row['source_index'])+'</td>' if source_column else '')+'<td>'+e(row['value'])+'</td>'+('<td>'+e(row['ordinary_coefficient'])+'</td>' if m['index_kind']=='factorial' else '')+'</tr>' for row in m['samples'])
    return ('<section id="definition"><p class="sa-section-kicker">01 / Read the sequence</p><h2>Definition and indexing</h2><p class="sa-definition-lede">'+e(m['definition'])+'</p>'
        '<dl class="sa-definition-facts"><div><dt>Argument</dt><dd>'+e(m['domain'])+'</dd></div><div><dt>Local offset</dt><dd>0 — the first term is a(0)</dd></div><div><dt>Meaning of n</dt><dd>'+e(m['index_meaning'])+'</dd></div><div><dt>Value convention</dt><dd>'+e(m['normalization'])+'</dd></div></dl>'
        '<p class="sa-symbol-guide">'+e(m['symbols'])+'</p><h3>Read the first six terms</h3><div class="table-scroll sa-index-map" tabindex="0" role="region" aria-label="Index mapping"><table><caption>How the displayed index maps to the definition</caption><thead><tr>'+headings+'</tr></thead><tbody>'+rows+'</tbody></table></div>'
        '<div class="sa-term-inspector" id="sa-term-inspector" hidden><h3>Inspect an indexed term</h3><form id="sa-term-form"><label for="sa-term-index">Stored index n<input id="sa-term-index" type="number" min="0" max="63" step="1" value="2" aria-describedby="sa-term-help"></label><button type="submit">Inspect term</button></form><p id="sa-term-help" class="sa-note">Choose n=0–63 from the recorded data. The definition extends beyond this stored window.</p><p id="sa-term-error" class="sa-error" role="alert" hidden></p><div id="sa-term-result"><p id="sa-term-label" class="sa-field-label"></p><p class="sa-selected-value"><code id="sa-term-value"></code></p><p id="sa-term-basis" class="sa-note"></p><div class="sa-hit-actions"><button type="button" id="sa-term-copy">Copy this value</button><a id="sa-term-data-link" href="#n-2">Show in data table ↓</a></div></div><p id="sa-term-status" class="sa-sr-only" role="status" aria-live="polite"></p></div>'
        '<details class="sa-index-guide"><summary>Offset, source index, and snapshot position</summary><p>An offset describes the first index, not the value of the first term. Here the local offset is 0, so the first displayed value is a(0), which can be 0, 1, 2, or another value. The stored window is n=0–63; the plot explorer has its own generator limits.</p><p>Reciprocal entries map n to ordinary degree Nn. Signed even Euler entries map n to Euler index 2n. Snapshot match positions count terms within an exported excerpt and do not supply its mathematical offset. See <a href="https://oeis.org/wiki/Offsets">OEIS guidance on offsets</a>.</p></details></section>')
