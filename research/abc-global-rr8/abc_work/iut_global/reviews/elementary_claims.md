# Focused independent review of RR5 elementary claims

Reviewer: `/root/rr5_proof_review`, 2026-10-25. Base checkpoint: RR4,
archive SHA-256 `689847eefd2cf75b9804b574d6613c13d10606e6e805a979cd74facb998ea8ae`.
The exact raw inputs and their SHA-256 digests are recorded in
`elementary_claims_inputs.json`. No author proof was edited.

The three internal mathematical claims below are **proved as written** at
their stated scopes. This review does not pass the source-dependent IUT
compatibility assertion, identify an IUT model, or establish ABC. The
literature-calibration paragraphs were not independently source-audited here.

## 1. Global pair-allocation count

**Claim card and verdict: proved as written.** For real X>=2, Y>=1,
delta>0, let B(X,Y) count ordered positive primitive additive triples
a+b=c<=X with rad(abc)<=Y. Then

    B(X,Y) <= 3 C(2,delta) Y^(2/3) X^(2 delta),
    C(k,delta) = product_p (1+k/[p(p^delta-1)]).

Consequently, for every epsilon>0 and eta>0 the count E_epsilon(X) of
triples with c>rad(abc)^(1+epsilon) satisfies

    E_epsilon(X) <= 3 C(2,eta/2)
                       X^[2/(3(1+epsilon))+eta].

Dependency graph:

1. The Euler product in the pinned RR2 counting proof converges and equals
   the nonnegative sum of k^omega(n)/(rad(n)n^delta).
2. On n<=Z, rad(n)<=T, the multiplier TZ^delta/(rad(n)n^delta) is at least
   1. Thus the weighted count is at most C(k,delta)TZ^delta.
3. Pairwise coprimality and the identity
   [rad(a)rad(b)][rad(a)rad(c)][rad(b)rad(c)]=rad(abc)^2 select a pair
   with radical product at most Y^(2/3).
4. That pair has product at most X^2. Each prime power of its product is
   allocated wholly to one of the two factors, giving exactly 2^omega(n)
   ordered coprime factorizations. Each pair and its type determine the
   remaining entry of a+b=c.
5. Taking the union of the three pair types and applying item 2 proves the
   bound. Overlap or invalid recovered entries only cause overcounting.

Obligations passed: convergence for every delta>0, the weighted inequality,
pairwise coprimality, factor allocation, recovery from each pair type, and
the substitution Y=X^[1/(1+epsilon)], delta=eta/2. The n=1 allocation is
also valid: 2^omega(1)=1. The minimal triple (1,1,2), Y=1, and nonintegral
X or Y create no exception to the upper-bound argument.

Decisive check: the full proof is a union bound over three injectively
encoded pair types. It does not require a distribution assumption about
primes or independence of a and b. No finite computation is load-bearing.

Remaining global gap: the exponent is positive, so the bound permits an
infinite sparse exceptional set. No exclusion of all sufficiently large
exceptional heights follows. The statement's claimed correspondence with
an existing literature baseline is a separate source question, not a
novelty conclusion of this review.

## 2. Numerical realization and error stability

**Claim card and verdict: proved as written.** For real q0 and an arbitrary
set V of real numbers, with extended supremum, these are equivalent:
q0<=sup(V); for every eta>0 some v in V satisfies v>q0-eta; every finite
real upper bound b of V also satisfies q0<=b. For nonnegative finite E,
the same criterion at q0-E transfers a bound V<=b to q0<=b+E.

For nonempty V with finite supremum s, the smallest nonnegative admissible
loss is max(0,q0-s). This is an infimum that is actually admissible under
the approximate, rather than exact-attainment, formulation.

Dependency graph: least-upper-bound property -> approximate realization
criterion -> substitution q0-E -> scalar loss formula. The amplification
claim follows separately by combining Theta>=kappa Q-L and Theta<=Q+E,
with kappa>1, to obtain (kappa-1)Q<=E+L.

Obligations passed: V empty makes all realization conditions fail, while
V unbounded above makes the upper-bound condition vacuous and supplies no
finite bound to transfer. A finite unattained supremum still suffices.
The example V={q0-1/m:m>=1} verifies why exact attainment is unnecessary.
Branch compatibility is essential: a bound for V_2={-100} cannot be used
with realization in V_1 union V_2 when V_1={0}, q0=0.

The separate ABC stability claim also passes as an implication. With
H=log(c), r=log(rad(abc)), a fixed K>0, and fixed errors F satisfying
KH<=Kr+F and F<=delta H+C_delta uniformly in the triple for every
delta>0, choosing delta=K epsilon/(1+epsilon) gives

    H <= (1+epsilon)r+C_delta/(K-delta).

Applying this first with epsilon/2 bounds the radical of every violation
at exponent epsilon, then bounds c, so gives finiteness. Positivity of
K-delta and uniformity of C_delta are both explicit. No source-dependent
identification of Q with H or of kappa with an IUT parameter is used.

Remaining IUT gap: the actual admissible value set, its common
normalization, a realization/cofinality property, and the required
arithmetic error estimates have not been constructed or proved here.
These conditional lemmas cannot pass evidence claiming the compatibility
or full ABC itself. The next mathematical check is the derivation of
that actual comparison from the stated IUT inputs.

## 3. Unit and integral-lattice repair candidate

**Claim card and verdict: proved as written.** In a local field K with
valuation ring O, residue cardinality q and uniformizer pi, take m,k>=1
and integers s_j>=1. For the full lattices

    L_theta = direct_sum_j pi^(s_j m)O,
    L_q = direct_sum_j pi^m O,

every M in GL_k(O) and every O-lattice H containing M L_theta and L_q
satisfy

    [log mu(H)-log mu(M L_theta)]/k
        >= (average_j s_j-1)m log q.

Dependency graph: normalized Haar measure of each fractional ideal ->
product measure of L_theta -> det(M) a unit and measure preservation ->
containment H superset L_q -> the log-volume inequality.

All obligations passed. The lower bound is attained at M=identity,
H=L_q, so it is optimal over the precise stated class. The lattice
convention supplies finite positive measure, making the logarithms
well-defined. For k=1 and s_1=1 the obstruction vanishes as stated. For
square weights s_j=j^2 and k>=2, their average is
(k+1)(2k+1)/6>1, so the loss is linear in m log q. A root of unity has
valuation zero and therefore cannot alter an ideal by multiplication.
The scalar example 81 Z_3 subset 3 Z_3 has index 27 and log-volume
increase 3 log 3, with the stated orientation of containment and measure.

Remaining dictionary gap: the note does not claim that actual IUT
indeterminacies or hulls are this lattice construction. The proof refutes
sublinear-cost enlargement only inside this precise candidate. It is not
a counterexample to IUT or to its intended global comparison.

## Provenance and checks

This is a fresh delegated audit of the raw statements and derivations.
I reconstructed the critical implications from their definitions, read the
RR2 Euler-product leaf, checked boundary cases, and pinned the inspected
files by SHA-256. No numerical script or proof assistant was used or
needed for these elementary proofs. Agreement between agents is not a
formal proof certificate.

The source-dependent interpretation of IUT remains outside this focused
audit. No claimed literature record or full theorem of an external paper
has been certified merely by reading its title or a source excerpt.
