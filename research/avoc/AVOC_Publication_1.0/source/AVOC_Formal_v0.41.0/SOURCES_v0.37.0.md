# AVOC v0.37.0 source provenance

- Frozen cumulative source baseline: `AVOC_Formal_v0.35.0.zip`.
- Retained v0.36 specification documents: preserved under
  `history/v0.36.0_documentation_only/`; the corresponding full v0.36 source archive was not
  available in the workspace.
- New formal modules: `LazyStagedControl`, `LazyStagedRecovery`, `LazyStagedExamples`,
  `LazyStagedCodec`.
- New executable entrypoint and coordinator: `tools/LazyStagedMain.lean`,
  `tools/run_lazy_staged.py`, `tools/lazy_staged_workflow.py`.
- Toolchain and dependency pins are unchanged from the frozen baseline.
