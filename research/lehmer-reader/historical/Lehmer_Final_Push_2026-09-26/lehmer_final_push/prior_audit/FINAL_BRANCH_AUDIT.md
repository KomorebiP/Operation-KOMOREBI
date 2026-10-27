# Independent audit of the final arithmetic and polynomial theorems

26 September 2026. Reviewer: isolated subagent `prior_audit`.

**Primary verdict: proved as written.** This verdict applies to arithmetic
Theorem A and polynomial claim PC-ALL, precisely as pinned below. No claim
that Lehmer's conjecture has been solved is included. The raw arguments and
the critical external leaves were independently read and reconstructed.
Parent-supplied suggestions were visible, so this is not a blind review.

## Pinned statements

1. `arithmetic/NOTE.md`, Theorem A, SHA256
   `1ec2de878cc6fd4b09e5fc44d2564c1bf2240f6a19a407825ed66cbb3f909a89`:
   for every positive integer M, a positive natural density set of primes p
   satisfies p=-1 modulo 5M and tau(p)=0 modulo M. At every such prime,
   R(p^r)=0 modulo M simultaneously for every positive exponent r.
2. `null_span/POLYNOMIAL_CONTENT_THEOREM.md`, PC-ALL, SHA256
   `2e51d0136a6cd62f6887100a24c5567f3e5a56fb49f50c478fd05906471bd786`:
   every finite symmetric polynomial Q over C, restricted to sum v_i=0,
   whose weighted sum is zero on every shell, has every homogeneous component
   separately null on every shell. Consequently its weighted sum on each
   exact-content sector is zero.

The local filtered-Frobenius Theorem B is outside this audit. The audit does
not certify historical novelty, formalization, or any computational claim.
Neither audited theorem requires finite computation as proof.

## Arithmetic Theorem A

The dependency chain is Deligne's representation, an invariant lattice,
complex conjugation, one actual-image finite quotient, Chebotarev, and the
already proved local generating series for R. No surjectivity or independence
of residual representations is used.

| Obligation | Verdict | Check |
|---|---|---|
| Rank-two representation with trace tau(p) | Passed | Deligne's geometric Frobenius representation, dualized |
| Determinant epsilon_l^11 | Passed | Alternating pairing to Q_l(-11), then duality |
| Stable integral lattice | Passed | Compactness bounds all translates; their sum lies between two lattices |
| Exact trace zero at complex conjugation | Passed | In characteristic zero an involution of determinant -1 has eigenvalues 1,-1 |
| Prime l=2 | Passed | Diagonalization happens before reduction, over Q_2 |
| Compatible simultaneous conditions | Passed | Complex conjugation itself is an element of the joint actual image |
| Positive natural density | Passed | Nonempty conjugacy class in a finite Galois group |
| M=1 | Passed | Empty representation product; cyclotomic quotient modulo 5 remains |
| All local exponents | Passed | Formal quotient is 1, denominator has constant coefficient 1 |
| Simultaneous zero as an integer | Not claimed | The prime set depends on M |

The source's original W is cohomological, with geometric Frobenius giving
det(1-FX)=1-tau(p)X+p^11X^2. Its dual has that same polynomial at arithmetic
Frobenius. Its determinant is the eleventh power of the cyclotomic character.
The determinant statement at complex conjugation is unchanged under duality.
This convention is consistent; it does not invert p incorrectly.

For the invariant lattice, compactness of the image in GL_2(Q_l) gives an a
such that every translate of L0 lies in l^(-a)L0. The Z_l-span of all translates
contains L0, is contained in that larger finitely generated lattice, and is
stable. It is therefore a rank-two lattice, sufficient for every l-power
reduction. Normality and openness of the joint kernel give a finite Galois
extension. Every prescribed trace is a conjugacy invariant, and the
cyclotomic factor is abelian. The entire stated prime set, up to finitely
many ramified primes, is a union of conjugacy classes. Its natural density
therefore exists and is positive, not merely its lower density.

