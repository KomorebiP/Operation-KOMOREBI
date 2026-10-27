# Independent mathematical audit: SF-DISCOVERY-110

Date: 2026-10-09. Auditor: `/root/v11_math_audit`, with a separate bounded
arithmetic/sieve review by `/root/v11_math_audit/resolution_leaves` and an
independent rational recomputation delegated by that reviewer. Base checkpoint:
SF-DISCOVERY-100. This report applies to the exact SHA256 revisions below.

**Normalized claim.** For every real \(0<q,r,a,b<1\), the normalized coupled
system

\[
U'=1+U(qz)V(rz),\qquad V'=1+U(az)V(bz),\qquad U(0)=V(0)=0
\]

has the entire-function, growth, reduction and inverse properties specified
below. The resolution atlas proves its stated sufficient disk, depth and
polynomial-degree certificates under its explicit hypotheses.

**Primary verdict: proved as written.** This verdict concerns the current
proofs, after correction of the atlas's initial-segment hypothesis. No
remaining mathematical gap was found in the audited claims. It is not a
claim of machine-checked formalization, optimal bounds, historical priority,
or complete coverage of every program in the release.

## 1. Exact claim cards and scope

| Claim | Quantified domain and conclusion | Authoritative locator |
|---|---|---|
| Coupled existence and growth | Every quadruple in \((0,1)^4\) gives a unique normalized entire pair with strictly positive ordinary coefficients at every odd degree and zero even coefficients. Both orders and lower orders equal the unique positive \(\rho\) satisfying \(\operatorname{spr}P(\rho)=1\), where \(P(s)=\bigl(\begin{smallmatrix}q^s&r^s\\a^s&b^s\end{smallmatrix}\bigr)\). | `coupled_growth_proof.md`, Theorems 1–2 |
| Type bounds and proportions | Both lower and upper \(\rho\)-types are positive and finite. Their two component vectors are positive multiples of the displayed right eigenvector. Existence of either component's ordinary type limit implies existence of the other's. | `coupled_growth_proof.md`, Theorems 2–3; independently reconstructed barrier proof |
| Constant linear operator projections | On all analytic zero-constant inputs, a nonzero complex row is autonomous exactly when \(q=a,r=b\) and it is a multiple of \((1,-1)\). Therefore no invertible constant state change completely decouples the operator. This algebraic statement holds for positive nonzero scales, even without contraction. | `coupled_structure.md`, Theorem S1 |
| Solution identities and generic inverse | \(U=V\) iff the unordered scale pairs agree. Complex amplitude/argument rescaling of the components occurs iff \(D=0\), equivalently \(q=b\) or \(qb=ar\). If \(D\ne0\), ordinary coefficients through degree seven determine the four ordered positive scales. | `coupled_structure.md`, S7; `coupled_identifiability.md`, Sections 1–2 |
| Resolution certificates | RA-1–RA-3 give a compact difference bound and sufficient separating radius; RA-4–RA-8 give exact prime-difference envelopes and a conditioned depth bracket; RA-9–RA-10 prove low-degree positivity and exhibit a negative degree-seven norm at \(\delta=10^{-12}\). | `resolution_atlas.md`, Sections 1–3 |

For the inverse statements, write
\[
U(z)=z+\sum_{n\ge1}u_nz^{2n+1},\qquad
V(z)=z+\sum_{n\ge1}v_nz^{2n+1},
\]
and define \(p=qr\), \(k=ab\), \(D=k^2u_2-p^2v_2\). Lower and upper type
mean respectively the liminf and limsup of \(\log M_i(R)/R^\rho\), with
\(M_i(R)=\max_{|z|=R}|F_i(z)|\), \(F_1=U,F_2=V\).

Ordinary Taylor coefficients and factorial-normalized derivatives were kept
distinct throughout the audit. The inverse is for labeled components. The
operator theorem is an identity on arbitrary inputs, while the reduction
theorems concern the distinguished normalized solution. Those are different
contracts, and the proofs preserve that distinction.

