"""Exact closed-form additions from Collections II and III.

Author: Komorebi P.
Only finite rational/integer calculations are executed. Source proofs and
parameter restrictions are recorded in research/sequence-closed-forms.
"""
from fractions import Fraction
from functools import lru_cache
from math import comb, factorial, gcd

from sequence_closed_forms import rising, falling

COUNT = 24
SOURCE = ('https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/'
          'research/sequence-closed-forms/COLLECTION_II_ADDITIONS.md')


def terminating_hypergeometric(upper, lower, argument, degree):
    """Evaluate a terminating pFq as an exact rational finite sum."""
    term = Fraction(1)
    value = term
    for k in range(1, degree + 1):
        term *= Fraction(argument, k)
        for parameter in upper:
            term *= parameter + k - 1
        for parameter in lower:
            term /= parameter + k - 1
        value += term
    return value


def sparse_finite(n, p, q, r, u=1, v=1):
    """Finite two-delay coefficient, valid at zero weights and negative r."""
    if n < 0 or p <= 0 or q <= 0:
        raise ValueError('Use nonnegative n and positive integer delays')
    r, u, v = map(Fraction, (r, u, v))
    return sum((Fraction(rising(r, i + j) * u**i * v**j,
                         factorial(i) * factorial(j))
                for i in range(n // p + 1)
                for j in range(n // q + 1) if p*i + q*j == n),
               Fraction(0))


def sparse_hyper(n, p, q, r, u=1, v=1):
    """Terminating QF(Q-1) for p!=q, with safe endpoints.

    A finite rational result is returned, not a symbolic hypergeometric object.
    At v=0 or an invalid residue the coefficient uses its finite definition.
    """
    if n < 0 or p <= 0 or q <= 0:
        raise ValueError('Use nonnegative n and positive integer delays')
    r, u, v = map(Fraction, (r, u, v))
    if p == q:
        return (Fraction(rising(r, n//p), factorial(n//p)) *
                (u+v)**(n//p)) if n % p == 0 else Fraction(0)
    if p > q:
        return sparse_hyper(n, q, p, r, v, u)
    d = gcd(p, q)
    if n % d:
        return Fraction(0)
    P, Q = p//d, q//d
    nu = n//d
    I = (nu * pow(P, -1, Q)) % Q
    J = (nu-P*I)//Q
    if J < 0:
        return Fraction(0)
    if v == 0:
        return sparse_finite(n, p, q, r, u, v)
    D = Q-P
    M = I+J
    K = J//P
    upper = [Fraction(-J+t, P) for t in range(P)]
    upper += [Fraction(r+M+t, D) for t in range(D)]
    lower = [Fraction(I+1+t, Q) for t in range(Q)]
    lower.remove(Fraction(1))
    argument = (Fraction((-1)**P * P**P * D**D, Q**Q) *
                u**Q / v**P)
    front = rising(r, M)*u**I*v**J / (factorial(I)*factorial(J))
    return front*terminating_hypergeometric(upper, lower, argument, K)


def weighted_jet_even(n, d, lam=1):
    """J_(n,d)(lam), with all zero-prefix conventions included."""
    if d < 0:
        raise ValueError('The falling-factorial weight is nonnegative')
    if n < 2*d:
        return 0
    return sum(comb(n,2*m)*falling(m,d)*comb(2*m,m)*lam**(n-2*m)
               for m in range(d,n//2+1))


def weighted_jet(n, d, lam=1, c=1):
    """S_n^[d](lam,c)=J_n+differentiated odd-block contribution."""
    if n < 0:
        return 0
    return weighted_jet_even(n,d,lam)+c*n*weighted_jet_even(n-1,d,lam)


def hankel_4f3(N, c):
    """Terminating 4F3 for H_N(c). The empty determinant is special."""
    if N < 0:
        raise ValueError('Determinant size must be nonnegative')
    if N == 0:
        return 1
    c = Fraction(c)
    total = Fraction(1)
    for k in range(1, N//2+1):
        total += ((-1)**k *
                  Fraction((2*k-1)*N*(N-1)*comb(N+2*k-2,4*k-2),4*k) *
                  c**(2*k))
    result = 2**(N-1)*total
    return int(result) if result.denominator == 1 else result


@lru_cache(maxsize=None)
def _chebyshev_remainder(n, d, c):
    """C_n(x) modulo x^2+(2d+1)c*x-4, as (x coefficient, constant)."""
    if n == 0:
        return 0, 2
    if n == 1:
        return 1, 0
    a, b = _chebyshev_remainder(n-1,d,c)
    aa, bb = _chebyshev_remainder(n-2,d,c)
    return b-(2*d+1)*c*a-aa, 4*a-bb


def _hat_remainder(n, d, c):
    k = d+1
    A, B = 0, 0
    for j in range(k+1):
        weight = (-1)**j*comb(k,j)*falling(n,j)*falling(n-k-1-j,k-j)
        a,b = _chebyshev_remainder(abs(n-2*j),d,c)
        A += weight*a
        B += weight*b
    return A,B


def _R(N, d):
    result = Fraction(1)
    for j in range(d):
        result *= Fraction(factorial(j)*rising(N-2*d+j,d+1),
                           factorial(d+j+1))
    return result


def weighted_hankel_closed(N,d,c):
    """Root-free fixed-size Chebyshev remainder formula (Collection III W3/W4).

    Exact at singular blocks and repeated roots; no determinant is computed.
    """
    if N < 0 or d < 0:
        raise ValueError('Size and integer weight must be nonnegative')
    if N == 0:
        return 1
    c = Fraction(c)
    a_d = factorial(2*d)//factorial(d)
    rho = (-1)**(d+1)*2*a_d
    A,B = _hat_remainder(N,d,c)
    AA,BB = _hat_remainder(N+1,d,c)
    prefactor = (Fraction(rho**N*factorial(d)*factorial(d+1),
                           2**(2*d+3)*factorial(2*d+1)*factorial(2*d+2)) *
                 _R(N,d))
    result = prefactor*(B*AA-A*BB)
    return int(result) if result.denominator == 1 else result


def meixner_pollaczek_integer(s, twice_x, count=COUNT):
    """Q_0=1, Q_1=2x, Q_(n+1)=2x Q_n-n(n+s-1)Q_(n-1)."""
    if count <= 0:
        return []
    values = [1]
    if count == 1:
        return values
    values.append(twice_x)
    for n in range(1,count-1):
        values.append(twice_x*values[n]-n*(n+s-1)*values[n-1])
    return values


def extended_catalogue():
    """11 additional exact integer instances; no historical novelty claim."""
    from sequence_formula_catalogue import record, variant
    results=[]
    def add(identifier,title,kind,family,values,first,second,note,oeis=None):
        forms=[
            variant('Defining finite formula','finite sum',first,note,SOURCE),
            variant('Equivalent construction','closed form',second,
                    'The exact formula is source-linked and not inferred from finite agreement.',SOURCE)
        ]
        row=record(identifier,title,kind,values,forms,N=1,degree='n',
                   closed_form_collection=True,closed_form_family=family)
        row.update(source=SOURCE,source_note='Closed Forms II–III. Exact integer specialization.',
                   status='Source-derived exact formula · historical priority unassessed',
                   explanation=note)
        row['tags']+=['closed forms','weighted hierarchy','2026-11-19']
        if oeis:
            row['oeis']=oeis
            row['source_claimed_oeis']=True
        results.append(row)
    for d in range(5):
        add(f'KFOR-CF-JET-{d:02d}',
            f'Polynomially weighted binomial transform · d={d}',
            'weighted binomial jet','GF-CF-BINOMIAL-JETS',
            [weighted_jet(n,d) for n in range(COUNT)],
            f'u(n)=J(n,{d})+n*J(n-1,{d}); J(n,d)=sum_(m=d)^floor(n/2) binom(n,2m)*falling(m,d)*binom(2m,m)',
            f'sum u(n)z^n=((2*{d})!/{d}!)z^(2*{d})*(1+(2*{d}-1)z-(2*{d}+4)z^2)/(1-2z-3z^2)^({d}+3/2)',
            'The finite sum defines every index, including the zero prefix. '
            'The equivalent ordinary generating function follows from the falling-factorial basis.',
            oeis='A163865' if d==0 else None)
    for d in (2,3,4):
        add(f'KFOR-CF-W-{d}-1',
            f'Weighted swinging Hankel determinants · d={d}, c=1',
            'weighted Hankel','GF-CF-WEIGHTED-HANKEL',
            [weighted_hankel_closed(n,d,1) for n in range(COUNT)],
            f'W(N)=det(mu_(i+j))_(0<=i,j<N); mu_n=F_{d}[x^n]+n*F_{d}[x^(n-1)]',
            f'W(N)=root-free Chebyshev remainder formula W3/W4, with k={d+1}; '
            f'Q_{d}(z)=((1+rho*z)^4+({2*d+1})^2*rho^2*z^2)^(({d}+1)*({d}+2)+1), rho=(-1)^({d}+1)*2*(2*{d})!/{d}!',
            'Empty determinant equals one. Values 1 through 2d vanish. '
            'The original proof gives a fixed-size Chebyshev formula and an exact eventual recurrence order.')
    for s in (1,2,3):
        add(f'KFOR-CF-MP-{s:02d}-01',
            f'Integer Meixner–Pollaczek polynomial · s={s}, x=1',
            'Meixner–Pollaczek integer','GF-CF-MEIXNER',
            meixner_pollaczek_integer(s,2),
            f'Q(0)=1, Q(1)=2, Q(n+1)=2Q(n)-n(n+{s}-1)Q(n-1)',
            f'Q(n)=i^n*({s})_n*2F1(-n,{s}/2+i;{s};2) [terminating]',
            'Integer specialization of a classical polynomial family. '
            'The recurrence determines the values without complex arithmetic.')
    assert len(results)==11
    return results


def extended_families():
    """A source-linked classical polynomial family, not a novelty claim."""
    title='Integer Meixner–Pollaczek polynomial realizations'
    formula='Q_(n+1)=2x Q_n-n(n+s-1)Q_(n-1); Q_0=1, Q_1=2x'
    return [dict(id='GF-CF-MEIXNER',title=title,engine=None,
                 domain='n>=0; polynomial parameters s and 2x',
                 formula=formula,
                 note='Classical Meixner–Pollaczek recurrence with integer polynomial specialization. The 2F1 expression is terminating when s>0.',
                 paper='CLOSED-FORMS-II-III',locator=1,
                 mode='Source-linked construction',
                 derivation=SOURCE,family_type='discrete construction',
                 source=SOURCE+'#L1',paper_title='Closed Forms Collection II, paper formula P3',
                 url='generalized-families/GF-CF-MEIXNER.html',
                 kind='generalized family',tags=['generalized','closed forms'],
                 status='Source-linked construction',offset=0,terms=[],
                 formulas=[dict(title='Classical recurrence',kind='family definition',
                                expression=formula,source=SOURCE)],
                 recurrence='',explanation='No historical priority claim',
                 collection='generalized',paper_refs=[],family_names=[title])]


def append_proved_representations(entries):
    """Add verified formula variants without changing any stored source terms."""
    from sequence_formula_catalogue import variant
    by_id = {row['id']:row for row in entries}
    additions={
        'KFOR-CF-W-0-1':[
            ('Universal swinging Hankel 4F3','hypergeometric',
             'H_N(c)=2^(N-1)*4F3(-N/2,(1-N)/2,(N-1)/2,N/2; -1/2,-1/4,1/4; -c^2/16), N>=1; H_0=1; here c=1',
             'This finite polynomial is independent of the binomial-shift parameter. All zeros in c are real and nonzero.')],
        'KFOR-CF-W-1-1':[
            ('Uniform weighted Chebyshev determinant','closed form',
             'For any d>=0, W_N^[d](c) equals the fixed-size Chebyshev divided determinant W3; W_0=1 separately. Here d=1,c=1.',
             'The root-free remainder identity W4 also covers coincident roots.')],
        'KFOR-CF-S-2-5-1-1-1':[
            ('Terminating residue-five hypergeometric subsequence','hypergeometric',
             'a(5m)=5F4(-m/2,(1-m)/2,(m+1)/3,(m+2)/3,(m+3)/3;1/5,2/5,3/5,4/5;108/3125)',
             'The formula specifies only the n=5m residue subsequence; the defining generating function covers every n.')],
        'KFOR-CF-PAD-1':[
            ('Residue-class 3F2 formula','hypergeometric',
             'For n>=3, a(n)=[z^(n-3)](1-z^2-z^3)^(-1); apply the uniform 3F2 residue formula with p=2,q=3. Initial terms a(0)=1,a(1)=a(2)=0.',
             'Respect the n=0,1,2,4 endpoint conventions. Do not multiply a nonterminating hypergeometric value by zero.')],
        'KFOR-T-04':[
            ('Four-block tangent Bernoulli formula','closed form',
             'T_4(n)=-2^(2n+3)*(2^(4n+4)-1)*B_(4n+4)/(4n+4)=T_2(2n+1)/2^(2n+1)',
             'B_m uses t/(exp(t)-1)=sum B_m*t^m/m!. The source index is 4n+3.')],
    }
    for identifier,forms in additions.items():
        if identifier not in by_id:
            raise ValueError('Expected source record missing: '+identifier)
        target=by_id[identifier]
        for title,kind,expression,note in forms:
            target['formulas'].append(variant(title,kind,expression,note,SOURCE))
    return entries
