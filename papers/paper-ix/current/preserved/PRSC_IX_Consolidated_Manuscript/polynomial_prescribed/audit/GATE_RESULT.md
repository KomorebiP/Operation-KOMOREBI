# Prescribed-parameter obstruction gate result

PASS: 65/65 stages, 245.016 seconds.

- 39 mathematical modules compiled from source, including four new prescribed modules.
- Five positive control modules and ten statement contract modules compiled.
- Eight mathematically invalid controls rejected with the expected type mismatch.
- All 375 explicit declaration closures audited: 296 theorems, 71 definitions,
  and eight abbreviations. Only the listed standard axioms were used.
- All 35 inherited mathematical sources remained byte-identical to the previous
  first-order motion release. All 270 compiled output files were hashed and reconciled.
- Independent raw-proof review and gate provenance reconciliation both passed.

The four new mathematical modules contain 16 theorems, ten definitions, and
three abbreviations. Control and contract declarations are included only in
the complete audit totals above. The expanded final contracts derive the
residual from the original lower-root condition and count actual residue
vectors satisfying all three explicit restrictions.

Report SHA-256: `4aa1dc1b3629fbc593f1d3221b75e85d9deca777de2484113fe6a03b5a174724`.
Inventory SHA-256: `ef611d846092623eb94a25167f5e4e15f7180f0d8f9842cd11882f7e97da6fcd`.
Reconciliation SHA-256: `59a6acd2fb72a80bd6bb04eb1c004e053f0efbdcc057503d0601412aebcdb861`.
Reviewed-source record SHA-256: `652d5f4ebb88f653aee742ee01fb0b244586c5aa3e39ab12b27adaa36ccda857`.

The full report and raw compiler logs are in `verification/` in the release.
The gate began with an empty project build directory. The pinned Lean kernel
and precompiled Mathlib dependencies were reused, as stated in GATE_PROTOCOL.md.
The supplied version 1 computation manifest validator passed on its first
invocation with the fresh gate directory as the artifact root. The validator
output is preserved in dev/gate_manifest/. Version 1 schema limitations are
reported there; the separate gate report records exact source hashes,
commands, compiled output hashes, and timeouts.

The finite obstruction criterion covers every positive modulus q, including
composite q and q=1, at depth L>=1. The vector-space rank formulas require a
prime modulus. This release does not claim compatible infinite lifting for
arbitrary prescribed parameter sequences or general singular branches.
