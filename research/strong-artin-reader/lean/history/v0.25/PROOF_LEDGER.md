# Proof ledger — Strong Artin v0.25

Evidence: fresh 17-source-module replay plus an all-new-constant axiom audit.
Every result has the hypotheses in its Lean statement. Arithmetic instantiation is not supplied.

## ResidualLayer

- `structure` `Komorebi.StrongArtin.ResidualLayer.Reduction` (source line 14).
- `def` `Komorebi.StrongArtin.ResidualLayer.FaithfulAt` (source line 21).
- `theorem` `Komorebi.StrongArtin.ResidualLayer.Reduction.map_pi_smul` (source line 27).
- `theorem` `Komorebi.StrongArtin.ResidualLayer.Reduction.map_eq_of_difference_divisible` (source line 31).
- `theorem` `Komorebi.StrongArtin.ResidualLayer.Reduction.scaled_error_raises_one` (source line 37).
- `theorem` `Komorebi.StrongArtin.ResidualLayer.Reduction.leading_residue_unique` (source line 43).
- `theorem` `Komorebi.StrongArtin.ResidualLayer.Reduction.faithfulAt_of_injective_smul` (source line 50).
- `def` `Komorebi.StrongArtin.ResidualLayer.coordinateReduction` (source line 70).
- `theorem` `Komorebi.StrongArtin.ResidualLayer.coordinateReduction_apply` (source line 107).

## MovingSyzygyError

- `theorem` `Komorebi.StrongArtin.MovingSyzygyError.normalized_error_compatible` (source line 14).
- `theorem` `Komorebi.StrongArtin.MovingSyzygyError.normalized_error_compatible_of_relation_congruence` (source line 30).
- `theorem` `Komorebi.StrongArtin.MovingSyzygyError.unnormalized_error_satisfies_next_order_relation` (source line 47).

## GradedCompatibleHensel

- `theorem` `Komorebi.StrongArtin.GradedCompatibleHensel.next_order_of_normalized_error_in_range` (source line 22).
- `theorem` `Komorebi.StrongArtin.GradedCompatibleHensel.next_order_of_exact_moving_relations` (source line 52).
- `theorem` `Komorebi.StrongArtin.GradedCompatibleHensel.next_order_of_dual_kernel_compatibility` (source line 75).
- `theorem` `Komorebi.StrongArtin.GradedCompatibleHensel.exists_approximation_to_finite_order` (source line 94).
- `theorem` `Komorebi.StrongArtin.GradedCompatibleHensel.exists_exact_root_from_graded_compatibility` (source line 128).

## TruncatedUniformizerLayer

- `theorem` `Komorebi.StrongArtin.TruncatedUniformizerLayer.residue_zero_of_killed_by_power` (source line 11).
- `theorem` `Komorebi.StrongArtin.TruncatedUniformizerLayer.coordinate_reduction_faithful` (source line 34).

## PolynomialResidueModel

- `def` `Komorebi.StrongArtin.PolynomialResidueModel.reduceExpr` (source line 16).
- `theorem` `Komorebi.StrongArtin.PolynomialResidueModel.eval_reduceExpr` (source line 23).
- `theorem` `Komorebi.StrongArtin.PolynomialResidueModel.deriv_reduceExpr` (source line 32).
- `def` `Komorebi.StrongArtin.PolynomialResidueModel.reduceSystem` (source line 43).
- `theorem` `Komorebi.StrongArtin.PolynomialResidueModel.derivative_residue_comparison` (source line 46).
- `def` `Komorebi.StrongArtin.PolynomialResidueModel.relationMap` (source line 63).
- `def` `Komorebi.StrongArtin.PolynomialResidueModel.reduceRelations` (source line 80).
- `theorem` `Komorebi.StrongArtin.PolynomialResidueModel.relation_residue_comparison` (source line 83).

## PrincipalResidueFaithfulness

- `theorem` `Komorebi.StrongArtin.PrincipalResidueFaithfulness.isUnit_of_nonzero_residue` (source line 13).
- `theorem` `Komorebi.StrongArtin.PrincipalResidueFaithfulness.residue_zero_of_nonterminal_power_kills` (source line 30).
- `theorem` `Komorebi.StrongArtin.PrincipalResidueFaithfulness.coordinate_faithful_of_nonterminal_power` (source line 43).

