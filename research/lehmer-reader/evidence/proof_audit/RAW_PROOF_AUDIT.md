# Raw proof audit of the Lehmer research packages

Audit date: 9 October 2026. Publication: Operation Komorebi, Conjecture Series 07.

Normalized target: for the fixed normalized weight-12 level-one cusp form
\(\Delta(q)=q\prod_{m\ge1}(1-q^m)^{24}=\sum_{n\ge1}\tau(n)q^n\), prove
\(\tau(n)\ne0\) for every positive integer \(n\).

**Primary verdict: incomplete, with the smallest missing implication being
nonvanishing of the actual prime coefficient \(\tau(p)\).** The audited program
does not supply this implication. The internal proofs of the side theorems
listed below reconstruct correctly. Their external inputs are separately
authenticated in the release literature audit. Finite rank and coefficient
checks have only their stated ranges.

This pass read the raw notes and reconstructed critical arguments. It did not
use the older audit verdict as a proof. Existing historical review notes were
visible, so this is an isolated critical review rather than a claim of a blind
experiment or a mathematically independent model. No manuscript or historical
source was modified. Source hashes are recorded in `source_hashes.json`.

## Source locator convention

All locators are relative to the release project root `lehmer_set/`.

* `TREE` means `historical/Lehmer_Packet_Tree_Sharp_Boundary_2026-09-26/lehmer_attempt/RESEARCH_NOTE.md`.
* `TRANSPORT` means `historical/Lehmer_Primitive_Content_Transport_2026-09-26/lehmer_transport/RESEARCH_NOTE.md`.
* `PC-ALL` means `historical/Lehmer_Final_Push_2026-09-26/lehmer_final_push/null_span/POLYNOMIAL_CONTENT_THEOREM.md`.
* `ARITHMETIC` means `historical/Lehmer_Final_Push_2026-09-26/lehmer_final_push/arithmetic/NOTE.md`.
* `INTERPOLATION` means `historical/Lehmer_Final_Push_2026-09-26/lehmer_final_push/null_span/NOTE.md`.
* `MODEL` means `historical/Lehmer_Final_Push_2026-09-26/lehmer_final_push/prior_audit/SYNTHETIC_MODEL.md`.
* `NULLS` means `historical/Lehmer_null_packet_resolution_2026-09-26/lehmer_residual_audit/continuation_symmetry/RESEARCH_NOTE.md`.
* `RESIDUAL` means `historical/Lehmer_residual_audit_2026-09-26/lehmer_residual_audit/RESEARCH_NOTE.md`.

## Exact claim cards

### P1. Packet identity and its domain

Objects are integer vectors with five coordinates indexed by 0 through 4,
\[
\mathcal V_n=\{v:v_i\equiv i\pmod5,\ \sum_i v_i=0,\ \sum_i v_i^2=10n\},
\quad D(v)=\prod_{i<j}(v_i-v_j),\quad W(v)=D(v)/288.
\]
The identity is \(\tau(n)=\sum_{v\in\mathcal V_n}W(v)\) for every positive
integer \(n\). External leaf: Han's five-core V-coding and hook identity,
specialized to five cores and parameter 25. The exact shift is core size
\(n-1\), with \(\|v\|^2/10-1=n-1\). This shift cannot be dropped.

Every packet weight is a nonzero integer. Integrality follows from the
determinant of the integer-valued binomial basis. The ten reversed differences
give positive overall sign, including at negative coordinates. Distinct
residues ensure no coordinate difference is zero. Modulo 5, the numerator has
the residue 288, so \(W(v)\equiv1\pmod5\).

The involution is \(J(v)_i=-v_{-i\bmod5}\). Its coordinate permutation has
two transpositions, and negation contributes degree-ten sign +1. Thus
\(W(Jv)=W(v)\), not its negative. J also preserves the shell and content.

Verdict: proved using the authenticated Han input S02 and the reconstructed
internal normalization and invariance arguments. Locators: NULLS sections 1 and 3,
TRANSPORT section 1, TREE section 1.

### P2. Exact primitive decomposition

