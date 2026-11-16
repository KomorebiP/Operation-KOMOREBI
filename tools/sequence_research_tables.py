"""Finite coefficient tables and columns from the published Komorebi registry.

These expose complete polynomial rows, not new historical priority claims.
"""
from bisect import bisect_right
from functools import lru_cache
from html import escape as e
from math import comb

ROWS = 13

def exact_integer(value):
    if getattr(value,'denominator',1)!=1:raise ValueError('Expected an integral coefficient; refusing to truncate a rational value')
    return int(value)


def cell_coordinates(entry, index):
    table = entry['triangle']
    row = bisect_right(table['row_offsets'], index) - 1
    if row < 0 or index >= table['row_offsets'][row] + table['row_lengths'][row]:
        raise ValueError('Cell index lies outside the stored triangle')
    return row, index - table['row_offsets'][row]


def triangle_section(entry):
    if not entry.get('triangle'):
        return ''
    table = entry['triangle']; width = max(table['row_lengths'])
    head = '<th scope="col">Row n / column k</th>' + ''.join('<th scope="col">'+str(k)+'</th>' for k in range(width))
    body = ''
    for n, (start, size) in enumerate(zip(table['row_offsets'], table['row_lengths'])):
        cells = ''.join('<td'+(' class="sl-zero"' if entry['terms'][start+k]=='0' else '')+'><a href="#n-'+str(start+k)+'" title="Row '+str(n)+', column '+str(k)+'">'+entry['terms'][start+k]+'</a></td>' for k in range(size))
        body += '<tr><th scope="row">'+str(n)+'</th>'+cells+('<td class="sl-outside" aria-label="Outside the row" colspan="'+str(width-size)+'"></td>' if size<width else '')+'</tr>'
    return '<section id="triangle"><h2>Coefficient triangle</h2><p>'+e(table['description'])+' Select a coefficient to find its flat index in the exact table. The row selector in the plot also displays the complete row polynomial.</p><p class="sl-triangle-help" hidden>Tab to the triangle. Use arrow keys to move between coefficients, Home/End within a row, and Enter to find the exact indexed value.</p><div class="sar-scroll sl-triangle" tabindex="0" role="region" aria-label="Coefficient triangle, rows and columns"><table><caption>Complete stored rows n=0–'+str(len(table['row_lengths'])-1)+'; coefficients retain their signs and zeros.</caption><thead><tr>'+head+'</tr></thead><tbody>'+body+'</tbody></table></div></section>'


