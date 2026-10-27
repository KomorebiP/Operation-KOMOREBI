# Lean guide self-review

Proofread: `lean/Quantum_Arithmetic_Lean_Guide_Body.tex`,
`lean/Lean_Concordance.json`, `lean/Lean_Concordance.csv`, and
`reviews/FORMAL_SCOPE_AUDIT.md`.

- Routine edits: scope and terminology reconciled with actual current source;
  source line locators use newline-preserving comment stripping rather than
  stripped-text byte offsets.
- Mathematical-token changes: none in preserved Lean source or literal excerpts.
- Unresolved mathematical issues: none in the fixed-example formal concordance.
  General-modulus/polyphase/measurement interfaces remain explicitly out of scope.
- Validation: static concordance builder PASS; 96 unique theorem names and
  per-theorem archived axiom records; 96 physical source line matches against
  archived theorem index; five source hash and eleven check-log hash matches;
  all 96 theorem names included in guide inventory; Verbatim and longtable
  environments balanced.
- PDF layout validation: performed by the parent release build after wrapping
  this guide body. This self-review does not claim a PDF rendering pass.
- Fresh Lean execution: NOT_RUN; pinned runtime restoration failed with HTTP
  502 on all three documented materialization attempts. Archived source build
  and kernel replay remain separately identified.

Literal proof blocks are read from exact source windows by
`lean/build_guide_body.py`; the generator does not recreate or translate them.
