# Continue Komorebi Physics Lean v0.1.0

Read `README.md`, `docs/SOURCE_MAP.md`, `docs/FULL_EDITION_ROADMAP.md`, the complete declaration inventory, and `verification/final/report.json`.

## Verified starting point

- Source: the included 550-page full physics master, SHA recorded in `reference/source_manifest.json`.
- Fresh final run: PASS, 37 new + 39 preserved = 76 theorem declarations in seven active modules.
- Axiom audit: all 96 named declarations, only propext/Classical.choice/Quot.sound; four invalid controls rejected.
- New modules: Atlas, Transfer, Refinement, Examples.
- Preserved source: QuantumPacketCore, TensorRefinement, MovingFrames. All three are byte-identical to the recovered Paper VII v0.6.0 snapshot.
- Recovered portable compiler: Lean 4.34.0-rc2, exact Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06.

## Resume

Restore the portable kit from the seven `Lean_Offline_0N.zip` parts using `runtime_restore_support/assemble.py` if the current runtime is absent. Do not feed those Zstandard chunks to an XZ decoder. Run the supplied verifier against the actual restored kit before treating prior logs as current evidence.

Next target: Chapter 2.6, equations (2.50)–(2.57), whole-object deformation under a time-dependent invertible frame. Read physical PDF page 19 carefully. Reuse `MovingFrames.matrix_product_derivative` and the existing adjoint differentiation results where applicable. Keep the three product-rule terms and all inverse/regularity hypotheses explicit. Add new source-to-equation entries and recheck the cumulative active library.

## Do not change these boundaries

The fine atlas laws, skew condition and vector evolution law are hypotheses. Norm balance and coarse additivity are conclusions. The new theory uses finite atlases and globally defined bounded maps; it does not implement countable unbounded dynamics. Existing moving-frame coverage is finite-matrix. Do not claim the entire chapter, master, gravity sector or empirical physics complete. Preserve corrections to the historical additive dark-sector branch.

## One-line continuation prompt

“Open Komorebi_Physics_Lean_v0.1.0_Checked_Block_01.zip, read CONTINUE_HERE.md and the verified source map completely, restore the pinned portable Lean runtime, rerun the cumulative verifier, and prove the next literal full-edition block without weakening the stated hypotheses or importing the desired conclusion as an assumption.”
