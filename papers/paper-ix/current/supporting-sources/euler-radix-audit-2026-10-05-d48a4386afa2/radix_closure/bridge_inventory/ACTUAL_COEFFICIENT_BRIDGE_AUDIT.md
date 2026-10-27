# Actual coefficient gates for the radix, Cartier, and lattice bridges

Base checkpoint: Euler-shifted-obstruction-20261005. Base archive SHA256:
7125e5ed1ce7b0a3fb25473284ac92fa1a4c6db42862980f1b07cbfb50233dea.
The source archive and preceding checkpoints were not changed. No Lean build
was run. This audit inspected the theorem statements and proof sources in the
newly materialized primary project packages.
Exact source paths and SHA256 digests are recorded in SOURCE_PINS.json.

**Target and verdict.** For every ordinary T>=0 such that
r=(17659+2^18 T)2^640-161 has true terminal161, prove the stationary scalar
Phi_r(2^(2r-25)) is nonzero. **Incomplete, with the smallest missing
implication:** the prescribed Bernoulli coefficient vector must be excluded
from the value/derivative contact locus. The inspected bridge theorems do not
provide this exclusion. The following audit proves three more precise gate
results using the actual coefficients, and computes the exact lattice defect
of the available spatial compiler.

## 1. Source-to-target dictionary

Source abbreviations below refer to directories under ../sources/extracted/.

| Source | Actual statement inspected | Dictionary and applicability to Euler |
|---|---|---|
| Padic Block05, THEOREM_NOTE.md and lean/KomorebiPadic/RadixDescent.lean | Exact Kummer carry descent and one minimum-cost representative per radix block | Its source r is a modulus exponent P, its Q is a correction-layer barrier, and its q is a diagonal correction index. These are not the Euler cutoff r or its tail-packet q. It computes which rational-mask correction branches survive; it imposes no condition on Bernoulli unit ratios. |
| Padic Block12, RepresentativeBudgetClosedForm.lean and RepresentativeBudgetParameterEnvelope.lean | Exact finite sum of representative counts and a parameter-only upper bound | K=floor((P-1)/(h+1)), d=floor(K/(p(p-1))). For p=2,h=0 the bound is 2P+2+d(d+1). It bounds compiler work at a chosen precision, not the precision at which Phi must become nonzero. |
| Cartier Bridge01, THEOREM_NOTE.md, Theorems1-3 | Exact section formula for BF=A F(z^p), with A,B integral polynomials and p∤B(0), plus finite denominator and degree bounds | Actual Bernoulli-tail generating functions fail the rational-mask hypothesis, as proved in section2. The normalized spatial rational mask does satisfy it, as in section4. |
| Cartier Bridge02, THEOREM_NOTE.md, sections9-10 | The literal one-layer normal form lifts modulo p^(s+1) iff p^(-(s-1))E_B vanishes modulo p | This is an obstruction to preserving one chosen representation. The series F always lifts uniquely. No source-to-target map identifies this obstruction with Phi or the repeated-root equations. For the actual normalized spatial mask the obstruction is already nonzero modulo2, while its exact finite spatial compiler still exists. |
| Universal Lane Transport v1.16 full source, manuscript/Komorebi_Stratified_Universality_Foundations_v1.15.0_Block15.tex, Block06 | Smith-Tor and inverse-limit theorems for an integer-valued sequence already having finite rational section rank | The spatial R sequence qualifies and its Smith invariants are computed in section4. Actual beta and gamma have infinite rational section rank by section3. The finite meromorphic prefix also fails the stable integral-lattice gate by section5. |
| Same manuscript, propositions block02-obstruction-packets and typed-obstruction-comparison | Relative cokernel obstructions transport only through compatible underlying correction data | No compatible correction map is supplied by the Euler value/derivative equation. Naming both quantities an obstruction does not supply that map. |

The exact finite-correction identity in Bridge01/02 is sound as written: expand
B^p=B(z^p)+pE_B by the negative-binomial series, retain k<P, and apply Cartier
sectioning. Block12 changes the arithmetic of a work bound, not its semantic
scope. These audited implications pass. Their proposed direct implication to
Euler stationary nonvanishing is not addressed by those theorems.

## 2. Actual Bernoulli tails have no rational dyadic mask

Use the prescribed rational coefficients

    f(z)=(z/sinh z)^2=sum_(m>=0) beta_m z^(2m),
    H(t)=sum_(m>=0) beta_m t^m,
    gamma_(r,q)=2^(-mu_r) 8^q beta_(r+q)/beta_r.

Here beta_0=1, and every beta_m is nonzero; the inherited exact valuation
v2(beta_m)=s2(m)-1 for m>=1 already proves nonvanishing.