At a prime in the specified class, chi_5(p)=1, p^10=1 modulo M, p^11=-1
modulo M and tau(p)=0 modulo M. Thus

\[
\sum_{r\ge0}R(p^r)X^r
\equiv\frac{1-X^2}{1-X^2}=1\quad\text{in }(\mathbb Z/M)[[X]].
\]

This use of formal inversion works for composite and even M. The constant
coefficient is R(1)=1, while precisely all positive-exponent coefficients
vanish. The argument has no exponent bound or unsupported exchange of limits.

## Consequence for the synthetic model

The prime existence input in `prior_audit/SYNTHETIC_MODEL.md` is now verified
by this independent audit. Accordingly that model lemma is unconditional in
the ordinary mathematical sense of relying on established Deligne and
Chebotarev theorems. Its manuscript still isolates the input for provenance;
there is no remaining conjectural hypothesis.

Using Theorem A with 10M supplies q>B with q=-1 modulo 50M and tau(q)=0
modulo 10M. The model proof then establishes all claimed finite-data,
congruence, recurrence, parity, bound and primitive-square properties.
It does not require tau(q) to be nonzero as an integer. The manuscript's
explicit refusal to assert nonmodularity is correct: if tau(q)=0, the model
could be the original sequence itself. This logical distinction does not
weaken its counterexample to an implication from only the retained axioms.

## Polynomial claim PC-ALL

The dependency chain is the Euclidean homogeneous harmonic decomposition,
alternating symmetry, vector-valued harmonic theta modularity, the explicit
one-dimensional sign space, derivatives of modular forms, separation of
quasimodular weights, and the parent gcd scaling induction.

| Obligation | Verdict | Check |
|---|---|---|
| Homogeneous decomposition on the hyperplane | Passed | Its defining ideal is homogeneous and S5-invariant |
| Alternation of harmonic pieces | Passed | Uniqueness plus equivariance of the Laplacian and squared norm |
| No harmonic terms below degree 10 | Passed | Ten distinct reflection linear factors divide every alternating polynomial |
| Discriminant group and cosets | Passed | L*=A4*/sqrt(5), quotient A4*/5A4, cardinality 5^5 |
| One sign component | Passed | Repeated residues give an odd stabilizer; distinct residues give one free orbit of 120 |
| Trivial T character | Passed | Regular integral representatives have squared norm divisible by 10 |
| Trivial S character | Passed | Rank-four Weil action descends to SL2; on the sign line T=1 and (ST)^3=S^2 |
| Fixed coset and exponent | Passed | x=v/sqrt(5) has Q(x)=norm(v)^2/10 |
| Derivative factor and weight | Passed | Radial insertion multiplies q^n by (10n)^j; weight becomes 12+d |
| Odd degrees and fixed packets | Passed | J preserves content and W; odd Q changes sign and vanishes at fixed packets |
| Analytic convergence | Passed | Polynomial growth is dominated by the Gaussian on compact upper-half-plane subsets |
| Nonnegative transformation powers | Passed | Depth at most d/2 is less than weight 12+d |
| Zariski density of primitive bottom rows | Passed | Fix infinitely many c, vary infinitely many coprime d |
| Homogeneous weight separation | Passed | Distinct total degrees in an ordinary polynomial cannot cancel |
| Exact-content conclusion | Passed | Each homogeneous component is null; gcd induction applies separately |
| Infinite or nonsymmetric corrections | Out of scope | Neither is part of PC-ALL |

Several potentially fragile steps admit direct reconstruction.

First, for harmonic h_l in dimension four,

\[
\Delta(s_2^j h_l)=4j(l+j+1)s_2^{j-1}h_l.
\]

All coefficients on the right are nonzero for j>0. Induction on degree,
applied to the Laplacian of a homogeneous polynomial, constructs the harmonic
decomposition; successive powers of the Laplacian give uniqueness. Therefore
permutations preserve its individual components. In the coordinate ring of
the hyperplane, the ten reflection equations v_i-v_j are distinct irreducible
linear factors. Alternation forces each factor to divide h_l, hence their
product D divides it. There is no omitted exceptional harmonic degree below
10, and j<=d/2 follows from l=10+d-2j>=10.

