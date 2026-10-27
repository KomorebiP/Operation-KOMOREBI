# Continue Komorebi Physics Lean v0.3.0

Read AGENTS.md, README.md, STATUS.md, docs/SOURCE_MAP.md, docs/BLOCK_03_PROOF_GUIDE.md, docs/FULL_EDITION_ROADMAP.md, declaration_inventory.json and verification/final/report.json before editing. Read the complete relevant source pages, not just a theorem-title snippet.

## Verified starting point

- Full 550-page source master included; SHA-256 `ea289c7c1bd2090296e4d436c9ef38b617066becc40cd33c44507f1386a61bc0`.
- Fresh cumulative PASS: 210 theorems, 263 audited named declarations, 15 mathematical modules, 15 correctly rejected invalid controls.
- Counts: 83 Block 03 + 51 Block 02 + 37 Block 01 + 39 recovered Paper VII theorems.
- All ten Block 02 mathematical source files are byte-identical and preservation is checked automatically.
- Five new modules: NonlinearFlow, RefinementTower, MixedTransfer, UniversalBalance, ExtensionExamples.
- Lean 4.34.0-rc2; Mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.

## Restore and rerun

Use the exact existing kit when available. Otherwise restore the seven `Lean_Offline_0N.zip` parts with `runtime_restore_support/assemble.py`. The pieces contain Zstandard chunks, not XZ. The source ZIP does not contain those multi-gigabyte runtime parts.

The production kit path was `/mnt/data/lean_parts/Komorebi_Portable_Lean_4.34.0-rc2`; treat that as a historical location, not an assurance about a new runtime. Run:

```bash
bash run_checks.sh /actual/path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

Cumulative verification takes longer than one short outer tool command. Use a supervised process/log and inspect the completed report rather than miscounting an interrupted run. Every module and every axiom batch must pass. The verifier itself uses sequential bounded commands, deletes local build outputs and checks complete inventories.

## Next literal block

Read physical master page 24 (printed 11), Chapter 4.4, equations (4.23)–(4.28). Construct the tensor-product `MixedTransfer.MatrixAtlas` using the actual matrix tensor/Kronecker product. Prove the projector laws, joint probabilities for general joint density matrices, and both marginal trace identities. Existing recovered tensor algebra is useful but is not the whole mixed-state result. Do not replace an arbitrary joint state with a product-state-only witness.

Then read physical page 25 (printed 12), Chapter 4.6, equations (4.35)–(4.44). Derive actual entropy, power-sum and Rényi derivatives from actual probability derivatives and antisymmetric current. Make strict positivity and q≠1 explicit where needed. Keep logarithmic and real-power domain restrictions precise; do not turn a claimed entropy identity into an assumption.

Next read Chapter 4.7, (4.45)–(4.52): derive the diagonal population equation from the actual Lindblad generator and rank-one jump matrices. Track square-root rates, anticommutator factors, off-diagonal assumptions, index orientation and nonnegative rates.

## Reuse and API notes

`NonlinearFlow` evaluates a state-dependent skew generator along the actual trajectory. `RefinementTower.push_comp` handles distinct finite label spaces; `pushList_eq` handles arbitrary depth on one fixed label type. Matrix interpretation of `aggregateCurrent` requires actual incidence when claiming a coarse atlas.

`MixedTransfer.MatrixAtlas` contains fine projector laws and Hermiticity, not desired continuity fields. `hasDerivAt_trace_mul` and `hasDerivAt_entry` give actual differentiation. `probability_cast` supplies the literal complex trace under Hermiticity. `amplitude_reverse` has the essential conjugation, as confirmed by the source image. `probability_normalized` requires PSD and trace one. `coarsen` is a proof-bearing construction.

The pinned Lean module system may need `import all TensorRefinement` for unfolding its recovered coarse definition. Matrix function representations sometimes need `Matrix.of` or an explicit `change`. Use `open scoped Matrix ComplexOrder` for matrix notation and the complex PSD order; concrete matrix norm calculations can use `Mathlib.Analysis.Matrix.Normed` with `Matrix.Norms.Elementwise`. Do not rewrite globally by antisymmetry with `simp_rw`: it can loop. The retained development logs record these repaired failures.

## Boundaries to preserve

Pure-state analytic results allow arbitrary-dimensional complex inner-product/Hilbert spaces with bounded globally defined operators and finite atlases. Mixed-state results here are finite matrices. Neither gives countable sums, unbounded domains or trace-class limits for free.

All-time conservation assumes an actual all-time trajectory. No solution existence/uniqueness or initial-density positivity-preservation theorem is present. The affine exact example solves the matrix equation at zero only. The universal scalar-balance layer explicitly assumes scalar balance; the quantum layers derive it from microscopic derivatives.

Chapter 3's physical units, variational statements and asymptotics remain separately unmapped. Later gravity/cosmology claims are not certified by the core algebra. Preserve the corrected dark-sector branch and supersession notes. Do not invent a full-edition completion percentage or claim empirical validation.

## One-line continuation

“Open Komorebi_Physics_Lean_v0.3.0_Checked_Block_03.zip, read CONTINUE_HERE.md and the source map completely, restore and rerun the pinned cumulative verifier, then prove the next literal tensor-marginal/information-transport block while preserving all finite/countable, bounded/unbounded, partition/overlap, assumed-flow/proved-balance, positivity and mathematical/empirical boundaries.”