H(t)=t/sinh(sqrt(t))^2 is a single-valued meromorphic function of t: the
power series of sinh(sqrt(t))^2 is single-valued. Its poles are precisely
t=-pi^2 n^2 for n>=1, all double. It has no pole on the nonnegative real
axis. Thus H(t)/H(t^2) has a pole at every -pi^2 n^2, because H(t^2) is
analytic and nonzero at those negative-real points. It cannot be rational.

For any fixed cutoff r>=1 define

    J_r(t)=sum_(q>=0) 8^q beta_(r+q) t^q
          =[H(8t)-sum_(m<r) beta_m(8t)^m]/(8t)^r.

The apparent singularity at zero is removable. J_r has a double pole at
every t=-pi^2 n^2/8. In J_r(t)/J_r(t^2), the denominator is analytic at
all these points because its argument is positive. A possible zero of the
denominator only increases the pole order. Therefore J_r(t)/J_r(t^2) is
not rational either.

Multiplying J_r by the constant 2^(-mu_r)/beta_r does not change its
canonical mask. Hence the actual gamma generating function cannot satisfy
BF=A F(t^2) with nonzero rational polynomials A,B. In particular it does
not lie in the integral rational-mask class of Bridge01/02. This is a
uniform statement about all actual cutoffs, not a failed low-degree fit.

This excludes a direct application to the ordinary packet-index series.
It does not exclude a different representation, an index-dependent
compiler, or a nonlinear Bernoulli identity.

## 3. Actual beta and gamma have infinite rational section rank

**Elementary denominator lemma.** Suppose a rational sequence a(n) has a
finite-dimensional dyadic section space over Q. Choose a rational basis
of actual sections. Both digit transitions have rational matrices and
evaluation at zero is a rational row. Clearing their finitely many
denominators by an integer D, and the initial/output denominators by C,
shows that a(n) has denominator dividing C D^(ell+1), where ell is the
binary length of n. Consequently, whenever a(n) is nonzero,

    |a(n)| >= 1/(C D^(ell+1)) >= c (n+1)^(-A)

for suitable positive constants c,A. A nonzero rational finite-rank
sequence cannot decay exponentially at every sufficiently large index.

For any fixed real R with sqrt(8)<R<pi, the function f(z) is analytic on
the closed disc |z|<=R. Cauchy's coefficient estimate gives

    |beta_m| <= M_R R^(-2m).

Every beta_m is nonzero. Thus beta has infinite rational dyadic section
rank by the lemma. For each fixed r, the same estimate gives

    |gamma_(r,q)| <= C_r (8/R^2)^q,

with 8/R^2<1, and every gamma_(r,q) is nonzero. Therefore each actual
gamma sequence also has infinite rational dyadic section rank.

The same conclusion holds over Q_2: every finite matrix of rational
section values has the same rank over Q and Q_2. Equivalently, if finitely
many rational sections span over Q_2, an invertible finite rational
evaluation matrix expresses all section coordinates rationally.

The denominator lemma uses only that digit length is O(log n), so both
infinite-rank conclusions hold for every fixed radix k>=2, over Q or Q_2.

This closes the proposed direct finite-rank Smith-lattice bridge for the
actual beta and gamma packet-index sequences. It says nothing against
fixed-precision automata whose rank grows with precision, nor against
the finite *spatial* compiler of the full regularized measure.

## 4. The spatial compiler has an exact nontrivial Smith defect

Use the already reconstructed rational spatial states

    R=2y(y^2+1)/(y^4-y^2+1), S=2(y+1)/(y^2-y+1),
    U=1/(1+y+y^2), V=y/(1+y+y^2).

The actual section orbit consists of initial R,S, zero, and the six states
with (U,V) coordinates

    (2,4),(2,-2),(-4,-2),(4,2),(-2,2),(-2,-4).

Therefore the raw section lattice has basis

    R, S, 2U+4V, 2U-2V.

These four functions are rationally independent: R has primitive-twelfth
root poles, S has primitive-sixth root poles, and U,V are independent
on the primitive-third denominator. All four coefficient sequences are
purely periodic with period12, since their reduced denominators divide
1-y^12 and their numerators have smaller degree. Thus evaluation on
coordinates0,...,11 identifies the full sequence lattice faithfully.

In the displayed raw basis its integral coefficient matrix has rows

    (0, 2, 2, 2), (2, 4, 2,-4), (0, 2,-4, 2),
    (4,-2, 2, 2), (0,-4, 2,-4), (2,-2,-4, 2),
    (0, 2, 2, 2),(-2, 4, 2,-4), (0, 2,-4, 2),
    (-4,-2,2,2), (0,-4,2,-4), (-2,-2,-4,2).