Second, a coset of A4*/5A4 has a representative a+(t/5)1 with sum a_i=-t.
If all residues a_i modulo 5 are distinct, their sum is 0 modulo 5, forcing
t=0 among t=0,...,4. Each permutation of the five distinct residues gives
one coset; any two representatives with these residues and zero sum differ
by 5A4. If two residues coincide, their transposition fixes the coset and
negates the alternating theta coefficient. This proves the sign-space count
and the vanishing of all nonregular components. For regular cosets,
sum a_i^2 is 0 modulo 5 and even, so the quadratic exponent is integral.
The orthogonal S5 action commutes with the Weil action; hence the latter
restricts to this one-dimensional space. The stated S,T deduction is valid
there. Odd harmonic degrees need not be assigned a nonzero scalar modular
form, because J already cancels their packet sums.

Third, derivative insertion is exactly 10^j, not 2^j or 5^j, because the
fixed packet exponent is norm(v)^2/10. For the j-th derivative of the
harmonic piece the weight is

\[
(10+d-2j+2)+2j=12+d.
\]

Thus all radial pieces within one homogeneous Q_d have the same
quasimodular weight, while different degrees have different weights.

Finally, at fixed z the transformation formula produces an ordinary finite
polynomial in c,d; the depth bound prevents negative powers. Each primitive
integer pair occurs as a bottom row of an SL2(Z) matrix. If that polynomial
vanishes on all primitive pairs, fixing any positive prime c gives infinitely
many roots in d, and then varying c forces all coefficient polynomials to
vanish. Its homogeneous component of weight k therefore vanishes; evaluation
at (0,1) recovers F_k(z). This proves separate nullness without assuming
algebraic independence of Eisenstein series or silently treating a filtered
ring as a graded direct sum.

Once separate nullness is established, the parent content proof applies in
each degree over C exactly as over Q. In particular, finite nonhomogeneous
polynomials do not evade the opposite conserved content masses at n=121.
For a prime shell there is still only one content sector, so this result
does not force its mass to be nonzero.

## Exact source checks

The following full source passages were rechecked on 26 September 2026. No
new PDF cache was created, and no novelty search was attempted.

- Deligne, *Formes modulaires et representations l-adiques*, Bourbaki expose
  355; author-hosted English transcription dated 28 June 2004,
  https://publications.ias.edu/sites/default/files/5_FormesModulaires.pdf .
  The introduction identifies the rank-two representation and normalization;
  (3.20) supplies its pairing; (4.8) fixes geometric versus arithmetic
  Frobenius; (5.7), specialized to k=10, gives the required characteristic
  polynomial. The construction is unconditional; the historical conditional
  discussion of Weil bounds is not used to prove Theorem A.
- Stevenhagen–Lenstra, *Chebotarev and his density theorem*, author-hosted
  manuscript, https://websites.math.leidenuniv.nl/algebra/chebotarev.pdf .
  PDF page 2 was inspected as an image: it defines natural density relative
  to rational primes and states the finite-Galois conjugacy-class theorem
  with density |C|/|G|. The application meets exactly those hypotheses.
- Ibukiyama–Williams, *Hermitian modular forms and algebraic modular forms
  on SO(6)*, arXiv:2505.23497v1, Section 3.4, printed pages 18–19,
  https://arxiv.org/pdf/2505.23497 . The checked vector-valued harmonic theta
  construction has weight degree plus half the rank, for the discriminant
  Weil representation. Here rank is four and the explicit sign-line proof
  supplies scalar full level. No conjectural correspondence from that paper
  is used.

The strongest safe joint outcome is therefore an exact finite-modulus
limitation, an unconditional synthetic-model theorem for the retained
arithmetic axioms, and content conservation for every finite symmetric
polynomial universal null correction. The remaining implication for Lehmer
is still nonvanishing of the actual prime-shell total.
