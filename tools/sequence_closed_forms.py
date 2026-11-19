"""Exact finite integer records from Closed Forms Collections II and III.

Author: Komorebi P.
The infinite formulas are documented separately. These instances are finite,
reproducible windows, not claims of historical novelty or OEIS exclusion.
"""
from math import comb

COUNT = 24
SOURCE = ('https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/'
          'research/sequence-closed-forms/IDENTITIES.md')


def rising(a, k):
    result = 1
    for j in range(k):
        result *= a+j
    return result


def falling(a, k):
    result = 1
    for j in range(k):
        result *= a-j
    return result


def sparse_coefficients(p, q, u, v, power, count=COUNT):
    """Coefficients of (1-u*z**p-v*z**q)**(-power), exactly."""
    assert p > 0 and q > 0 and power > 0
    values = [1]
    for n in range(1, count):
        numerator = 0
        for delay, weight in ((p, u), (q, v)):
            if n >= delay:
                numerator += weight*(n+(power-1)*delay)*values[n-delay]
        assert numerator % n == 0
        values.append(numerator//n)
    return values


def padovan_powers(power, count=COUNT):
    """[z**n] ((1-z**2)/(1-z**2-z**3))**power."""
    sparse = sparse_coefficients(2, 3, 1, 1, power, count)
    return [sum((-1)**j*comb(power,j)*sparse[n-2*j]
                for j in range(min(power,n//2)+1)) for n in range(count)]


def four_block(a, count=COUNT):
    """T_m(a) from the logarithmic derivative of V_a, m=1..count."""
    values = [0]
    for m in range(1,count+1):
        A = lambda k: 1-4*k*a+2*k*(4*k-1)*a*a
        value = (-1)**(m+1)*A(m)
        value += sum((-1)**(k+1)*comb(4*m-1,4*k)*A(k)*values[m-k]
                     for k in range(1,m))
        values.append(value)
    return values[1:]


def weighted_moments(d,c,count):
    """L_{d,c}[x**n] = F_d[x**n]+cn F_d[x**(n-1)]."""
    def base(n):
        if n<0 or n%2:
            return 0
        m=n//2
        return falling(m,d)*comb(2*m,m)
    return [base(n)+c*n*base(n-1) for n in range(count)]


def exact_det(matrix):
    """Exact fraction-free determinant, including zero pivots."""
    n=len(matrix)
    if not n:
        return 1
    a=[list(row) for row in matrix]
    denom,sign=1,1
    for k in range(n-1):
        if a[k][k]==0:
            pivot=next((i for i in range(k+1,n) if a[i][k]),None)
            if pivot is None:
                return 0
            a[k],a[pivot]=a[pivot],a[k]
            sign=-sign
        pivot=a[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                numerator=a[i][j]*pivot-a[i][k]*a[k][j]
                assert numerator % denom == 0
                a[i][j]=numerator//denom
            a[i][k]=0
        denom=pivot
    return sign*a[-1][-1]


def weighted_hankel(d,c,count=COUNT):
    moments=weighted_moments(d,c,2*count-2)
    return [exact_det([[moments[i+j] for j in range(n)] for i in range(n)])
            for n in range(count)]


def beta_weights(L,a,b):
    return [comb(L,r)*rising(a,r)*rising(b,L-r) for r in range(L+1)]


def beta_moments(L,a,b,count=COUNT):
    """Integer unnormalized moments U_n=(a+b)_L*M_n."""
    weights=beta_weights(L,a,b)
    return [sum(weight*r**n for r,weight in enumerate(weights)) for n in range(count)]


def beta_determinants(L,a,b,count=COUNT):
    """Hankel determinants of unnormalized integer moments."""
    moments=beta_moments(L,a,b,2*min(L+1,count-1)+1)
    result=[]
    for n in range(count):
        if n>L+1:
            result.append(0)
        else:
            result.append(exact_det([[moments[i+j] for j in range(n)] for i in range(n)]))
    return result


def closed_form_catalogue():
    """Twenty-four curated instances with separated source and review status."""
    from sequence_formula_catalogue import variant,record
    entries=[]
    def add(identifier,title,family,kind,values,formula,alternative,note,offset=0):
        forms=[variant('Exact defining formula','coefficient formula',formula,note,SOURCE),
               variant('Independent identity','recurrence',alternative,
                       'Use exact integer arithmetic. The listed terms are a finite window.',SOURCE)]
        row=record(identifier,title,kind,values,forms,N=1,degree='n',
                   closed_form_collection=True,closed_form_family=family)
        row.update(offset=offset,source=SOURCE,
                   source_note='Closed Forms Collections II–III. Written proofs and separate exact replay; novelty unassessed.',
                   status='Source-derived exact formula · historical priority unassessed',
                   explanation=note)
        row['tags']+=['closed forms','2026-11-19','reproduced finite data']
        entries.append(row)
    for p,q,u,v,r in [(2,3,1,1,1),(2,3,1,1,2),(2,5,1,1,1),
                      (3,5,1,2,1),(2,3,2,1,3),(3,4,1,-1,2)]:
        add(f'KFOR-CF-S-{p}-{q}-{u}-{v}-{r}',
            f'Sparse two-delay · p={p}, q={q}, u={u}, v={v}, r={r}',
            'GF-CF-SPARSE','sparse two-delay',sparse_coefficients(p,q,u,v,r),
            f'a(n)=[z^n](1-({u})z^{p}-({v})z^{q})^(-{r})',
            f'a(0)=1; n*a(n)={u}*(n+({r}-1)*{p})*a(n-{p})+{v}*(n+({r}-1)*{q})*a(n-{q}); a(k)=0 for k<0',
            'Formal coefficients, valid for the displayed integer parameters.')
    for r in (1,2):
        add(f'KFOR-CF-PAD-{r}',f'Padovan generating-function power · r={r}',
            'GF-CF-PADOVAN','Padovan power',padovan_powers(r),
            f'a(n)=[z^n]((1-z^2)/(1-z^2-z^3))^{r}',
            f'a(n)=sum_(j=0)^min({r},floor(n/2)) (-1)^j binom({r},j)*[z^(n-2j)](1-z^2-z^3)^(-{r})',
            'Padovan convention: r=1 yields a(0)=1, a(1)=a(2)=0, then a(n)=a(n-2)+a(n-3) for n>=3.')
    for a in (-2,-1,0,1,2,3):
        id_part=('m'+str(-a)) if a<0 else ('p'+str(a))
        add(f'KFOR-CF-R-{id_part}',f'Four-block logarithmic sequence · a={a}',
            'GF-CF-FOUR-BLOCK','four-block polynomial',four_block(a),
            f'T(m)=(4m-1)![x^(4m-1)](-V_a\'(x)/V_a(x)); V_a(x)=(cosh(x/sqrt(2))-a*x/sqrt(2)*sinh(x/sqrt(2)))*(cos(x/sqrt(2))+a*x/sqrt(2)*sin(x/sqrt(2)))',
            f'T(m)=(-1)^(m+1)*A_m+sum_(k=1)^(m-1) (-1)^(k+1)*binom(4m-1,4k)*A_k*T(m-k); A_k=1-4k*({a})+2k(4k-1)*({a})^2',
            'First local index is m=1. The defining recurrence gives an integer polynomial in a at each m.',offset=1)
    for d,c in ((0,0),(0,1),(1,0),(1,1)):
        add(f'KFOR-CF-W-{d}-{c}',f'Weighted moment Hankel determinant · d={d}, c={c}',
            'GF-CF-WEIGHTED-HANKEL','weighted Hankel',weighted_hankel(d,c),
            f'a(N)=det(mu_(i+j))_(0<=i,j<N); mu_n=F_{d}[x^n]+({c})*n*F_{d}[x^(n-1)]',
            f'F_d[x^(2m)]=falling(m,{d})*binom(2m,m); F_d[x^(2m+1)]=0; a(0)=1',
            'Exact determinants. For d>0, a(N)=0 for 1<=N<=2d. Empty determinant equals one.')
    for L,a,b in ((4,1,1),(5,1,2),(6,2,1),(7,2,3)):
        add(f'KFOR-CF-BM-{L}-{a}-{b}',
            f'Unnormalized beta-binomial ordinary moments · L={L}, a={a}, b={b}',
            'GF-CF-BETA-MOMENTS','beta-binomial moments',beta_moments(L,a,b),
            f'U(n)=sum_(k=0)^{L} k^n*binom({L},k)*({a})_k*({b})_({L}-k)',
            f'U(n)=({a+b})_{L}*M(n); M(n)=sum_(k=0)^{L} k^n*w_k; w_k=binom({L},k)*({a})_k*({b})_({L}-k)/({a+b})_{L}',
            'Integer unnormalized ordinary moments, not normalized probability moments. Use 0^0=1.')
    for L,a,b in ((4,1,1),(6,2,1)):
        add(f'KFOR-CF-BH-{L}-{a}-{b}',
            f'Beta-binomial unnormalized Hankel determinant · L={L}, a={a}, b={b}',
            'GF-CF-BETA-HANKEL','beta-binomial Hankel',beta_determinants(L,a,b),
            f'H(N)=det(U_(i+j))_(0<=i,j<N); U_n=sum_(k=0)^{L} k^n*binom({L},k)*({a})_k*({b})_({L}-k)',
            f'H(N)=({a+b})_{L}^N*prod_(j=0)^(N-1) (j!*({a})_j*({b})_j*falling({L},j)*({a+b+L})_j/({a+b})_(N+j-1)); H(0)=1; H(N)=0 for N>{L+1}',
            'Normalized determinants are multiplied by (a+b)_L^N. Terms remain exact integers.')
    assert len(entries)==24
    return entries


def closed_form_families():
    """Eight construction groups, including two definition-only families."""
    groups=[
        ('GF-CF-SPARSE','Sparse two-delay coefficients','p,q,r positive; integer u,v',
         'C_n=[z^n](1-u z^p-v z^q)^(-r)',
         'Includes degenerate coincident delays and zero coefficients.'),
        ('GF-CF-PADOVAN','Padovan and rational generating-function powers','r positive integer',
         'P_r(z)=((1-z^2)/(1-z^2-z^3))^r',
         'The Padovan r=1 initial values are 1,0,0.'),
        ('GF-CF-FOUR-BLOCK','Four-block logarithmic polynomials','a complex; m>=1',
         '-V_a\'(x)/V_a(x)=sum_(m>=1) T_m(a)*x^(4m-1)/(4m-1)!',
         'Each T_m is an integer polynomial; the written proof establishes positivity for real a.'),
        ('GF-CF-WEIGHTED-HANKEL','Factorially weighted Hankel determinants','d>=0 integer; c complex; N>=0',
         'W_N=det(F_d[x^(i+j)]+c(i+j)F_d[x^(i+j-1)])',
         'Includes singular initial blocks and exceptional repeated-root parameters.'),
        ('GF-CF-BETA-MOMENTS','Beta-binomial ordinary moments','L>=0 integer; a,b>0',
         'M_n=sum_(k=0)^L k^n binom(L,k)(a)_k(b)_(L-k)/(a+b)_L',
         'Published integer windows use unnormalized moments (a+b)_L*M_n.'),
        ('GF-CF-BETA-HANKEL','Beta-binomial Hankel determinants','L>=0 integer; a,b>0; N>=0',
         'D_N=det(M_(i+j))_(0<=i,j<N)',
         'The normalized product vanishes above support rank L+1. Published integer windows scale by (a+b)_L^N.'),
        ('GF-CF-BINOMIAL-JETS','Polynomially weighted binomial transforms','n>=0; polynomial weight',
         'a_n=sum_(k=0)^n binom(n,k) P(k) b_k',
         'Definition-only family; see Collection II for the terminating hypergeometric formulas.'),
        ('GF-CF-ENTIRE-SCALING','Entire scaling and reciprocal-zero families','complex t; finite N>=2',
         'F(t)=0F3(; -1/2,-1/4,1/4; -t^2/256)',
         'Definition-only family; Collection III proves the scaling limit and describes its zero set.')
    ]
    result=[]
    for identifier,title,domain,formula,note in groups:
        source=SOURCE+'#L1'
        result.append(dict(id=identifier,title=title,engine=None,domain=domain,
            formula=formula,note=note,paper='CLOSED-FORMS-II-III',locator=1,
            mode='Source-linked construction',derivation=source,
            family_type='discrete construction' if identifier!='GF-CF-ENTIRE-SCALING' else 'analytic family',
            source=source,paper_title='Closed Forms Collections II and III',
            url='generalized-families/'+identifier+'.html',kind='generalized family',
            tags=['generalized','closed forms'],status='Source-linked construction',
            offset=0,terms=[],formulas=[dict(title='General definition',kind='family definition',
                                             expression=formula,source=source)],
            recurrence='',explanation=note,collection='generalized',
            paper_refs=[],family_names=[title]))
    return result


if __name__=='__main__':
    print('Closed-form sequences: generators for sparse, Padovan, four-block and Hankel families')
    print('Padovan:',padovan_powers(1)[:12])