For \(g(v)=\gcd(v_0,\ldots,v_4)>0\), one has \(5\nmid g(v)\).
Define \(R(n)\) by summing only packets of content one. Let
\(\chi(g)=(g/5)\), with value zero when 5 divides g. Then
\[
\tau(n)=\sum_{g^2\mid n}\chi(g)g^{10}R(n/g^2),\qquad
R(n)=\sum_{d^2\mid n}\mu(d)\chi(d)d^{10}\tau(n/d^2).
\]

The scaling map is \(u_j=v_{gj\bmod5}/g\). It gives standard residues after
division, zero coordinate sum, and squared norm \(10n/g^2\). The latter is
divisible by 10: residues give divisibility by 5, and \(u_i^2\equiv u_i\pmod2\)
gives divisibility by 2. Therefore \(g^2\mid n\). The inverse map recovers
all packets of exact content g. The residue permutation has sign chi(g),
so the weight factor is \(\chi(g)g^{10}\). The square-supported Möbius inverse
has precisely the displayed sign and exponent.

Verdict: proved internally from P1. Locator: TRANSPORT section 4.

### P3. Homogeneous content conservation

For a symmetric homogeneous polynomial Q of degree d, over rational or complex
coefficients, suppose \(\sum_{v\in\mathcal V_n}W(v)Q(v)=0\) for every n.
Then the same sum is zero inside each exact-content sector of each shell.

Symmetry removes the residue permutation, while homogeneity contributes
\(g^d\). Thus the full Q sum is
\(\sum_{g^2\mid n}\chi(g)g^{10+d}R_Q(n/g^2)\). The g=1 term is R_Q(n).
All other nonzero terms use a smaller positive index, so induction proves
R_Q(n)=0. The n=1 base has no smaller nonzero term. Linearity permits finite
combinations with coefficients chosen for a target shell.

Verdict: proved internally. Locator: TRANSPORT section 4. This argument alone
does not cover arbitrary nonhomogeneous polynomials or arbitrary functions.

### P4. Finite symmetric polynomial content conservation

Let Q be any finite symmetric polynomial over the complex numbers, restricted
to the four-dimensional hyperplane H with coordinate sum zero. Suppose it is
universally weighted-null. Every homogeneous component Q_d is separately
universally null, and its exact-content sums vanish separately. Therefore all
exact-content Q sums vanish.

The internal proof is reconstructed in detail below. External leaf: harmonic
theta modularity for an even lattice and a homogeneous harmonic polynomial.
Verdict: proved using the authenticated harmonic theta input S03 and the
reconstructed internal argument. Locator: PC-ALL sections 1 through 3. Infinite series, nonsymmetric
polynomials, shell-dependent functions, and arbitrary nonpolynomial
corrections are outside its hypotheses.

### P5. Dyadic mixed-sign boundary

For k at least one put M=2^k. A sector is the residue vector
\(c_i=(v_i-i)/5\pmod M\), identifying residue vectors related by J. Define
\[
N_k=\left\lceil\frac{100M^2+10M+2}{35}\right\rceil
=\frac{20M^2+2M+\gamma_k}{7},
\]
where gamma is 7, 1, 6 when k modulo 3 is 1, 2, 0 respectively. Every sector
on every positive shell n below N_k is sign-pure, and a mixed-sign sector
exists at n=N_k.

Verdict: internal universal proof passed. Locator: TREE section 3. It is a
first-shell theorem over all positive integer indices. It does not assert
that N_k is prime, and it is distinct from a unique-J-orbit threshold.

### P6. Refinement exact sequence

Fix one shell and a finite list of universally null Q_j. Let t_k be the
occupied-sector mass vector and M_k its correction matrix. If A aggregates
child sectors to parents, then t_k=A t_(k+1), M_k=A M_(k+1). Write
H_k=ker(1^T), T_k=im M_k and E_k=H_k/T_k. There is an exact sequence
\[
0\longrightarrow\ker A/M_{k+1}(\ker M_k)
\longrightarrow E_{k+1}\longrightarrow E_k\longrightarrow0.
\]

