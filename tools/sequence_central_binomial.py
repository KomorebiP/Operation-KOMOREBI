"""Exact weighted central binomial sums and their uniform recurrence.

Author: Komorebi P.
The construction is defined for every complex parameter in the source proof.
This numerical implementation accepts exact integers and Fraction parameters.
The stored integer specializations are known OEIS sequences, with no claim of
historical priority for the general recurrence or its special cases.
"""
from fractions import Fraction
from math import comb


COUNT = 24
FAMILY_ID = 'GF-CF-CENTRAL-BINOMIAL'
SOURCE = ('https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/'
          'research/sequence-closed-forms/CENTRAL_BINOMIAL_RECURRENCE.md')


def _nonnegative_index(value, name):
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f'{name} must be a nonnegative integer')
    if value < 0:
        raise ValueError(f'{name} must be a nonnegative integer')
    return value


def _exact_parameter(value):
    if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
        raise TypeError('r must be an int or Fraction')
    return value


def _reduced(value):
    if isinstance(value, Fraction) and value.denominator == 1:
        return value.numerator
    return value


def central_binomial_sum(n, r):
    """Evaluate sum binom(n,floor(k/2))*(-r)**(n-k), 0<=k<=n.

    The exponent-zero convention includes 0**0=1. The returned integer or
    Fraction is exact; floating-point and implicit string conversions are
    deliberately rejected.
    """
    n = _nonnegative_index(n, 'n')
    r = _exact_parameter(r)
    return _reduced(sum(comb(n, k // 2) * (-r)**(n-k)
                        for k in range(n+1)))


def central_binomial_coefficients(r, last):
    """Return exact coefficients a_0(r),...,a_last(r), with inclusive last.

    For nonzero r, use the independent first-order relation
      r*a_n + (r*r+1)*a_(n-1) = (r+1)*binom(n-1,floor((n-1)/2)).
    At r=0, evaluate the defining central binomial coefficients directly,
    since the first-order relation no longer solves for a_n.
    """
    r = _exact_parameter(r)
    last = _nonnegative_index(last, 'last')
    if r == 0:
        return [comb(n, n // 2) for n in range(last+1)]
    values = [1]
    quadratic = r*r+1
    for n in range(1, last+1):
        numerator = ((r+1)*comb(n-1, (n-1)//2)
                     - quadratic*values[-1])
        values.append(_reduced(Fraction(numerator) / r))
    return values


def central_binomial_polynomial(n):
    """Return ascending integer coefficients of a_n(r) as a polynomial in r.

    The coefficient at position j is (-1)**j*binom(n,floor((n-j)/2)).
    Its degree is exactly n, including the constant polynomial at n=0.
    """
    n = _nonnegative_index(n, 'n')
    return tuple((-1)**j * comb(n, (n-j)//2) for j in range(n+1))


def _representations(r=None):
    from sequence_formula_catalogue import variant

    parameter = '' if r is None else f'r={r}; '
    finite = (parameter + 'a(n)=sum_(k=0)^n '
              'binom(n,floor(k/2))*(-r)^(n-k)')
    generating = (parameter + 'sum_(n>=0) a(n)*z^n = '
                  '(1+z*C(z^2))/(sqrt(1-4*z^2)*(1+r*z*C(z^2))); '
                  'C(z)=(1-sqrt(1-4*z))/(2*z), C(0)=1')
    recurrence = (
        parameter + 'r*n*a(n)+((r^2+1)*n-2*r)*a(n-1)'
        '-(4*r*(n-2)+2*(r^2+1))*a(n-2)'
        '-4*(r^2+1)*(n-2)*a(n-3)=0 for n>=3; '
        'a(0)=1, a(1)=1-r, a(2)=r^2-r+2')
    if r == 0:
        recurrence += '; at r=0, a(n)=binom(n,floor(n/2)) for all n>=0'
    elif r is None:
        recurrence += '; at r=0, use a(n)=binom(n,floor(n/2))'
    return [
        variant('Defining finite sum', 'finite sum', finite,
                'Use n>=0 and the exponent-zero convention 0^0=1.', SOURCE),
        variant('Catalan generating function', 'generating function', generating,
                'C is the Catalan formal power series. Each square root has '
                'constant term one; C(0)=1 is its removable value.', SOURCE),
        variant('Uniform four-term recurrence', 'recurrence', recurrence,
                'The identity holds for every complex r. Its coefficient of '
                'a(n) vanishes at r=0. In that case use '
                'a(n)=binom(n,floor(n/2)).', SOURCE),
    ]


def central_binomial_catalogue():
    """Six known integer specializations, each with three exact representations."""
    from sequence_formula_catalogue import record

    specializations = (
        (-1, 'm1', 'A000079'),
        (0, '0', 'A001405'),
        (1, '1', 'A126869'),
        (2, '2', 'A127361'),
        (3, '3', 'A127362'),
        (4, '4', 'A127363'),
    )
    records = []
    for r, suffix, oeis in specializations:
        formulas = _representations(r)
        item = record(
            f'KFOR-CF-CB-{suffix}',
            f'Weighted central binomial sum · r={r}',
            'weighted central binomial sum',
            central_binomial_coefficients(r, COUNT-1), formulas,
            N=1, r=r, degree='n', closed_form_collection=True,
            closed_form_family=FAMILY_ID)
        item.update(
            source=SOURCE,
            source_note='Known OEIS specialization. The source gives a uniform '
                        'proof and records the earlier recurrence attributions.',
            status='Known sequence specialization · uniform proof',
            explanation='The finite sum, Catalan generating function, and '
                        'recurrence describe the same sequence at the stated '
                        'parameter. Indices begin at zero.',
            recurrence=formulas[2]['expression'],
            oeis=oeis, source_claimed_oeis=True,
            calculator={'mode': 'central_binomial', 'r': r})
        item['tags'] += ['closed forms', 'binomial sums', 'parameter recurrence',
                         'known sequence']
        records.append(item)
    return records


def central_binomial_families():
    """A source-linked parameter family with explicit specializations and proof."""
    title = 'Weighted central binomial sums'
    formula = 'a_n(r)=sum_(k=0)^n binom(n,floor(k/2))*(-r)^(n-k)'
    formulas = _representations()
    return [dict(
        id=FAMILY_ID, title=title, engine=None,
        domain='r in C; n>=0', formula=formula,
        note='A uniform four-term recurrence for an established binomial-sum '
             'family. The source includes every complex parameter and explains '
             'the degenerate recurrence at r=0.',
        paper='CLOSED-FORMS-II-III', locator=1,
        mode='Source-linked construction', derivation=SOURCE,
        family_type='discrete construction', source=SOURCE+'#L1',
        paper_title='Closed Forms Collection II and III, central binomial recurrence',
        url=f'generalized-families/{FAMILY_ID}.html',
        kind='generalized family', tags=['generalized', 'closed forms',
                                         'binomial sums', 'parameter recurrence'],
        status='Known family · uniform proof', offset=0, terms=[],
        formulas=formulas, recurrence=formulas[2]['expression'],
        explanation='The parameter specializations have established OEIS '
                    'identifications. No historical priority claim is made.',
        collection='generalized', paper_refs=[], family_names=[title])]
