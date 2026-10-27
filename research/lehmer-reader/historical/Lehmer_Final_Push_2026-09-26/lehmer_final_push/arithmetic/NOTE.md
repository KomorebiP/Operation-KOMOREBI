# Final arithmetic push: two exact limits of the local approach

26 September 2026. Parent: `LEHMER-CONTENT-TRANSPORT-02`.

**Lehmer remains unresolved.** This branch establishes two precise barriers,
rather than a contradiction to a hypothetical prime zero. First, arbitrarily
strong *fixed* simultaneous congruence tests fail at infinitely many actual
primes. Second, trace zero is compatible with the local filtered Frobenius
conditions of weight 12. These are standard-theorem consequences and explicit
constructions; no historical novelty is claimed.

## 1. Every fixed congruence depth has actual prime survivors

**Theorem A.** For every integer M>=1 there is a set of rational primes of
positive natural density such that

\[
p\equiv-1\pmod{5M},\qquad \tau(p)\equiv0\pmod M.
\]

For every such prime, simultaneously for all r>=1,

\[
R(p^r)\equiv0\pmod M.
\]

Here R is exactly the primitive residual from the parent checkpoint; R(1)=1.
The density assertion means density relative to all rational primes. No
specific density for the full displayed set is calculated: the proof embeds
a positive-density Chebotarev subset in it. The full set is itself a union of
conjugacy classes in the same finite quotient, so it also has a positive
natural density.

### Proof of simultaneous prime congruences

For each prime ell dividing M, Deligne's representation associated to Delta
is a continuous representation

\[
\rho_\ell:G_{\mathbb Q}\longrightarrow\mathrm{GL}_2(\mathbb Q_\ell)
\]

unramified outside ell, with characteristic polynomial at arithmetic
Frobenius p!=ell equal to

\[
X^2-\tau(p)X+p^{11}.
\]

It has determinant epsilon_ell^11, where epsilon_ell is the cyclotomic
character. The determinant identity follows either from the alternating
pairing in Deligne's construction or by density of Frobenius and the displayed
determinants. For conventions, Deligne's original cohomological W uses
geometric Frobenius; use its dual to obtain the arithmetic-Frobenius
normalization written here. Both conventions agree at complex conjugation.

Choose a stable Z_ell lattice. This requires no image-surjectivity theorem:
the compact image has bounded translates of any initial lattice L0, so
L=sum_g rho_ell(g)L0 is a stable lattice between L0 and ell^-a L0 for some a.

If c is complex conjugation, c^2=1 and epsilon_ell(c)=-1. Hence
det rho_ell(c)=-1. In characteristic zero an involution is diagonalizable,
and its two eigenvalues must be 1,-1. In particular

\[
\operatorname{tr}\rho_\ell(c)=0
\]

as an *exact* Z_ell identity. This remains true when ell=2; it is not inferred
from an invalid characteristic-two diagonalization.

Write M=product ell^e. Form the single finite quotient given by the joint map

\[
\Psi:G_{\mathbb Q}\longrightarrow
\left(\prod_{\ell^e\Vert M}\mathrm{GL}_2(\mathbb Z/\ell^e)\right)
\times(\mathbb Z/5M)^\times,
\qquad
g\longmapsto((\rho_\ell(g)\bmod\ell^e)_\ell,\epsilon_{5M}(g)).
\]

Let G be the **actual image**, not the whole displayed product. Its kernel
defines a finite Galois extension K/Q. Let C be the conjugacy class of Psi(c).
Chebotarev gives a set of unramified rational primes with Frobenius in C and
natural density |C|/|G|>0. At these primes the trace in each factor is zero,
while the cyclotomic factor is -1. Therefore ell^e divides tau(p) for every
ell^e||M and p=-1 mod 5M. No independence between the representations or their
cyclotomic determinants is assumed. For M=1 the representation product is
empty and the cyclotomic quotient modulo 5 suffices.

### Proof for every local primitive exponent

The congruence modulo 5 gives chi_5(p)=chi_5(-1)=1. In (Z/M)[[X]], the already
proved local generating series therefore specializes to

\[
\sum_{r\ge0}R(p^r)X^r
=\frac{1-p^{10}X^2}{1-\tau(p)X+p^{11}X^2}
\equiv\frac{1-X^2}{1-X^2}=1.
\]