Every occupied parent has a child, so A maps the zero-total spaces onto one
another. It maps T_child onto T_parent by the defining matrix identity.
Moreover \(T_{k+1}\cap\ker A=M_{k+1}(\ker M_k)\). Since a zero A image also
has zero total, ker A is already a subspace of H_child. These facts give
exactness and the claimed rank-difference formula.

Verdict: proved internally. Locator: TRANSPORT section 2. E_k is a vector
space defect. It does not count failed sign certificates, and nonzero E_k
does not imply that a sign certificate is impossible.

### P7. Primitive prime-power nonvanishing and zero equivalence

R is multiplicative and has local factor
\[
\sum_{r\ge0}R(p^r)X^r
=\frac{1-\chi(p)p^{10}X^2}{1-\tau(p)X+p^{11}X^2}.
\]
For every prime p and m at least one, \(R(p^{2m})\ne0\). Consequently
R(s^2) is nonzero for every positive integer s, including s=1. For odd
p different from 5, every odd block is \(\tau(p)\) times an odd integer
polynomial, interpreted by polynomial division before evaluation when
\(\tau(p)=0\). Together with the p=2 and p=5 controls this proves
\[
R(n)=0\iff\exists p:\ v_p(n)\text{ is odd and }\tau(p)=0\iff\tau(n)=0.
\]

Verdict: internal proofs reconstructed correctly, with classical Hecke,
parity and modulo-5 inputs authenticated separately. Locator: TRANSPORT
sections 5 through 7 and TREE section 1. The square theorem does not imply
prime nonvanishing, because a=0 gives nonzero even residual blocks directly.

### P8. Actual fixed-modulus survivors

For every positive integer M, a set of actual rational primes of positive
natural density satisfies \(p\equiv-1\pmod{5M}\) and
\(\tau(p)\equiv0\pmod M\). For each such prime and every positive exponent r,
\(R(p^r)\equiv0\pmod M\).

The proof uses the actual joint finite image of Deligne's representations and
the cyclotomic character. Complex conjugation supplies a compatible element,
without image-surjectivity or independence assumptions. Characteristic-zero
diagonalization before reducing modulo 2 is essential. Chebotarev supplies a
positive-density Frobenius class. The local R factor then reduces to
\((1-X^2)/(1-X^2)=1\) over \((\mathbb Z/M)[[X]]\), since the constant term
of the denominator is a unit. R(1)=1 is preserved.

Verdict: proved using the authenticated Deligne and Chebotarev leaves S05,
S06 and S08 and the reconstructed internal application. Locator:
ARITHMETIC section 1. The prime varies with M. There is no integer-zero
conclusion and no exclusion of adaptive moduli.

### P9. Local zero-trace compatibility

For each prime p take D with basis e_1,e_2 and
\(\varphi(e_1)=e_2\), \(\varphi(e_2)=-p^{11}e_1\), N=0. For any rational
line L set the filtration to D in degrees at most 0, L in degrees 1 through
11, and zero thereafter. Then D is weakly admissible with Frobenius
polynomial \(X^2+p^{11}\).

Both total invariants equal 11. A proper rational Frobenius-stable line would
give an eigenvalue in Q_p whose valuation has twice an integer equal to 11,
which is impossible. Therefore all proper-subobject inequalities are vacuous.
The local crystalline realization uses Colmez-Fontaine and the N=0 comparison
identity. These are cohomological filtration and Frobenius conventions.

Verdict: weak admissibility proved internally, and crystalline realization
proved using the authenticated classification input S09. Locator:
ARITHMETIC section 2. This is not an identification with the global Delta
representation at any prime.

### P10. Countermodel for weaker arithmetic premises

For every real B at least one and positive M, there is an integral
multiplicative sequence f agreeing with tau through B and modulo 10M at all
indices, obeying all weight-12 Hecke recurrences, the global divisor bound,
the parity and mod-5 conditions, and primitive-square nonvanishing, while
f(q)=0 at some prime q>B.

Apply P8 with modulus 10M, select q>B in its positive-density set, replace the
prime parameter tau(q) by zero, and leave all other parameters unchanged.
Integral recurrence induction gives agreement modulo 10M. At q the even
blocks are \((-q^{11})^m\), odd blocks zero, and the primitive even blocks
are \((-1)^m q^{11m-1}(q+1)\). The local divisor bound holds and multiplies
globally. Other square blocks are those of R.