No `.mathbox` ledger or applicable `AGENTS.md` was found in the audited project.
The proof sources were read-only for this auditor. The sole output owned by
this audit is this report; the atlas author made the identified correction.

## 2. Dependency graph and leaf status

1. **Coupled analytic branch:** coefficient matching → unique positive odd
   formal pair → elementary local majorant → contraction continuation →
   positive-real-axis maximum modulus → exact scalar determinant root and
   positive eigenvectors → fixed-width lower comparison and shifted-log upper
   comparison → finite positive types → left-eigenvector type alignment.
   All arrows are internal analytic or algebraic proofs.
2. **Independent growth reconstruction:** the same precisely defined pair →
   delayed differential comparison → exact polynomial-exponential lower and
   upper barriers → positive finite type bounds. The formulas, seed intervals
   and derivative inequalities were checked directly, rather than accepting
   the independent author's verdict.
3. **Structure branch:** constancy on projection fibers → polynomial
   interpolation test → row proportional to \((1,-1)\) → monomial tests →
   equality of the two ordered operator rows. No growth theorem is used.
4. **Inverse branch:** cubic and fifth coefficients → exact factorization of
   \(D\) → explicit scalar rescaling construction; separately, two quadratic
   candidate sets → seventh-coefficient separation when \(D\ne0\) → ordered
   recovery. Scalar existence follows from the directly checked contraction
   construction in `routes/asymmetric_dilation.md`.
5. **Weak-tap branch:** the inherited positive weight-polynomial majorant and
   fixed-width type proof in `new_results/dilation_type.md` → explicit compact
   Lipschitz bound and positive lower type → RA-1–RA-3. These inherited proof
   leaves were read and reconstructed, including the constants.
6. **Arithmetic branch:** an absolutely convergent squarefree Euler product →
   removed-prime mass → frequency maximum → derivative/disk estimates and
   monotone threshold bracket. The corresponding part of
   `new_results/arithmetic_inverse.md` was checked directly.
7. **Sieve branch:** real polynomial interpolation and weighted
   Cauchy–Schwarz → RA-9; complete initial positive-node segment → root-factor
   envelope and integral tail → RA-10. The earlier generic detector in
   `new_results/multi_prime_sieve.md` is used only for its stated degree-21
   comparison. No numerical eigenvalue is a proof leaf.
8. **External numerical identity:** the conversion
   \(D(4)=\zeta(4)/\zeta(8)=105/\pi^4\) was checked against NIST DLMF as
   recorded in Section 6. The structural envelope and rational certificates
   can also be read without this conversion.

There is no circular dependency in these branches. Finite computations check
formula transcription and particular rational certificates; no universal
analytic conclusion depends on the reported number of passing assertions.

## 3. Obligation matrix