@lru_cache(maxsize=1)
def research_additions():
    from sequence_formula_catalogue import record, variant, REGISTRY_URL, secancy_polynomials, theta_polynomial_rows, inverse_power, hyper, COUNT
    entries = []

    def add_table(identifier, title, kind, rows, forms, source, variable='x', multiplier=1, research=True, **parameters):
        flat = [value for row in rows for value in row]
        item = record(identifier, title, kind, flat, forms, N=parameters.pop('N', multiplier), degree='row degree', research_addition=True, **parameters)
        offsets=[]; position=0
        for row in rows:
            offsets.append(position); position+=len(row)
        item.update(index_symbol='j', source=source, triangle=dict(row_lengths=list(map(len,rows)), row_offsets=offsets, variable=variable, degree_multiplier=multiplier, description='Row n lists the ordinary coefficients in '+variable+', in increasing column order k. The flat index j counts all preceding rows, then advances by k.'), explanation='The local j is a row-major cell index. It is not the polynomial degree n. All complete rows n=0–12 are stored, including zero coefficients.', status='Research-derived coefficient table · historical novelty unassessed' if research else 'Classical block kernel · used in Komorebi transfer calculus')
        item['tags'] += ['triangle','coefficient table','polynomial coefficients'] + (['research-derived'] if research else ['project kernel'])
        entries.append(item)
        return item

    for N in range(2,13):
        source=REGISTRY_URL+'#L489'
        forms=[variant('Ordinary parameter coefficients','coefficient formula',f'T(n,k)=[r^k] P_({N},n)(r)\nP_({N},n)(r)=({N}n)! [z^({N}n)] D_{N}(z)^(-r)\nD_{N}(z)=sum_(m>=0) (-1)^m z^({N}m)/({N}m)!', '0≤k≤n. These are ordinary coefficients in r; no k! scaling is applied.',source),
               variant('Finite composition formula','finite sum',f'T(n,k)=({N}n)! sum_(ell=k)^n [ell,k]_1/ell! * (-1)^(n+ell) sum_(q_1+...+q_ell=n; q_i>=1) product_i 1/({N}q_i)!', '[ell,k]_1 denotes unsigned first-kind Stirling numbers. T(0,0)=1. For n>0 the constant coefficient is zero.',source),
               variant('Block-binomial parameter law','polynomial identity',f'P_({N},n)(r+s)=sum_(q=0)^n binom({N}n,{N}q) P_({N},q)(r) P_({N},n-q)(s)', 'Evaluating a row polynomial at a nonnegative integer r recovers the reciprocal-power family.',source)]
        item=add_table(f'KFOR-TRI-P-{N:02d}',f'Secancy coefficient triangle · N={N}','secancy coefficient triangle',secancy_polynomials(N,ROWS),forms,source,'r',N,N=N)
        item['related_records']=[dict(id=f'KFOR-P-{N:02d}-{k:02d}',note=f'The k={k} column, continued through 24 nonzero-index positions.') for k in (1,2,3)]

    source=REGISTRY_URL+'#L525'
    add_table('KFOR-TRI-H','Euler-transfer theta coefficient triangle','theta coefficient triangle',theta_polynomial_rows(ROWS),[
        variant('Theta coefficient definition','coefficient formula','T(n,k)=[x^k] Theta_(2n)(x)\nTheta_(2n)(x)=(2n)! [z^(2n)] sech(xz) sech(z)^x','Row n has degree 2n, so 0≤k≤2n. Its flat index is j=n^2+k.',source),
        variant('Secancy-polynomial convolution','finite sum','T(n,k)=(-1)^n sum_(q=0)^n binom(2n,2q) A_2(q) [x^(k-2q)] P_(2,n-q)(x)','Coefficients outside the degree range are zero. Signs use the signed sech convention.',source),
        variant('Hypergeometric coefficient definition','hypergeometric','T(n,k)=(2n)! [x^k z^(2n)] ((0F1(;1/2;x^2 z^2/4))^(-1) exp(-x log(0F1(;1/2;z^2/4))))','A bivariate coefficient extraction, not a single hypergeometric term.',source)], source,'x',2,N=2)

    for N in range(2,9):
        for r in range(1,4):
            source=REGISTRY_URL+'#L458'
            q=inverse_power(N,0,r,ROWS)
            rows=[[exact_integer(comb(n,k)*q[(n-k)//N]) if (n-k)%N==0 else 0 for k in range(n+1)] for n in range(ROWS)]
            forms=[variant('Block-Appell coefficient table','coefficient formula',f'T(n,k)=[x^k] E_n(x)\nE_n(x)=n! [z^n] exp(xz) ({hyper(N)})^(-{r})','This is the j=0 congruential block. Rows are ordinary polynomials in x; source degree is n.',source),
                   variant('Sparse coefficient formula','coefficient formula',f'T(n,k)=binom(n,k) c(n-k)\nc(m)=m! [z^m] ({hyper(N)})^(-{r})',f'c(m)=0 unless {N} divides m. Its nonzero coefficients are the reciprocal-power coefficients with alternating signs in the block index. The diagonal equals 1.',source),
                   variant('Appell derivative law','polynomial identity','k*T(n,k)=n*T(n-1,k-1)','For k≥1. Differentiating a row polynomial gives n times the preceding row polynomial.',source)]
            item=add_table(f'KFOR-TRI-A-{N:02d}-{r:02d}',f'Block-Appell coefficient triangle · N={N}, r={r}','block-Appell coefficient triangle',rows,forms,source,'x',1,N=N,power=r)
            item['related_records']=[dict(id=f'KFOR-AC-{N:02d}-{r:02d}-{k:02d}',note=f'The nonzero support of column k={k}, indexed by n={N}m+{k}.') for k in (1,2,3,4)]
            q=inverse_power(N,0,r,COUNT)
            for k in range(1,5):
                values=[exact_integer(comb(N*m+k,k)*v) for m,v in enumerate(q)]
                forms=[variant('Supported Appell column','coefficient formula',f'a(n)=[x^{k}] E_({N}n+{k})(x)\nE_m(x)=m! [z^m] exp(xz) ({hyper(N)})^(-{r})',f'The local index is n. The polynomial row is {N}n+{k}; other rows of this column vanish.',source),
                       variant('Reciprocal-power coefficient formula','coefficient formula',f'a(n)=(-1)^n binom({N}n+{k},{k}) A(n)\nA(n)=({N}n)! [z^({N}n)] D_{N}(z)^(-{r})\nD_{N}(z)=sum_(q>=0) (-1)^q z^({N}q)/({N}q)!','The sign belongs to the positive block denominator used by the congruential Appell family.',source),
                       variant('Hypergeometric coefficient formula','hypergeometric',f'a(n)=(({N}n+{k})!/{k}!) [z^({N}n)] ({hyper(N)})^(-{r})','Both factorial indices and the compressed coefficient exponent retain their original roles.',source)]
                column=record(f'KFOR-AC-{N:02d}-{r:02d}-{k:02d}',f'Block-Appell supported column · N={N}, r={r}, k={k}','block-Appell coefficient column',values,forms,N=N,power=r,k=k,source_shift=k,degree=f'{N}n+{k}',research_addition=True)
                column.update(source=source,status='Research-derived column · historical novelty unassessed',explanation=f'The full coefficient column is zero outside rows congruent to {k} modulo {N}, beginning at row {k}. This record stores its supported values, using local n=0–23 and polynomial row {N}n+{k}.',related_records=[dict(id=item['id'],note='Read the complete stored coefficient triangle and plot individual rows.')])
                column['tags']+=['research-derived','Appell coefficient column','supported column']; entries.append(column)

    for N in range(2,13):
        source=REGISTRY_URL+'#L489'; q=inverse_power(N,0,1,ROWS)
        for inverse in (False,True):
            rows=[[comb(N*n,N*k)*(exact_integer(q[n-k]) if inverse else 1) for k in range(n+1)] for n in range(ROWS)]
            forms=[variant('Block-binomial kernel','term formula',f'T(n,k)=binom({N}n,{N}k)'+(' c(n-k)' if inverse else ''),'0≤k≤n. The normalization selects multiples of N in the ordinary binomial triangle.',source),
                   variant('Transfer action','finite sum','b(n)=sum_(k=0)^n T(n,k) a(k)','This is the lower-triangular operator on complete block-indexed prefixes, not a fixed-length convolution.',source)]
            if inverse:forms.append(variant('Inverse kernel coefficients','coefficient formula',f'c(m)=({N}m)! [z^({N}m)] ({hyper(N)})^(-1)','The forward and inverse block kernels multiply to the identity by the defining reciprocal-series identity.',source))
            add_table(f'KFOR-TRI-B{ "I" if inverse else ""}-{N:02d}',f'{"Inverse block-binomial" if inverse else "Block-binomial"} triangle · N={N}','inverse block-binomial triangle' if inverse else 'block-binomial triangle',rows,forms,source,'x',N,research=False,N=N)
    assert len(entries)==139 and len({entry['id'] for entry in entries})==139
    return entries