The denominator is invertible as a formal power series because its constant
coefficient is 1, including for composite or even M. Equivalently, the Hecke
coefficients satisfy T_0=1,T_1=0,T_r=T_{r-2} modulo M, so T_even=1,
T_odd=0; R_1=T_1=0 and R_r=T_r-T_{r-2}=0 for r>=2. This includes all boundary
cases without claiming R(1)=0. QED.

### Exact implication for the research program

For any fixed finite list of moduli m_1,...,m_s, apply the theorem with their
least common multiple. Infinitely many actual primes defeat every certificate
in that list whose decisive step is showing tau(p), or any R(p^r), nonzero
modulo one of the m_i. The strengthened simultaneous statement includes all
local exponents, rather than merely a finite selection of them.

This **does not** prove that all conceivable congruence arguments fail. It
does not exclude a modulus chosen as a function of p, a uniform valuation
bound with additional input, or a global argument that uses congruences for a
different purpose. Nor does it produce a prime with tau(p)=0. Quantifiers are
essential: for each M the surviving primes may be different. One cannot pass
from `for all M there exists p` to `there exists p for all M`.

The result is compatible with the previous theorem R(p^(2m))!=0: the even
blocks can be nonzero integers divisible by any preassigned M at suitable
primes. Thus their nonvanishing gives no fixed auxiliary-prime unit that can
force the first block to survive.

## 2. A trace-zero local filtered Frobenius object exists

**Theorem B.** At every prime p, there is a weakly admissible two-dimensional
filtered phi-module over Q_p with monodromy N=0, filtration jumps 0 and 11,
and Frobenius characteristic polynomial X^2+p^11.

Let D=Q_p e_1+Q_p e_2, N=0, and set

\[
\varphi(e_1)=e_2,\qquad\varphi(e_2)=-p^{11}e_1.
\]

For any Q_p-line L in D, set Fil^i D=D for i<=0, L for 1<=i<=11, and 0
for i>=12. Then t_H(D)=11=t_N(D), the latter because det phi=p^11.
There is no proper nonzero phi-stable Q_p-subspace: such a line would give an
eigenvalue lambda in Q_p satisfying lambda^2=-p^11, impossible because
2v_p(lambda)=11. Thus all required proper-subobject inequalities are vacuous,
and D is weakly admissible.

Colmez--Fontaine's Theorem A makes D admissible. Consequently it is realized
by a two-dimensional semistable Q_p-representation, and N=0 makes that
representation crystalline. The last assertion also follows directly from
B_cris=B_st^(N=0) and the comparison isomorphism. These conventions refer to
the **cohomological** realization: filtration jumps 0,11 and Frobenius
determinant p^11. Dualizing changes the Galois/Hodge sign convention; no claim
that this local representation is the restriction of Delta is being made.

Its Newton slopes are 11/2,11/2, and its complex Frobenius eigenvalues are
plus/minus i p^(11/2). Those numbers are algebraic integers and have the
required weight 11 absolute value. Hence zero trace obeys integrality,
purity/Deligne's size bound, and weak admissibility simultaneously. Local
slope or filtration inequalities alone do not furnish the missing
contradiction. This construction does not assert the global existence of a
level-one modular form with a specified prime coefficient zero.

A related useful restriction is elementary: for an actual prime p>=5,
Deligne's bound and tau(p)!=0 imply v_p(tau(p))<=5, because
p^6>2p^(11/2). Therefore v_p(tau(p))>=6 would itself imply tau(p)=0. This is
not a contradiction; zero is exactly the remaining permitted case. The
previous even-block proof's nonzero parameters of valuation>=6 are useful
synthetic controls, but cannot occur for actual tau(p) with p>=5.

## 3. Executed exact checks and their limits

`check_arithmetic.py` was run under the bounded mathbox runner; the manifest
in `computation001/manifest.json` passed the provenance validator. It uses
only exact Python integers and no numerical or probabilistic backend.

- tau coefficients through 10000 came from the Jacobi triangular recurrence;
  coefficients through 128 were checked independently against the defining
  q-product.
- Twenty-four selected moduli were searched for the simultaneous prime
  conditions through 10000. Twenty-two had witnesses; 11 and 19 had none in
  this bounded search. This is consistent with, and does not prove, Theorem A.
- The first witness for each successful modulus gave 704 primitive congruence
  checks, through exponent 32.
- For each M=1,...,256, synthetic p=5M-1 and a in {-2M,0,3M} gave 24576
  recurrence congruence checks. Synthetic p need not be prime.
