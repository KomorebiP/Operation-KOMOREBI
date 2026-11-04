# Special Functions: factorial normalization, Block16

SF-LEAN-B16 proves **all-index factorial normalization** of the exact rational
binomial derivative arrays: A_n=(2n+1)!u_n and B_n=(2n+1)!v_n. This holds
for arbitrary rational scales, including signed and noncontracting data.
A finite paired append-array model is proved equal to the inclusive prefix;
enumerating and dividing by (2n+1)! gives the ordinary coefficient array.
Its enumerate/multiply/sum polynomial equals the certified polynomial.
Under strict positive contractions and adequate majorant fuel, the resulting
exact rational endpoints enclose the actual real canonical functions.

There are **30 new theorem declarations**, for **435 registered names**.
All **63 fresh replay steps** pass across sixteen coupled modules: 396
theorem axiom audits, sixteen kernel replays, four expected rejections and
one positive fixture. The finite core's 39-name evidence is inherited and
Mathlib imports are cached. Review provenance is self-review.

The [report](../monographs/special-functions/formalization/Block16/REPORT.md),
[claim map](../monographs/special-functions/formalization/Block16/CLAIM_MAP.json),
[review](../monographs/special-functions/formalization/Block16/SELF_REVIEW.md),
[source](../monographs/special-functions/lean/CoupledNormalization.lean),
[I/O inventory](../monographs/special-functions/formalization/Block16/IO_MANIFEST.json)
and [receipt](../monographs/special-functions/formalization/Block16/evidence/receipt.json)
bind the extension. Formal I/O records 56 inputs, 64 packaged outputs,
sixteen generated objects and 37 staging copies; the separate source
assessment records 34 inputs and two outputs. Development sources and logs
are labeled separately from accepted proof evidence.

Replay `tools/verify_coupled_normalization.py` with Lean 4.34.0-rc2, Mathlib
aeb72f1e9981b6d35b426b16dca7759be3e7ba06 and a new external directory.
It installs nothing and makes no network request.

The Lean list and exact rational operations are mathematical specifications.
**Full Python refinement remains open**, including interpreter/Fraction/stdlib
semantics, validation and mutation, guarded disk-majorant loop/resource
failures and returned dictionary behavior. Next: prove successful ladder
traces match the fuel majorant and preserve step/bit errors. Other J
degree/denominator/symmetry, ancillary F/H, I and broad A-E coverage remain.
Ordinary type convergence is conditional. No whole-book percentage is claimed.
See the [live continuation](../monographs/special-functions/CONTINUE_HERE.md)
and [remaining work](../monographs/special-functions/formalization/Block16/REMAINING_WORK.md).
