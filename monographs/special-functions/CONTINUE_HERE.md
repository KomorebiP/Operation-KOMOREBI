# Continue Special Functions formalization

Current checkpoint: **SF-LEAN-B09**, based on repository commit
`b672123ad852de103130420565a6c1e9645b63f5`. Start with
`formalization/Block09/REPORT.md`, claim/declaration maps, self-review,
I/O inventory and source-bound receipt.

`lean/CoupledLowerGrowth.lean` adds 16 theorem declarations proving
log(F_i(R)) >= c_minus*w_i*(R+C)^rho for every R>=2 and both actual canonical
real functions. Here rho is the positive characteristic exponent, w its
max-normalized positive right vector, Q=maxScale, m=minScale, B=1+2/m,
C=Q/(1-Q), and c_minus=log(2)/(B+C)^rho. Each c_minus*w_i is strictly
positive and uniformly bounds log(F_i(R))/R^rho below. The corresponding
complex norm lower comparison is also proved. The closed-cap induction uses
d=(1-Q)B+Q>0, includes endpoints, and works for every rho>0.

The registered scope is 217 names, including supporting lemmas and the
preceding 201 names. The explicit lower comparison is complete. Formal
liminf/limsup type bounds, the upper comparison, radial exponent limit and
F.3 type-vector proportions remain open.

Next executable target: `Explicit upper comparison` in
`monograph/sections_v11/coupled_growth_full.tex`. First derive
F_i(R)<=R*(1+UReal(pR)*VReal(p'R)) for R>=0 from the actual derivative
equations and monotonicity (rows (q,r) and (a,b)). Establish F_i(1)<=2
from the existing coefficient majorant. Then prove the simultaneous seed
ladder R_k=Q^(-k), Z_0=2, Z_k=Q^(-k)*(1+Z_(k-1)^2), and its explicit
logarithmic bound log(Z_N)<=W_N with
W_N=(2^(N+1)-1)log(2)+(2^(N+1)-N-2)log(1/Q).
Use `Convex.image_sub_le_mul_sub_of_deriv_le` on [0,R]; its pinned source
is Mathlib/Analysis/Calculus/Deriv/MeanValue.lean:355. Block08 supplies the
global real derivatives, origin values and monotone positive restrictions.

After that set Delta=log(1/m),
D=max(log(1/(qr)),log(1/(ab)))+log(2), choose N with Q^(-N)>=3/m,
and obtain the seed on t in [1,1+Delta]. Prove the delayed upper recurrence
for G_i(t)=log(F_i(exp(t)))+t+D and propagate with positive delays in
[log(1/Q),Delta]. Check all constants, logarithm domains and endpoints.
Only then identify the real liminf/limsup types and prove the radial exponent
limit. Operator decoupling and broader coverage are separate obligations.

Replay `tools/verify_coupled_lower_growth.py` with Lean 4.34.0-rc2,
Mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`, and a new external
directory. The native Windows toolchain and imports are cached. The replay
has 42 steps over nine coupled modules, freshly axiom-auditing 178 declarations
and inheriting the finite core's 39-name evidence. Imported Mathlib is not
freshly rebuilt/replayed. Review is self-review.

Block09/IO_MANIFEST.json inventories 35 inputs, 43 packaged outputs and nine
unbundled generated objects with hashes. Source, audit, controls, verifier,
correspondence, current status, catalogue and this file are updated together.
Immutable source manifests exclude live guidance.

The closed-cap route succeeded. First-failure/infimum proof is deferred for
future continuity-based estimates; branching-tree proof is deferred for
extensions needing explicit leaf weights. Their boundary/termination checks
remain untried, not exhausted. Earlier block reports retain older alternatives.
No delegated or delayed runs remain. Preserve all nine blocks and dated
guides, manuscript sources and reading PDFs. New proofs belong in a new block.
The root package manifest is an older release snapshot, not current archive
validation.