Verdict: proved from P7, P8 and the classical Deligne bound. Locator: MODEL.
This is a counterexample to an implication from precisely those weaker
premises. It is not a counterexample to Lehmer for the fixed Delta. It is
also not valid to call f nonmodular unconditionally: if tau(q)=0 already,
the construction could equal tau.

### P11. Interpolation and sign criteria

On a fixed shell the even symmetric invariants
\((s_4/C^2,s_3^2/C^3,s_3s_5/C^4,s_5^2/C^5)\), C=10n, identify exactly
the J-orbits. For N orbits, arbitrary rational orbit values are realized by
an even symmetric homogeneous polynomial of degree 10(N-1), with a constant
polynomial at N=1. This follows from Newton identities and an explicit
Lagrange basis in a separating degree-ten invariant.

Verdict: proved internally. Locator: INTERPOLATION sections 1 and 2.
Universal nullness is not part of the conclusion. The constructed transfers
at 7 and 31 fail at shell 1. The harmonic projection of s_2 D into degree 12
is zero although the polynomial is nonzero on a shell, so harmonicization
has no general value-preservation principle.

If all content-preserving transfers were available, common-sign feasibility
would still depend on the signs of the conserved content totals. At a prime,
where there is one content class, a nonzero common-sign corrected vector
exists exactly when tau(p) is nonzero. Completeness does not establish that
the common sign is nonzero. Locator: INTERPOLATION section 4, TREE section 5B.

## Earlier residual and auxiliary-polynomial claims

The initial residual note gives an exact divisor convolution, rather than a
new nonvanishing input. For primes p, with
\(S_4(p)=\sum_{k=1}^{p-1}k^4\sigma(k)\sigma(p-k)\), it states
\[
\tau(p)=p^4(85-49p-84p^2+50p^3)-840S_4(p).
\]
The displayed constant and coefficients are consistent with the full-index
formula after substituting sigma(p)=1+p and sigma_3(p)=1+p^3. For p>7,
840 is a p-adic unit, so p^4 divisibility is equivalent on both sides. The
Deligne bound is strictly less than p^6 for p>=5, giving an exact zero test
modulo p^6. These are reductions. They do not show that the forbidden residue
never occurs, and the stronger bound v_p(tau(p))<=3 remains a separate
unproved sufficient target.

The differential extraction has a nonzero cusp coefficient. Its final
identity is
\(\Delta=50\mathcal D^4B+35\mathcal D^4A-84\mathcal D^5A
-840A\mathcal D^4A\), where A and B are the divisor-sum series. The trace
moment inversion likewise retains tau with coefficient -1 in the tenth
moment. Neither an invertible differential extraction nor a unit triangular
inverse removes the original unknown coefficient. The precise trace-moment
normalization is an external-source leaf rather than something to fill from
memory. Locator: RESIDUAL sections 1 through 3.

The dyadic counterexample refutes a narrowly typed integral interpolation
claim. Every restricted integral power series in Z_2 has integral divided
differences and is 1-Lipschitz. The historical values at u=15 and u=47 of
F(u)=tau(2^14u-1)/2^14 have distinct residues modulo 2 while the arguments
agree modulo 32. The claimed divided difference is therefore not integral.
Exact authentication of the large coefficients is computational evidence.
This does not refute all analytic models, models with denominators, finer
residue classes or extra variables. Locator: RESIDUAL section 4.

For fixed n, the auxiliary packet polynomial P_n(T) is an actual integer
polynomial of degree at most ten, and P_n(5)=288tau(n). Root analysis in its
auxiliary variable is legitimate. It is not interpolation in n or in the
prime index. At n=499 the relevant simple root has one extra 5-adic digit of
valuation, giving v_5(tau(499))=4. At n=16249, G(1)=15 modulo25 and G'(1)=0
modulo5 force G(1+5y)=15 modulo25 for every y in Z_5. The latter is a
universal statement about one fixed residue class of one fixed polynomial,
proved by the exact integral Taylor identity. A sample of 625 y values is
only a secondary check. Locator: the five-core package's
`continuation_5core/RESEARCH_NOTE.md`, sections 3 through 5.

