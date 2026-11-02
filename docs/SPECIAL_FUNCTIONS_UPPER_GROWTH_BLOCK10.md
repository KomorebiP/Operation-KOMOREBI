# Special Functions: explicit upper growth, Block10

SF-LEAN-B10 proves the manuscript's explicit upper comparison for both
canonical functions: log(F_i(R))<=c_plus*w_i*R^rho-log(R)-D for every R>=e.
The constants match F.2, use a parameter-only geometric seed ladder, and
require no evaluation of an unknown solution. A suitable seed index exists;
the canonical wrapper selects the least one. Its upper coefficients are
positive. Together with Block09, this gives explicit positive finite
two-sided bounds on log(F_i(R))/R^rho for every R>=e, including rho<1.

The addition has 34 named theorem declarations, for 251 registered names.
All 45 fresh replay steps pass across ten coupled modules; 212 coupled
declarations receive fresh axiom audits. The finite core's 39-name evidence
is inherited. Pinned Mathlib is cached rather than freshly rebuilt/replayed.
Review is self-review. Four rejection controls and the positive fixture pass,
including the exact quarter-scale rho=1/2 upper comparison.

The [report](../monographs/special-functions/formalization/Block10/REPORT.md),
[claim map](../monographs/special-functions/formalization/Block10/CLAIM_MAP.json),
[review](../monographs/special-functions/formalization/Block10/SELF_REVIEW.md),
[I/O inventory](../monographs/special-functions/formalization/Block10/IO_MANIFEST.json)
and [receipt](../monographs/special-functions/formalization/Block10/evidence/receipt.json)
bind the exact scope, 38 inputs, 46 packaged outputs, ten generated object
hashes and 25 staged source copies. The public verifier is
`tools/verify_coupled_upper_growth.py` under the Special Functions directory.
Use a fresh external output directory and the existing pinned toolchain.

Next: formal real liminf/limsup type bounds and the radial exponent limit,
then F.3 proportions. Operator decoupling and full analytic coverage remain
open. The [continuation](../monographs/special-functions/CONTINUE_HERE.md)
has the next executable target. Earlier proofs, manuscripts and reading PDFs
are preserved. No new complete archive validation is claimed.
