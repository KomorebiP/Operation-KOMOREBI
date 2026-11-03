# Special Functions: guarded majorants, Block17

SF-LEAN-B17 proves the exact rational guarded-majorant algorithm specification:
first-small-radius ladders, bounded step counts, reverse-fold equality to the
proved fuel model, explicit step/size errors and abstract input-validation order.
Every successful return certifies the actual complex disk bound and exact
real polynomial endpoints under the original strict-contraction hypotheses.

Radius one needs a step. Radius zero returns before resource validation after
valid scales. A small-radius seed is not bit-checked; size checks follow each
reverse-fold update. Q=1/2,R=2 gives ladder [2,1] and bound 500/81. Guard errors
remain errors; finite adequate mathematical fuel does not promise fixed-limit success.

**30 new theorems; 465 registered names. All 66 fresh replay steps pass** across
seventeen modules, including 426 theorem axiom audits, seventeen kernel replays,
four expected rejections and one positive fixture. Finite-core evidence for
39 names is inherited; Mathlib is cached. Review provenance is self-review.

The [report](../monographs/special-functions/formalization/Block17/REPORT.md),
[claim map](../monographs/special-functions/formalization/Block17/CLAIM_MAP.json),
[review](../monographs/special-functions/formalization/Block17/SELF_REVIEW.md),
[Lean source](../monographs/special-functions/lean/CoupledGuardedMajorant.lean),
[I/O inventory](../monographs/special-functions/formalization/Block17/IO_MANIFEST.json)
and [receipt](../monographs/special-functions/formalization/Block17/evidence/receipt.json)
bind the proof. Formal I/O has 59 inputs, 67 packaged outputs, seventeen objects
and 39 staging copies. Separate assessment I/O has 37 inputs/two outputs;
development/preflight diagnostics are labeled separately.

Replay tools/verify_coupled_guarded_majorant.py with Lean 4.34.0-rc2 and Mathlib
aeb72f1e9981b6d35b426b16dca7759be3e7ba06 in a new external directory.
The verifier installs nothing and makes no network request.

This is the Lean algorithm model, including abstract invalid-input tags.
**Full Python runtime refinement remains open**: interpreter, Fraction,
stdlib bit_length/comb/factorial, type/exception objects, mutation and dictionary
correspondence are separate. Next: a typed certified-evaluation result composing
the proved arrays, guarded majorant and endpoint fields. Other J/F/H, I and A-E
remain; ordinary type convergence is conditional. No whole-book percentage exists.
Use [current guidance](../monographs/special-functions/current/README.md),
[live continuation](../monographs/special-functions/current/CONTINUE_HERE.md)
and [remaining work](../monographs/special-functions/formalization/Block17/REMAINING_WORK.md).
