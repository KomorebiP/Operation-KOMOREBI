# SF-LEAN-B10: explicit upper logarithmic growth

For the actual canonical pair with 0<q,r,a,b<1, this block proves the
manuscript's explicit upper comparison, for each component and every R>=e:

\[
\log F_i(R)\le c_+w_i R^\rho-\log R-D.
\]

Here F=(UReal,VReal), rho is the unique positive characteristic exponent,
w its max-normalized positive right eigenvector, Q=max(q,r,a,b),
m=min(q,r,a,b), Delta=log(1/m), and
D=max(log(1/(qr)),log(1/(ab)))+log(2). Choose any natural N with
(1/Q)^N>=3/m, and put

\[
W_N=(2^{N+1}-1)\log2+(2^{N+1}-N-2)\log(1/Q),
\quad S=W_N+1+\Delta+D,\quad c_+=e^{-\rho}S/\min(w_1,w_2).
\]

Such N exists. The canonical coefficient wrapper uses the least such N;
its coefficients c_plus*w_i are strictly positive and depend only on the
parameters, the characteristic exponent and vector. Together with Block09,
both growth ratios log(F_i(R))/R^rho now have explicit positive lower and
finite upper real bounds for all R>=e. The complex norm bound at the positive
point is also proved; Block08 identifies that norm with the attained maximum
on its sphere.

The source `lean/CoupledUpperGrowth.lean` adds **34 named theorem declarations**,
including supporting lemmas, bringing the registered scope to **251 names**:
39 inherited finite-core names and 29,21,19,16,13,19,23,22,16,34 in Blocks01-10.
This completes the two explicit comparison subsections of F.2. Formal real
liminf/limsup type bounds, the radial exponent limit and F.3 proportions are
not yet asserted as Lean theorems. Full monograph coverage remains open.

## Proof and exact correspondence

The authority is Theorem F.2, `Explicit upper comparison`, in
`monograph/sections_v11/coupled_growth_full.tex` (lines 266-350 at the base).
All ordered inequalities are real. The upper mean-value comparison on [0,R]
applied to the actual derivative equations gives
F_i(R)<=R*(1+UReal(pR)*VReal(p'R)) for R>=0, including zero. The geometric
coefficient bound and actual real HasSum expansions give F_i(1)<=2.

Set R_n=(1/Q)^n, Z_0=2 and Z_(n+1)=R_(n+1)*(1+Z_n^2). Each contracted
argument at R_(n+1) lies below R_n. Positivity and monotonicity therefore
give both F_i(R_n)<=Z_n. Also Z_n>=1. Taking logarithms yields
log(Z_(n+1))<=(n+1)log(1/Q)+log(2)+2log(Z_n); the displayed W_n satisfies
that same affine recurrence with the exact initial value. Induction proves
log(Z_n)<=W_n. All subtraction in the closed formula is in the real field.

The Archimedean power theorem gives an admissible N. For 1<=t<=1+Delta,
exp(t)<=e/m<3/m<=R_N, hence log(F_i(exp(t)))<=W_N. The auxiliary e<3
proof uses exp(1/6)<=6/5, raises this inequality to the sixth power and uses
(6/5)^6<3, entirely in Lean with exact rational arithmetic. No new cached
Mathlib module or floating-point estimate is needed.

For G_i(t)=log(F_i(exp(t)))+t+D, the full-radius inequality and child values
>=1 yield G_1(t)<=G_1(t-delta_q)+G_2(t-delta_r), with the analogous second
row, whenever t>=1+Delta. Here delta_p=log(1/p). The correction D supplies
both inequalities D>=delta_p+delta_p'+log(2). Every delay lies in the closed
interval [log(1/Q),Delta], whose lower endpoint is positive.

The seed comparison G_i(t)<=S<=c_plus*w_i*exp(rho*t) holds on [1,1+Delta].
The row equations P(rho)w=w and
exp(rho*(t-delta_p))=p^rho*exp(rho*t) propagate it. Closed-cap induction,
transported from Block09's radius induction, covers every t>=1 with all
endpoints included. Substituting t=log(R) gives the boxed upper comparison.
No additional continuity argument at interval boundaries, rho>=1 assumption,
or type-limit premise is used.

Canonical wrappers prove coefficient positivity, the upper ratio bounds,
the two-sided ratio bounds using Block09, and complex norm transport.
[CLAIM_MAP.json](CLAIM_MAP.json) covers all 34 names and distinguishes the
remaining conclusions; [declarations.json](declarations.json) binds their
source locations and hash.

## Verification and I/O

The source-bound [receipt](evidence/receipt.json) has **45 passing steps**:
version, nine dependency revisions, warning-as-error compilation and exact
axiom audits for ten coupled modules, same-kernel replay of those modules,
four expected rejection controls and one positive fixture file. All **212
coupled theorem declarations** are freshly axiom-audited. The finite core's
39-name evidence is inherited. The allowed logical axioms are propext,
Classical.choice and Quot.sound. Pinned Mathlib imports are cached rather
than freshly rebuilt/replayed; there is no independent-review claim.

The controls reject a negative radius for the full upper recurrence, the
inadmissible worked seed index N=0, omission of the product-floor premises
in the logarithmic upper inequality, and a placeholder. These are specific
interface/arithmetic rejections, not general counterexample theorems for
every possible variant. The positive fixture checks R=0, the bound at one,
worked N=8, the canonical explicit upper comparison, the quarter-scale ladder
Z_1=20 and Z_2=6416, and the global rho=1/2 comparison with N=2 and w=(1,1).
It also consumes the positive coefficient and two-sided ratio interfaces.

```text
python tools/verify_coupled_upper_growth.py --toolchain /path/to/toolchain --mathlib /path/to/mathlib --work /path/to/new/sf-block10
```

Use a new external work directory; --git and --packages support other local
layouts. No dependency installation or network access is performed. Lean is
4.34.0-rc2 and Mathlib is aeb72f1e9981b6d35b426b16dca7759be3e7ba06.
[IO_MANIFEST.json](IO_MANIFEST.json) hashes 38 actual inputs, 46 packaged
outputs, ten unbundled generated objects and 25 staged source copies.
[SOURCE_MANIFEST.json](SOURCE_MANIFEST.json) seals the immutable block records,
dated guide, evidence and all replay inputs, excluding itself and live guidance.
Review and prose validation are in SELF_REVIEW.md and PROOFREADING.md.

## Checkpoint and continuation

Base: 2661894c45768d240e9c2fcc4524061e404a0411. Cutoff and assessment are
this same SF-LEAN-B10 source-bound checkpoint. The mean-value/geometric-seed/
logarithmic-delay route resolves the registered upper-comparison target.
The FTC route is deferred for later integral identities; its first uncertain
step is the integral/real-embedding API. The direct weighted-supersolution
route is deferred for sharper constants; its first uncertainty is a uniform
parameter-only seed for rho<1. Neither is refuted or exhausted. Older reports
preserve earlier alternatives. No delegated or delayed runs remain.

Next: formalize the real liminf/limsup type bounds and radial exponent limit
from the now-proved two-sided comparisons. First prove eventual upper and
lower boundedness of the growth ratios and bind each real liminf/limsup to
those constants. Then squeeze log(log(F_i(R)))/log(R) to rho, with all
logarithm domains and atTop filters explicit. F.3 proportions then require
scaled liminf/limsup transport and the positive left eigenvector. Operator
decoupling and broader analytic coverage remain separate. Earlier proof
blocks, manuscript sources, reading PDFs and dated guides are preserved.
The root archive manifest remains its older release snapshot.
