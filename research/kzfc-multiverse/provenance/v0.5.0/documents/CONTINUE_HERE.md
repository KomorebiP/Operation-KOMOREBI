# Continue from v0.5.0

Use this archive as the authoritative source. The v0.4.0 predecessor is retained under provenance; its 12 mathematical modules are byte-for-byte preserved. Read THEORY.md, PROOF_BOUNDARY.md and the five new modules before editing.

## Completed target

Do not redo the ambient-to-set or set-to-formula translation. `Komorebi.MembershipFormula.extensionFormula_iff_filterExtension` already connects an actual membership-only first-order formula to CompleteFilterExtension. `extensionFormula_iff_residual` closes the residual comparison for regular kappa. The exact interpretation uses the initial-ordinal ZFSet code of kappa.

## Next bounded target

Encode the regular-uncountable initial-cardinal guard as actual membership syntax and prove its interpretation. Then build the guarded closed existence sentence. Do not just existentially close extensionFormula: that would include the aleph0 theorem and fail to express the intended large-cardinal axiom.

A further target is an object-language residual/constraint encoding and an internal ZFC proof or arbitrary-model semantic comparison. Keep internal functions, cardinality and completeness separate from external notions. Proving an equivalence in the concrete ZFSet universe does not by itself supply that step.

## Reproduction

Read REPRODUCE.md. Use the pinned runtime and run:

    python3 scripts/run_recorded.py --clean --sequential-build

The serial strategy avoids the failed parallel clean attempt. Read actual results and recorded process exit, not just old logs. A fresh verification removes stale verdicts. Generate fresh manifests only from the new recorded run; do not reuse old output hashes.

## Guardrails

Do not introduce the desired conclusion as a field of an admissible-system record. Do not add an axiom of uncountable existence to make the comparison pass. Do not relabel semantic adequacy as ZFC derivability or relative consistency. Preserve the relative-intersection convention and its empty-family regression. Degree labels alone do not establish increased foundational strength.
