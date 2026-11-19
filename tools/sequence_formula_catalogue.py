"""Exact, source-linked parameter instances and multiple formula representations.

The enumeration is a documented finite slice of published construction schemas.
Parameter instances are not assertions of pairwise distinct infinite sequences.
"""
from fractions import Fraction
from functools import lru_cache
from html import escape as e
from math import comb, factorial
import re

REGISTRY_PATH = 'monographs/special-functions/supporting-sources/projector-special-functions-registry/Projector_Special_Functions_Registry.tex'
REGISTRY_URL = 'https://github.com/KomorebiP/Operation-KOMOREBI/blob/62973b08e84a71db189423e1fff67de56409fc96/' + REGISTRY_PATH
COUNT = 24


def variant(title, kind, expression, note='', source=REGISTRY_URL):
    return dict(title=title, kind=kind, expression=expression, note=note, source=source)


def hyper_parameters(N, j):
    return [str(Fraction(j + 1 + k, N)) for k in range(N) if j + 1 + k != N]


def hyper(N, j=0, sign=''):
    return f"0F{N-1}(; {', '.join(hyper_parameters(N,j))}; {sign}z^{N}/{N**N})"


@lru_cache(maxsize=None)
def inverse_power(N, j, power, count=COUNT):
    """Ordinary-series differential identity D H' = -r D' H, H(0)=1."""
    d = [Fraction(factorial(j), factorial(N*n+j)) for n in range(count)]
    h = [Fraction(1)]
    for n in range(1, count):
        h.append(-sum((n+(power-1)*k)*d[k]*h[n-k] for k in range(1,n+1))/n)
    return tuple(h[n]*factorial(N*n) for n in range(count))


def tangent(N, count=COUNT):
    from sequence_atlas import reciprocal
    a=reciprocal(N,1,count)
    return [sum((-1)**k*comb(N*(n+1)-1,N*(k+1)-1)*a[n-k] for k in range(n+1)) for n in range(count)]


