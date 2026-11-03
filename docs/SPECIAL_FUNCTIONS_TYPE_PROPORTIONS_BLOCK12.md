# Special Functions: component type proportions, Block12

SF-LEAN-B12 proves the registered canonical Theorem F.3: lower and upper
type vectors are positive ordered scalar multiples of the max-normalized
characteristic vector. Both component ratios equal r^rho/(1-q^rho) and
(1-b^rho)/a^rho. Either both ordinary type limits exist or neither does;
given one component limit, the vector limit is a positive multiple of w.
Existence of those ordinary limits is not asserted unconditionally.

The addition has 26 theorem declarations, for 299 registered names.
All 51 fresh verification steps pass across twelve coupled modules, with
260 fresh axiom audits, twelve kernel replays, four expected rejections and
a positive interface fixture. The finite core's 39-name evidence is inherited;
pinned Mathlib is cached, not freshly rebuilt or replayed. Review is self-review.

The [report](../monographs/special-functions/formalization/Block12/REPORT.md),
[claim map](../monographs/special-functions/formalization/Block12/CLAIM_MAP.json),
[review](../monographs/special-functions/formalization/Block12/SELF_REVIEW.md),
[source](../monographs/special-functions/lean/CoupledTypeProportions.lean),
[I/O inventory](../monographs/special-functions/formalization/Block12/IO_MANIFEST.json)
and [receipt](../monographs/special-functions/formalization/Block12/evidence/receipt.json)
bind the actual proof and replay. Formal I/O has 44 inputs, 52 packaged
outputs, twelve generated objects and 29 staging copies. The separately
bound remaining-work assessment uses twenty inputs and two outputs.

Use `tools/verify_coupled_type_proportions.py` under Special Functions,
with Lean 4.34.0-rc2, Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06
and a new external work directory. The verifier installs nothing and makes
no network request. [Live continuation](../monographs/special-functions/CONTINUE_HERE.md)
gives the next exact target; [remaining work](../monographs/special-functions/formalization/Block12/REMAINING_WORK.md)
retains the source-mapped backlog.

The registered F.1-F.3, G.1 and guarded G.2 contracts are complete.
Ancillary F scalar identities, H.1 operator classification, I-J resolution
and certified-evaluator refinement, and broader A-E analytic coverage remain.
No whole-book completion percentage is established. Source editions,
historical evidence and reading PDFs are preserved.