Each individual auxiliary packet polynomial has finite roots in [-4,4], but
the aggregate signed sum need not. The exact signs P_31(10)<0<P_31(11)
provide a valid counterexample to the proposed aggregate root-location rule.
The all-prime irreducibility statement is not proved: the factorization
record covers only primes through 2000. Locator: NULLS section 9.

The auxiliary valuation equalities v_ell(tau(p))=v_ell(p+1), for ell=2,3,5,
are refuted by explicit prime examples in the final valuation branch. The
first-failure labels require the exhaustive prime iterator through 150000
and exact coefficient authentication. They are finite minimum searches, not
counterexamples to Lehmer and not a rejection of every possible valuation
estimate. These finite evidence obligations are assigned to the fresh
computation audit, rather than inferred from the printed result tables.

## Critical reconstruction: PC-ALL

The ring on H is graded because its defining linear relation is homogeneous.
For a symmetric component Q_d, DQ_d is alternating of degree 10+d. Unique
Euclidean harmonic decomposition writes it as
\(\sum_j s_2^j h_{10+d-2j}\). The Laplacian and squared norm commute with
permutations, so every harmonic piece is alternating. An alternating
polynomial vanishes on each reflection hyperplane v_i=v_j. The ten distinct
linear factors are irreducible in the polynomial ring on H and all divide
the polynomial. Therefore D divides every nonzero piece, its degree is at
least 10, and j is at most d/2. This controls depth and transformation powers.

For L=sqrt(5)A_4, the discriminant module is A_4*/5A_4 with 3125 elements.
Write a representative a+(t/5)1 with sum a_i=-t and 0<=t<5. Equal coordinate
residues admit a transposition stabilizer and kill an alternating theta
component. Distinct residues form a single free S_5 orbit of 120 elements,
and force t=0. Consequently the sign space has dimension one. For regular
cosets the norm is divisible by 5, and is even because the coordinate sum is
zero. Thus the Weil T action is 1 there. The Weil action commutes with S_5
and descends to SL_2 in rank four. On its invariant one-dimensional sign line
the relation (ST)^3=S^2 gives S=1. The fixed regular coset is v/sqrt(5) and
its quadratic exponent is ||v||^2/10. The source-dependent harmonic theta
lemma therefore gives the exact scalar full-level weight l+2.

The radial insertion s_2^j multiplies the nth Fourier coefficient by (10n)^j.
It is exactly 10^j times the jth q derivative, not 5^j or 2^j. Its
quasimodular weight is (10+d-2j+2)+2j=12+d and depth at most d/2. Polynomial
lattice growth is dominated by the Gaussian in the upper half-plane, so
termwise differentiation is justified. Odd Q_d components cancel under J
separately in every content class. Fixed J packets have Q_d(v)=0 in that case.

For the finitely many even weights, at a fixed z the transformation laws of
a proposed relation sum F_k=0 form the polynomial
\(P_z(c,d)=\sum_{k,r}f_{k,r}(z)c^r(cz+d)^{k-r}\). All powers are nonnegative
by the depth bound. P_z vanishes on every primitive integer bottom row of an
SL_2 matrix. For each positive prime c there are infinitely many admissible d,
so the polynomial in d is zero. Its coefficients then vanish at infinitely
many c. Hence P_z is identically zero. Distinct weights have distinct total
degrees as ordinary homogeneous polynomials. Their components vanish
separately, and evaluating each at (c,d)=(0,1) gives F_k(z)=0. This proves
weight separation without an unsupported algebraic-independence assertion.

Each homogeneous null then obeys P3. Summing finitely many zero content sums
proves PC-ALL. The proof is universal. Finite theta tests authenticate concrete
Q polynomials but do not establish this all-polynomial theorem.

## Critical reconstruction: sharp tree boundary

