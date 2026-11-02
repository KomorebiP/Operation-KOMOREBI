# SF-LEAN-B09: explicit lower logarithmic growth

For the actual canonical pair with 0<q,r,a,b<1, this block proves

\[
\log F_i(R)\ge c_-w_i(R+C)^\rho\qquad(R\ge2,\ i=1,2),
\]

where F=(UReal,VReal), rho is the unique positive characteristic exponent,
w is its max-normalized positive right eigenvector, Q=max(q,r,a,b),
m=min(q,r,a,b), B=1+2/m, C=Q/(1-Q), and c_minus=log(2)/(B+C)^rho.
Each coefficient c_minus*w_i is strictly positive. The block also proves
c_minus*w_i <= log(F_i(R))/R^rho for every R>=2, and transports the lower
comparison to the norms of the actual complex functions at R.

There are **16 new theorem declarations**, including supporting lemmas,
and **217 registered names**: 39 inherited finite-core names and
29,21,19,16,13,19,23,22,16 in Blocks01 through 09. This proves the explicit
lower-comparison subsection of F.2, not the whole growth theorem. The upper
comparison, formal liminf/limsup type bounds, radial exponent limit, F.3
type-vector proportions, operator decoupling and wider coverage remain open.

## Proof and correspondence

The exact source is Theorem F.2, subsection `Explicit lower comparison`, in
`monograph/sections_v11/coupled_growth_full.tex` (lines 199-264 at the base).
Block08 supplies the real-axis interpretation, F_i(R)>=R for R>=0,
logarithmic final-unit recurrences and child radii >=2 for R>=B. Block07
supplies rho>0 and the positive normalized right eigenvector.

On [2,B], the proposed right side is <=log(2), since w_i<=1 and positive
real powers are monotone. The linear lower bound gives log(F_i(R))>=log(R)
>=log(2). For each scale p<=Q, the identity (1-Q)C=Q gives
p(R+C)<=p(R-1)+C. Also d=(1-Q)B+Q>0, and R>=B implies
p(R-1)<=R-d. The four children therefore lie in [2,R-d].

Apply the comparison at those children, use monotonicity and multiplicativity
of real powers on nonnegative inputs, and use each row of P(rho)w=w. The two
logarithmic recurrences then propagate the paired inequality. A separate
general lemma proves induction on the closed caps [2,B+n*d]; an Archimedean
argument puts each finite R in one cap. All endpoints are included, so this
implementation needs no additional continuity argument. It uses rho>0,
with no convexity or rho>=1 assumption.

The generic theorem permits any nonnegative eigenvector bounded by one.
Canonical wrappers select the normalized vector and prove both coefficients
strictly positive. Since R^rho<=(R+C)^rho and R^rho>0 at R>=2, division gives
the uniform growth-ratio lower bounds. Block08's exact real-axis norm identity
gives the complex-norm wrapper. Block08 separately identifies these positive
real values with the attained spherical maximum norms.

See [CLAIM_MAP.json](CLAIM_MAP.json) and [declarations.json](declarations.json)
for the exact interfaces and hypotheses. The source is
`lean/CoupledLowerGrowth.lean`; logical audit commands are in
`lean/CoupledLowerGrowthAudit.lean`.

## Validation and I/O

The [receipt](evidence/receipt.json) records **42 passing steps**: toolchain
version, nine dependency revisions, warning-as-error compilation and axiom
audits of nine coupled modules, same-kernel replay of those modules, four
negative controls and one positive fixture file. All **178 coupled theorem
declarations** are freshly axiom-audited; the finite core's 39-name evidence
is inherited. Allowed logical axioms are propext, Classical.choice and
Quot.sound. Pinned Mathlib is reused from cache, not freshly rebuilt/replayed.

The negative controls reject zero descent, a reversed shift sign, removal of
the seed lower threshold, and a placeholder. The positive file checks the
exact worked C=7/3 and d=4, the saturated shift at p=Q, the endpoint R=2,
canonical global interfaces and positive coefficient/ratio wrappers. It
also instantiates all four scales at 1/4 with rho=1/2 and vector (1,1), using
an exact square-root identity. These controls test hypotheses and real-power
interfaces; no numerical simulation supports the universal theorem.

```text
python tools/verify_coupled_lower_growth.py --toolchain /path/to/toolchain --mathlib /path/to/mathlib --work /path/to/new/sf-block09
```

Use a new directory outside the release. --git and --packages support other
local layouts. The verifier neither installs nor downloads dependencies. Lean
is 4.34.0-rc2; Mathlib is aeb72f1e9981b6d35b426b16dca7759be3e7ba06.
[IO_MANIFEST.json](IO_MANIFEST.json) lists 35 actual input files, 43 packaged
outputs and nine unbundled generated object hashes. The immutable
[SOURCE_MANIFEST.json](SOURCE_MANIFEST.json) binds all formal inputs, block
records, evidence and the dated guide, excluding itself and live guidance.
The [review](SELF_REVIEW.md) is self-review, not independent review.

## Checkpoint and continuation

Base: b672123ad852de103130420565a6c1e9645b63f5. The exact source hash in
SELF_REVIEW and the receipt define this checkpoint. The closed-cap route
resolves the registered target. The first-failure/infimum alternative is
deferred for estimates requiring a continuity interface; its first uncertainty
is closed failure-set and boundary handling. A branching-tree alternative is
deferred for extensions needing explicit leaf weights; its first uncertainty
is termination with weight bookkeeping. Neither is refuted or exhausted.
There are no delegated or delayed runs.

Next executable target: the `Explicit upper comparison` subsection of F.2.
First derive F_i(R)<=R*(1+UReal(pR)*VReal(p'R)) for R>=0 by the actual
derivative equations and monotonicity. Then certify the seed ladder
R_k=Q^(-k), Z_0=2, Z_k=Q^(-k)*(1+Z_(k-1)^2), including F_i(1)<=2 from
the coefficient majorant. Bound log(Z_N) by the manuscript's W_N before
propagating its shifted logarithmic comparison with positive delays.
The pinned API `Convex.image_sub_le_mul_sub_of_deriv_le` in
Mathlib/Analysis/Calculus/Deriv/MeanValue.lean (line 355), applied on [0,R],
is the immediate counterpart of Block08's lower mean-value comparison.
Only after the upper bounds should real liminf/limsup type identifications
and the radial exponent limit be claimed. Earlier blocks, dated guides,
manuscript sources and reading PDFs are preserved. The root archive manifest
remains its older release snapshot; this is no new complete archive validation.
