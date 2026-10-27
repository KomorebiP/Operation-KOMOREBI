# Finitely generated rational subgroups: checked return

Owner: `/root/reachability`. Parent: checked Lean v0.6.0 archive SHA-256 `032f61f0e176f0f3abfeb3615b8936ebd9edb7c3f9a07b6b8ad25877ec7aef70`.

Production artifact: `RealizationBoundaries/RationalFG.lean`.
Source SHA-256: `e4e8b760d90286f1e43f73e8bf1a2bb041120a8f0fd752ed9f0aa07b0b0163aa`.

## Results

- `finite_rationals_common_cyclic_lattice`: every actual finite set `s : Finset ℚ` lies in `zmultiples (1/d)` for an explicitly witnessed positive common denominator `d`, the product of its denominators.
- `rational_subgroup_fg_isAddCyclic (H : AddSubgroup ℚ) (hH : H.FG) : IsAddCyclic H`.
- `rational_fg_isAddCyclic (H : AddSubgroup ℚ) [AddGroup.FG H] : IsAddCyclic H`.
- `rational_fg_equiv_int (H : AddSubgroup ℚ) [AddGroup.FG H] (hH : H ≠ ⊥) : Nonempty (H ≃+ ℤ)`.
- `rational_fg_generator (H : AddSubgroup ℚ) [AddGroup.FG H] : ∃ q : H, Function.Surjective (fun n : ℤ => n • q)`.

The common denominator proof embeds the subgroup into an actual cyclic rational lattice, so its subgroup cyclicity follows. The nonzero branch uses ordered additive cyclic group classification. The zero subgroup case is preserved for the cyclicity and generator statements. This module supplies the rational-image dependency for exact monograph 5.5; it does not by itself classify arbitrary finitely generated subgroups of the selector groups.

## Verification

- `verification/development/RationalFG_003.json`: compiler exit 0, warnings as errors, autoImplicit false, 2.10 seconds, final source hash above.
- `verification/development/RationalFG_replay.log`: kernel replay exit 0.
- `verification/development/RationalFG_contract.log`: exact theorem types and allowed axiom check exit 0.
- `rational_fg_equiv_int` depends only on `propext`, `Classical.choice`, `Quot.sound`.
- Preliminary compilations 001–002 are development failures (one algebraic rewrite, an ordered-subgroup import, and the current Lean local-instance proof style linter). All are corrected in 003.

The structural owner was notified and is integrating the exact 5.5 wrapper. Add `RationalFG` before the structural module in root imports and the serial build/replay list.