| Obligation | Status | Decisive check |
|---|---|---|
| Normalization, uniqueness and parity | Passed | Recursion in all ordinary degrees determines the next coefficient; the odd construction therefore excludes extra even terms. |
| Local convergence and entire continuation | Passed | \(u_n,v_n\le2^{-n}\); the integral extension on \(R/Q\) uses only old values at contracted arguments. |
| Matrix orientation | Passed | Each row describes one derivative and each column one child component; the growth vector is a right eigenvector. |
| Root existence and uniqueness | Passed | \((1-q^s)(1-b^s)\) strictly increases and \((ar)^s\) strictly decreases from the opposite endpoint values. |
| Spectral radius, without an unverified Perron theorem | Passed | The explicit positive-matrix quadratic formula identifies the positive eigenvalue as the spectral radius; at the root the other eigenvalue is \(q^\rho+b^\rho-1\in(-1,1)\). |
| Fixed-width lower bound, including \(0<\rho<1\) | Passed | Children are at least 2, the shifted powers use only monotonicity, and every child decreases radius by at least \(d>0\). |
| Explicit finite upper type | Passed | Checked the seed bound \(W_N\), the shift constant \(D\), and induction with strictly positive logarithmic delays. |
| Independent barrier constants | Passed | Exact derivative/product ratio, lower seed ordering, upper seed ordering, monotonicity of the upper product, and the additive forcing were all checked. |
| Type-vector proportions | Passed | The liminf/limsup inequalities have the stated directions; the positive left eigenvector forces both differences to vanish. |
| Coincident and exchanged scales | Passed | Equal/reversed pairs are handled; \(U=V\) along one solution does not produce an autonomous operator projection. |
| Zero and unit boundaries | Passed as exclusions | The zero-scale order-zero example and the all-unit tangent example are valid; neither is in \((0,1)^4\). |
| Operator theorem for arbitrary scalar functionals | Passed | Fiber constancy, rather than an assumed quadratic form of the scalar functional, yields the obstruction. |
| Complex rescaling constants and effective contractions | Passed | \(AB=1,B^2=k/p\); both reduction surfaces give effective scales strictly between 0 and 1. |
| Ordered inverse and repeated candidates | Passed | Positive roots have distinct squares; repeated roots already select uniquely. The two selection differences have the claimed factors. |
| RA-1–RA-3 and noise interpretation | Passed | The disk bound is uniform; midpoint ambiguity is under the stated absolute error allowance; the radius is sufficient, not necessary. |
| RA-4–RA-8 and tolerance hypothesis | Passed | Every removed frequency is at most \(\lambda_p\); the stated strict tolerance condition ensures a positive bracket and a unique crossing. |
| All real polynomials of degree at most four | Passed | Interpolation covers the whole space, and \(\delta K_4/12<1\) is an exact rational inequality. |
| RA-10 infinite positive tail | Passed after correction | Current \(S\) is exactly the complete initial segment; every remaining positive node lies to the right of every killed node. |
| Hankel indexing and unresolved degrees | Passed | Degree four means order five; a degree-seven negative norm disproves positive semidefiniteness at order eight. Degrees five and six are not decided. |
| Ordinary type-limit existence | Not addressed | Equality of the lower and upper scalar types is not proved. |
| Optimal radii, optimal detector degree, universal numerical complexity | Out of scope | None is claimed by these sufficient bounds. |
| Historical priority and identification with all named function classes | Out of scope | No novelty theorem or universal nonreduction statement is inferred. |

## 4. Critical reconstructions and constants

### Coupled growth

In the lower comparison, \(B=1+2/m\) ensures

\[
p(R-1)\ge2,\qquad
p(R-1)+C-p(R+C)=(1-p)C-p\ge0
\]

for every scale \(p\), since \(C=Q/(1-Q)\ge p/(1-p)\). The child decrease

\[
Q(R-1)\le R-[(1-Q)B+Q]\qquad(R\ge B)
\]

validates the interval induction. No convexity of \(x^\rho\) is used.

In the upper comparison, if the two delays in a row are \(a_1,a_2\), the
required shifted-log inequality is exactly

\[
2t+\log2+D\le2t-a_1-a_2+2D,
\]

which follows from \(D\ge a_1+a_2+\log2\). Summing the seed recurrence gives

\[
W_N=(2^{N+1}-1)\log2+(2^{N+1}-N-2)\log(1/Q)
\]

with the correct \(N=0\) value \(\log2\). The stated choice of \(N\) covers the
entire logarithmic seed interval because \(e<3\).

For the independent barrier \(W_i(x)=D x^{\rho-1}e^{kv_ix^\rho}\), direct
differentiation gives