## PolynomialMovingSyzygyHensel

- `theorem` `Komorebi.StrongArtin.PolynomialMovingSyzygyHensel.exists_exact_root_of_moving_polynomial_relations` (source line 23).
- `theorem` `Komorebi.StrongArtin.PolynomialMovingSyzygyHensel.exists_exact_root_over_truncated_regular_coefficients` (source line 61).
- `theorem` `Komorebi.StrongArtin.PolynomialMovingSyzygyHensel.exists_exact_root_over_principal_nilpotent_residue` (source line 96).

## SquareZeroRepresentationDefect

- `def` `Komorebi.StrongArtin.SquareZeroRepresentationDefect.defect` (source line 13).
- `def` `Komorebi.StrongArtin.SquareZeroRepresentationDefect.relation` (source line 16).
- `def` `Komorebi.StrongArtin.SquareZeroRepresentationDefect.correction` (source line 20).
- `def` `Komorebi.StrongArtin.SquareZeroRepresentationDefect.perturb` (source line 24).
- `theorem` `Komorebi.StrongArtin.SquareZeroRepresentationDefect.associativity_identity` (source line 27).
- `theorem` `Komorebi.StrongArtin.SquareZeroRepresentationDefect.defect_perturb` (source line 33).
- `theorem` `Komorebi.StrongArtin.SquareZeroRepresentationDefect.relation_correction` (source line 40).
- `theorem` `Komorebi.StrongArtin.SquareZeroRepresentationDefect.defect_maps_to_zero` (source line 48).
- `theorem` `Komorebi.StrongArtin.SquareZeroRepresentationDefect.relation_independent_of_coefficient_lifts` (source line 55).
- `theorem` `Komorebi.StrongArtin.SquareZeroRepresentationDefect.correction_satisfies_relation` (source line 70).
- `theorem` `Komorebi.StrongArtin.SquareZeroRepresentationDefect.defect_perturb_of_square_zero` (source line 81).
- `theorem` `Komorebi.StrongArtin.SquareZeroRepresentationDefect.representation_lift_iff_defect_correctable` (source line 91).

## GradedCompatibilityExamples

- `def` `Komorebi.StrongArtin.GradedCompatibilityExamples.quadraticSystem` (source line 19).
- `def` `Komorebi.StrongArtin.GradedCompatibilityExamples.quadraticRelations` (source line 24).
- `theorem` `Komorebi.StrongArtin.GradedCompatibilityExamples.quadratic_exact_moving_identity` (source line 27).
- `theorem` `Komorebi.StrongArtin.GradedCompatibilityExamples.quadratic_residual_exactness` (source line 33).
- `theorem` `Komorebi.StrongArtin.GradedCompatibilityExamples.exists_redundant_quadratic_root` (source line 71).
- `theorem` `Komorebi.StrongArtin.GradedCompatibilityExamples.normalized_error_repairs_fixed_target_failure` (source line 95).
- `theorem` `Komorebi.StrongArtin.GradedCompatibilityExamples.square_plus_one_has_no_root_mod_four` (source line 102).
- `theorem` `Komorebi.StrongArtin.GradedCompatibilityExamples.residual_identity_relation_does_not_lift` (source line 107).

## IntrinsicGradedLiftingCapstone

- `theorem` `Komorebi.StrongArtin.IntrinsicGradedLiftingCapstone.image_eq_relation_kernel_of_dual_exactness` (source line 21).
- `theorem` `Komorebi.StrongArtin.IntrinsicGradedLiftingCapstone.exists_exact_root_from_syzygy_corrected_dual_exactness` (source line 35).

## Count and boundary

42 theorems, 12 definitions and one structure, in 10 new modules and 937 source lines.
The 55 named constants were audited. Only propext, Classical.choice and Quot.sound occur.
There is no claim of a new unconditional Langlands case, a continuous H2 theorem, or universal arithmetic compatibility.
