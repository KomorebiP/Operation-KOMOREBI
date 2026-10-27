# Proof ledger — v0.35

All entries are checked as written. The arithmetic/global exclusions in RESEARCH_BOUNDARY.md remain in force. Counts include helpers and examples.

## FrobeniusNormRigidity.lean

- `theorem Komorebi.StrongArtin.FrobeniusTower.power_fibre_injective` (line 12)
- `theorem Komorebi.StrongArtin.FrobeniusTower.exists_unique_power_lift` (line 25)
- `def Komorebi.StrongArtin.FrobeniusTower.adjoint` (line 47)
- `def Komorebi.StrongArtin.FrobeniusTower.Nonresonant` (line 54)
- `theorem Komorebi.StrongArtin.FrobeniusTower.nonresonant_of_unipotent_adjoint` (line 58)
- `theorem Komorebi.StrongArtin.FrobeniusTower.adjoint_one` (line 64)
- `theorem Komorebi.StrongArtin.FrobeniusTower.nonresonant_identity` (line 68)

## MixedCharacteristicUniqueStep.lean

- `theorem Komorebi.StrongArtin.FrobeniusTower.conjugate_power_coord` (line 11)
- `theorem Komorebi.StrongArtin.FrobeniusTower.layer_norm_coordinates` (line 20)
- `theorem Komorebi.StrongArtin.FrobeniusTower.layer_norm_bijective` (line 34)
- `theorem Komorebi.StrongArtin.FrobeniusTower.mixed_unique_power_lift` (line 51)

## PrimePowerCoefficientTower.lean

- `def Komorebi.StrongArtin.FrobeniusTower.modulus` (line 8)
- `theorem Komorebi.StrongArtin.FrobeniusTower.modulus_zero` (line 12)
- `theorem Komorebi.StrongArtin.FrobeniusTower.modulus_succ` (line 14)
- `theorem Komorebi.StrongArtin.FrobeniusTower.modulus_eq_pow` (line 15)
- `theorem Komorebi.StrongArtin.FrobeniusTower.prime_dvd_modulus` (line 22)
- `theorem Komorebi.StrongArtin.FrobeniusTower.modulus_ne_zero` (line 26)
- `abbrev Komorebi.StrongArtin.FrobeniusTower.Coeff` (line 33)
- `abbrev Komorebi.StrongArtin.FrobeniusTower.MatrixUnits` (line 35)
- `def Komorebi.StrongArtin.FrobeniusTower.coefficientDown` (line 37)
- `def Komorebi.StrongArtin.FrobeniusTower.coefficientResidue` (line 40)
- `theorem Komorebi.StrongArtin.FrobeniusTower.coefficientResidue_zero` (line 43)
- `theorem Komorebi.StrongArtin.FrobeniusTower.coefficientResidue_down` (line 47)
- `def Komorebi.StrongArtin.FrobeniusTower.down` (line 53)
- `def Komorebi.StrongArtin.FrobeniusTower.red` (line 56)
- `theorem Komorebi.StrongArtin.FrobeniusTower.red_zero` (line 59)
- `theorem Komorebi.StrongArtin.FrobeniusTower.red_down` (line 66)
- `theorem Komorebi.StrongArtin.FrobeniusTower.layer_residualFrobenius` (line 73)
- `theorem Komorebi.StrongArtin.FrobeniusTower.unique_next_root` (line 82)

## CompatibleFrobeniusRoots.lean

- `abbrev Komorebi.StrongArtin.FrobeniusTower.Compatible` (line 10)
- `theorem Komorebi.StrongArtin.FrobeniusTower.unique_root_at_every_level` (line 14)
- `theorem Komorebi.StrongArtin.FrobeniusTower.exists_unique_compatible_root_tower` (line 37)
- `theorem Komorebi.StrongArtin.FrobeniusTower.unipotent_adjoint_unique_tower` (line 60)
- `theorem Komorebi.StrongArtin.FrobeniusTower.identity_residue_unique_tower` (line 70)

