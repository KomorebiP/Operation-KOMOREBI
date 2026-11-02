# Continue Special Functions formalization

Current checkpoint: **SF-LEAN-B10**, based on repository commit
`2661894c45768d240e9c2fcc4524061e404a0411`. Start with
`formalization/Block10/REPORT.md`, its claim/declaration maps, self-review,
I/O inventory and source-bound execution receipt.

`lean/CoupledUpperGrowth.lean` adds 34 theorem declarations proving the
explicit F.2 upper comparison log(F_i(R))<=c_plus*w_i*R^rho-log(R)-D for
every R>=e and both actual canonical functions. The manuscript constants
use only the parameters and characteristic data; an admissible seed index
exists and the canonical wrapper chooses the least one. The geometric
seed and W_N formula, positive upper coefficients, and two-sided positive
finite bounds on log(F_i(R))/R^rho are proved. This includes rho<1.

The registered scope is 251 names, including supporting lemmas and the
preceding 217 names. Both explicit comparison subsections of F.2 are proved.
Real liminf/limsup type bounds, the radial exponent limit and F.3 type-vector
proportions remain open as formal statements.

Next executable target in `monograph/sections_v11/coupled_growth_full.tex`:
finish F.2's type bounds and radial exponent limit. Begin with
`canonical_two_sided_growth_ratio`: for every R>=e, each ratio lies between
its positive canonical lower and upper coefficients. Use this to prove the
eventual boundedness premises for real filter liminf/limsup atTop, then
identify positive finite lower/upper types and their order. Do not rely on
the default real liminf/limsup value without the boundedness hypotheses.

For the radial exponent, take logarithms of the two-sided comparison for
large R. Squeeze log(log(F_i(R)))/log(R) between rho plus the constant log
coefficients divided by log(R). Make log(F_i(R))>0, R^rho>0, log(R)>0 and
the eventual domains explicit. Transport to maximum-modulus language through
Block08's attained maximum identity. F.3 then needs scaled liminf/limsup
transport, both coupled row inequalities, the positive left eigenvector and
the one-dimensional eigenvalue-one space. Operator and wider coverage remain
separate obligations.

Pinned API entry points are Filter.limsup_le_of_le, Filter.le_liminf_of_le
and Filter.liminf_le_limsup in Mathlib/Order/LiminfLimsup.lean:141-185.
Supply the bounded/cobounded premises explicitly. For the squeeze error,
Tendsto.div_atTop with Real.tendsto_log_atTop sends each constant/log(R) to
zero; the logarithmic-growth lemma need not assume the growth ratio converges.

Replay `tools/verify_coupled_upper_growth.py` with Lean 4.34.0-rc2,
Mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`, and a new external
directory. The native Windows toolchain and imports remain cached. All 45
steps cover ten coupled modules, freshly axiom-auditing 212 declarations
and inheriting the finite core's 39-name evidence. Imported Mathlib is not
freshly rebuilt/replayed. Review is self-review.

`formalization/Block10/IO_MANIFEST.json` inventories 38 inputs, 46 packaged
outputs, ten unbundled generated objects and 25 staged source copies with
hashes. Source, audits, controls, verifier, correspondence, status, catalogue
and this live file are updated together. Immutable manifests exclude live
guidance. Preserve all ten blocks, dated guides, manuscripts and reading PDFs.

The mean-value/geometric-seed/log-delay route succeeded. The FTC route is
deferred for future integral identities; its first uncertainty is the
integral/embedding API. A direct weighted supersolution is deferred for
sharper constants; its first uncertainty is a parameter-only seed for rho<1.
Neither is exhausted or refuted. Older reports retain earlier alternatives.
No delegated or delayed runs remain. New proofs belong in a new block.
The root archive manifest remains an older release snapshot.