def appell(N, j, power, x, count=COUNT):
    q=inverse_power(N,j,power,count)
    return [sum(comb(n,N*k)*q[k]*x**(n-N*k) for k in range(n//N+1)) for n in range(count)]


@lru_cache(maxsize=None)
def secancy_polynomials(N, count=COUNT):
    """Ordinary coefficients [r^k] P_(N,n)(r), from exponential Bell columns."""
    cumulants=[0]+tangent(N,count-1)
    rows=[[1]]
    for n in range(1,count):
        row=[0]
        for k in range(1,n+1):
            total=sum(comb(N*n,N*m)*cumulants[m]*(rows[n-m][k-1] if k-1<len(rows[n-m]) else 0) for m in range(1,n+1))
            assert total%k==0,(N,n,k)
            row.append(total//k)
        rows.append(row)
    return tuple(tuple(row) for row in rows)


@lru_cache(maxsize=None)
def theta_polynomial_rows(count=COUNT):
    """[x^k] Theta_(2n)(x); the sign of the signed Euler branch is retained."""
    from sequence_atlas import reciprocal
    p=secancy_polynomials(2,count);secant=reciprocal(2,1,count)
    return tuple(tuple((-1)**n*sum(comb(2*n,2*j)*secant[j]*p[n-j][k-2*j] for j in range(n+1) if 0<=k-2*j<len(p[n-j])) for k in range(2*n+1)) for n in range(count))


def research_catalogue():
    """Source-derived additions; priority and pairwise distinctness are unassessed."""
    entries=[]
    def add(item,family,offset,explanation,source):
        item.update(offset=offset,research_family=family,status='Research-derived family · historical novelty unassessed',source=source,source_note='Explicit definitions in the authored special-function registry. The registry requests a literature audit before historical novelty is claimed.',explanation=explanation)
        item['tags']+=['research-derived',family];entries.append(item)
    for N in range(2,13):
        rows=secancy_polynomials(N,COUNT+8);source=REGISTRY_URL+'#L489'
        for k in range(1,9):
            values=[rows[n][k] for n in range(k,k+COUNT)]
            forms=[variant('Parameter-polynomial coefficient','coefficient formula',f'a(n)=[r^{k}] P_({N},n)(r); P_({N},n)(r)=({N}n)! [z^({N}n)] D_{N}(z)^(-r); D_{N}(z)=sum_(m>=0) (-1)^m z^({N}m)/({N}m)!',source=source),
                variant('Finite composition and Stirling formula','finite sum',f'a(n)=({N}n)! sum_(ell={k})^n [ell,{k}]_1/ell! * (-1)^(n+ell) sum_(q_1+...+q_ell=n; q_i>=1) product_i 1/({N}q_i)!', '[ell,k]_1 is the unsigned Stirling number of the first kind. Empty sums are zero. This is an ordinary coefficient in r, without multiplying by k!.',source),
                variant('Bell-column recurrence','recurrence',f'B(0,0)=1; B(n,0)=0 for n>0; B(n,k)=sum_(m=1)^n binom({N}n,{N}m) K(m) B(n-m,k-1)/k; K(m)=({N}m)! [z^({N}m)] (-log D_{N}(z)); a(n)=B(n,{k})', 'Use B(n,k)=0 outside 0<=k<=n. K(m) is a block cumulant, not a raw generating-function coefficient.',source),
                variant('Hypergeometric parameter coefficient','hypergeometric',f'a(n)=({N}n)! [r^{k} z^({N}n)] ({hyper(N,0,"-")})^(-r)', 'Coefficient extraction from a parameterized inverse hypergeometric generator; this is not a single hypergeometric term formula.',source)]
            item=record(f'KFOR-P-{N:02d}-{k:02d}',f'Secancy parameter column · N={N}, k={k}','secancy parameter column',values,forms,N=N,k=k,degree=f'{N}n')
            if k==1:item['related_records']=[dict(id=f'KFOR-T-{N:02d}',note=f'The same coefficients appear in the transfer tangent after reindexing: a(n)=T_{N}(n-1), n>=1. Their source Taylor degrees differ by one. This follows by differentiating -log D_{N}(z).')]
            add(item,'transfer-secancy parameter polynomials',k,f'The coefficient of r^{k} in P_({N},n)(r) is zero for 0<=n<{k}. The stored window starts at the first nonzero local index n={k}; ordinary polynomial coefficients are used, without a k! factor.',source)
    rows=theta_polynomial_rows(COUNT+6);source=REGISTRY_URL+'#L525'
    for x in range(1,13):
        values=[sum(value*x**k for k,value in enumerate(row)) for row in rows[:COUNT]]
        forms=[variant('Theta polynomial specialization','generating function',f'sum a(n) z^(2n)/(2n)! = sech({x}z) sech(z)^{x}; a(n)=Theta_(2n)({x})', 'n is the local even-degree index; the source Taylor degree is 2n. Signs are retained.',source),
            variant('Finite signed Euler convolution','finite sum',f'a(n)=sum_(j=0)^n binom(2n,2j) E_(2j) {x}^(2j) H_(2(n-j))^({x}); E_(2j)=(2j)! [z^(2j)] sech(z); H_(2m)^({x})=(2m)! [z^(2m)] sech(z)^{x}', 'Both Euler factors use the signed sech convention.',source),
            variant('Product of inverse hypergeometric generators','hypergeometric',f'sum a(n) z^(2n)/(2n)! = (0F1(;1/2;{x*x}z^2/4))^(-1) (0F1(;1/2;z^2/4))^(-{x})', 'This is a product of inverse hypergeometric generating functions, not a single hypergeometric term formula.',source)]
        add(record(f'KFOR-H-{x:02d}',f'Euler-transfer theta · x={x}','Euler-transfer theta',values,forms,N=2,x=x,degree='2n'),'Euler-transfer theta polynomials',0,'The authored registry defines Theta_(2n)(x) by sech(xz) sech(z)^x. This record evaluates x at the stated positive integer. Its source degree is 2n, not n.'+(' At x=1 the generator is the classical sech(z)^2 specialization.' if x==1 else ''),source)
    for k in range(1,13):
        offset=(k+1)//2;values=[rows[n][k] for n in range(offset,offset+COUNT)]
        forms=[variant('Theta polynomial coefficient','coefficient formula',f'a(n)=[x^{k}] Theta_(2n)(x); Theta_(2n)(x)=(2n)! [z^(2n)] (sech(xz) exp(x log(sech(z))))', 'The logarithm is the formal power series with constant term zero. Ordinary coefficients in x are used.',source),
            variant('Finite secancy-polynomial convolution','finite sum',f'a(n)=(-1)^n sum_(j=0)^n binom(2n,2j) A_2(j) [x^({k}-2j)] P_(2,n-j)(x); A_2(j)=(2j)! [z^(2j)] sec(z)', 'A polynomial coefficient outside its degree range is zero. This relates the two research-derived families.',source),
            variant('Hypergeometric coefficient extraction','hypergeometric',f'a(n)=(2n)! [x^{k} z^(2n)] ((0F1(;1/2;x^2 z^2/4))^(-1) exp(-x log(0F1(;1/2;z^2/4))))', 'A formal bivariate coefficient formula; not a claim that the extracted sequence is a hypergeometric term.',source)]
        add(record(f'KFOR-HC-{k:02d}',f'Theta polynomial column · k={k}','theta polynomial column',values,forms,N=2,k=k,degree='2n'),'Euler-transfer theta polynomials',offset,f'Theta_(2n)(x) has degree 2n. Its x^{k} coefficient vanishes for n<{offset}; the stored window begins at n={offset}. Signs and ordinary polynomial coefficients are retained.',source)
    return entries


def formula_variants(entry):
    if entry.get('formulas'):
        return entry['formulas']
    kind=entry['kind'];source=entry['source']
    if not source.startswith('https:'):
        source='https://komorebip.github.io/Operation-KOMOREBI/'+source
    result=[variant('Defining representation','definition',entry['formula'],source=source)]
    from sequence_linear_research import legacy_representations
    result+=legacy_representations(entry)
    if kind=='reciprocal':
        N,r=entry['N'],entry['power']
        result += [variant('Hypergeometric coefficient formula','hypergeometric',f'a(n)=({N}n)! [z^({N}n)] ({hyper(N,0,"-")})^(-{r})', 'This is a coefficient formula using a hypergeometric generating function, not a claim that its reciprocal is a single hypergeometric function.'),
            variant('Finite composition formula','finite sum',f'a(n)=({N}n)! sum_(k=0)^n (-1)^(n+k) binom({r}+k-1,k) sum_(q_1+...+q_k=n; q_i>=1) product_i 1/({N}q_i)!', 'The k=0 inner sum is 1 when n=0 and 0 otherwise.')]
    else:
        alternatives={
            'fibonacci':('Binet formula','closed form','F(n)=((1+sqrt(5))/2)^n/sqrt(5)-((1-sqrt(5))/2)^n/sqrt(5)'),
            'lucas':('Binet formula','closed form','L(n)=((1+sqrt(5))/2)^n+((1-sqrt(5))/2)^n'),
            'pell':('Root formula','closed form','P(n)=((1+sqrt(2))^n-(1-sqrt(2))^n)/(2sqrt(2))'),
            'factorial':('Gamma formula','closed form','a(n)=Gamma(n+1)'),
            'central-binomial':('Rising-factorial formula','hypergeometric','a(n)=4^n (1/2)_n/(1)_n; sum a(n)t^n=1F0(1/2;;4t)'),
            'catalan':('Rising-factorial formula','hypergeometric','a(n)=4^n (1/2)_n/(2)_n; sum a(n)t^n=2F1(1/2,1;2;4t)'),
            'bell':('Exponential generating function','generating function','sum B(n)t^n/n! = exp(exp(t)-1)'),
            'fubini':('Finite inclusion-exclusion formula','finite sum','F(n)=sum_(k=0)^n sum_(j=0)^k (-1)^(k-j) binom(k,j) j^n; use 0^0=1'),
            'triangular':('Binomial formula','closed form','a(n)=binom(n+1,2)'),
            'square':('Binomial formula','closed form','a(n)=2 binom(n,2)+n'),
            'cube':('Binomial formula','closed form','a(n)=6 binom(n,3)+6 binom(n,2)+n'),
            'power-two':('Exponential form','closed form','a(n)=exp(n log(2))'),
            'power-three':('Exponential form','closed form','a(n)=exp(n log(3))'),
        }
        if kind in alternatives:
            title,typ,text=alternatives[kind]
            result.append(variant(title,typ,text,'(x)_n is the rising factorial; formulas have the entry’s original index convention.',source))
    return result


def display_note(formula):
    note=formula['note']
    if note.startswith('(x)_n is the rising factorial; formulas have '):return 'This formula uses the entry’s original index convention.'
    return note


def formula_block(entry):
    formulas=formula_variants(entry)
    return '<div class="sl-formulas"><p>'+str(len(formulas))+' recorded representation'+('s' if len(formulas)!=1 else '')+'. Formula types distinguish term formulas from generating functions and recurrences.</p><p class="sl-notation"><code>[z^k]</code> extracts a coefficient. <code>(u)_m</code> is the rising factorial, with <code>(u)_0=1</code>. <code>pFq</code> denotes a generalized hypergeometric series. Numerators and positive denominators are taken after reduction to lowest terms.</p>'+''.join(
        '<details class="sl-formula" data-formula-kind="'+e(f['kind'])+'"'+(' open' if i==0 else '')+'><summary>'+e(f['title'])+' <span>· '+e(f['kind'])+'</span></summary><pre tabindex="0" role="region" aria-label="'+e(f['title'])+'">'+e(f['expression'])+'</pre>'
        +('<p>'+e(display_note(f))+'</p>' if display_note(f) else '')+'<p><a href="'+e(f['source'])+'">Definition and derivation source</a></p></details>' for i,f in enumerate(formulas))+'</div>'


def record(identifier,title,kind,values,formulas,**extra):
    return dict(id=identifier,title=title,kind=kind,terms=[str(v) for v in values],formulas=formulas,
        formula=formulas[0]['expression'],recurrence='',source=REGISTRY_URL,source_note='Published projector special-function registry; the listed parameter range is an explicit catalogue slice.',
        offset=0,index_symbol='n',tags=[kind]+sorted({f['kind'] for f in formulas}),status='Published construction · novelty unassessed',classification='family',
        explanation='An exact parameter instance. Different instances may share finite terms or describe the same infinite sequence; no pairwise distinctness claim is made.',oeis=None,**extra)


@lru_cache(maxsize=1)
def expanded_catalogue():
    from sequence_atlas import catalogue, reciprocal, terms
    base=catalogue();entries=[]
    for N in range(2,17):
        for r in range(1,9):
            if N<=8 and r<=3:
                continue # Existing KSEQ identifiers remain authoritative.
            seed=dict(kind='reciprocal',N=N,power=r,source=REGISTRY_URL,formula=f'sum a(n)z^({N}n)/({N}n)! = D_{N}(z)^(-{r}); D_{N}(z)=sum (-1)^k z^({N}k)/({N}k)!')
            entries.append(record(f'KFOR-R-{N:02d}-{r:02d}',f'Reciprocal power · N={N}, r={r}','reciprocal power',reciprocal(N,r,COUNT),formula_variants(seed),N=N,power=r,degree=f'{N}n'))
        entries.append(record(f'KFOR-T-{N:02d}',f'Transfer tangent · N={N}','logarithmic companion',tangent(N),[
            variant('Logarithmic-derivative generator','generating function',f'-D_{N}\'(z)/D_{N}(z)=sum a(n)z^({N}(n+1)-1)/({N}(n+1)-1)!'),
            variant('Hypergeometric generator','hypergeometric',f'a(n)=({N}(n+1)-1)! [z^({N}(n+1)-1)] (-d/dz log({hyper(N,0,"-")}))')],N=N,degree=f'{N}(n+1)-1'))
    for N in range(2,13):
        for j in range(1,N):
            for r in range(1,5):
                q=inverse_power(N,j,r)
                for part in ('numerator','denominator'):
                    forms=[variant('Normalized inverse section','coefficient formula',f'q(n)=({N}n)! [z^({N}n)] ((z^{j}/{factorial(j)}) / sum_(k>=0) z^({N}k+{j})/({N}k+{j})!)^{r}; a(n)={part}(q(n))', 'q(n) is reduced to lowest terms; its denominator is positive. The plot contains the selected integer component, not the rational coefficient.'),
                        variant('Hypergeometric inverse section','hypergeometric',f'q(n)=({N}n)! [z^({N}n)] ({hyper(N,j)})^(-{r}); a(n)={part}(q(n))'),
                        variant('Exact coefficient recurrence','recurrence',f'd(k)={factorial(j)}/({N}k+{j})!; h(0)=1; h(n)=-sum_(k=1)^n (n+({r}-1)k)d(k)h(n-k)/n; q(n)=({N}n)!h(n); a(n)={part}(q(n))')]
                    entries.append(record(f'KFOR-C-{N:02d}-{j:02d}-{r:02d}-{part[:3]}',f'Congruential Euler {part} · N={N}, j={j}, r={r}','congruential '+part,[getattr(v,part) for v in q],forms,N=N,j=j,power=r,rational_terms=[str(v) for v in q],component=part,degree=f'{N}n'))
    for N in range(2,7):
        for j in range(N):
            for r in range(1,3):
                for x in (1,2):
                    q=appell(N,j,r,x)
                    for part in (('numerator',) if j==0 else ('numerator','denominator')):
                        forms=[variant('Block-Appell coefficient formula','coefficient formula',f'q(n)=n! [z^n] exp({x}z) ({hyper(N,j)})^(-{r}); a(n)={part}(q(n))', 'The ordinary degree is n, without compression. Reduce q(n) before taking its positive denominator or signed numerator.'),
                            variant('Finite binomial sum','finite sum',f'q(n)=sum_(k=0)^floor(n/{N}) binom(n,{N}k) E_({N}k)^({N},{j};{r}) {x}^(n-{N}k); a(n)={part}(q(n))', 'E_(Nk) denotes the rational coefficient of CE_(N,j)(z)^r in the (Nk)! normalization.'),
                            variant('Hypergeometric Appell generator','hypergeometric',f'sum q(n) z^n/n! = exp({x}z) ({hyper(N,j)})^(-{r}); a(n)={part}(q(n))')]
                        entries.append(record(f'KFOR-A-{N:02d}-{j:02d}-{r:02d}-{x}-{part[:3]}',f'Block-Appell {part} · N={N}, j={j}, r={r}, x={x}','Appell '+part,[getattr(v,part) for v in q],forms,N=N,j=j,power=r,x=x,rational_terms=[str(v) for v in q],component=part,degree='n'))
    selected=['fibonacci','lucas','pell','catalan','central-binomial','triangular','square','cube','power-two','power-three','factorial','bell','fubini']
    for kind in selected:
        original=next(x for x in base if x['kind']==kind)
        all_values=terms(original,12*COUNT)
        for N in range(2,13):
            for j in range(N):
                m=f'({N}n+{j})'
                source_formula=re.sub(r'(?<![A-Za-z])n(?![A-Za-z])','m',original['formula']).replace('a(m)','b(m)')
                forms=[variant('Subsequence definition','term formula',f'a(n)=b({N}n+{j}), where b is {original["title"]}. Source formula (index m): '+source_formula,f'n=0 selects the source index {j}; each step advances the source index by {N}. The source formula uses m, while the local subsequence uses n.', 'https://komorebip.github.io/Operation-KOMOREBI/sequences/'+original['id']+'.html'),
                    variant('Root-of-unity generating section','generating function',f'sum a(n) z^({N}n+{j}) = (1/{N}) sum_(ell=0)^({N}-1) omega^(-{j}ell) F(omega^ell z); omega=exp(2pi i/{N})', 'F(z)=sum b(m)z^m. This is a formal coefficient-selection identity.')]
                if kind in ('catalan','central-binomial'):
                    denominator=2 if kind=='catalan' else 1
                    forms.append(variant('Rising-factorial term formula','hypergeometric',f'a(n)=4^{m} (1/2)_{m}/({denominator})_{m}', '(u)_m is a finite rising factorial. It is evaluated exactly at the nonnegative integer source index.'))
                    top=', '.join(['1']+[str(Fraction(2*j+1+2*k,2*N)) for k in range(N)])
                    bottom=', '.join(str(Fraction(j+denominator+k,N)) for k in range(N))
                    forms.append(variant('Hypergeometric ordinary generating function','hypergeometric',f'sum a(n)t^n = b({j}) * {N+1}F{N}({top}; {bottom}; {4**N}t)', 'Formal power series. The parameter lists are intentionally left uncancelled; repeated parameters may simplify.'))
                elif kind in ('bell','fubini'):
                    generator='exp(exp(t)-1)' if kind=='bell' else '1/(2-exp(t))'
                    forms.append(variant('Exponential coefficient formula','coefficient formula',f'a(n)={m}! [t^{m}] {generator}', 'The factorial and coefficient exponent both use the source index, not the local n.'))
                elif len(formula_variants(original))>1:
                    f=formula_variants(original)[1]
                    forms.append(variant('Alternative source formula','closed form',f['expression']+'; replace every source index n by '+m, 'The substitution acts on the source formula before evaluating the local sequence.',f['source']))
                entries.append(record(f'KFOR-S-{kind}-{N:02d}-{j:02d}',f'{original["title"]} · indices {N}n+{j}','classical multisection',[all_values[N*n+j] for n in range(COUNT)],forms,N=N,j=j,degree=f'{N}n+{j}',parent=original['id'],source_kind=kind))
    entries+=research_catalogue()
    from sequence_research_tables import research_additions
    entries+=research_additions()
    from sequence_linear_research import linear_catalogue
    entries+=linear_catalogue()
    # Curated, source-linked instances with separate OEIS review status.
    from sequence_closed_forms import closed_form_catalogue
    entries+=closed_form_catalogue()
    from sequence_closed_forms_extended import extended_catalogue,append_proved_representations
    entries+=extended_catalogue()
    append_proved_representations(entries)
    assert len({x['id'] for x in entries})==len(entries)
    return entries


if __name__=='__main__':
    import argparse
    import json
    from pathlib import Path
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--id');parser.add_argument('--output',type=Path);args=parser.parse_args()
    entries=expanded_catalogue()
    if args.id:
        entries=[x for x in entries if x['id']==args.id]
        if not entries:parser.error('Unknown parameter record')
    if args.output:args.output.write_text(json.dumps(entries,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    elif args.id:print(json.dumps(entries[0],ensure_ascii=True,indent=2))
    else:print(json.dumps(dict(records=len(entries),stored_terms=sum(len(x['terms']) for x in entries),formula_representations=sum(len(x['formulas']) for x in entries))))
