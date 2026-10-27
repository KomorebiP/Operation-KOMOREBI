# Verification summary — 1.7.0

- 13 production Lean builds and 13 own-kernel replays passed.
- 149 explicit named declarations audited, including 93 named theorems.
- Six invalid proof controls rejected; one extra-axiom control rejected by the
  audit policy after Lean correctly accepted reasoning relative to that axiom.
- 169 source tests and 169 installed-wheel tests passed with no failures or skips.
- 65,536 protected rule problems and 223,232 covers match independent finite
  model enumeration. The previous 5,039 binary linear systems also pass.
- 69 pages, 24 numbered vector figures, 41 stable result groups.
- 131 predecessor mathematical environments unchanged, 18 new environments.

Current reports: `data/release_verification.json`,
`data/publication_verification_1.7.0.json`,
`data/recovery_extension_checks_1.7.0.json`, and
`evidence/formal_1.7.0/verification.json`.

Kernel replay is against pinned cached dependencies, not a fresh Mathlib build
or an independent checker implementation. Finite software checks do not replace
an arbitrary-input refinement theorem. See `FINALIZATION_REPORT.md` for details.
