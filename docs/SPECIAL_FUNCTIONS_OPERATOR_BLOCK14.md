# Special Functions: autonomous projections, Block14

SF-LEAN-B14 proves the registered main H.1 operator theorem for positive
scales, without assuming contraction or distinct scale nodes. A nonzero
complex row has an arbitrary scalar functional of its projection on every
zero-constant analytic input exactly when q=a, r=b and the row is
gamma*(1,-1), gamma!=0. The projected field is zero. No invertible constant
complex 2x2 change decouples the operator. Entire-function and actual local
analytic-germ versions are both proved; no quadratic ansatz on the scalar
functional is imposed.

There are **27 new theorem declarations**, for **369 registered names**.
All **57 fresh verification steps** pass across fourteen coupled modules:
330 theorem axiom audits, fourteen kernel replays, four expected rejections
and one positive fixture. The finite core's 39-name evidence is inherited;
pinned Mathlib imports are cached. Review provenance is self-review.

The [report](../monographs/special-functions/formalization/Block14/REPORT.md),
[claim map](../monographs/special-functions/formalization/Block14/CLAIM_MAP.json),
[review](../monographs/special-functions/formalization/Block14/SELF_REVIEW.md),
[source](../monographs/special-functions/lean/CoupledOperator.lean),
[I/O inventory](../monographs/special-functions/formalization/Block14/IO_MANIFEST.json)
and [receipt](../monographs/special-functions/formalization/Block14/evidence/receipt.json)
bind the proof and exact replay. Formal I/O has 50 inputs, 58 packaged outputs,
fourteen generated objects and 33 staging copies. The separate remaining-work
assessment has 26 inputs and two outputs. Development diagnostics are separately
identified and are not accepted proof evidence.

Replay `tools/verify_coupled_operator.py` under Special Functions with
Lean 4.34.0-rc2, Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06 and
a new external work directory. The verifier installs nothing and makes no
network request. [Live continuation](../monographs/special-functions/CONTINUE_HERE.md)
and [remaining work](../monographs/special-functions/formalization/Block14/REMAINING_WORK.md)
retain the exact next targets and boundaries.

Next major target: Appendix J arbitrary-radius exact evaluation. Some F
explanatory correspondence, H's odd-input-only/tensor variants, I's resolution
mechanisms and broad A-E analytic development remain. Ordinary type convergence
is conditional. No exhaustive whole-book correspondence or completion
percentage is established. Earlier sources and evidence retain their bytes.