\[
\frac{W_i'(x)}{W_1(p_{i1}x)W_2(p_{i2}x)}
=\frac{k\rho v_i+(\rho-1)x^{-\rho}}
 {D(p_{i1}p_{i2})^{\rho-1}}.
\]

The proof's lower and upper choices make the required inequalities hold on
their whole rays, including the case \(\rho<1\). The upper product is at
least one, so its factor-of-two derivative bound controls the forcing \(1\).

The type alignment does not require synchronized maximizing subsequences:
the general finite-sum liminf/limsup inequalities yield

\[
\underline t\ge P(\rho)\underline t,\qquad
\overline t\le P(\rho)\overline t.
\]

Multiplication by a positive left eigenvector shows every nonnegative
difference coordinate is zero. This justifies the claimed proportions but
does not imply a type limit or convergence of the ratio of the logarithms.

Direct rational recursion independently reproduces the worked pair's
coefficients through degree seven:

\[
(u_1,u_2,u_3)=
\left(\frac2{75},\frac{88}{234375},\frac{18814}{8544921875}\right),
\]
\[
(v_1,v_2,v_3)=
\left(\frac7{50},\frac{8211}{1250000},
\frac{85664601}{625000000000}\right).
\]

### Structure and inverse

For the operator, interpolation produces an input template equal to one at
all distinct nonzero scale nodes. Constancy on each projection fiber forces

\[
(c_1+c_2)(c_2y-c_1x)=0\quad\text{for every }x,y.
\]

A nonzero row must therefore satisfy \(c_2=-c_1\). Subtracting the zero-
projection instance then forces \(w(qz)g(rz)=w(az)g(bz)\). Three monomial
tests and positivity give \(q=a,r=b\). This reasoning covers coincident nodes.

With \(p=qr,k=ab\), expanding from the coefficients yields

\[
15D=pk\{pk(q^2-b^2)+k^2r^2-p^2a^2\}
=pk ar(q^2-b^2)(qb-ar).
\]

For the first quadratic's two roots \(xx'=kp\), reciprocal-square
substitution gives exactly the displayed difference

\[
u_3(x)-u_3(x')=\frac{pD}{7k^2}(x^2-x'^2).
\]

