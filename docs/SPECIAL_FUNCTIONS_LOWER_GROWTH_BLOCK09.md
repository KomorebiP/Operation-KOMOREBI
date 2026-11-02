# Special Functions: lower logarithmic growth, Block09

SF-LEAN-B09 proves the explicit lower comparison in Theorem F.2:
log(F_i(R)) >= c_minus*w_i*(R+C)^rho for both canonical functions and every
real R>=2, with the manuscript's C=Q/(1-Q), B=1+2/m and
c_minus=log(2)/(B+C)^rho. The canonical coefficients are strictly positive,
and bound log(F_i(R))/R^rho below uniformly. The proof works for all rho>0,
including rho<1, by closed-cap radius induction and real-power monotonicity.

The addition has 16 named theorem declarations, for 217 registered names.
The fresh replay passes 42 steps across nine coupled modules and audits 178
coupled declarations. The finite core's 39-name evidence is inherited; pinned
Mathlib is cached rather than freshly rebuilt/replayed. Review is self-review.
Four negative controls are rejected and the positive fixture includes an
exact rho=1/2 example.

The [report](../monographs/special-functions/formalization/Block09/REPORT.md),
[claim map](../monographs/special-functions/formalization/Block09/CLAIM_MAP.json),
[review](../monographs/special-functions/formalization/Block09/SELF_REVIEW.md),
[I/O inventory](../monographs/special-functions/formalization/Block09/IO_MANIFEST.json)
and [receipt](../monographs/special-functions/formalization/Block09/evidence/receipt.json)
bind the exact scope, 35 input files, 43 packaged outputs and nine generated
object hashes. The public replay is `tools/verify_coupled_lower_growth.py`
under the Special Functions directory. Use a fresh external output directory.

Next: full-radius product upper recurrence, geometric seed ladder and explicit
upper comparison. Real liminf/limsup type bounds, the radial exponent limit,
type-vector proportions, operator decoupling and full analytic coverage remain
open. The live [continuation](../monographs/special-functions/CONTINUE_HERE.md)
has the executable next target. Prior proof blocks, manuscript sources and
reading PDFs are preserved. No new complete archive validation is claimed.
