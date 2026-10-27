# Continue Komorebi Physics Lean v0.4.0

Read AGENTS.md, README.md, STATUS.md, docs/SOURCE_MAP.md, docs/BLOCK_04_PROOF_GUIDE.md, docs/FULL_EDITION_ROADMAP.md, declaration_inventory.json and verification/final/report.json before editing. Read the full relevant source pages, not only snippets.

## Checkpoint

The completed cumulative verifier must report PASS: **304 theorems, 372 audited named declarations, 20 mathematical modules, 23 negative controls**. Counts are 94 Block 04 + 83 Block 03 + 51 Block 02 + 37 Block 01 + 39 recovered Paper VII. All 15 preceding mathematical modules are byte-preserved. The five new modules are TensorAtlas, PartialTrace, InformationTransport, EntanglementWitness and QuantumInformationExamples.

The full 550-page master is in reference/, SHA-256 `ea289c7c1bd2090296e4d436c9ef38b617066becc40cd33c44507f1386a61bc0`. Toolchain: Lean 4.34.0-rc2; Mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.

## Restore and rerun

Reuse the exact kit when available. Otherwise restore all seven `Lean_Offline_0N.zip` parts with `runtime_restore_support/assemble.py`. They contain Zstandard chunks, not XZ. The source ZIP contains restoration support, not the multi-gigabyte runtime pieces.

Historical production kit: `/mnt/data/lean_parts/Komorebi_Portable_Lean_4.34.0-rc2`. Establish the actual current path; do not assume it persists across chats.

```bash
bash run_checks.sh /actual/path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

Use supervised bounded command batches and inspect the final report. An outer tool-call timeout is not a failed mathematical theorem, nor proof of completion. Never count a process that has not finished. The verifier removes local outputs, recompiles everything, and audits all names.

## Next literal block: Lindblad reduction

Read physical PDF page 25 (printed 12), Chapter 4.7, equations (4.45)–(4.52), including the rendered source image. Construct actual jump matrices

    L_ab = sqrt(gamma_ab) |a><b|,     gamma_ab ≥ 0.

Define the actual Lindblad matrix generator as the sum over distinct ordered indices of

    L_ab rho L_ab* - (1/2)(L_ab* L_ab rho + rho L_ab* L_ab).

First prove the one-jump gain and loss formulas directly from entries. Then derive the population equation

    p_a' = ∑ b, (gamma_ab p_b - gamma_ba p_a)

from the **original matrix HasDerivAt hypothesis**, not by defining the population derivative to be the desired expression. Prove the antisymmetric current and total cancellation. Allow general density matrices with off-diagonal coherence; diagonal-only examples are not the full claim. Keep the a←b orientation and explain why the diagonal rate terms cancel even though the source generator excludes self-jumps.

Use exact nonnegative-rate witnesses and negative controls detecting a missing anticommutator half, reversed source/target, omitted loss, and incorrect square-root scaling. Applying Block 04's information formulas to an actually proved population balance is a useful next bridge. Do not claim entropy monotonicity for general rates without additional hypotheses.

After the literal reduction, read the next source pages before choosing Chapter 5 work. ODE existence and positivity preservation from initial data remain distinct obligations; a trace-zero generator is not a positivity proof.

## Reusable interfaces

`MixedTransfer.MatrixAtlas` contains fine projector laws and Hermiticity. It does not contain assumed continuity or probability conclusions. `MixedTransfer.hasDerivAt_entry` and `hasDerivAt_trace_mul` derive actual derivatives from the original matrix curve. `probability_cast` matches the real-valued representation to the literal trace under Hermiticity.

`MatrixAtlas.tensor` is a proof-bearing constructed Kronecker atlas. `tensor_marginal_left_trace` and the right version accept arbitrary joint matrices. `PartialTrace.left/right` are actual entrywise sums; `left/right_posSemidef` and `hasDerivAt_left/right` are independently proved. Local multiplication and remote cyclicity lemmas are available without replacing general joint states by products.

`InformationTransport.hasDerivAt_functional` supplies a general current chain rule. The entropy, real-power and Rényi theorems assume actual scalar balance at the abstract interface; `MatrixAtlas.hasDerivAt_packet_*` discharge that from von Neumann flow. Strict positivity is required. Rényi additionally needs a nonempty packet type and q≠1.

`EntanglementWitness.HasFiniteProductDecomposition` is explicitly a finite nonnegative sum of pure product matrices. Its positive-partial-transpose consequence is proved. The Bell example excludes all such representations with an exact negative quadratic pairing; do not weaken this to merely nonproduct while also not claiming unproved abstract equivalences.

Pinned API notes: use scope `Kronecker`; `Matrix.mul_kronecker_mul` has the collapse orientation opposite a product of two Kronecker matrices. `hasDerivAt_pi` needs `Mathlib.Analysis.Calculus.Deriv.Prod`. Complex conjugate sums simplify with `star_sum`; dependent deltas may need `Finset.sum_ite_irrel` before sum_ite_eq. Explicit `change` helps normalize derivatives of function multiplication. Never globally rewrite both orientations of antisymmetry in a simplifier loop. Failed and repaired attempts are retained.

## Boundaries

Keep all 20 current mathematical files unchanged in the next release unless a correction is explicitly justified and documented. Preserve the prior manifests, provenance and declaration identities.

The tensor/reduced-state layer is finite matrices. Earlier bounded pure-state theorems may have infinite-dimensional ambient spaces, but that does not supply countable sums, unbounded domains or infinite-dimensional partial traces. No initial-density positivity-preservation theorem is present. Packet entropy is not von Neumann entropy; antisymmetric balance gives no universal production sign. Zero-probability and q=1 limits remain unproved.

Chapter 3 has not been completely inventoried. Later gravity/cosmology claims and empirical agreement are not certified by these core identities. Preserve the corrected dark-sector branch and supersession notes. Do not invent a full-edition completion percentage.

## One-line continuation

“Open Komorebi_Physics_Lean_v0.4.0_Checked_Block_04.zip, read CONTINUE_HERE.md and the source map completely, restore and rerun the pinned cumulative verifier, then derive the literal Lindblad packet-jump block from the actual matrix generator while preserving every proof boundary and all checked source files.”
