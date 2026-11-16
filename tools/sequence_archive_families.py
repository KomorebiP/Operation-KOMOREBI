"""Family descriptions and coordinate maps for the preserved KOM001–KOM090 archive.

These bindings do not regenerate, modify, or reclassify the archived integers.
The source generator and each record retain the exact original convention.
"""

ARCHIVE_GROUPS = (
    (1, 7, 'GF-RECIPROCAL'),
    (8, 12, 'GF-CLASSICAL-REFERENCES'),
    (13, 16, 'GF-KBONACCI'),
    (17, 28, 'GF-RECIPROCAL'),
    (29, 35, 'GF-BLOCK-LOGARITHMIC'),
    (36, 42, 'GF-BLOCK-TRANSFORMS'),
    (43, 46, 'GF-BLOCK-HANKEL'),
    (47, 57, 'GF-BLOCK-VALUATIONS'),
    (58, 65, 'GF-DIGIT-RESIDUES'),
    (66, 68, 'GF-CYCLIC-SUBSETS'),
    (69, 74, 'GF-PASCAL-VALUATIONS'),
    (75, 76, 'GF-TOTIENT-PREFIX'),
    (77, 77, 'GF-PRIME-POWER-SUPPORT'),
    (78, 79, 'GF-COLLATZ-READOUTS'),
    (80, 84, 'GF-SMITH-POLYNOMIALS'),
    (85, 87, 'GF-CLIFFORD-WORDS'),
    (88, 90, 'GF-CYCLIC-MASKS'),
)
ARCHIVE_MEMBERSHIP = {
    f'KOM{number:03d}': family
    for first, last, family in ARCHIVE_GROUPS
    for number in range(first, last + 1)
}