## PadicMatrixTowerLimit.lean

- `def Komorebi.StrongArtin.FrobeniusTower.padicCoefficient` (line 11)
- `def Komorebi.StrongArtin.FrobeniusTower.integralRepresentatives` (line 13)
- `theorem Komorebi.StrongArtin.FrobeniusTower.representative_compatibility` (line 17)
- `def Komorebi.StrongArtin.FrobeniusTower.scalarLimit` (line 34)
- `theorem Komorebi.StrongArtin.FrobeniusTower.scalarLimit_spec` (line 39)
- `theorem Komorebi.StrongArtin.FrobeniusTower.padicCoefficient_ext` (line 53)
- `theorem Komorebi.StrongArtin.FrobeniusTower.padicCoefficient_down` (line 61)
- `def Komorebi.StrongArtin.FrobeniusTower.matrixLimit` (line 72)
- `theorem Komorebi.StrongArtin.FrobeniusTower.matrixLimit_spec` (line 77)
- `theorem Komorebi.StrongArtin.FrobeniusTower.padicMatrix_ext` (line 83)
- `def Komorebi.StrongArtin.FrobeniusTower.padicUnitReduction` (line 90)
- `theorem Komorebi.StrongArtin.FrobeniusTower.padicUnitReduction_compatible` (line 93)
- `theorem Komorebi.StrongArtin.FrobeniusTower.padicUnit_ext` (line 100)
- `theorem Komorebi.StrongArtin.FrobeniusTower.unitValues_compatible` (line 109)
- `theorem Komorebi.StrongArtin.FrobeniusTower.unitInverses_compatible` (line 115)
- `def Komorebi.StrongArtin.FrobeniusTower.unitLimit` (line 122)
- `theorem Komorebi.StrongArtin.FrobeniusTower.unitLimit_spec` (line 136)

## PadicFrobeniusRoot.lean

- `theorem Komorebi.StrongArtin.FrobeniusTower.exists_unique_padic_frobenius_root` (line 8)
- `theorem Komorebi.StrongArtin.FrobeniusTower.identity_residue_unique_padic_root` (line 35)
- `theorem Komorebi.StrongArtin.FrobeniusTower.unipotent_adjoint_unique_padic_root` (line 43)

## SimultaneousPadicFrobenius.lean

- `theorem Komorebi.StrongArtin.FrobeniusTower.padic_power_injective_on_residue` (line 8)
- `theorem Komorebi.StrongArtin.FrobeniusTower.simultaneous_padic_roots_iff` (line 19)
- `theorem Komorebi.StrongArtin.FrobeniusTower.identity_family_padic_roots_iff` (line 46)

## FrobeniusTowerControls.lean

- `abbrev Komorebi.StrongArtin.FrobeniusTower.Controls.k` (line 7)
- `abbrev Komorebi.StrongArtin.FrobeniusTower.Controls.n` (line 9)
- `def Komorebi.StrongArtin.FrobeniusTower.Controls.unipotent` (line 10)
- `theorem Komorebi.StrongArtin.FrobeniusTower.Controls.unipotent_adjoint_cube` (line 18)
- `theorem Komorebi.StrongArtin.FrobeniusTower.Controls.unipotent_unique_padic_square_root` (line 24)
- `def Komorebi.StrongArtin.FrobeniusTower.Controls.reduce27to9` (line 31)
- `def Komorebi.StrongArtin.FrobeniusTower.Controls.reduce9to3` (line 33)
- `theorem Komorebi.StrongArtin.FrobeniusTower.Controls.partial_cube_branch` (line 34)
- `theorem Komorebi.StrongArtin.FrobeniusTower.Controls.partial_branch_has_no_next_lift` (line 36)
- `theorem Komorebi.StrongArtin.FrobeniusTower.Controls.no_padic_cube_root_above_four` (line 41)
- `theorem Komorebi.StrongArtin.FrobeniusTower.Controls.target_has_a_different_full_root` (line 52)