For the second quadratic \(yy'=k^3/p\), the difference is

\[
v_3(y)-v_3(y')=\frac{D}{7k}(y^2-y'^2).
\]

These are nonzero for distinct positive candidates if \(D\ne0\). Complex
rescaling adds no extra exception, since the cubic coefficient already forces

\[
B^2=k/p>0.
\]

On the reduction surfaces the stated scalar construction was substituted into
both equations, with the factor interchange performed on the \(q=b\) branch.

### Resolution atlas

The rational coefficient/tail certificate gives

\[
L(1)\le0.2418902661853593191\ldots<0.241890267.
\]

Here the first decimal is a display of the exact rational upper certificate,
not an asserted exact value of \(L(1)\). The omitted normalized curve tail
with \(N=100\) is bounded by \(12\cdot101(3/4)^{203}<5.26\times10^{-23}\).
For the slow type estimate, the constants sum to

\[
V_2+1+\Delta+B_+=1+(15+2+5)\log2=1+22\log2.
\]

The two nontrivial constraints in RA-3 imply

\[
c_\varepsilon R^\rho\ge
C_0\sqrt R+\log2,
\]

which suffices for the factor-of-two separation. This cannot be read as a
lower bound on the first detectable radius.

For the prime envelope, the \(n=p\) atom gives the lower bound while the
whole removed mass gives the upper bound. The latter mass exceeds \(p^{-4}\)
strictly, so \(T_-\le T_+\). The three rational disk envelopes are
approximately \(1.282563851452239\times10^{-8}\),
\(1.286406830709968\times10^{-12}\), and
\(1.329606656972569\times10^{-16}\); all three atlas table entries round
upward. The displayed threshold endpoints and base-ten cancellation logs
also agree with separate 60-digit evaluations of the exact formulas.

For the sieve, an independent standalone `Fraction` reconstruction gives

\[
K_4=
\frac{50514908345004728790362803172127509183274576217}
{335885047078429094572066571550720000},
\]

and hence \(12/K_4=7.979071321703636\ldots\times10^{-11}>10^{-12}\).
The degree-seven detector has

\[
C_S=\frac{756482048}{20777538825},\qquad
r_S=\frac{3856}{102487},
\]

and exact quadratic-form upper bound

\[
-\frac{15826137987144873004599381600181003979030412432101}
{268942940499754428454007595929096317709056198913616000000000000}
=-5.8845708899205420252\ldots\times10^{-14}<0.
\]

Its positive-tail upper bound is
\(3.6542911007945797472\ldots\times10^{-15}\). Both displayed decimal
upper bounds round in the safe direction. For this fixed \(S\), \(m=2\)
fails the sufficient criterion and \(m=3\) passes. The inherited generic
detector's degree-20 bound is positive and its degree-21 bound negative,
confirming that limited comparison without claiming optimality.

## 5. Correction history and implementation scope

The initial RA-10 wording allowed \(S\) to **contain** all labels through
\(K\), which could include additional later labels. That does not ensure
\(|x-x_n|\le1-x_n\) at every remaining positive node. The author changed the
condition to \(S\) being **exactly** the odd squarefree labels at most \(K\),
with \(K\) an odd squarefree integer. The auditor and the separately assigned
leaf reviewer identified the same issue before sharing that finding. Their
agreement is not the proof: the corrected ordering of nodes is the decisive
missing implication. All worked examples and the checker already satisfied
the stronger condition.

The added `coupled_inverse.py` was read line by line. Its two candidate sums
and products match the proof, both contraction tests are imposed, and the
seventh coefficients are compared exactly. `recover_squared_scales` returns
exact rational squared scales; `recover_rational_scales` additionally requires
rational square roots. These APIs do not implement noisy-data inference or a
uniform stable inverse. They reject \(D=0\), nonpositive supplied coefficients,
and data without a unique admissible candidate pair.

The recorded inverse check covers 256 rational parameter tuples, with 166
generic and 90 reduced points, jets through degree seven, three scalar
reduction cases through degree 29, and 2,728 exact assertions. This bounded
run verifies its own enumerated scope; the universal theorem comes from the
proof. A code-path review confirms the enumeration and count categories.

Three targeted independent-formula checks were additionally executed without
calling the coefficient-generation checker:

- Rational squared scales \((1/2,1/8,1/5,5/49)\), with \(p=1/4,k=1/7\),
  recover exactly through `recover_squared_scales`; the rational-scale API
  correctly rejects their irrational square roots.
- \((q,r,a,b)=(1/2,1/2,2/5,5/8)\) recovers exactly with a repeated first
  quadratic root and \(D\ne0\).
- \((q,r,a,b)=(2/5,5/8,1/2,1/2)\) recovers exactly with a repeated second
  quadratic root and \(D\ne0\).

The atlas checker reports 985 rational and 16 floating checks. Its sample
envelope checks are not promoted to universal statements. The audit checked
the interpolation identity, analytic envelope, tail argument, and actual
rounding directions separately. The figure builder was inspected for the
meaning of its curves and truncation bounds; visual layout approval belongs
to the separate figure review. No broad suite rerun was needed for this
read-only proof audit.

## 6. Source and command record

The audit used `rg --files`, direct reads of the pinned proofs and relevant
inherited sections, Python `fractions.Fraction` reconstructions, 60-digit
`mpmath` display checks, and `hashlib.sha256` pins. The targeted inverse checks
used direct coefficient formulas from the manuscript, not `coupled_lab`.
The independently delegated sieve recomputation did not import or execute
`checks/resolution_v11.py`.

The external source question was only the even-zeta numerical conversion.
The official **NIST Digital Library of Mathematical Functions**, Chapter 25,
Section 25.6, version 1.2.8, release 2026-09-15, was read on 2026-10-09:

- <https://dlmf.nist.gov/25.6.E1> supplies the values at 2, 4 and 6.
- <https://dlmf.nist.gov/25.6.E2> supplies the positive-even Bernoulli formula.
- <https://dlmf.nist.gov/25.6.E16> supplies the positive-even recurrence;
  taking \(n=4\) with the values above gives \(\zeta(8)=\pi^8/9450\).

Thus \((\pi^4/90)/(\pi^8/9450)=105/\pi^4\). The source and project use the
same Riemann zeta normalization, and every required argument is a positive
even integer. This is a verified numerical-constant leaf, not a novelty
search. No third-party source copy was added by this read-only source pass.
No external functional-differential theorem is needed by the coupled proof.

## 7. Exact revision pins

All paths are relative to the release root. A later change to a proof or a
used premise requires a scoped recheck; the verdict is not automatically
inherited by a different hash.

| Artifact | SHA256 |
|---|---|
| `research_v11/TARGET_CONTRACT.json` | `17b7ee8966c8337843911ee5803f629d5ad8ee15e178a35b41f1e9550652aabe` |
| `research_v11/coupled_growth_proof.md` | `0faa09bdc4d434e2fb9a9a5bb5f6f6b2122a3de30656b8c8c9c73206c08f763b` |
| `research_v11/coupled_independent_derivation.md` | `63f9fd9171b5686450e5c422dbccc61a29548dfbe66dff4d92db03b0c3596779` |
| `research_v11/coupled_structure.md` | `5ca874efc3bbe4e3b9584175c1565ade3d4aa120566fdca2107521a718f44161` |
| `research_v11/coupled_identifiability.md` | `8e8c8f7c5b3a5a2667ac82c633d82c647d0a1b184e4d8cab6431bf53e2396ee9` |
| `research_v11/resolution_atlas.md` | `a5960fb85336f3a89b08d1bc2d5e69202c67ea4652c363bd44d3588ecdc634e6` |
| `routes/asymmetric_dilation.md` | `5956a622393e36f646a15c4a1c439c1a2682c53eb52e198a1f4463e190925911` |
| `new_results/dilation_type.md` | `4a438fa513b06cc729d8317c565bc2a45dc9da253964d3d9ce406a5ac6f97494` |
| `new_results/arithmetic_inverse.md` | `a8c29614a565231ac91e14c17312928ebdc40bcd5c1597e73b487f1f8b00cc81` |
| `new_results/multi_prime_sieve.md` | `5b5997c122e80bfad68cbb20698e704788e9ff6b82e72794418efde3a0df716e` |
| `coupled_inverse.py` | `7a20582094149e667a834e6b5059ae6456d1d5bf00422dfb0de0f6b05640a2e0` |
| `checks/coupled_inverse_v11.py` | `8c021ec4c1d216dcab7e9246a2dd4f8b6f29e384153b3980608a2d1f2645581a` |
| `evidence/v11/coupled_inverse_checks.json` | `87ad596384f12f138f3889a2e962f6d0983388525bba7ece2e2186f65051cb98` |
| `checks/resolution_v11.py` | `ac5fe57ab2abad9b8aafe5ca9d48d9c1652f8acf6cbc3b3ea446e0877b8fc877` |
| `build_resolution_figures.py` | `9ae016f807110ae992bfe000df2c165e101f43bed2e5e2e61cc2182a9e0b9a6c` |
| `evidence/v11/resolution_checks.json` | `56fd0d3b10333a690a39c27a73514c1c95d73e6761d0d8145a755b8b9349a3f1` |
| `evidence/v11/resolution_figures.json` | `41cbf76950ce99b93edd9d9067aa529d0a91de33df3c6561ce7b777e46d81abf` |
| `evidence/v11/resolution_review.json` | `f3460930a3652f2947628aa14eea8584952f3653ec6abab7f015a3349ae0a8da` |

## 8. Remaining gap and safe closeout

There is no remaining implication missing from the normalized claims audited
here. The strongest safe conclusion is the full coupled entire-order and
positive finite type theorem, type-vector alignment, the precisely scoped
operator and solution reduction classifications, exact generic degree-seven
identifiability, and the atlas's stated sufficient resolution certificates.

The existence of ordinary type limits, optimal detector degrees five or six,
optimal separation radii, and historical priority remain unresolved or outside
this audit. Numerical agreement cannot settle those questions. The cheapest
next release check is to compare the final packaged proof hashes against
Section 7 and inspect manuscript transcriptions of the constants and domain
restrictions.

Proofreading self-review covered this report in full: notation, domain
restrictions, coefficient normalizations, display delimiters, exact fractions,
and SHA256 transcription. No unresolved local issue remains. No mathematical
token in a source proof was edited by the auditor.
