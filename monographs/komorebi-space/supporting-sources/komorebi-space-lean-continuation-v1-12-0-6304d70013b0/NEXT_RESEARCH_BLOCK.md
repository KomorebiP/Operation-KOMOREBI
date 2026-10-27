# Next Lean block: the infinite diagonal model

This is a restart contract. The current accepted checkpoint must be read from the final ledger before relying on its new WR15 proofs. The remaining principal groups are WR10–WR12. Their printed source is frozen in `records/targets/05i_diagonal_regularization.tex`.

## First target: WR10

Work in the actual real ℓ² Hilbert space with coordinates indexed by positive integers. Define the bounded diagonal operator (Tu)ₙ = uₙ/n and the datum wₙ = 1/n. Construct their Hilbert-space membership and operator properties, including the adjoint and norm. For every integer m ≥ 1, construct aₙ = m²/(m²+n²) and vₙ = n/(m²+n²). Prove membership in ℓ² and the infinite-vector normal equation at α = m⁻². Use the accepted regularization theorem to identify the unique optimizer.

Prove the actual infinite sums Aₘ = ‖a‖² and Bₘ = ‖v‖² satisfy m/4 ≤ Aₘ ≤ 4m/3 and 1/[4(m+1)] ≤ Bₘ ≤ 2/m. For every integer K ≥ m, retain the nonnegative tails and exact bounds Aₘ − Aₘ,ₖ ≤ m⁴/(3K³) and Bₘ − Bₘ,ₖ ≤ 1/K. Finite truncation calculations cannot substitute for the Hilbert membership, optimizer identity or infinite-sum estimates.

First executable step: inspect the pinned mathlib ℓ² and diagonal multiplication APIs, then choose one positive-index convention and prove the bounded self-adjoint operator plus datum membership. Freeze that convention before parallelizing tail estimates and normal-equation proofs.

## Subsequent targets

| Group | Complete obligation |
| --- | --- |
| WR11 | Aₘ/m → π/4 and mBₘ → π/4, with justified infinite Riemann sums or an equivalent rigorous route. Prove M β(M) → π/4 for every large real budget, using the actual infinite problem. Retain the hard-prefix comparison constant 1. |
| WR12 | Construct the attainable datum bₙ = 1/n² and its minimum-norm preimage 1/n. Identify the squared bias norm with Bₘ. For 0 < δ ≤ 1 and m = ⌈δ⁻²ᐟ³⌉, prove the two-stage bound √(2/m) + δm/2 ≤ (√2+1)δ¹ᐟ³ for the noisy correction, with the integer rounding fully accounted for. |

The accepted WR08 limits and WR09/WR16 noise and stopping-rule theorems provide general infrastructure. They do not supply the explicit diagonal formulas, tail constants or rates. The inexact-solver extension of the diagonal rate is adjacent work and must not be silently counted as a completed principal WR12 theorem without its own statement check.

## Continuation discipline

Retain the accepted parent unchanged and add source modules. Preserve failed attempts with exact source, command, environment and diagnostics. Promote coverage only after strict cumulative replay, full new types, all-declaration axiom checks, meaningful controls and independent statement review. Keep partial lemmas distinct from completion of each numbered group.

The monograph PDF is still the historical v1.10.0 publication. Updating its status notes and companion guides is a separate publication pass after the Lean checkpoint is accepted. A whole-monograph proof audit and refinement of executable numerical certificates also remain separate.