Opposite-sign packets in the same J-identified sector can be oriented so
w-v=5Md with nonzero d in A_4. Put a=5M/2 and m=(v+w)/2. For k>=1 these are
integral, equal norms give m dot d=0, and
\(10n=||m||^2+a^2||d||^2\). The positive even norm of d cannot be 2: then
d is a root e_i-e_j, and orthogonality forces a coordinate difference of v
equal to plus or minus 5M, contradicting its nonzero residue i-j modulo 5.

If ||d||^2>=6, the lower bound is already strictly stronger than the desired
one for every M>=2. If ||d||^2=4, d has two +1 entries, two -1 entries and a
zero. Two coordinate pairs have equal d entries, eight do not. No difference
factor is zero. If all eight unequal-pair contributions to D(v)D(w) were
negative, their product would be positive. Thus some such contribution is
positive, forcing |m_i-m_j|>=a|delta|+1 by integrality. Projection of e_i-e_j
to d-perp has squared norm 2-delta^2/4. Cauchy gives the smaller lower bound
4(a+1)^2/7 when |delta|=1, and a stronger one for |delta|=2. Hence
\(n\ge(100M^2+10M+2)/35\), and integer rounding gives N_k.

The k=1 witness lies on shell 13. For the three k modulo 3 families the sum,
norm and coordinate residues can be checked as exact affine and quadratic
identities. Their coordinate-difference signs stay fixed on the stated ranges,
with opposite Vandermonde signs. These symbolic identities, coupled with
M modulo 7 cycling through 2,4,1, prove all-depth attainment. Checking
k<=64 is secondary evidence and does not supply the universal quantifier.

## Obligation matrix

The dependency graph can be read as the following exact mapping. The last row
has a missing leaf and is not licensed by any earlier row.

| Claim | Internal dependencies | External or execution leaf |
|---|---|---|
| P1 packet identity | Residues and determinant normalization | Han five-core and hook identities |
| P2 primitive transform | P1, gcd scaling, square Möbius inversion | None beyond P1 |
| P3 homogeneous conservation | P2 scaling and induction | None |
| Universal concrete null Q | Alternation, H Laplacian, sign-line argument | Harmonic theta theorem, level-one valence, exact symbolic certificate |
| P4 finite-polynomial conservation | Harmonic decomposition, weight separation, P3 | Harmonic theta theorem |
| P5 tree boundary | Sector definition, projection bound, witness identities | Exact witness algebra, with no unbounded search requirement |
| P6 refinement | Aggregation identity and quotient linear algebra | None |
| P7 square and zero criteria | P2, recurrence polynomial and integer-root arguments | Hecke, parity, modulo-5 contracts |
| P8 fixed-modulus survivors | Stable lattice, exact involution trace, actual joint image, P7 local factor | Deligne representations, Chebotarev |
| P9 crystalline local model | Odd valuation, total Hodge and Newton invariants | Colmez-Fontaine and N=0 comparison |
| P10 arithmetic countermodel | P7, P8, multiplicative construction | Deligne size bound for unchanged blocks |
| P11 orbit interpolation | Newton identities and degree-ten separator | None beyond packet domain |
| Lehmer nonvanishing | Prime reduction and actual fixed Delta | Missing independent all-prime nonzero coefficient implication |