def archive_parameters(identifier):
    """Return explorer parameters only for identical supported constructions."""
    if identifier not in ARCHIVE_MEMBERSHIP:
        return None
    number = int(identifier[3:])
    if 1 <= number <= 7:
        return dict(N=number + 1, r=1)
    if 13 <= number <= 16:
        return dict(k=number - 10)
    if 17 <= number <= 26:
        return dict(N=2 + (number - 17) // 2, r=2 + (number - 17) % 2)
    if number in (27, 28):
        return dict(N=number - 20, r=2)
    return None


def archive_definitions():
    """Describe documented discrete constructions, without adding browser engines."""
    definitions = [
        (
            'GF-CLASSICAL-REFERENCES', 'Classical combinatorial reference sequences',
            369, 'n>=0; the selected named sequence fixes its initial values and normalization',
            'B(n+1)=sum_(k=0)^n binom(n,k) B(k); C(n)=binom(2n,n)/(n+1)',
            'Bell, ordered Bell/Fubini, derangement, Euler up/down, and Catalan records provide classical reference points. '
            'The displayed formulas are examples; each linked record supplies its own complete definition and initial values. '
            'This is a reference collection, not one new parameter family.',
        ),
        (
            'GF-BLOCK-LOGARITHMIC', 'Euler-block logarithmic derivative coefficients',
            46, 'N>=2; n>=0; the stored archive uses N=2..8',
            "L_N(n)=(Nn)! [z^(Nn)] (-z D_N'(z)/D_N(z)); L_N(0)=0",
            'Here D_N(z)=sum_(m>=0) (-1)^m z^(Nm)/(Nm)!. The extra factor z changes both the degree and the coefficient scale. '
            'For n>=1, L_N(n)=Nn T_N(n-1), where T_N is the transfer-tangent sequence. '
            'The archived values keep this convention and are not silently replaced by tangent-explorer values.',
        ),
        (
            'GF-BLOCK-TRANSFORMS', 'Binomial and Stirling transforms of Euler blocks',
            56, 'N>=2; n>=0; choose the binomial or Stirling transform',
            'B_N(n)=sum_(k=0)^n binom(n,k) A_N(k); S_N(n)=sum_(k=0)^n S(n,k) A_N(k)',
            'A_N(k)=(Nk)! [z^(Nk)] D_N(z)^(-1), with the alternating factorial block D_N. '
            'S(n,k) denotes the Stirling number of the second kind. The transforms act on the local sequence index k, '
            'not on the source degree Nk. Archived examples cover binomial transforms at N=3..6 and Stirling transforms at N=3..5.',
        ),
        (
            'GF-BLOCK-HANKEL', 'Hankel determinants of Euler blocks',
            103, 'N>=2; n>=0; determinant order n+1',
            'H_N(n)=det(A_N(i+j))_(0<=i,j<=n)',
            'A_N is the factorial-normalized reciprocal Euler block. The matrix uses local indices i+j. '
            'The four archived sequences use N=2..5 and store determinant sizes 1 through 9. '
            'Signed determinant values are retained; the finite table does not assert positivity for every size.',
        ),
        (
            'GF-BLOCK-VALUATIONS', 'Prime-adic valuations of Euler blocks',
            149, 'N>=2; p prime; n>=0; A_N(n) nonzero',
            'V_(N,p)(n)=v_p(A_N(n))',
            'A_N is the positive reciprocal Euler block. For a nonzero integer a, v_p(a) is the exponent of p in a. '
            'The archive contains eleven declared (N,p) choices and their exact finite valuations. '
            'No finite integer is assigned to v_p(0), and these values do not supply a uniform valuation formula.',
        ),
        (
            'GF-DIGIT-RESIDUES', 'Digit-sum residue packets',
            179, 'base b>=2; modulus m>=2; 0<=r<m; word length n>=0',
            'C_(b,m,r)(n)=sum_(j>=0) [x^(mj+r)] (1+x+...+x^(b-1))^n',
            'Count length-n base-b digit strings whose digit sum is r modulo m. Leading zeros are allowed. '
            'The empty word contributes one at n=0 exactly when r=0. Binary popcount packets are the b=2 specializations. '
            'The archived generator updates the entire residue-count vector exactly.',
        ),
        (
            'GF-CYCLIC-SUBSETS', 'Cyclic subset-sum packets',
            192, 'N>=1; 0<=r<N; choose all subset sizes or even subset size',
            'F_N(x,y)=product_(j=1)^(N-1) (1+y x^j)',
            'The sum-residue count is the sum of coefficients of x^(qN+r)y^k in F_N, over q>=0 and the allowed k. '
            'Selecting even k keeps even-cardinality subsets of {1,...,N-1}. The empty subset is included. '
            'Here N is the sequence index: the residue-one archive starts at N=2, while residue-zero records start at N=1.',
        ),
        (
            'GF-PASCAL-VALUATIONS', 'Pascal-row valuation distributions and sums',
            167, 'p prime; n>=0; valuation level j>=0',
            'C_(p,j)(n)=sum_(k=0)^n [v_p(binom(n,k))=j]; V_p(n)=sum_(k=0)^n v_p(binom(n,k))',
            'Square brackets in the counting formula denote an indicator, equal to one when its condition holds. '
            'The archive includes level j=1,2 for p=2,3 and the corresponding row sums. '
            'All binomial coefficients are nonzero. The familiar digit-carry interpretation is classical.',
        ),
        (
            'GF-TOTIENT-PREFIX', 'Totient prefix-fiber statistics',
            230, 'n>=1; phi is Euler’s totient with phi(1)=1',
            'M(n)=sum_(k=1)^n [phi(k)=phi(n)]; D(n)=#{phi(k):1<=k<=n}',
            'M(n) counts matches to phi(n) only inside the prefix 1..n. D(n) counts distinct totient values in that prefix. '
            'The two archived readouts retain this finite-prefix definition; they do not count unrestricted inverse-totient fibers '
            'and do not settle Carmichael’s conjecture.',
        ),
        (
            'GF-PRIME-POWER-SUPPORT', 'Prime-power support and exponent slack',
            222, 'integer n>=1; rad(1)=1',
            'E(n)=n/rad(n); rad(n)=product_(p|n) p',
            'The product defining rad(n) runs over distinct prime divisors. Dividing n by its radical retains the '
            'multiplicity beyond the first copy of each prime. E(1)=1. This archived arithmetic function is a classical reference.',
        ),
        (
            'GF-COLLATZ-READOUTS', 'Odd Collatz jump and image readouts',
            246, 'n>=0; the odd input is 2n+1',
            'J(n)=v_2(3(2n+1)+1); U(n)=(3(2n+1)+1)/2^(J(n))',
            'J(n) records the exact power of two removed after one odd Collatz step, and U(n) is the resulting odd integer. '
            'These are pointwise readouts indexed by the input, not consecutive positions in a single orbit. '
            'Their finite values do not establish a uniform jump bound or convergence of every orbit.',
        ),
        (
            'GF-SMITH-POLYNOMIALS', 'Formal Smith transfer polynomials and coefficient readouts',
            267, 'n>=0; polynomial variable s; coefficient column 0<=k<=n',
            'P_0(s)=Q_0(s)=1; P_(n+1)(s)=(1+s)P_n(s)+Q_n(s); Q_(n+1)(s)=P_n(s)',
            'The five archived readouts are P_n(0), P_n(1), the sum of squared coefficients, the coefficient at floor(n/2), '
            'and the complete coefficient triangle. For the triangle, flat j=n(n+1)/2+k identifies [s^k]P_n(s). '
            'This is a formal transfer-polynomial model; no particular physical circuit realization is asserted.',
        ),
        (
            'GF-CLIFFORD-WORDS', 'Single-qubit Clifford identity-word counts',
            301, 'n>=0; gate alphabet {H,S}, {H,S,S^(-1)}, or {H,S,X}',
            'a_G(n)=(M_G^n)_(e,e)',
            'M_G is the transition matrix for left multiplication by the declared gates on the 24 signed-Pauli-axis '
            'Clifford actions, and e is the identity action. Matrix entries count gate choices. '
            'Words are ordered and repeated gates remain distinct choices. Identity means identity modulo global phase; '
            'these are finite-group walks, not arbitrary SU(2) matrix identities.',
        ),
        (
            'GF-CYCLIC-MASKS', 'Cyclic subgroup-coset mask counts',
            321, 'n>=1; optional subgroup-size cutoff K>=1',
            'C_K(n)=sum_(h|n, h<=K) n/h; C(n)=sum_(h|n) n/h',
            'A subgroup of the cyclic group Z/n of size h has n/h cosets. The archived records use all subgroup sizes, '
            'or the cutoffs K=2 and K=3. The unrestricted count equals the classical divisor sum. '
            'Only subgroup-coset masks are counted, not every possible contractive mask.',
        ),
    ]
    result = []
    for identifier, title, line, domain, formula, note in definitions:
        reference = identifier == 'GF-CLASSICAL-REFERENCES'
        result.append(dict(
            id=identifier, title=title, engine=None, domain=domain, formula=formula,
            note=note, paper='ARCHIVE', locator=line,
            mode='Classical reference collection' if reference else 'Source-defined discrete construction',
            family_type='reference collection' if reference else 'discrete construction',
        ))
    return result
