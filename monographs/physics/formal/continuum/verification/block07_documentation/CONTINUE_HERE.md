# Continue Komorebi Physics Lean v0.7.0

Read AGENTS.md, README.md, STATUS.md, docs/BLOCK_07_PROOF_GUIDE.md, docs/BLOCK_07_DECLARATION_INDEX.md, docs/SOURCE_MAP.md, docs/CLAIM_LEDGER.json, docs/FULL_EDITION_ROADMAP.md, declaration_inventory.json and verification/final/report.json before editing. Read complete relevant manuscript pages, inspecting the actual page image wherever notation is ambiguous.

## Checkpoint and restore

The checked inventory is 572 theorems, 688 inventoried declarations, 34 mathematical modules and 50 invalid controls. Only a completed PASS audit confirms the checkpoint. Restore all seven checksum-matching portable parts using runtime_restore_support/assemble.py, or use an already restored exact-pin kit. One actual production kit was /mnt/data/lean_parts/Komorebi_Portable_Lean_4.34.0-rc2; a fresh container may differ.

Lean is 4.34.0-rc2 and Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06. Do not silently upgrade or replace dependencies. Restoration is local assembly/extraction, not remote fetching.

```bash
python3 scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --out verification/baseline
```

Use one worker, bounded per-module runs, and warnings as errors. The imported dependency cache is reused, not independently rebuilt wholesale. Recompile all local modules before describing a new cumulative checkpoint. Preserve current mathematical modules byte-for-byte, create a new preservation ledger for all 34 modules, and retain earlier preservation layers. Do not modify proof interfaces solely to make invalid controls pass.

## Immediate Block 08 target

Chapter 5.4, physical PDF page 28, printed page 15, equations (5.22)–(5.31): Parseval-channel realization and dilation. The source starts with bounded maps V_i:H→K_i satisfying sum_i V_i* V_i=I. Construct the resulting effects, then prove their Born probabilities equal ||V_i psi||². Prove actual state reconstruction and the double-sum channel-to-channel operator formula with the adjoint order unchanged. Construct the finite direct-sum analysis V, its isometry identity V*V=I, coordinate projectors Pi_i, and the compression F_i=V*Pi_i V.

Separate the given-Parseval-family theorem from any universal theorem constructing V_i from an arbitrary effect atlas. A universal factorization/dilation needs actual positive square roots or an alternative construction, with relevant Hilbert completeness and domain assumptions. Do not supply the desired compression identity as an input and then claim to have constructed it. Equation (5.32) is already checked by EffectAtlas.ofAtlas_current.

## Reusable current interfaces

`PositiveEffects`: EffectAtlas requires only positive Hermitian effects and sum identity. Its actual probability derivative, normalization, boundary flux and sharp-case bridge are available.

`MovingEffects`: hasDerivAt_effectExpectation differentiates the actual operator and vector arguments; differentiated_selfAdjoint and derivative_sum prove source reality/cancellation. Conjugation and actual commutator derivatives use K=dot(U)U*.

`EffectRefinement`: actual address-map effects, p^c=Rp, s^c=Rs, J^c=RJR^T, derivatives and associative coarsening.

`WeightedEffects`: fixed nonnegative real column-normalized weights produce a positive atlas. Probability/current/source formulas and composition are proved. Time-dependent weights are not covered.

`EffectExamples`: rational nonprojector effects, norm-one state, actual nonzero current, and globally positive scalar sine effects with nonzero moving source. Do not call the affine state curve a global solution or the scalar sine family a unitary orbit.

## Evidence and packaging

Update declaration_inventory.json, Audit.lean, aggregate, the verifier module/control inventory, source map and claim ledger. Audit every new proof-bearing definition as well as theorem declarations. A failure/timeout is never a theorem or a successful negative control. Preserve failed snapshots outside active modules. Only propext, Classical.choice and Quot.sound are permitted dependencies.

Re-run the cumulative verifier; package only after completed PASS using scripts/package_release.py. Then safely extract into a fresh directory and run scripts/recheck_archive.py, retaining the external archive-check JSON. Do not duplicate the multi-gigabyte runtime or share font files. Keep the original master manuscript and source hashes in the package.

## Boundaries

No ODE existence/uniqueness, initial-state positivity-preserving or completely positive semigroup, zero-population entropy extension, general-graph convergence rate, automatic coarse Markov model, quantum-relative-entropy theorem, infinite series/tower convergence, countable/unbounded/trace-class extension, full Chapter 3 inventory, gravitational/cosmological completion, or empirical validation has been supplied. Preserve corrected scale-covariant dark-sector bookkeeping rather than restoring rejected additive branches.

## One-line continuation prompt

Open `Komorebi_Physics_Lean_v0.7.0_Checked_Block_07.zip`, read `CONTINUE_HERE.md` completely, restore and freshly verify the 572-theorem checkpoint with the pinned portable Lean kit, preserve all active sources and proof boundaries, then prove the next Chapter 5.4 Parseval-channel realization and dilation block and deliver a cumulative audited ZIP.