| Obligation | Result | Reason and scope |
|---|---|---|
| Objects and shell normalization | Passed internally | Fixed integer residues, zero sum, exponent norm squared divided by 10 |
| Packet identity external normalization | External-source dependent | Han's core-size shift and weight factor must be authenticated |
| J action, integrality and content scaling | Passed | Exact determinant and permutation arguments |
| Primitive transform and square theorem | Passed internally | Covers a=0, valuation 5, primes 2 and 5, exponent zero controls |
| Tau prime-power zero reduction | Passed internally | Root-of-unity argument includes explicit 2 and 3 exceptions |
| Harmonic operator and factor degrees | Passed | Polynomial cancellation, H metric and alternation |
| Scalar theta normalization | Passed internally with external leaf | Rank-four harmonic theta theorem must be authenticated |
| Separation of finite quasimodular weights | Passed | Ordinary polynomial degrees and Zariski-density proof |
| All finite symmetric polynomial content theorem | Passed internally with external leaf | No extension to nonsymmetric or nonpolynomial objects |
| Tree boundary all depths | Passed | Universal lower bound plus symbolic witness families |
| Refinement exact sequence | Passed | Surjective aggregation and correct intersection quotient |
| Actual finite-image congruence proof | Passed internally with external leaves | Actual image, stable lattice, exact trace zero before reduction |
| Trace-zero local model | Passed internally with external leaf | Weak admissibility direct, realization source-dependent |
| Arithmetic sequence countermodel | Passed from stated inputs | No modular or global representation assertion |
| Finite rank optimality beyond tested family | Not addressed | No such universal theorem in the sources |
| All-degree null-span completeness | Not addressed | Explicitly open in the source |
| Global Delta/local-model identification | Not addressed | Local model not identified with actual global representation |
| Actual all-prime tau nonvanishing | Incomplete | No uniform independent nonzero total or discriminator |
| Formal proof-assistant verification | Out of scope | No compiled proof certificate is claimed |
| Historical novelty | Out of scope | No priority conclusion follows from this audit |

## Exact remaining gap and strongest safe statement

The program has exact identities, content invariants, local recurrence
theorems, sharply delimited obstruction theorems, finite rational sign
certificates and finite rank resolutions. It has not proved that the actual
total on every prime shell is nonzero. Modulo 5 eliminates the prime classes
1, 2 and 3, and p=5 is explicit, so one may retain prime indices congruent to
4 modulo 5 as the unresolved family. The audited primitive transform does
not shrink this family, because R(p)=tau(p).

The fixed-modulus survivor theorem has the quantifier order
\(\forall M\ \exists\text{ infinitely many }p\). It cannot be changed to
\(\exists p\ \forall M\). A compatible local trace-zero representation is
not an actual zero coefficient of Delta. Full correction rank at selected
primes is not a theorem at every prime. A shell-null interpolant is not a
universal-null polynomial. A strict rational sign certificate at one prime
proves that case, while completeness of a correction space alone does not
produce such a certificate.

The cheapest substantive next check is to name an exact global property of
Delta or an actual prime-shell relation absent from the weaker arithmetic
countermodel, then derive a uniform consequence that excludes zero. Merely
increasing a coefficient bound, adding a fixed congruence modulus, or repeating
the same recurrence and square theorem cannot supply that missing implication.

## Scope of this review and reproducibility

### Current external-leaf reconciliation

The final sixteen-entry source contract record is
`evidence/literature/source_contracts.json`, SHA-256
`4966eb2c00b7214da5a6a3f6c6195aef97d10da189a52ab0eda2ccf3dceeb04a`.
Its companion `CHECKED_SOURCES.md` was read in full in this review turn.
This record resolves the external-source dependencies noted in the initial
claim cards. Han normalization is S02, harmonic theta is S03, valence is S04,
Deligne representations and purity/conventions are S05–S06, Chebotarev is S08,
local realization is S09, trace moments are S12, five-core cardinality is S13,
normalized differential relations are S15, and the classical Hecke/parity/
modulo-5 leaves are S16. The sign-line scalar descent remains the internal
project argument reconstructed above, rather than a conclusion silently
attributed to S03.

The source audit explicitly records access limits for rereading Lehmer's
original proof and Niebur's original proof. Neither limit is used to fill a
missing proof in this program: prime reduction is separately reconstructed,
and the S4 identity is derived from the authenticated differential relations.
Moriya–Smyth's checked restatement is labeled as such. No all-source-original-
proof rereading or historical-priority certification is asserted.

With those scoped external inputs authenticated, the relevant side-theorem
dependencies are passed. The primary Lehmer target verdict remains incomplete.

Read-only inspection used `sed`, `rg`, and Python's ZIP reader before and after
safe extraction. The source locators and SHA-256 values pin the exact raw notes.
The reviewer did not rerun the historical large coefficient searches in this
proof pass. Fresh computational replay and enumerator coverage belong to the
separate release computation audit. No finite output was used as a substitute
for the universal proofs reconstructed here. Exact external source passages
are checked in the separate literature workflow, not inferred from historical
source-access assertions or search snippets.