- The trace, determinant and phi^2=-p^11 I identities were checked for all
  1229 primes through 10000. The universal absence of Q_p-eigenlines is proved
  by the valuation argument, not by those finite checks.

Examples: M=13 has p=9749 with tau(p)=12127359091293650772750; M=17 has
p=4079 with tau(p)=33736922998225945680; M=128 has p=1279 with
tau(p)=-82794023701285120. The complete selected-modulus table is in the
JSON result.

## 4. Self-review and remaining gap

Primary verdict: **proved as written**, conditional only in the ordinary
sense of using the explicitly checked established external theorems below.
This is a self-review of this branch, not an independent referee verdict.

| Obligation | Status | Evidence |
|---|---|---|
| Deligne representation, normalization and determinant | Passed | [D], dual convention and determinant comparison above |
| Integral reductions for all prime powers, including 2 | Passed | Compact-image lattice proof; trace computed before reduction |
| Joint finite Galois quotient exists | Passed | Kernel of actual finite-image joint representation |
| Positive natural density | Passed | [C], rational-prime theorem and density definition |
| Primitive congruence at all exponents | Passed | Formal generating-series identity; r=0,1 checked explicitly |
| Weak admissibility of zero-trace model | Passed | Equality of total invariants; no stable rational line |
| Crystalline realization | Passed | [CF], Theorem A and N=0 period-ring identity |
| Actual global prime zero excluded | Incomplete | No implication from the two local-compatible constructions to a global obstruction |

The surviving obligation is unchanged: exclude tau(p)=0 for the actual
global Delta at every prime p. A successful final step must use information
that distinguishes its global prime coefficients from the compatible
trace-zero local data, or a genuinely uniform arithmetic estimate whose
proof does not presuppose prime nonvanishing.

## Sources, authentication and scope

All passages checked 26 September 2026. No source PDFs were retained locally;
the locators and exact statements were checked with web PDF extraction and,
where appropriate, page screenshots. No global novelty search is claimed.

[D] Pierre Deligne, *Formes modulaires et representations l-adiques*,
Seminaire Bourbaki 1968/69, expose 355, published 1971, pp.139--172.
Primary original: https://www.numdam.org/item/SB_1968-1969__11__139_0.pdf .
The original p.171 (PDF page 34) was inspected: equation(5.7), specialized to
k=10, gives the rank two characteristic polynomial H_p. The unramified
construction is in Section 4; the determinant pairing is(3.20).
The author-hosted English transcription dated 28 June 2004 was also checked:
https://publications.ias.edu/sites/default/files/5_FormesModulaires.pdf ,
especially pp.1--2,17 and 19--20. Its typographical errors do not enter the
argument. The paper's Weil-to-Ramanujan implication was conditional at the
time; representation existence used here is unconditional. The size-bound
remark uses the subsequently established Deligne bound already part of the
parent program, and is not needed for either theorem above.

[C] Peter Stevenhagen and Hendrik W. Lenstra Jr., *Chebotarev and his density
theorem*, Mathematical Intelligencer 18 (1996), no.2,26--37.
Author/institution-hosted manuscript:
https://websites.math.leidenuniv.nl/algebra/chebotarev.pdf . PDF page 2 defines
natural density relative to primes and states the rational Chebotarev
theorem with density #C/#G. This is a checked scholarly exposition of the
classical theorem, not a claim of reproving it here. The proof above only
uses the rational-prime case, so no number-field norm normalization remains.

[CF] Pierre Colmez and Jean-Marc Fontaine, *Construction des representations
p-adiques semi-stables*, Inventiones Mathematicae 140 (2000),1--43.
Author-hosted manuscript:
https://webusers.imj-prg.fr/~pierre.colmez/CF.pdf . Theorem A on manuscript
p.2 establishes weakly admissible implies admissible; Section 3.4 p.22
states the equality and all-subobject inequalities used here; Section 4.1
and the corollary on p.24 give the representation equivalence; p.11 gives
B_cris=B_st^(N=0). Application: K=K0=Q_p, sigma=id, dimD=2,N=0.

Overlap classification: Theorem A's Galois argument is a formal consequence
of classical Deligne and Chebotarev, not a new general theorem. Its all-r
primitive formulation is an explicit translation to this project's R.
Theorem B is an elementary example of the established filtered-module
classification. The conclusions are new to this project's recorded route
analysis; that is not a claim of mathematical priority.