Exact gcds of all minors of sizes1,2,3,4 are respectively2,4,8,96.
The Smith invariants are consequently

    2,2,2,12,

and the saturation defect is

    C = (Z/2)^3 direct-sum Z/12.

At p=2 the valuations are (1,1,1,2), so Universal Lane Block06 gives
the exact semantic image size

    2^[3(P-min(P,1))+(P-min(P,2))]

modulo2^P. This is an actual arithmetic constraint on the full spatial
measure. It tracks information lost by coefficient reduction. It does
not state that a nonlinear moment/value functional is nonzero, and
there is no contradiction with the previously proved valuations of b
and its derivatives.

For comparison, normalize the rational mask by

    F(y)=R(y)/(2y)=(1+y^2)/(1-y^2+y^4).

Its dyadic mask has

    A=(1+y^2)(1-y^4+y^8),
    B=(1-y^2+y^4)(1+y^4),
    BF=A F(y^2).

The coefficient of y^2 in E_B=(B^2-B(y^2))/2 is -1, hence h=0.
Bridge02's literal one-layer formula consequently fails already modulo4.
Nevertheless the exact spatial compiler above exists over Q_2. This
specific actual mask demonstrates why failure of one compressed normal
form is not failure of the underlying series, let alone nonvanishing of
its stationary residual scalar.

## 5. The actual meromorphic prefix cannot have a stable integral lattice

The companion spatial audit gives the exact meromorphic prefix transform

    F_r(t)=sum_(0<=n<r) beta_n t^(2n-2)
       [4^(n-1)(cosh(3t)-cosh(t))
        +36^n/12 (cosh(9t)-cosh(3t))],

where y=exp(t). Spatial sectioning obeys

    C_b[y^j t^k] = 2^(-k)y^((j-b)/2)t^k  if j=b mod2,
                  0                         otherwise.

After four bits the residue1 modulo16 isolates j=1 from the six exponents
{1,-1,3,-3,9,-9}. Hence

    C_(16,1) F_r
      =-sum_(0<=n<r) [beta_n 4^(n-1)/2]16^(-(2n-2)) t^(2n-2).

Every displayed coefficient is nonzero. Repeated zero sections multiply
the t^(2n-2) term by the distinct eigenvalues

    lambda_n=2^(2-2n).

The Vandermonde determinant is nonzero, so the rational orbit span
contains each of the r modes t^(-2),1,t^2,...,t^(2r-4). In particular,
for every actual cutoff r>=3, zero section has the eigenvalue1/4 on an
invariant subspace.

If this finite-dimensional Q_2 space admitted any spanning finite
Z_2-lattice preserved by zero section, its matrix in a lattice basis
would be integral. Every eigenvalue would then be integral over Z_2,
contradicting v2(1/4)=-2. Equivalently the orbit of a nonzero t^2 mode
would be unbounded in every such lattice. This argument excludes
*every* choice of finite spanning integral lattice, not just the
displayed coordinates.

Thus adjoining the actual finite cutoff states to the bounded measure
does not make Universal Lane's stable integral-lattice hypotheses hold.
The obstruction is already present for r=3 and remains for the focused
huge-cutoff family. Renormalizing each section by a depth-dependent
power of2 changes the transfer and requires its own exact precision-loss
ledger; it is not the unchanged Smith bridge.

## 6. Verification and exact remaining implication

check_bridge_gates.py uses exact integers and Fraction only. It computes
the period12 Smith matrix and all relevant minors; independently checks
beta_1,...,beta_36 by formal-series inversion and Bernoulli recurrence;
checks four actual gamma sections at cutoffs1,...,4; and checks the
prefix eigenmode Vandermonde for cutoffs1,...,8. The universal rank and
nonintegrality conclusions are the proofs in sections3 and5, not an
extrapolation of these samples.

The bounded run is in certified_run/manifest.json with results.json and
logs. Its manifest was validated against the current input hashes.

Dependency graph:

    prescribed beta -> exact gamma generating series
       -> infinite poles of canonical mask -> no rational-mask input
       -> rationality + exponential decay -> infinite section rank

    prescribed finite prefix -> residue1/16 section
       -> all nonzero distinct eigenmodes -> no stable integral lattice

    full spatial R -> finite period12 section lattice
       -> exact Smith defect -> full-measure reduction information

No arrow in this graph excludes the actual contact equations
C_r(s)=b(s), C_r'(s)=b'(s). A new successful bridge must retain the
nonintegral prefix transfer or use another Bernoulli-specific relation
and then prove that this actual contact is impossible. The audited
budget, obstruction-lifting, and Smith theorems cannot supply that last
arrow solely by changing coordinates.
