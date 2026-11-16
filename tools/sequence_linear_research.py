"""Ordinary k-step families and explicitly finite hypergeometric forms."""
from fractions import Fraction as Q
from functools import lru_cache
from math import comb, factorial

SOURCE='https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/src/komorebi_math/sequences/families.py#L81'
DERIVATION='https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/research/sequence-connections/IDENTITIES.md#generalized-k-step-coefficients'
LEGACY_ORDERS={'KOM013':3,'KOM014':4,'KOM015':5,'KOM016':6}


def coefficients(order,power,weight,count=24):
    if not all(type(v) is int for v in (order,power,weight,count)) or order<2 or power<1 or weight<1 or count<1:raise ValueError('Use integer order>=2, power>=1, weight>=1 and count>=1')
    a=[1]
    for n in range(1,count):
        value=weight*sum((n+(power-1)*j)*a[n-j] for j in range(1,min(order,n)+1))
        if value%n:raise ArithmeticError('Nonintegral k-step coefficient')
        a.append(value//n)
    return a


def rising(x,n):
    value=Q(1)
    for j in range(n):value*=x+j
    return value


@lru_cache(maxsize=None)
def finite_hypergeometric(order,power,weight,m):
    """The finite definition in IDENTITIES.md; no automatic parameter cancellation."""
    if m<0:return Q(0)
    k,r,c=order,power,weight
    top=[Q(i-m,k+1) for i in range(k+1)]
    bottom=[Q(i+1-r-m,k) for i in range(k)]
    argument=Q(c*(k+1)**(k+1),(c+1)**(k+1)*k**k)
    total=term=Q(1)
    for j in range(1,m//(k+1)+1):
        term*=argument/j
        for a in top:term*=a+j-1
        for b in bottom:
            denominator=b+j-1
            if not denominator:raise ArithmeticError('A lower parameter vanished within the finite cutoff')
            term/=denominator
        total+=term
    return (c+1)**m*comb(r+m-1,m)*total


def hyper_terms(k,r,c):
    top=', '.join(f'({i}-m)/{k+1}' for i in range(k+1))
    bottom=', '.join(f'({i+1-r}-m)/{k}' for i in range(k))
    arg=Q(c*(k+1)**(k+1),(c+1)**(k+1)*k**k)
    return f'H(m)={c+1}^m binom({r}+m-1,m) {k+1}F{k}({top}; {bottom}; {arg})'


def representations(k,r,c,traditional=False):
    from sequence_formula_catalogue import variant
    cut='The hypergeometric notation here means the finite sum j=0..floor(m/'+str(k+1)+'). Do not cancel parameters before truncation or use an unrestricted analytic value. H(m)=0 for m<0. All factorials are ordinary; no EGF normalization is used.'
    h=f'H(m)=sum_(j=0)^floor(m/{k+1}) (-{c})^j binom({r}+m-{k}j-1,m-{k}j) binom(m-{k}j,j) {c+1}^(m-{k+1}j)'
    outer=f'a(n)=sum_(ell=0)^min({r},n) (-1)^ell binom({r},ell) H(n-ell)'
    generator=f'sum_(n>=0) a(n)z^n = (1-{c} sum_(j=1)^{k} z^j)^(-{r})'
    recurrence=f'a(0)=1\na(n)={c} sum_(j=1)^min({k},n) (n+({r}-1)j)a(n-j)/n'
    if traditional:
        generator=f'sum_(n>=0) a(n)z^n = z^{k-1}/(1-sum_(j=1)^{k} z^j)'
        outer=f'a(n)=H(n-{k-1})-H(n-{k})'
        recurrence=f'a(n)=0 for 0<=n<{k-1}; a({k-1})=1; a(n)=sum_(j=1)^{k} a(n-j) for n>={k}'
    return [variant('Ordinary generating function','generating function',generator,'The seed convention is '+(f'{k-1} initial zeros, then one.' if traditional else 'a(0)=1. For r=c=1, a(n)=T(n+k-1;k).'),DERIVATION),
            variant('Finite binomial closed form','finite sum',outer+'\n'+h,'H(m)=0 for m<0. These are finite integer sums, including n=0.',SOURCE if traditional else DERIVATION),
            variant('Finite hypergeometric closed form','hypergeometric',outer+'\n'+hyper_terms(k,r,c),cut,DERIVATION),
            variant('Exact recurrence and initial values','recurrence',recurrence,'The recurrence applies for '+(f'n>={k}.' if traditional else 'n>=1. The division by n is exact.'),SOURCE if traditional else DERIVATION)]


@lru_cache(maxsize=1)
def linear_catalogue():
    from sequence_formula_catalogue import record
    result=[]
    for k in range(2,17):
        for r in range(1,5):
            for c in (1,2):
                identifier=f'KFOR-LR-{k:02d}-{r:02d}-{c:02d}'
                item=record(identifier,f'Weighted k-step coefficients · order {k}, power {r}, weight {c}','k-step reciprocal power',coefficients(k,r,c),representations(k,r,c),recurrence_order=k,power=r,weight=c,degree='n',linear_addition=True)
                item.update(source=DERIVATION,source_note='Derived from the maintained k-bonacci ordinary generating function; the derivation and finite hypergeometric convention are written explicitly.',status='Derived recurrence family · historical novelty unassessed',explanation='Ordinary coefficients of (1-c(z+...+z^k))^(-r). The constant coefficient is one. These are not compressed EGF coefficients.',research_family='linear recurrence calculus')
                item['tags']+=['research-derived','linear recurrence calculus','k-bonacci','ordinary generating function']
                if r==c==1:
                    item.update(classification='known-family',status='Classical k-bonacci tail · explicit seed shift')
                    parent='KSEQ-000025' if k==2 else f'KOM{k+10:03d}' if k<=6 else f'KFOR-KB-{k:02d}'
                    item['related_records']=[dict(id=parent,note=f'The standard zero-seeded convention has T(n+k-1;k)=a(n), with k={k}. The shift is {k-1}.')]
                result.append(item)
    for k in range(7,17):
        values=[0]*(k-1)+coefficients(k,1,1,49-k)
        item=record(f'KFOR-KB-{k:02d}',f'{k}-bonacci numbers · standard zero seeds','k-bonacci',values,representations(k,1,1,True),recurrence_order=k,power=1,weight=1,degree='n',linear_addition=True)
        item.update(source=SOURCE,classification='known-family',status='Classical recurrence · standard seed convention',source_note='Maintained k-bonacci recurrence and finite binomial formula.',explanation=f'Indices 0 through {k-2} are zero; index {k-1} is one. Exactly 48 terms are stored.',research_family='linear recurrence calculus')
        item['tags']+=['research-derived','linear recurrence calculus','k-bonacci']
        item['related_records']=[dict(id=f'KFOR-LR-{k:02d}-01-01',note=f'The normalized nonzero tail begins at source index {k-1}.')]
        result.append(item)
    return result


def legacy_representations(entry):
    k=LEGACY_ORDERS.get(entry.get('id'))
    if not k:return []
    return representations(k,1,1,True)[:3]
