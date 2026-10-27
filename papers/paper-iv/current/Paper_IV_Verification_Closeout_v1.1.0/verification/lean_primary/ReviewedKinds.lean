import KomorebiPaperIV
open Lean Elab Command
set_option maxRecDepth 10000
run_cmd do
  let env ← getEnv
  match env.find? ``Komorebi.PaperIV.cyclicProjector with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.cyclicProjector"
  match env.find? ``Komorebi.PaperIV.coeff_cyclicProjector with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.coeff_cyclicProjector"
  match env.find? ``Komorebi.PaperIV.cyclicProjector_eq_zero_of_residue_ne with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.cyclicProjector_eq_zero_of_residue_ne"
  match env.find? ``Komorebi.PaperIV.cyclicProjector_eq_of_mod_eq with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.cyclicProjector_eq_of_mod_eq"
  match env.find? ``Komorebi.PaperIV.cyclicProjector_idempotent with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.cyclicProjector_idempotent"
  match env.find? ``Komorebi.PaperIV.cyclicProjector_orthogonal with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.cyclicProjector_orthogonal"
  match env.find? ``Komorebi.PaperIV.sum_cyclicProjector with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.sum_cyclicProjector"
  match env.find? ``Komorebi.PaperIV.cyclicProjector_add with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.cyclicProjector_add"
  match env.find? ``Komorebi.PaperIV.cyclicProjector_sum with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.cyclicProjector_sum"
  match env.find? ``Komorebi.PaperIV.cyclicProjector_product_packet with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.cyclicProjector_product_packet"
  match env.find? ``Komorebi.PaperIV.cyclicProjector_product_other with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.cyclicProjector_product_other"
  match env.find? ``Komorebi.PaperIV.cyclic_product_law with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.cyclic_product_law"
  match env.find? ``Komorebi.PaperIV.finiteRootAverage with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.finiteRootAverage"
  match env.find? ``Komorebi.PaperIV.coeff_finiteRootAverage with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.coeff_finiteRootAverage"
  match env.find? ``Komorebi.PaperIV.finiteRootAverage_eq_cyclicProjector with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.finiteRootAverage_eq_cyclicProjector"
  match env.find? ``Komorebi.PaperIV.exponentialGeneratingSeries with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.exponentialGeneratingSeries"
  match env.find? ``Komorebi.PaperIV.coeff_exponentialGeneratingSeries with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.coeff_exponentialGeneratingSeries"
  match env.find? ``Komorebi.PaperIV.transferSectionCoeff with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.transferSectionCoeff"
  match env.find? ``Komorebi.PaperIV.transferSection with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.transferSection"
  match env.find? ``Komorebi.PaperIV.coeff_transferSection with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.coeff_transferSection"
  match env.find? ``Komorebi.PaperIV.finiteRootAverage_exp_eq_transferSection with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.finiteRootAverage_exp_eq_transferSection"
  match env.find? ``Komorebi.PaperIV.finiteRootAverage_rescale_exp_eq_transferSection with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.finiteRootAverage_rescale_exp_eq_transferSection"
  match env.find? ``Komorebi.PaperIV.derivative_exponentialGeneratingSeries with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.derivative_exponentialGeneratingSeries"
  match env.find? ``Komorebi.PaperIV.iterate_derivative_exponentialGeneratingSeries with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.iterate_derivative_exponentialGeneratingSeries"
  match env.find? ``Komorebi.PaperIV.transferSectionCoeff_succ_of_pos with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.transferSectionCoeff_succ_of_pos"
  match env.find? ``Komorebi.PaperIV.transferSectionCoeff_succ_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.transferSectionCoeff_succ_zero"
  match env.find? ``Komorebi.PaperIV.derivative_transferSection_of_pos with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.derivative_transferSection_of_pos"
  match env.find? ``Komorebi.PaperIV.derivative_transferSection_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.derivative_transferSection_zero"
  match env.find? ``Komorebi.PaperIV.transferSectionCoeff_add_period with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.transferSectionCoeff_add_period"
  match env.find? ``Komorebi.PaperIV.iterate_derivative_transferSection with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.iterate_derivative_transferSection"
  match env.find? ``Komorebi.PaperIV.constantCoeff_iterate_derivative_transferSection with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.constantCoeff_iterate_derivative_transferSection"
  match env.find? ``Komorebi.PaperIV.signedSectionCoeff with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedSectionCoeff"
  match env.find? ``Komorebi.PaperIV.signedSection with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedSection"
  match env.find? ``Komorebi.PaperIV.coeff_signedSection with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.coeff_signedSection"
  match env.find? ``Komorebi.PaperIV.signedSection_eq_inv_pow_mul_transferSection with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedSection_eq_inv_pow_mul_transferSection"
  match env.find? ``Komorebi.PaperIV.signedSectionCoeff_succ_of_pos with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedSectionCoeff_succ_of_pos"
  match env.find? ``Komorebi.PaperIV.signedSectionCoeff_succ_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedSectionCoeff_succ_zero"
  match env.find? ``Komorebi.PaperIV.derivative_signedSection_of_pos with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.derivative_signedSection_of_pos"
  match env.find? ``Komorebi.PaperIV.derivative_signedSection_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.derivative_signedSection_zero"
  match env.find? ``Komorebi.PaperIV.signedSectionCoeff_add_period with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedSectionCoeff_add_period"
  match env.find? ``Komorebi.PaperIV.iterate_derivative_signedSection with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.iterate_derivative_signedSection"
  match env.find? ``Komorebi.PaperIV.constantCoeff_iterate_derivative_signedSection with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.constantCoeff_iterate_derivative_signedSection"
  match env.find? ``Komorebi.PaperIV.signedSection_eq_finiteRootAverage_rescale_exp with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedSection_eq_finiteRootAverage_rescale_exp"
  match env.find? ``Komorebi.PaperIV.signedSection_zero_eq_finite_exponential_average with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedSection_zero_eq_finite_exponential_average"
  match env.find? ``Komorebi.PaperIV.formalExpFamily with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.formalExpFamily"
  match env.find? ``Komorebi.PaperIV.formalExpFamily_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.formalExpFamily_zero"
  match env.find? ``Komorebi.PaperIV.formalExpFamily_one with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.formalExpFamily_one"
  match env.find? ``Komorebi.PaperIV.reducedDenominator with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedDenominator"
  logInfo "PAPER_IV_KIND_BATCH_PASS 0 48"
run_cmd do
  let env ← getEnv
  match env.find? ``Komorebi.PaperIV.coeff_reducedDenominator with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.coeff_reducedDenominator"
  match env.find? ``Komorebi.PaperIV.constantCoeff_reducedDenominator with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.constantCoeff_reducedDenominator"
  match env.find? ``Komorebi.PaperIV.signedSection_zero_eq_expand_reducedDenominator with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedSection_zero_eq_expand_reducedDenominator"
  match env.find? ``Komorebi.PaperIV.negativeLogDenominator with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.negativeLogDenominator"
  match env.find? ``Komorebi.PaperIV.constantCoeff_negativeLogDenominator with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.constantCoeff_negativeLogDenominator"
  match env.find? ``Komorebi.PaperIV.exp_subst_logOf with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.exp_subst_logOf"
  match env.find? ``Komorebi.PaperIV.mul_derivative_logOf with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.mul_derivative_logOf"
  match env.find? ``Komorebi.PaperIV.formalExpFamily_eq_exp_subst with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.formalExpFamily_eq_exp_subst"
  match env.find? ``Komorebi.PaperIV.reciprocalSeries with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reciprocalSeries"
  match env.find? ``Komorebi.PaperIV.constantCoeff_reciprocalSeries with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.constantCoeff_reciprocalSeries"
  match env.find? ``Komorebi.PaperIV.reciprocalSeries_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reciprocalSeries_zero"
  match env.find? ``Komorebi.PaperIV.reciprocalSeries_neg_one with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reciprocalSeries_neg_one"
  match env.find? ``Komorebi.PaperIV.reciprocalSeries_one_eq_inverse with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reciprocalSeries_one_eq_inverse"
  match env.find? ``Komorebi.PaperIV.reciprocalCoeff with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reciprocalCoeff"
  match env.find? ``Komorebi.PaperIV.reciprocalOrdCoeff with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reciprocalOrdCoeff"
  match env.find? ``Komorebi.PaperIV.reciprocalCoeff_zero_parameter with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reciprocalCoeff_zero_parameter"
  match env.find? ``Komorebi.PaperIV.reciprocalCoeff_zero_parameter_of_pos with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reciprocalCoeff_zero_parameter_of_pos"
  match env.find? ``Komorebi.PaperIV.formalExpFamily_semigroup with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.formalExpFamily_semigroup"
  match env.find? ``Komorebi.PaperIV.blockCoeff with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.blockCoeff"
  match env.find? ``Komorebi.PaperIV.blockCoeff_mul with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.blockCoeff_mul"
  match env.find? ``Komorebi.PaperIV.reciprocal_block_convolution with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reciprocal_block_convolution"
  match env.find? ``Komorebi.PaperIV.reciprocalSeries_add with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reciprocalSeries_add"
  match env.find? ``Komorebi.PaperIV.reciprocalCoeff_addition with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reciprocalCoeff_addition"
  match env.find? ``Komorebi.PaperIV.egfCoeff with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.egfCoeff"
  match env.find? ``Komorebi.PaperIV.egfCoeff_mul with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.egfCoeff_mul"
  match env.find? ``Komorebi.PaperIV.reciprocal_binomial_type with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reciprocal_binomial_type"
  match env.find? ``Komorebi.PaperIV.derivative_rescale_exp with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.derivative_rescale_exp"
  match env.find? ``Komorebi.PaperIV.derivative_formalExpFamily with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.derivative_formalExpFamily"
  match env.find? ``Komorebi.PaperIV.formalExpFamily_coefficient_recurrence with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.formalExpFamily_coefficient_recurrence"
  match env.find? ``Komorebi.PaperIV.kappaCoeff with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.kappaCoeff"
  match env.find? ``Komorebi.PaperIV.reducedTangentSeries with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedTangentSeries"
  match env.find? ``Komorebi.PaperIV.coeff_reducedTangentSeries with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.coeff_reducedTangentSeries"
  match env.find? ``Komorebi.PaperIV.reducedDenominator_mul_reducedTangentSeries with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedDenominator_mul_reducedTangentSeries"
  match env.find? ``Komorebi.PaperIV.reducedTangent_coefficient_convolution with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedTangent_coefficient_convolution"
  match env.find? ``Komorebi.PaperIV.derivative_reciprocalSeries with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.derivative_reciprocalSeries"
  match env.find? ``Komorebi.PaperIV.reciprocalSeries_coefficient_recurrence with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reciprocalSeries_coefficient_recurrence"
  match env.find? ``Komorebi.PaperIV.reciprocalOrdCoeff_newton with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reciprocalOrdCoeff_newton"
  match env.find? ``Komorebi.PaperIV.inverse_coefficient_convolution with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.inverse_coefficient_convolution"
  match env.find? ``Komorebi.PaperIV.constantCoeff_inverse_of_one with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.constantCoeff_inverse_of_one"
  match env.find? ``Komorebi.PaperIV.normalizedResidueSection with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.normalizedResidueSection"
  match env.find? ``Komorebi.PaperIV.coeff_normalizedResidueSection with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.coeff_normalizedResidueSection"
  match env.find? ``Komorebi.PaperIV.constantCoeff_normalizedResidueSection with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.constantCoeff_normalizedResidueSection"
  match env.find? ``Komorebi.PaperIV.residueInverseCoeff with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.residueInverseCoeff"
  match env.find? ``Komorebi.PaperIV.residueInverseCoeff_triangular with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.residueInverseCoeff_triangular"
  match env.find? ``Komorebi.PaperIV.residueInverseCoeff_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.residueInverseCoeff_zero"
  match env.find? ``Komorebi.PaperIV.residueInverseCoeff_recurrence with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.residueInverseCoeff_recurrence"
  match env.find? ``Komorebi.PaperIV.appellSeries with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.appellSeries"
  match env.find? ``Komorebi.PaperIV.appellCoeff with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.appellCoeff"
  logInfo "PAPER_IV_KIND_BATCH_PASS 48 48"
run_cmd do
  let env ← getEnv
  match env.find? ``Komorebi.PaperIV.egfCoeff_rescale_exp with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.egfCoeff_rescale_exp"
  match env.find? ``Komorebi.PaperIV.appellCoeff_zero_parameter with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.appellCoeff_zero_parameter"
  match env.find? ``Komorebi.PaperIV.appell_addition with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.appell_addition"
  match env.find? ``Komorebi.PaperIV.appellCoeff_at_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.appellCoeff_at_zero"
  match env.find? ``Komorebi.PaperIV.appellPolynomial with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.appellPolynomial"
  match env.find? ``Komorebi.PaperIV.derivative_appellPolynomial with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.derivative_appellPolynomial"
  match env.find? ``Komorebi.PaperIV.formalAppellPolynomial with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.formalAppellPolynomial"
  match env.find? ``Komorebi.PaperIV.derivative_formalAppellPolynomial with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.derivative_formalAppellPolynomial"
  match env.find? ``Komorebi.PaperIV.eval_formalAppellPolynomial with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.eval_formalAppellPolynomial"
  match env.find? ``Komorebi.PaperIV.blockCoefficientSequence with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.blockCoefficientSequence"
  match env.find? ``Komorebi.PaperIV.blockCoefficientSequence_mul with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.blockCoefficientSequence_mul"
  match env.find? ``Komorebi.PaperIV.appellPolynomial_eq_sparse_sum with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.appellPolynomial_eq_sparse_sum"
  match env.find? ``Komorebi.PaperIV.appellPolynomial_eq_block_sum with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.appellPolynomial_eq_block_sum"
  match env.find? ``Komorebi.PaperIV.residueAppellPolynomial_explicit with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.residueAppellPolynomial_explicit"
  match env.find? ``Komorebi.PaperIV.appellSeries_two_parameter with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.appellSeries_two_parameter"
  match env.find? ``Komorebi.PaperIV.appell_two_parameter_convolution with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.appell_two_parameter_convolution"
  match env.find? ``Komorebi.PaperIV.egfConstantCoeffAction with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.egfConstantCoeffAction"
  match env.find? ``Komorebi.PaperIV.egfConstantCoeffAction_X_pow with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.egfConstantCoeffAction_X_pow"
  match env.find? ``Komorebi.PaperIV.egfConstantCoeffAction_residue_X_pow with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.egfConstantCoeffAction_residue_X_pow"
  match env.find? ``Komorebi.PaperIV.polynomialDifferentialEval with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.polynomialDifferentialEval"
  match env.find? ``Komorebi.PaperIV.polynomialDifferentialEval_X with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.polynomialDifferentialEval_X"
  match env.find? ``Komorebi.PaperIV.truncatedDifferentialOperator with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.truncatedDifferentialOperator"
  match env.find? ``Komorebi.PaperIV.coeff_trunc_mul_trunc_of_lt with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.coeff_trunc_mul_trunc_of_lt"
  match env.find? ``Komorebi.PaperIV.X_pow_dvd_trunc_mul_trunc_sub_one with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.X_pow_dvd_trunc_mul_trunc_sub_one"
  match env.find? ``Komorebi.PaperIV.truncatedDifferentialOperator_mul_apply_of_natDegree_le with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.truncatedDifferentialOperator_mul_apply_of_natDegree_le"
  match env.find? ``Komorebi.PaperIV.truncatedDifferentialOperator_normalizedResidueSection_inverse with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.truncatedDifferentialOperator_normalizedResidueSection_inverse"
  match env.find? ``Komorebi.PaperIV.appellPolynomial_isMonicOfDegree with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.appellPolynomial_isMonicOfDegree"
  match env.find? ``Komorebi.PaperIV.blockAppellPolynomial_isMonicOfDegree with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.blockAppellPolynomial_isMonicOfDegree"
  match env.find? ``Komorebi.PaperIV.eval_appellPolynomial_block_covariance with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.eval_appellPolynomial_block_covariance"
  match env.find? ``Komorebi.PaperIV.residueAppellPolynomial_isMonicOfDegree with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.residueAppellPolynomial_isMonicOfDegree"
  match env.find? ``Komorebi.PaperIV.eval_residueAppellPolynomial_covariance with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.eval_residueAppellPolynomial_covariance"
  match env.find? ``Komorebi.PaperIV.blockCoeff_rescale with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.blockCoeff_rescale"
  match env.find? ``Komorebi.PaperIV.thetaSeries with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.thetaSeries"
  match env.find? ``Komorebi.PaperIV.thetaCoeff with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.thetaCoeff"
  match env.find? ``Komorebi.PaperIV.thetaCoeff_reconstruction_unfactored with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.thetaCoeff_reconstruction_unfactored"
  match env.find? ``Komorebi.PaperIV.thetaCoeff_reconstruction with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.thetaCoeff_reconstruction"
  match env.find? ``Komorebi.PaperIV.thetaSeries_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.thetaSeries_zero"
  match env.find? ``Komorebi.PaperIV.thetaCoeff_zero_parameter with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.thetaCoeff_zero_parameter"
  match env.find? ``Komorebi.PaperIV.thetaCoeff_zero_parameter_of_pos with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.thetaCoeff_zero_parameter_of_pos"
  match env.find? ``Komorebi.PaperIV.thetaSeries_neg_one_of_even with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.thetaSeries_neg_one_of_even"
  match env.find? ``Komorebi.PaperIV.thetaCoeff_neg_one_of_even_of_pos with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.thetaCoeff_neg_one_of_even_of_pos"
  match env.find? ``Komorebi.PaperIV.cyclicProjector_fixed_iff_rescale_covariant with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.cyclicProjector_fixed_iff_rescale_covariant"
  match env.find? ``Komorebi.PaperIV.cyclicProjector_mem_range_iff_rescale_covariant with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.cyclicProjector_mem_range_iff_rescale_covariant"
  match env.find? ``Komorebi.PaperIV.bivariateExponentialGeneratingSeries with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.bivariateExponentialGeneratingSeries"
  match env.find? ``Komorebi.PaperIV.coeff_bivariateExponentialGeneratingSeries with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.coeff_bivariateExponentialGeneratingSeries"
  match env.find? ``Komorebi.PaperIV.separatedExponentialGeneratingSeries with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.separatedExponentialGeneratingSeries"
  match env.find? ``Komorebi.PaperIV.coeff_separatedExponentialGeneratingSeries with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.coeff_separatedExponentialGeneratingSeries"
  match env.find? ``Komorebi.PaperIV.transferSection_addition with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.transferSection_addition"
  logInfo "PAPER_IV_KIND_BATCH_PASS 96 48"
run_cmd do
  let env ← getEnv
  match env.find? ``Komorebi.PaperIV.residuePochhammerProduct with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.residuePochhammerProduct"
  match env.find? ``Komorebi.PaperIV.factorial_eq_residuePochhammerProduct with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.factorial_eq_residuePochhammerProduct"
  match env.find? ``Komorebi.PaperIV.residueZeroFCoeff with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.residueZeroFCoeff"
  match env.find? ``Komorebi.PaperIV.residueZeroFSeries with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.residueZeroFSeries"
  match env.find? ``Komorebi.PaperIV.coeff_residueZeroFSeries with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.coeff_residueZeroFSeries"
  match env.find? ``Komorebi.PaperIV.residueZeroFCoeff_normalization with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.residueZeroFCoeff_normalization"
  match env.find? ``Komorebi.PaperIV.residueParameter_eq_one with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.residueParameter_eq_one"
  match env.find? ``Komorebi.PaperIV.omitted_residuePochhammer_eq_factorial with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.omitted_residuePochhammer_eq_factorial"
  match env.find? ``Komorebi.PaperIV.transferSection_eq_residueZeroFSeries with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.transferSection_eq_residueZeroFSeries"
  match env.find? ``Komorebi.PaperIV.signedSection_addition with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedSection_addition"
  match env.find? ``Komorebi.PaperIV.signedDenominator_rescale_of_pow_eq_one with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedDenominator_rescale_of_pow_eq_one"
  match env.find? ``Komorebi.PaperIV.signedDenominator_map_conj with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedDenominator_map_conj"
  match env.find? ``Komorebi.PaperIV.cyclicAlgebraPolynomial with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.cyclicAlgebraPolynomial"
  match env.find? ``Komorebi.PaperIV.signedCyclicAlgebraPolynomial with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedCyclicAlgebraPolynomial"
  match env.find? ``Komorebi.PaperIV.CyclicAlgebra with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.CyclicAlgebra"
  match env.find? ``Komorebi.PaperIV.SignedCyclicAlgebra with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedCyclicAlgebra"
  match env.find? ``Komorebi.PaperIV.cyclicGenerator with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.cyclicGenerator"
  match env.find? ``Komorebi.PaperIV.signedCyclicGenerator with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedCyclicGenerator"
  match env.find? ``Komorebi.PaperIV.cyclicGenerator_pow with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.cyclicGenerator_pow"
  match env.find? ``Komorebi.PaperIV.signedCyclicGenerator_pow with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedCyclicGenerator_pow"
  match env.find? ``Komorebi.PaperIV.cyclicGenerator_pow_eq_mod with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.cyclicGenerator_pow_eq_mod"
  match env.find? ``Komorebi.PaperIV.signedCyclicGenerator_pow_eq_mod with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedCyclicGenerator_pow_eq_mod"
  match env.find? ``Komorebi.PaperIV.cyclicAlgebraPowerBasis with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.cyclicAlgebraPowerBasis"
  match env.find? ``Komorebi.PaperIV.signedCyclicAlgebraPowerBasis with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedCyclicAlgebraPowerBasis"
  match env.find? ``Komorebi.PaperIV.cyclicAlgebraPowerBasis_dim with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.cyclicAlgebraPowerBasis_dim"
  match env.find? ``Komorebi.PaperIV.signedCyclicAlgebraPowerBasis_dim with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedCyclicAlgebraPowerBasis_dim"
  match env.find? ``Komorebi.PaperIV.cyclicAlgebraExponentialSeries with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.cyclicAlgebraExponentialSeries"
  match env.find? ``Komorebi.PaperIV.signedCyclicAlgebraExponentialSeries with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedCyclicAlgebraExponentialSeries"
  match env.find? ``Komorebi.PaperIV.cyclicAlgebra_exponential_eq_sections with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.cyclicAlgebra_exponential_eq_sections"
  match env.find? ``Komorebi.PaperIV.signedCyclicAlgebra_exponential_eq_sections with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedCyclicAlgebra_exponential_eq_sections"
  match env.find? ``Komorebi.PaperIV.signedShiftPowerMatrix with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedShiftPowerMatrix"
  match env.find? ``Komorebi.PaperIV.signedShiftMatrix with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedShiftMatrix"
  match env.find? ``Komorebi.PaperIV.signedShiftPowerMatrix_apply with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedShiftPowerMatrix_apply"
  match env.find? ``Komorebi.PaperIV.signedShiftPowerMatrix_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedShiftPowerMatrix_zero"
  match env.find? ``Komorebi.PaperIV.signedShiftPowerMatrix_mul with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedShiftPowerMatrix_mul"
  match env.find? ``Komorebi.PaperIV.signedShiftMatrix_pow with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedShiftMatrix_pow"
  match env.find? ``Komorebi.PaperIV.signedShiftMatrix_pow_apply with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedShiftMatrix_pow_apply"
  match env.find? ``Komorebi.PaperIV.signedShiftMatrix_pow_order with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedShiftMatrix_pow_order"
  match env.find? ``Komorebi.PaperIV.signedFundamentalMatrix with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedFundamentalMatrix"
  match env.find? ``Komorebi.PaperIV.signedFundamentalMatrix_add with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedFundamentalMatrix_add"
  match env.find? ``Komorebi.PaperIV.signedFundamentalMatrix_neg with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedFundamentalMatrix_neg"
  match env.find? ``Komorebi.PaperIV.signedFundamentalMatrix_mul_neg with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedFundamentalMatrix_mul_neg"
  match env.find? ``Komorebi.PaperIV.signedFundamentalMatrix_isUnit with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedFundamentalMatrix_isUnit"
  match env.find? ``Komorebi.PaperIV.reducedDenominator_reciprocalSeries_differentialEquation with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedDenominator_reciprocalSeries_differentialEquation"
  match env.find? ``Komorebi.PaperIV.reciprocalOrdCoeff_parameter_equation with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reciprocalOrdCoeff_parameter_equation"
  match env.find? ``Komorebi.PaperIV.reciprocalCoeff_parameter_equation with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reciprocalCoeff_parameter_equation"
  match env.find? ``Komorebi.PaperIV.reciprocalCoeff_parameter_recurrence with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reciprocalCoeff_parameter_recurrence"
  match env.find? ``Komorebi.PaperIV.reciprocalCoeff_block_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reciprocalCoeff_block_zero"
  logInfo "PAPER_IV_KIND_BATCH_PASS 144 48"
run_cmd do
  let env ← getEnv
  match env.find? ``Komorebi.PaperIV.reciprocalCoeff_one with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reciprocalCoeff_one"
  match env.find? ``Komorebi.PaperIV.reciprocalCoeff_two_recurrence_form with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reciprocalCoeff_two_recurrence_form"
  match env.find? ``Komorebi.PaperIV.reciprocalCoeff_three_recurrence_form with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reciprocalCoeff_three_recurrence_form"
  match env.find? ``Komorebi.PaperIV.reciprocalCoeffPolynomial with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reciprocalCoeffPolynomial"
  match env.find? ``Komorebi.PaperIV.X_dvd_reciprocalCoeffPolynomial with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.X_dvd_reciprocalCoeffPolynomial"
  match env.find? ``Komorebi.PaperIV.coeff_zero_reciprocalCoeffPolynomial with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.coeff_zero_reciprocalCoeffPolynomial"
  match env.find? ``Komorebi.PaperIV.reciprocalCoeffPolynomialOver with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reciprocalCoeffPolynomialOver"
  match env.find? ``Komorebi.PaperIV.eval_reciprocalCoeffPolynomialOver with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.eval_reciprocalCoeffPolynomialOver"
  match env.find? ``Komorebi.PaperIV.formalTransferTangent with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.formalTransferTangent"
  match env.find? ``Komorebi.PaperIV.transferTangentCoeff with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.transferTangentCoeff"
  match env.find? ``Komorebi.PaperIV.transferTangentCoeff_eq_kappa with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.transferTangentCoeff_eq_kappa"
  match env.find? ``Komorebi.PaperIV.transferTangentCoeff_convolution with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.transferTangentCoeff_convolution"
  match env.find? ``Komorebi.PaperIV.transferTangentCoeff_recurrence with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.transferTangentCoeff_recurrence"
  match env.find? ``Komorebi.PaperIV.transferTangentCoeff_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.transferTangentCoeff_zero"
  match env.find? ``Komorebi.PaperIV.differentialBellSeries with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.differentialBellSeries"
  match env.find? ``Komorebi.PaperIV.differentialBellSeries_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.differentialBellSeries_zero"
  match env.find? ``Komorebi.PaperIV.differentialBellSeries_succ with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.differentialBellSeries_succ"
  match env.find? ``Komorebi.PaperIV.iterate_derivative_eq_differentialBellSeries_mul with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.iterate_derivative_eq_differentialBellSeries_mul"
  match env.find? ``Komorebi.PaperIV.derivative_signedSection_zero_eq_neg_formalTransferTangent_mul with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.derivative_signedSection_zero_eq_neg_formalTransferTangent_mul"
  match env.find? ``Komorebi.PaperIV.differentialBellSeries_neg_formalTransferTangent_eq_neg_one with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.differentialBellSeries_neg_formalTransferTangent_eq_neg_one"
  match env.find? ``Komorebi.PaperIV.normalizedResidueSectionAlg with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.normalizedResidueSectionAlg"
  match env.find? ``Komorebi.PaperIV.coeff_normalizedResidueSectionAlg with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.coeff_normalizedResidueSectionAlg"
  match env.find? ``Komorebi.PaperIV.constantCoeff_normalizedResidueSectionAlg with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.constantCoeff_normalizedResidueSectionAlg"
  match env.find? ``Komorebi.PaperIV.normalizedResidueSectionAlg_eq_normalizedResidueSection with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.normalizedResidueSectionAlg_eq_normalizedResidueSection"
  match env.find? ``Komorebi.PaperIV.normalizedResidueNegativeLog with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.normalizedResidueNegativeLog"
  match env.find? ``Komorebi.PaperIV.constantCoeff_normalizedResidueNegativeLog with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.constantCoeff_normalizedResidueNegativeLog"
  match env.find? ``Komorebi.PaperIV.residuePowerSeries with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.residuePowerSeries"
  match env.find? ``Komorebi.PaperIV.constantCoeff_residuePowerSeries with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.constantCoeff_residuePowerSeries"
  match env.find? ``Komorebi.PaperIV.residuePowerSeries_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.residuePowerSeries_zero"
  match env.find? ``Komorebi.PaperIV.residuePowerSeries_neg_one with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.residuePowerSeries_neg_one"
  match env.find? ``Komorebi.PaperIV.residuePowerSeries_one_eq_inverse with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.residuePowerSeries_one_eq_inverse"
  match env.find? ``Komorebi.PaperIV.residuePowerCoeff with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.residuePowerCoeff"
  match env.find? ``Komorebi.PaperIV.residuePowerCoeff_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.residuePowerCoeff_zero"
  match env.find? ``Komorebi.PaperIV.residuePowerCoeff_one_eq_residueInverseCoeff with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.residuePowerCoeff_one_eq_residueInverseCoeff"
  match env.find? ``Komorebi.PaperIV.residuePowerSeries_add with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.residuePowerSeries_add"
  match env.find? ``Komorebi.PaperIV.residuePowerCoeff_addition with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.residuePowerCoeff_addition"
  match env.find? ``Komorebi.PaperIV.residuePowerCoeffPolynomial with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.residuePowerCoeffPolynomial"
  match env.find? ``Komorebi.PaperIV.eval_residuePowerCoeffPolynomial with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.eval_residuePowerCoeffPolynomial"
  match env.find? ``Komorebi.PaperIV.coeff_residuePowerCoeffPolynomial_parameterDegree with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.coeff_residuePowerCoeffPolynomial_parameterDegree"
  match env.find? ``Komorebi.PaperIV.natDegree_residuePowerCoeffPolynomial with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.natDegree_residuePowerCoeffPolynomial"
  match env.find? ``Komorebi.PaperIV.expandedResidueNegativeLog with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.expandedResidueNegativeLog"
  match env.find? ``Komorebi.PaperIV.constantCoeff_expandedResidueNegativeLog with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.constantCoeff_expandedResidueNegativeLog"
  match env.find? ``Komorebi.PaperIV.expand_residuePowerSeries with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.expand_residuePowerSeries"
  match env.find? ``Komorebi.PaperIV.egfCoeff_expand_residuePowerSeries with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.egfCoeff_expand_residuePowerSeries"
  match env.find? ``Komorebi.PaperIV.residueAppellPolynomialParam with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.residueAppellPolynomialParam"
  match env.find? ``Komorebi.PaperIV.residueAppellPolynomialParam_eq_block with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.residueAppellPolynomialParam_eq_block"
  match env.find? ``Komorebi.PaperIV.residueAppellPolynomialParam_explicit with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.residueAppellPolynomialParam_explicit"
  match env.find? ``Komorebi.PaperIV.derivative_residueAppellPolynomialParam with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.derivative_residueAppellPolynomialParam"
  logInfo "PAPER_IV_KIND_BATCH_PASS 192 48"
run_cmd do
  let env ← getEnv
  match env.find? ``Komorebi.PaperIV.eval_residueAppellPolynomialParam_add with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.eval_residueAppellPolynomialParam_add"
  match env.find? ``Komorebi.PaperIV.eval_residueAppellPolynomialParam_two_parameter with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.eval_residueAppellPolynomialParam_two_parameter"
  match env.find? ``Komorebi.PaperIV.residueAppellPolynomialParam_isMonicOfDegree with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.residueAppellPolynomialParam_isMonicOfDegree"
  match env.find? ``Komorebi.PaperIV.eval_residueAppellPolynomialParam_covariance with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.eval_residueAppellPolynomialParam_covariance"
  match env.find? ``Komorebi.PaperIV.egfConstantCoeffAction_residuePowerSeries_X_pow with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.egfConstantCoeffAction_residuePowerSeries_X_pow"
  match env.find? ``Komorebi.PaperIV.truncatedDifferentialOperator_residuePowerSeries_inverse with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.truncatedDifferentialOperator_residuePowerSeries_inverse"
  match env.find? ``Komorebi.PaperIV.thetaPolynomial with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.thetaPolynomial"
  match env.find? ``Komorebi.PaperIV.eval_thetaPolynomial with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.eval_thetaPolynomial"
  match env.find? ``Komorebi.PaperIV.natDegree_thetaPolynomial_le with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.natDegree_thetaPolynomial_le"
  match env.find? ``Komorebi.PaperIV.X_dvd_thetaPolynomial with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.X_dvd_thetaPolynomial"
  match env.find? ``Komorebi.PaperIV.X_add_one_dvd_thetaPolynomial_of_even with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.X_add_one_dvd_thetaPolynomial_of_even"
  match env.find? ``Komorebi.PaperIV.derivative_rescale_series with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.derivative_rescale_series"
  match env.find? ``Komorebi.PaperIV.rescale_C_series with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.rescale_C_series"
  match env.find? ``Komorebi.PaperIV.scaledReciprocalLogDerivative with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.scaledReciprocalLogDerivative"
  match env.find? ``Komorebi.PaperIV.derivative_rescale_reciprocalSeries with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.derivative_rescale_reciprocalSeries"
  match env.find? ``Komorebi.PaperIV.thetaLogDerivativeSeries with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.thetaLogDerivativeSeries"
  match env.find? ``Komorebi.PaperIV.derivative_thetaSeries with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.derivative_thetaSeries"
  match env.find? ``Komorebi.PaperIV.coeff_thetaLogDerivativeSeries with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.coeff_thetaLogDerivativeSeries"
  match env.find? ``Komorebi.PaperIV.thetaOrdCoeff with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.thetaOrdCoeff"
  match env.find? ``Komorebi.PaperIV.thetaOrdCoeff_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.thetaOrdCoeff_zero"
  match env.find? ``Komorebi.PaperIV.thetaOrdCoeff_newton with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.thetaOrdCoeff_newton"
  match env.find? ``Komorebi.PaperIV.factorial_mul_kappaCoeff_one with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.factorial_mul_kappaCoeff_one"
  match env.find? ``Komorebi.PaperIV.thetaCoeff_one with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.thetaCoeff_one"
  match env.find? ``Komorebi.PaperIV.bellInput with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.bellInput"
  match env.find? ``Komorebi.PaperIV.completeExponentialBell with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.completeExponentialBell"
  match env.find? ``Komorebi.PaperIV.constantCoeff_bellInput with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.constantCoeff_bellInput"
  match env.find? ``Komorebi.PaperIV.completeExponentialBell_generating_coefficient with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.completeExponentialBell_generating_coefficient"
  match env.find? ``Komorebi.PaperIV.completeExponentialBell_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.completeExponentialBell_zero"
  match env.find? ``Komorebi.PaperIV.bellInput_reciprocal with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.bellInput_reciprocal"
  match env.find? ``Komorebi.PaperIV.reciprocalCoeff_bell_formula with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reciprocalCoeff_bell_formula"
  match env.find? ``Komorebi.PaperIV.coeff_one_negativeLogDenominator with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.coeff_one_negativeLogDenominator"
  match env.find? ``Komorebi.PaperIV.coeff_reciprocalCoeffPolynomialOver_parameterDegree with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.coeff_reciprocalCoeffPolynomialOver_parameterDegree"
  match env.find? ``Komorebi.PaperIV.natDegree_reciprocalCoeffPolynomialOver with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.natDegree_reciprocalCoeffPolynomialOver"
  match env.find? ``Komorebi.PaperIV.X_dvd_reciprocalCoeffPolynomialOver with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.X_dvd_reciprocalCoeffPolynomialOver"
  match env.find? ``Komorebi.PaperIV.exponentialSumJet with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.exponentialSumJet"
  match env.find? ``Komorebi.PaperIV.analyticAt_exponentialSumJet with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticAt_exponentialSumJet"
  match env.find? ``Komorebi.PaperIV.hasDerivAt_exponentialSumJet with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.hasDerivAt_exponentialSumJet"
  match env.find? ``Komorebi.PaperIV.iteratedDeriv_exponentialSum with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.iteratedDeriv_exponentialSum"
  match env.find? ``Komorebi.PaperIV.exponentialSum_ode with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.exponentialSum_ode"
  match env.find? ``Komorebi.PaperIV.entireTransfer with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireTransfer"
  match env.find? ``Komorebi.PaperIV.analyticAt_entireTransfer with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticAt_entireTransfer"
  match env.find? ``Komorebi.PaperIV.entireTransfer_eq_exponentialSum with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireTransfer_eq_exponentialSum"
  match env.find? ``Komorebi.PaperIV.hasSum_finiteRootAverage with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.hasSum_finiteRootAverage"
  match env.find? ``Komorebi.PaperIV.hasSum_entireTransfer with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.hasSum_entireTransfer"
  match env.find? ``Komorebi.PaperIV.entireTransfer_eq_tsum with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireTransfer_eq_tsum"
  match env.find? ``Komorebi.PaperIV.entireTransfer_independent_root with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireTransfer_independent_root"
  match env.find? ``Komorebi.PaperIV.entireTransfer_ode with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireTransfer_ode"
  match env.find? ``Komorebi.PaperIV.entireSigned with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireSigned"
  logInfo "PAPER_IV_KIND_BATCH_PASS 240 48"
run_cmd do
  let env ← getEnv
  match env.find? ``Komorebi.PaperIV.analyticAt_entireSigned with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticAt_entireSigned"
  match env.find? ``Komorebi.PaperIV.hasSum_entireSigned with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.hasSum_entireSigned"
  match env.find? ``Komorebi.PaperIV.entireSigned_eq_tsum with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireSigned_eq_tsum"
  match env.find? ``Komorebi.PaperIV.entireSigned_independent_roots with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireSigned_independent_roots"
  match env.find? ``Komorebi.PaperIV.entireSigned_zero_eq_average with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireSigned_zero_eq_average"
  match env.find? ``Komorebi.PaperIV.entireTransfer_derivative_at_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireTransfer_derivative_at_zero"
  match env.find? ``Komorebi.PaperIV.entireTransfer_initial_data with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireTransfer_initial_data"
  match env.find? ``Komorebi.PaperIV.entireSigned_eq_exponentialSum with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireSigned_eq_exponentialSum"
  match env.find? ``Komorebi.PaperIV.entireSigned_ode with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireSigned_ode"
  match env.find? ``Komorebi.PaperIV.entireSigned_derivative_eq_scaled_transfer with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireSigned_derivative_eq_scaled_transfer"
  match env.find? ``Komorebi.PaperIV.entireSigned_initial_data with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireSigned_initial_data"
  match env.find? ``Komorebi.PaperIV.exponentialJetMatrix with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.exponentialJetMatrix"
  match env.find? ``Komorebi.PaperIV.exponentialJetMatrix_factor with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.exponentialJetMatrix_factor"
  match env.find? ``Komorebi.PaperIV.det_exponentialJetMatrix with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.det_exponentialJetMatrix"
  match env.find? ``Komorebi.PaperIV.det_exponentialJetMatrix_constant with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.det_exponentialJetMatrix_constant"
  match env.find? ``Komorebi.PaperIV.analyticWronskian with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticWronskian"
  match env.find? ``Komorebi.PaperIV.transferWronskian_constant with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.transferWronskian_constant"
  match env.find? ``Komorebi.PaperIV.transferWronskian_eq with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.transferWronskian_eq"
  match env.find? ``Komorebi.PaperIV.signedWronskian_constant with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedWronskian_constant"
  match env.find? ``Komorebi.PaperIV.signedWronskian_eq_one with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedWronskian_eq_one"
  match env.find? ``Komorebi.PaperIV.hasSum_signedFundamentalMatrix_entry with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.hasSum_signedFundamentalMatrix_entry"
  match env.find? ``Komorebi.PaperIV.signedFundamentalMatrix_first_column with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedFundamentalMatrix_first_column"
  match env.find? ``Komorebi.PaperIV.signedFundamentalMatrix_diagonal with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedFundamentalMatrix_diagonal"
  match env.find? ``Komorebi.PaperIV.signedFundamentalMatrix_trace with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedFundamentalMatrix_trace"
  match env.find? ``Komorebi.PaperIV.hasSum_exponentialSumJet with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.hasSum_exponentialSumJet"
  match env.find? ``Komorebi.PaperIV.entireSigned_derivative_at_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireSigned_derivative_at_zero"
  match env.find? ``Komorebi.PaperIV.hasSum_entireSigned_derivative with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.hasSum_entireSigned_derivative"
  match env.find? ``Komorebi.PaperIV.signedFundamentalMatrix_entry_eq_derivative with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedFundamentalMatrix_entry_eq_derivative"
  match env.find? ``Komorebi.PaperIV.signedFundamentalMatrix_det with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedFundamentalMatrix_det"
  match env.find? ``Komorebi.PaperIV.companionDisplacement with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.companionDisplacement"
  match env.find? ``Komorebi.PaperIV.companionDisplacement_lt with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.companionDisplacement_lt"
  match env.find? ``Komorebi.PaperIV.companionEntrySign with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.companionEntrySign"
  match env.find? ``Komorebi.PaperIV.signedShiftMatrix_pow_entry_packet with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedShiftMatrix_pow_entry_packet"
  match env.find? ``Komorebi.PaperIV.signedFundamentalMatrix_entry with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedFundamentalMatrix_entry"
  match env.find? ``Komorebi.PaperIV.aeval_signedShiftMatrix_first_column with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.aeval_signedShiftMatrix_first_column"
  match env.find? ``Komorebi.PaperIV.signedShiftMatrix_no_small_annihilator with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedShiftMatrix_no_small_annihilator"
  match env.find? ``Komorebi.PaperIV.aeval_signedShiftMatrix_X_pow_add_one with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.aeval_signedShiftMatrix_X_pow_add_one"
  match env.find? ``Komorebi.PaperIV.signedShiftMatrix_charpoly with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedShiftMatrix_charpoly"
  match env.find? ``Komorebi.PaperIV.signedShiftMatrix_mem_spectrum_iff with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedShiftMatrix_mem_spectrum_iff"
  match env.find? ``Komorebi.PaperIV.signedShiftMatrix_charpoly_separable with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedShiftMatrix_charpoly_separable"
  match env.find? ``Komorebi.PaperIV.signedShiftMatrix_charpoly_roots_card with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedShiftMatrix_charpoly_roots_card"
  match env.find? ``Komorebi.PaperIV.signedShiftMatrix_charpoly_roots_nodup with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedShiftMatrix_charpoly_roots_nodup"
  match env.find? ``Komorebi.PaperIV.ode_all_derivatives_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.ode_all_derivatives_zero"
  match env.find? ``Komorebi.PaperIV.entire_ode_zero_of_initial_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entire_ode_zero_of_initial_zero"
  match env.find? ``Komorebi.PaperIV.entire_ode_unique with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entire_ode_unique"
  match env.find? ``Komorebi.PaperIV.transferCombination with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.transferCombination"
  match env.find? ``Komorebi.PaperIV.analyticAt_transferCombination with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticAt_transferCombination"
  match env.find? ``Komorebi.PaperIV.transferCombination_derivative with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.transferCombination_derivative"
  logInfo "PAPER_IV_KIND_BATCH_PASS 288 48"
run_cmd do
  let env ← getEnv
  match env.find? ``Komorebi.PaperIV.transferCombination_ode with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.transferCombination_ode"
  match env.find? ``Komorebi.PaperIV.transferCombination_initial with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.transferCombination_initial"
  match env.find? ``Komorebi.PaperIV.entireTransfer_solution_expansion with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireTransfer_solution_expansion"
  match env.find? ``Komorebi.PaperIV.transferCombination_injective with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.transferCombination_injective"
  match env.find? ``Komorebi.PaperIV.entire_eq_of_all_derivatives with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entire_eq_of_all_derivatives"
  match env.find? ``Komorebi.PaperIV.entire_derivative_of_formal with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entire_derivative_of_formal"
  match env.find? ``Komorebi.PaperIV.entireTransfer_derivative_of_pos with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireTransfer_derivative_of_pos"
  match env.find? ``Komorebi.PaperIV.entireTransfer_derivative_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireTransfer_derivative_zero"
  match env.find? ``Komorebi.PaperIV.entireSigned_derivative_of_pos with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireSigned_derivative_of_pos"
  match env.find? ``Komorebi.PaperIV.entireSigned_derivative_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireSigned_derivative_zero"
  match env.find? ``Komorebi.PaperIV.canonicalPrimitiveRoot with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalPrimitiveRoot"
  match env.find? ``Komorebi.PaperIV.canonicalSignedRoot with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedRoot"
  match env.find? ``Komorebi.PaperIV.canonicalPrimitiveRoot_isPrimitive with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalPrimitiveRoot_isPrimitive"
  match env.find? ``Komorebi.PaperIV.canonicalSignedRoot_pow with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedRoot_pow"
  match env.find? ``Komorebi.PaperIV.signedFundamentalMatrix_det_one with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedFundamentalMatrix_det_one"
  match env.find? ``Komorebi.PaperIV.norm_signedRoot with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.norm_signedRoot"
  match env.find? ``Komorebi.PaperIV.norm_entireSigned_zero_le with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.norm_entireSigned_zero_le"
  match env.find? ``Komorebi.PaperIV.entireSigned_two_eq_cos with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireSigned_two_eq_cos"
  match env.find? ``Komorebi.PaperIV.entireSigned_two_zero_iff with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireSigned_two_zero_iff"
  match env.find? ``Komorebi.PaperIV.entireSigned_two_zero_derivative_ne_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireSigned_two_zero_derivative_ne_zero"
  match env.find? ``Komorebi.PaperIV.entireSigned_two_zero_iff_nat with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireSigned_two_zero_iff_nat"
  match env.find? ``Komorebi.PaperIV.entireSigned_two_zero_order_one with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireSigned_two_zero_order_one"
  match env.find? ``Komorebi.PaperIV.orderTwo_zero_spacing with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.orderTwo_zero_spacing"
  match env.find? ``Komorebi.PaperIV.oddExponentialCenter with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.oddExponentialCenter"
  match env.find? ``Komorebi.PaperIV.near_cancellation_exists with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.near_cancellation_exists"
  match env.find? ``Komorebi.PaperIV.oddExponentialCenter_separation with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.oddExponentialCenter_separation"
  match env.find? ``Komorebi.PaperIV.near_cancellation_unique with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.near_cancellation_unique"
  match env.find? ``Komorebi.PaperIV.signedCombination with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedCombination"
  match env.find? ``Komorebi.PaperIV.signedCombination_eq_transfer with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedCombination_eq_transfer"
  match env.find? ``Komorebi.PaperIV.entireSigned_solution_expansion with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireSigned_solution_expansion"
  match env.find? ``Komorebi.PaperIV.signedCombination_injective with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedCombination_injective"
  match env.find? ``Komorebi.PaperIV.norm_one_add_lower_half with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.norm_one_add_lower_half"
  match env.find? ``Komorebi.PaperIV.log_one_add_lipschitz_half with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.log_one_add_lipschitz_half"
  match env.find? ``Komorebi.PaperIV.logarithmicZeroMap with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.logarithmicZeroMap"
  match env.find? ``Komorebi.PaperIV.logarithmicZeroMap_mapsTo with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.logarithmicZeroMap_mapsTo"
  match env.find? ``Komorebi.PaperIV.logarithmicZeroMap_lipschitz with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.logarithmicZeroMap_lipschitz"
  match env.find? ``Komorebi.PaperIV.logarithmicZeroMap_fixed_iff with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.logarithmicZeroMap_fixed_iff"
  match env.find? ``Komorebi.PaperIV.perturbed_exponential_unique_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.perturbed_exponential_unique_zero"
  match env.find? ``Komorebi.PaperIV.perturbed_exponential_zero_distance with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.perturbed_exponential_zero_distance"
  match env.find? ``Komorebi.PaperIV.perturbed_exponential_pointwise_distance with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.perturbed_exponential_pointwise_distance"
  match env.find? ``Komorebi.PaperIV.hasDerivAt_perturbed_exponential with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.hasDerivAt_perturbed_exponential"
  match env.find? ``Komorebi.PaperIV.perturbed_exponential_zero_derivative_lower with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.perturbed_exponential_zero_derivative_lower"
  match env.find? ``Komorebi.PaperIV.perturbed_exponential_zero_order_one with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.perturbed_exponential_zero_order_one"
  match env.find? ``Komorebi.PaperIV.perturbed_exponential_derivative_error with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.perturbed_exponential_derivative_error"
  match env.find? ``Komorebi.PaperIV.norm_log_one_add_sub_self_half with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.norm_log_one_add_sub_self_half"
  match env.find? ``Komorebi.PaperIV.perturbed_exponential_first_correction with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.perturbed_exponential_first_correction"
  match env.find? ``Komorebi.PaperIV.finiteExponentialRemainder with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.finiteExponentialRemainder"
  match env.find? ``Komorebi.PaperIV.analyticAt_finiteExponentialRemainder with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticAt_finiteExponentialRemainder"
  logInfo "PAPER_IV_KIND_BATCH_PASS 336 48"
run_cmd do
  let env ← getEnv
  match env.find? ``Komorebi.PaperIV.hasDerivAt_finiteExponentialRemainder with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.hasDerivAt_finiteExponentialRemainder"
  match env.find? ``Komorebi.PaperIV.iteratedDeriv_finiteExponentialRemainder with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.iteratedDeriv_finiteExponentialRemainder"
  match env.find? ``Komorebi.PaperIV.finiteExponentialRemainder_strip_bound with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.finiteExponentialRemainder_strip_bound"
  match env.find? ``Komorebi.PaperIV.finite_two_term_normalization with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.finite_two_term_normalization"
  match env.find? ``Komorebi.PaperIV.signedExponentialRemainder with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedExponentialRemainder"
  match env.find? ``Komorebi.PaperIV.signed_two_term_normalization with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signed_two_term_normalization"
  match env.find? ``Komorebi.PaperIV.signed_two_term_zero_iff with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signed_two_term_zero_iff"
  match env.find? ``Komorebi.PaperIV.canonicalSignedVertex with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedVertex"
  match env.find? ``Komorebi.PaperIV.signedPolygonGap with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedPolygonGap"
  match env.find? ``Komorebi.PaperIV.canonicalSignedVertex_exp with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedVertex_exp"
  match env.find? ``Komorebi.PaperIV.canonicalSignedVertex_re with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedVertex_re"
  match env.find? ``Komorebi.PaperIV.canonicalSignedVertex_im with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedVertex_im"
  match env.find? ``Komorebi.PaperIV.norm_canonicalSignedVertex with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.norm_canonicalSignedVertex"
  match env.find? ``Komorebi.PaperIV.canonicalSignedVertex_last_angle with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedVertex_last_angle"
  match env.find? ``Komorebi.PaperIV.canonicalSignedVertex_last_re with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedVertex_last_re"
  match env.find? ``Komorebi.PaperIV.canonicalSignedVertex_last_im with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedVertex_last_im"
  match env.find? ``Komorebi.PaperIV.signedPolygonGap_pos with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedPolygonGap_pos"
  match env.find? ``Komorebi.PaperIV.canonicalSignedVertex_re_gap with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedVertex_re_gap"
  match env.find? ``Komorebi.PaperIV.canonicalSignedRemainder_strip_bound with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedRemainder_strip_bound"
  match env.find? ``Komorebi.PaperIV.canonicalSignedVertex_adjacent_difference with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedVertex_adjacent_difference"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator"
  match env.find? ``Komorebi.PaperIV.signedZeroFrequency with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedZeroFrequency"
  match env.find? ``Komorebi.PaperIV.signedZeroCenter with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedZeroCenter"
  match env.find? ``Komorebi.PaperIV.signed_sine_pos with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signed_sine_pos"
  match env.find? ``Komorebi.PaperIV.signedZeroFrequency_ne_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedZeroFrequency_ne_zero"
  match env.find? ``Komorebi.PaperIV.signedZeroCenter_cancellation with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedZeroCenter_cancellation"
  match env.find? ``Komorebi.PaperIV.canonicalSignedRemainder_disk_bound with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedRemainder_disk_bound"
  match env.find? ``Komorebi.PaperIV.signedRemainder_eventually_small_on_disks with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedRemainder_eventually_small_on_disks"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_conj with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_conj"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_eventual_local_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_eventual_local_zero"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_unique_zero_real with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_unique_zero_real"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_local_zero_simple with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_local_zero_simple"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_eventual_positive_simple_zeros with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_eventual_positive_simple_zeros"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_local_zero_exponential_distance with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_local_zero_exponential_distance"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_local_strings with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_local_strings"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_zero_lattice_distance with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_zero_lattice_distance"
  match env.find? ``Komorebi.PaperIV.signedRemainderScale with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedRemainderScale"
  match env.find? ``Komorebi.PaperIV.signedRemainderEnvelope with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedRemainderEnvelope"
  match env.find? ``Komorebi.PaperIV.signedRemainderEnvelope_pos with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedRemainderEnvelope_pos"
  match env.find? ``Komorebi.PaperIV.signedRemainderEnvelope_bounds with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedRemainderEnvelope_bounds"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_first_correction with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_first_correction"
  match env.find? ``Komorebi.PaperIV.signedRemainderEnvelope_sq with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedRemainderEnvelope_sq"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_normalized_derivative_error with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_normalized_derivative_error"
  match env.find? ``Komorebi.PaperIV.signedFundamentalSector with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedFundamentalSector"
  match env.find? ``Komorebi.PaperIV.signed_cosine_pos with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signed_cosine_pos"
  match env.find? ``Komorebi.PaperIV.cosine_arc_upper with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.cosine_arc_upper"
  match env.find? ``Komorebi.PaperIV.canonicalSignedVertex_upper_boundary with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedVertex_upper_boundary"
  match env.find? ``Komorebi.PaperIV.canonicalSignedVertex_upper_projection with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedVertex_upper_projection"
  logInfo "PAPER_IV_KIND_BATCH_PASS 384 48"
run_cmd do
  let env ← getEnv
  match env.find? ``Komorebi.PaperIV.canonicalSignedVertex_sector_gap with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedVertex_sector_gap"
  match env.find? ``Komorebi.PaperIV.finite_one_term_normalization with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.finite_one_term_normalization"
  match env.find? ``Komorebi.PaperIV.finite_exponential_zero_balance with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.finite_exponential_zero_balance"
  match env.find? ``Komorebi.PaperIV.signedSectorWidth with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedSectorWidth"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_upper_sector_zero_bound with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_upper_sector_zero_bound"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_sector_zero_bound with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_sector_zero_bound"
  match env.find? ``Komorebi.PaperIV.signedSectorWidth_pos with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedSectorWidth_pos"
  match env.find? ``Komorebi.PaperIV.signedRemainder_eventually_small_on_strip with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedRemainder_eventually_small_on_strip"
  match env.find? ``Komorebi.PaperIV.signed_integer_center with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signed_integer_center"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_sector_exhaustion with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_sector_exhaustion"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_rotation with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_rotation"
  match env.find? ``Komorebi.PaperIV.signedFundamentalSector_polar with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedFundamentalSector_polar"
  match env.find? ``Komorebi.PaperIV.exists_signed_sector_rotation with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.exists_signed_sector_rotation"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_global_exhaustion with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_global_exhaustion"
  match env.find? ``Komorebi.PaperIV.signedZeroFrequency_norm with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedZeroFrequency_norm"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_order_rotation with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_order_rotation"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_derivative_rotation with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_derivative_rotation"
  match env.find? ``Komorebi.PaperIV.positive_real_rotation_unique with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.positive_real_rotation_unique"
  match env.find? ``Komorebi.PaperIV.signedZeroCenter_disk_index_unique with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedZeroCenter_disk_index_unique"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_large_zero_orbits with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_large_zero_orbits"
  match env.find? ``Komorebi.PaperIV.signedNormalizationFactor with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedNormalizationFactor"
  match env.find? ``Komorebi.PaperIV.signedNormalizationFactor_ne_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedNormalizationFactor_ne_zero"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_derivative_normalization with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_derivative_normalization"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_relative_derivative_error with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_relative_derivative_error"
  match env.find? ``Komorebi.PaperIV.signed_derivative_leading_norm with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signed_derivative_leading_norm"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_derivative_modulus_error with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_derivative_modulus_error"
  match env.find? ``Komorebi.PaperIV.signedFundamentalSector_of_arg with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedFundamentalSector_of_arg"
  match env.find? ``Komorebi.PaperIV.canonicalSignedRemainder_three_jet_bound with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedRemainder_three_jet_bound"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_two_term_dominance with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_two_term_dominance"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_zero"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_finite_zeros_on_compact with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_finite_zeros_on_compact"
  match env.find? ``Komorebi.PaperIV.onSignedZeroRay with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.onSignedZeroRay"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_eventually_simple_on_rays with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_eventually_simple_on_rays"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_finite_exceptional_zeros with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_finite_exceptional_zeros"
  match env.find? ``Komorebi.PaperIV.entireReducedDenominator with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireReducedDenominator"
  match env.find? ``Komorebi.PaperIV.reducedDenominator_coeff_complex with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedDenominator_coeff_complex"
  match env.find? ``Komorebi.PaperIV.reducedDenominator_coeff_norm with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedDenominator_coeff_norm"
  match env.find? ``Komorebi.PaperIV.reducedDenominator_entire_radius with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedDenominator_entire_radius"
  match env.find? ``Komorebi.PaperIV.analyticAt_entireReducedDenominator with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticAt_entireReducedDenominator"
  match env.find? ``Komorebi.PaperIV.hasSum_entireReducedDenominator with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.hasSum_entireReducedDenominator"
  match env.find? ``Komorebi.PaperIV.entireReducedDenominator_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireReducedDenominator_zero"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_eq_reduced_power with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_eq_reduced_power"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_order_eq_reduced with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_order_eq_reduced"
  match env.find? ``Komorebi.PaperIV.exists_complex_nth_root with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.exists_complex_nth_root"
  match env.find? ``Komorebi.PaperIV.entireReducedDenominator_zero_ne_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireReducedDenominator_zero_ne_zero"
  match env.find? ``Komorebi.PaperIV.entireReducedDenominator_finite_zeros_on_compact with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireReducedDenominator_finite_zeros_on_compact"
  match env.find? ``Komorebi.PaperIV.onSignedZeroRay_power_positive with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.onSignedZeroRay_power_positive"
  match env.find? ``Komorebi.PaperIV.entireReducedDenominator_finite_exceptional_zeros with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireReducedDenominator_finite_exceptional_zeros"
  logInfo "PAPER_IV_KIND_BATCH_PASS 432 48"
run_cmd do
  let env ← getEnv
  match env.find? ``Komorebi.PaperIV.entireReducedDenominator_eventually_positive_simple with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireReducedDenominator_eventually_positive_simple"
  match env.find? ``Komorebi.PaperIV.entireReducedDenominator_two_zero_iff with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireReducedDenominator_two_zero_iff"
  match env.find? ``Komorebi.PaperIV.entireReducedDenominator_two_zero_order_one with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireReducedDenominator_two_zero_order_one"
  match env.find? ``Komorebi.PaperIV.isLocalizedPositiveZero with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.isLocalizedPositiveZero"
  match env.find? ``Komorebi.PaperIV.signedPositiveZero with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedPositiveZero"
  match env.find? ``Komorebi.PaperIV.signedPositiveZero_spec with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedPositiveZero_spec"
  match env.find? ``Komorebi.PaperIV.signedPositiveZero_eq_of_unique with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedPositiveZero_eq_of_unique"
  match env.find? ``Komorebi.PaperIV.signedPositiveZero_local_strings with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedPositiveZero_local_strings"
  match env.find? ``Komorebi.PaperIV.signedPositiveZero_global_strings with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedPositiveZero_global_strings"
  match env.find? ``Komorebi.PaperIV.signedZeroCenter_ge_radius with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedZeroCenter_ge_radius"
  match env.find? ``Komorebi.PaperIV.signedPositiveZero_pos with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedPositiveZero_pos"
  match env.find? ``Komorebi.PaperIV.signedPositiveZero_injective_on_tail with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedPositiveZero_injective_on_tail"
  match env.find? ``Komorebi.PaperIV.reducedPositiveZero with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedPositiveZero"
  match env.find? ``Komorebi.PaperIV.reducedPositiveZero_global_strings with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedPositiveZero_global_strings"
  match env.find? ``Komorebi.PaperIV.reducedPositiveZero_injective_on_tail with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedPositiveZero_injective_on_tail"
  match env.find? ``Komorebi.PaperIV.reducedPositiveZero_local_strings with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedPositiveZero_local_strings"
  match env.find? ``Komorebi.PaperIV.signedZeroCenter_tendsto_atTop with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedZeroCenter_tendsto_atTop"
  match env.find? ``Komorebi.PaperIV.signedPositiveZero_sub_center_isBigO_one with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedPositiveZero_sub_center_isBigO_one"
  match env.find? ``Komorebi.PaperIV.signedPositiveZero_equivalent_center with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedPositiveZero_equivalent_center"
  match env.find? ``Komorebi.PaperIV.signedPositiveZero_tendsto_atTop with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedPositiveZero_tendsto_atTop"
  match env.find? ``Komorebi.PaperIV.reducedPositiveZero_equivalent_center_power with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedPositiveZero_equivalent_center_power"
  match env.find? ``Komorebi.PaperIV.signedPositiveZero_reciprocal_rpow_summable_iff with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedPositiveZero_reciprocal_rpow_summable_iff"
  match env.find? ``Komorebi.PaperIV.reducedPositiveZero_reciprocal_rpow_summable_iff with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedPositiveZero_reciprocal_rpow_summable_iff"
  match env.find? ``Komorebi.PaperIV.reducedPositiveZero_reciprocal_summable with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedPositiveZero_reciprocal_summable"
  match env.find? ``Komorebi.PaperIV.sequenceCounting with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.sequenceCounting"
  match env.find? ``Komorebi.PaperIV.lattice_window_counting with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.lattice_window_counting"
  match env.find? ``Komorebi.PaperIV.signedPositiveZero_lattice_windows with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedPositiveZero_lattice_windows"
  match env.find? ``Komorebi.PaperIV.signedPositiveZero_tail_counting with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedPositiveZero_tail_counting"
  match env.find? ``Komorebi.PaperIV.reducedTailProduct with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedTailProduct"
  match env.find? ``Komorebi.PaperIV.reducedPositiveZero_pos with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedPositiveZero_pos"
  match env.find? ``Komorebi.PaperIV.reducedTail_reciprocal_summable with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedTail_reciprocal_summable"
  match env.find? ``Komorebi.PaperIV.reducedTail_factors_norm_summable with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedTail_factors_norm_summable"
  match env.find? ``Komorebi.PaperIV.reducedTailProduct_multipliable with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedTailProduct_multipliable"
  match env.find? ``Komorebi.PaperIV.reducedTailProduct_uniform_on_compact with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedTailProduct_uniform_on_compact"
  match env.find? ``Komorebi.PaperIV.reducedTailProduct_locally_uniform with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedTailProduct_locally_uniform"
  match env.find? ``Komorebi.PaperIV.analyticAt_reducedTailProduct with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticAt_reducedTailProduct"
  match env.find? ``Komorebi.PaperIV.reducedTailProduct_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedTailProduct_zero"
  match env.find? ``Komorebi.PaperIV.reducedTailProduct_ne_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedTailProduct_ne_zero"
  match env.find? ``Komorebi.PaperIV.reducedTailProduct_zero_iff with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedTailProduct_zero_iff"
  match env.find? ``Komorebi.PaperIV.finiteWeight with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.finiteWeight"
  match env.find? ``Komorebi.PaperIV.finiteWeight_of_finite with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.finiteWeight_of_finite"
  match env.find? ``Komorebi.PaperIV.finiteWeight_mono with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.finiteWeight_mono"
  match env.find? ``Komorebi.PaperIV.finiteWeight_union_le with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.finiteWeight_union_le"
  match env.find? ``Komorebi.PaperIV.finiteWeight_eq_ncard with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.finiteWeight_eq_ncard"
  match env.find? ``Komorebi.PaperIV.finiteWeight_between_tail_and_exceptions with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.finiteWeight_between_tail_and_exceptions"
  match env.find? ``Komorebi.PaperIV.zeroDisk with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.zeroDisk"
  match env.find? ``Komorebi.PaperIV.analyticZeroCount with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticZeroCount"
  match env.find? ``Komorebi.PaperIV.entire_analyticOrderAt_ne_top with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entire_analyticOrderAt_ne_top"
  logInfo "PAPER_IV_KIND_BATCH_PASS 480 48"
run_cmd do
  let env ← getEnv
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_order_ne_top with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_order_ne_top"
  match env.find? ``Komorebi.PaperIV.entireReducedDenominator_order_ne_top with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireReducedDenominator_order_ne_top"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_zeroDisk_finite with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_zeroDisk_finite"
  match env.find? ``Komorebi.PaperIV.entireReducedDenominator_zeroDisk_finite with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireReducedDenominator_zeroDisk_finite"
  match env.find? ``Komorebi.PaperIV.signedZeroEnumeration_exists_ge_three with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedZeroEnumeration_exists_ge_three"
  match env.find? ``Komorebi.PaperIV.signedZeroEnumeration_exists_two with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedZeroEnumeration_exists_two"
  match env.find? ``Komorebi.PaperIV.signedZeroEnumeration_exists with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedZeroEnumeration_exists"
  match env.find? ``Komorebi.PaperIV.canonicalZeroEnumeration with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalZeroEnumeration"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.orbit with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.orbit"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.orbit_norm with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.orbit_norm"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.orbit_injective with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.orbit_injective"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.orbit_zero_simple with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.orbit_zero_simple"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.orbitDisk with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.orbitDisk"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.exceptions with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.exceptions"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.exceptions_finite with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.exceptions_finite"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.orbitDisk_finite_card with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.orbitDisk_finite_card"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.orbitDisk_subset with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.orbitDisk_subset"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.zeroDisk_subset_union with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.zeroDisk_subset_union"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.weighted_count_bounds with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.weighted_count_bounds"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_zero_counting with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_zero_counting"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.reducedRoot with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.reducedRoot"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.reducedDisk with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.reducedDisk"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.reducedExceptions with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.reducedExceptions"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.reducedRoot_norm with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.reducedRoot_norm"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.reducedRoot_injective with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.reducedRoot_injective"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.reducedRoot_zero_simple with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.reducedRoot_zero_simple"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.reducedExceptions_finite with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.reducedExceptions_finite"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.reducedDisk_finite_card with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.reducedDisk_finite_card"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.reducedDisk_subset with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.reducedDisk_subset"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.reducedZeroDisk_subset_union with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.reducedZeroDisk_subset_union"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.reduced_weighted_count_bounds with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.reduced_weighted_count_bounds"
  match env.find? ``Komorebi.PaperIV.entireReducedDenominator_zero_counting_power with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireReducedDenominator_zero_counting_power"
  match env.find? ``Komorebi.PaperIV.entireReducedDenominator_zero_counting with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireReducedDenominator_zero_counting"
  match env.find? ``Komorebi.PaperIV.ZeroPowerSummable with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.ZeroPowerSummable"
  match env.find? ``Komorebi.PaperIV.summable_iff_comp_of_finite_complement with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.summable_iff_comp_of_finite_complement"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.root_equivalent_lattice with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.root_equivalent_lattice"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.root_reciprocal_rpow_summable_iff with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.root_reciprocal_rpow_summable_iff"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.reducedRoot_reciprocal_rpow_summable_iff with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.reducedRoot_reciprocal_rpow_summable_iff"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.orbitZero with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.orbitZero"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.orbitZero_injective with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.orbitZero_injective"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.orbitZero_finite_complement with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.orbitZero_finite_complement"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.reducedZero with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.reducedZero"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.reducedZero_injective with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.reducedZero_injective"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.reducedZero_finite_complement with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.reducedZero_finite_complement"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_zero_power_summable_iff with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_zero_power_summable_iff"
  match env.find? ``Komorebi.PaperIV.entireReducedDenominator_zero_power_summable_iff with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireReducedDenominator_zero_power_summable_iff"
  match env.find? ``Komorebi.PaperIV.entireReducedDenominator_reciprocal_zeros_summable with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireReducedDenominator_reciprocal_zeros_summable"
  match env.find? ``Komorebi.PaperIV.weightedDirichletTerm with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.weightedDirichletTerm"
  logInfo "PAPER_IV_KIND_BATCH_PASS 528 48"
run_cmd do
  let env ← getEnv
  match env.find? ``Komorebi.PaperIV.weightedDirichletTerm_norm with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.weightedDirichletTerm_norm"
  match env.find? ``Komorebi.PaperIV.weightedDirichletTerm_differentiable with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.weightedDirichletTerm_differentiable"
  match env.find? ``Komorebi.PaperIV.weightedDirichletTerm_strip_bound with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.weightedDirichletTerm_strip_bound"
  match env.find? ``Komorebi.PaperIV.weightedDirichlet_locally_uniform with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.weightedDirichlet_locally_uniform"
  match env.find? ``Komorebi.PaperIV.weightedDirichlet_differentiableOn with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.weightedDirichlet_differentiableOn"
  match env.find? ``Komorebi.PaperIV.absoluteZeroZetaTerm with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.absoluteZeroZetaTerm"
  match env.find? ``Komorebi.PaperIV.absoluteZeroZeta with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.absoluteZeroZeta"
  match env.find? ``Komorebi.PaperIV.zero_norm_pos_of_value_at_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.zero_norm_pos_of_value_at_zero"
  match env.find? ``Komorebi.PaperIV.absoluteZeroZetaTerm_norm with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.absoluteZeroZetaTerm_norm"
  match env.find? ``Komorebi.PaperIV.absoluteZeroZeta_summable_norm_iff with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.absoluteZeroZeta_summable_norm_iff"
  match env.find? ``Komorebi.PaperIV.absoluteZeroZeta_locally_uniform with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.absoluteZeroZeta_locally_uniform"
  match env.find? ``Komorebi.PaperIV.absoluteZeroZeta_differentiableOn with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.absoluteZeroZeta_differentiableOn"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_zeta_absolute_convergence with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_zeta_absolute_convergence"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_zeta_locally_uniform with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_zeta_locally_uniform"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_zeta_holomorphic with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_zeta_holomorphic"
  match env.find? ``Komorebi.PaperIV.entireReducedDenominator_zeta_absolute_convergence with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireReducedDenominator_zeta_absolute_convergence"
  match env.find? ``Komorebi.PaperIV.entireReducedDenominator_zeta_locally_uniform with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireReducedDenominator_zeta_locally_uniform"
  match env.find? ``Komorebi.PaperIV.entireReducedDenominator_zeta_holomorphic with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireReducedDenominator_zeta_holomorphic"
  match env.find? ``Komorebi.PaperIV.signedPositiveZero_derivative_asymptotic with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedPositiveZero_derivative_asymptotic"
  match env.find? ``Komorebi.PaperIV.signedPositiveZero_unique_global_strings with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedPositiveZero_unique_global_strings"
  match env.find? ``Komorebi.PaperIV.signedPositiveZero_derivative_rotation with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedPositiveZero_derivative_rotation"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_large_zero_strings with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_large_zero_strings"
  match env.find? ``Komorebi.PaperIV.entireSigned_canonical_conj with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireSigned_canonical_conj"
  match env.find? ``Komorebi.PaperIV.entireSigned_canonical_real with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireSigned_canonical_real"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_derivative_real with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_derivative_real"
  match env.find? ``Komorebi.PaperIV.signed_sine_mul_center with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signed_sine_mul_center"
  match env.find? ``Komorebi.PaperIV.signedZeroCenter_positive_phase with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedZeroCenter_positive_phase"
  match env.find? ``Komorebi.PaperIV.signedZeroCenter_negative_phase with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedZeroCenter_negative_phase"
  match env.find? ``Komorebi.PaperIV.signedDerivativeScale with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedDerivativeScale"
  match env.find? ``Komorebi.PaperIV.signedDerivativeMainTerm with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedDerivativeMainTerm"
  match env.find? ``Komorebi.PaperIV.signedDerivativeScale_pos with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedDerivativeScale_pos"
  match env.find? ``Komorebi.PaperIV.signedDerivativeMainTerm_ne_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedDerivativeMainTerm_ne_zero"
  match env.find? ``Komorebi.PaperIV.signed_derivative_leading_phase with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signed_derivative_leading_phase"
  match env.find? ``Komorebi.PaperIV.signedLeadingCorrection with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedLeadingCorrection"
  match env.find? ``Komorebi.PaperIV.signedLeadingCorrection_eq_real_quotient with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedLeadingCorrection_eq_real_quotient"
  match env.find? ``Komorebi.PaperIV.signedLeadingCorrection_real with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedLeadingCorrection_real"
  match env.find? ``Komorebi.PaperIV.signedRemainderEnvelope_center_tendsto_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedRemainderEnvelope_center_tendsto_zero"
  match env.find? ``Komorebi.PaperIV.signedPositiveZero_first_correction with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedPositiveZero_first_correction"
  match env.find? ``Komorebi.PaperIV.norm_real_phase_sub_one_le with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.norm_real_phase_sub_one_le"
  match env.find? ``Komorebi.PaperIV.relative_error_through_unit_phase with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.relative_error_through_unit_phase"
  match env.find? ``Komorebi.PaperIV.signedPositiveZero_signed_derivative_asymptotic with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedPositiveZero_signed_derivative_asymptotic"
  match env.find? ``Komorebi.PaperIV.signedPositiveZero_eventual_derivative_sign with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedPositiveZero_eventual_derivative_sign"
  match env.find? ``Komorebi.PaperIV.signedPolygonGap_three with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedPolygonGap_three"
  match env.find? ``Komorebi.PaperIV.signedZeroCenter_three with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedZeroCenter_three"
  match env.find? ``Komorebi.PaperIV.canonicalSignedVertex_three_one with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedVertex_three_one"
  match env.find? ``Komorebi.PaperIV.canonicalSignedVertex_three_two with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedVertex_three_two"
  match env.find? ``Komorebi.PaperIV.signedExponentialRemainder_three with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedExponentialRemainder_three"
  match env.find? ``Komorebi.PaperIV.signedLeadingCorrection_three with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedLeadingCorrection_three"
  logInfo "PAPER_IV_KIND_BATCH_PASS 576 48"
run_cmd do
  let env ← getEnv
  match env.find? ``Komorebi.PaperIV.signedPositiveZero_three_correction with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedPositiveZero_three_correction"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_derivative_lower_bound with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_derivative_lower_bound"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_derivative_power_bound with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_derivative_power_bound"
  match env.find? ``Komorebi.PaperIV.branchedDirichletTerm with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.branchedDirichletTerm"
  match env.find? ``Komorebi.PaperIV.branchedDirichletTerm_differentiable with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.branchedDirichletTerm_differentiable"
  match env.find? ``Komorebi.PaperIV.branchedDirichletTerm_norm with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.branchedDirichletTerm_norm"
  match env.find? ``Komorebi.PaperIV.branchedDirichletTerm_strip_bound with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.branchedDirichletTerm_strip_bound"
  match env.find? ``Komorebi.PaperIV.branchedDirichlet_summable_norm with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.branchedDirichlet_summable_norm"
  match env.find? ``Komorebi.PaperIV.branchedDirichlet_locally_uniform with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.branchedDirichlet_locally_uniform"
  match env.find? ``Komorebi.PaperIV.branchedDirichlet_entire with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.branchedDirichlet_entire"
  match env.find? ``Komorebi.PaperIV.branchedDirichlet_halfplane with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.branchedDirichlet_halfplane"
  match env.find? ``Komorebi.PaperIV.SimpleZeros with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SimpleZeros"
  match env.find? ``Komorebi.PaperIV.SimpleZeros.toZero with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SimpleZeros.toZero"
  match env.find? ``Komorebi.PaperIV.SimpleZeros.toZero_injective with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SimpleZeros.toZero_injective"
  match env.find? ``Komorebi.PaperIV.SimpleZeros.order_one with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SimpleZeros.order_one"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_simple_zero_power_summable with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_simple_zero_power_summable"
  match env.find? ``Komorebi.PaperIV.simple_logarithm_re with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.simple_logarithm_re"
  match env.find? ``Komorebi.PaperIV.derivativeZeroWeight with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.derivativeZeroWeight"
  match env.find? ``Komorebi.PaperIV.derivativeZeroWeight_norm with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.derivativeZeroWeight_norm"
  match env.find? ``Komorebi.PaperIV.derivativeZeroWeight_power_summable with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.derivativeZeroWeight_power_summable"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_two_derivative_norm with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_two_derivative_norm"
  match env.find? ``Komorebi.PaperIV.derivativeZeroWeight_two_power_summable with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.derivativeZeroWeight_two_power_summable"
  match env.find? ``Komorebi.PaperIV.derivativeWeightedZeroZetaTerm with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.derivativeWeightedZeroZetaTerm"
  match env.find? ``Komorebi.PaperIV.derivativeWeightedZeroZeta with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.derivativeWeightedZeroZeta"
  match env.find? ``Komorebi.PaperIV.derivativeWeightedZeroZetaTerm_eq with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.derivativeWeightedZeroZetaTerm_eq"
  match env.find? ``Komorebi.PaperIV.derivativeWeightedZeroZeta_summable_norm with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.derivativeWeightedZeroZeta_summable_norm"
  match env.find? ``Komorebi.PaperIV.derivativeWeightedZeroZeta_two_summable_norm with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.derivativeWeightedZeroZeta_two_summable_norm"
  match env.find? ``Komorebi.PaperIV.derivativeWeightedZeroZeta_entire with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.derivativeWeightedZeroZeta_entire"
  match env.find? ``Komorebi.PaperIV.derivativeWeightedZeroZeta_two_holomorphic with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.derivativeWeightedZeroZeta_two_holomorphic"
  match env.find? ``Komorebi.PaperIV.positiveZetaTerm with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.positiveZetaTerm"
  match env.find? ``Komorebi.PaperIV.exponentialZetaDifference with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.exponentialZetaDifference"
  match env.find? ``Komorebi.PaperIV.positiveZetaTerm_entire with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.positiveZetaTerm_entire"
  match env.find? ``Komorebi.PaperIV.exponentialZetaDifference_entire with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.exponentialZetaDifference_entire"
  match env.find? ``Komorebi.PaperIV.real_log_lipschitz_one with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.real_log_lipschitz_one"
  match env.find? ``Komorebi.PaperIV.positiveZetaTerm_norm_le_rpow with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.positiveZetaTerm_norm_le_rpow"
  match env.find? ``Komorebi.PaperIV.exponentialZetaDifference_factor with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.exponentialZetaDifference_factor"
  match env.find? ``Komorebi.PaperIV.summable_polynomial_exponential with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.summable_polynomial_exponential"
  match env.find? ``Komorebi.PaperIV.exponentialZetaDifference_majorant with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.exponentialZetaDifference_majorant"
  match env.find? ``Komorebi.PaperIV.exponentialZetaDifference_locally_uniform with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.exponentialZetaDifference_locally_uniform"
  match env.find? ``Komorebi.PaperIV.exponentialZetaDifference_sum_entire with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.exponentialZetaDifference_sum_entire"
  match env.find? ``Komorebi.PaperIV.hurwitzRegularPart with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.hurwitzRegularPart"
  match env.find? ``Komorebi.PaperIV.hurwitzRegularPart_entire with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.hurwitzRegularPart_entire"
  match env.find? ``Komorebi.PaperIV.hurwitzZeta_meromorphicAt with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.hurwitzZeta_meromorphicAt"
  match env.find? ``Komorebi.PaperIV.hurwitzLatticeModel with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.hurwitzLatticeModel"
  match env.find? ``Komorebi.PaperIV.hurwitzLatticeModel_meromorphicAt with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.hurwitzLatticeModel_meromorphicAt"
  match env.find? ``Komorebi.PaperIV.hurwitzLatticeModel_differentiableAt with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.hurwitzLatticeModel_differentiableAt"
  match env.find? ``Komorebi.PaperIV.hurwitzLatticeModel_residue with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.hurwitzLatticeModel_residue"
  match env.find? ``Komorebi.PaperIV.meromorphicOrderAt_eq_neg_one_of_residue with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.meromorphicOrderAt_eq_neg_one_of_residue"
  logInfo "PAPER_IV_KIND_BATCH_PASS 624 48"
run_cmd do
  let env ← getEnv
  match env.find? ``Komorebi.PaperIV.positiveZetaTerm_mul with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.positiveZetaTerm_mul"
  match env.find? ``Komorebi.PaperIV.positiveZetaTerm_eq_cpow with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.positiveZetaTerm_eq_cpow"
  match env.find? ``Komorebi.PaperIV.positiveZetaTerm_norm with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.positiveZetaTerm_norm"
  match env.find? ``Komorebi.PaperIV.positiveZetaTerm_lattice_hasSum with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.positiveZetaTerm_lattice_hasSum"
  match env.find? ``Komorebi.PaperIV.signedZeroCenter_positive with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedZeroCenter_positive"
  match env.find? ``Komorebi.PaperIV.signedZeroCenter_reciprocal_square_summable with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedZeroCenter_reciprocal_square_summable"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.root_tendsto_atTop with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.root_tendsto_atTop"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.latticeCorrection with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.latticeCorrection"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.latticeCorrection_locally_uniform with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.latticeCorrection_locally_uniform"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.latticeCorrection_entire with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.latticeCorrection_entire"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.positiveZetaTerm_summable with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.positiveZetaTerm_summable"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.latticePrefix with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.latticePrefix"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.latticePrefix_entire with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.latticePrefix_entire"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.root_zeta_eq_model with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.root_zeta_eq_model"
  match env.find? ``Komorebi.PaperIV.tsum_injection_add_complement with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.tsum_injection_add_complement"
  match env.find? ``Komorebi.PaperIV.finite_subtype_tsum_entire with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.finite_subtype_tsum_entire"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.reducedExceptionZeta with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.reducedExceptionZeta"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.absoluteExceptionZeta with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.absoluteExceptionZeta"
  match env.find? ``Komorebi.PaperIV.absoluteZeroZetaTerm_entire with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.absoluteZeroZetaTerm_entire"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.reducedExceptionZeta_entire with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.reducedExceptionZeta_entire"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.absoluteExceptionZeta_entire with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.absoluteExceptionZeta_entire"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.reducedZetaTerm with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.reducedZetaTerm"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.orbitZetaTerm with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.orbitZetaTerm"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.reducedZeta_decomposition with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.reducedZeta_decomposition"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.absoluteZeta_decomposition with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.absoluteZeta_decomposition"
  match env.find? ``Komorebi.PaperIV.reducedZetaCorrection with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedZetaCorrection"
  match env.find? ``Komorebi.PaperIV.absoluteZetaCorrection with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.absoluteZetaCorrection"
  match env.find? ``Komorebi.PaperIV.reducedZetaCorrection_entire with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedZetaCorrection_entire"
  match env.find? ``Komorebi.PaperIV.absoluteZetaCorrection_entire with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.absoluteZetaCorrection_entire"
  match env.find? ``Komorebi.PaperIV.entireReducedDenominator_zeta_eq_hurwitz with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireReducedDenominator_zeta_eq_hurwitz"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_zeta_eq_hurwitz with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_zeta_eq_hurwitz"
  match env.find? ``Komorebi.PaperIV.reducedZetaContinuation with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedZetaContinuation"
  match env.find? ``Komorebi.PaperIV.absoluteZetaContinuation with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.absoluteZetaContinuation"
  match env.find? ``Komorebi.PaperIV.reducedZetaContinuation_meromorphic with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedZetaContinuation_meromorphic"
  match env.find? ``Komorebi.PaperIV.absoluteZetaContinuation_meromorphic with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.absoluteZetaContinuation_meromorphic"
  match env.find? ``Komorebi.PaperIV.reducedZetaContinuation_holomorphic_off_pole with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedZetaContinuation_holomorphic_off_pole"
  match env.find? ``Komorebi.PaperIV.absoluteZetaContinuation_holomorphic_off_pole with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.absoluteZetaContinuation_holomorphic_off_pole"
  match env.find? ``Komorebi.PaperIV.entire_add_preserves_residue with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entire_add_preserves_residue"
  match env.find? ``Komorebi.PaperIV.reducedZetaContinuation_residue with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedZetaContinuation_residue"
  match env.find? ``Komorebi.PaperIV.absoluteZetaContinuation_residue with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.absoluteZetaContinuation_residue"
  match env.find? ``Komorebi.PaperIV.reducedZetaContinuation_simple_pole with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedZetaContinuation_simple_pole"
  match env.find? ``Komorebi.PaperIV.absoluteZetaContinuation_simple_pole with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.absoluteZetaContinuation_simple_pole"
  match env.find? ``Komorebi.PaperIV.branchedZeroZetaTerm with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.branchedZeroZetaTerm"
  match env.find? ``Komorebi.PaperIV.branchedZeroZeta with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.branchedZeroZeta"
  match env.find? ``Komorebi.PaperIV.branchedZeroZetaTerm_entire with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.branchedZeroZetaTerm_entire"
  match env.find? ``Komorebi.PaperIV.RealLogOnReducedTail with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.RealLogOnReducedTail"
  match env.find? ``Komorebi.PaperIV.reducedBranchCorrection with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedBranchCorrection"
  match env.find? ``Komorebi.PaperIV.reducedBranchCorrection_entire with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedBranchCorrection_entire"
  logInfo "PAPER_IV_KIND_BATCH_PASS 672 48"
run_cmd do
  let env ← getEnv
  match env.find? ``Komorebi.PaperIV.branchedZeroZetaTerm_eq_absolute_on_tail with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.branchedZeroZetaTerm_eq_absolute_on_tail"
  match env.find? ``Komorebi.PaperIV.branchedReducedZeta_summable with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.branchedReducedZeta_summable"
  match env.find? ``Komorebi.PaperIV.branchedReducedZeta_eq_absolute_add_entire with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.branchedReducedZeta_eq_absolute_add_entire"
  match env.find? ``Komorebi.PaperIV.branchedReducedZetaContinuation with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.branchedReducedZetaContinuation"
  match env.find? ``Komorebi.PaperIV.branchedReducedZetaContinuation_eq with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.branchedReducedZetaContinuation_eq"
  match env.find? ``Komorebi.PaperIV.branchedReducedZetaContinuation_meromorphic with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.branchedReducedZetaContinuation_meromorphic"
  match env.find? ``Komorebi.PaperIV.branchedReducedZetaContinuation_holomorphic_off_pole with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.branchedReducedZetaContinuation_holomorphic_off_pole"
  match env.find? ``Komorebi.PaperIV.branchedReducedZetaContinuation_residue with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.branchedReducedZetaContinuation_residue"
  match env.find? ``Komorebi.PaperIV.branchedReducedZetaContinuation_simple_pole with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.branchedReducedZetaContinuation_simple_pole"
  match env.find? ``Komorebi.PaperIV.branchedReducedZetaContinuation_difference_entire with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.branchedReducedZetaContinuation_difference_entire"
  match env.find? ``Komorebi.PaperIV.quartic_root_square with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.quartic_root_square"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_four_eq_cos_cosh with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_four_eq_cos_cosh"
  match env.find? ``Komorebi.PaperIV.complex_cos_zero_iff_nat with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.complex_cos_zero_iff_nat"
  match env.find? ``Komorebi.PaperIV.quarticPositiveZero with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.quarticPositiveZero"
  match env.find? ``Komorebi.PaperIV.quarticPositiveZero_pos with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.quarticPositiveZero_pos"
  match env.find? ``Komorebi.PaperIV.quarticPositiveZero_div_sqrt with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.quarticPositiveZero_div_sqrt"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_four_zero_iff with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_four_zero_iff"
  match env.find? ``Komorebi.PaperIV.quarticPositiveZero_simple with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.quarticPositiveZero_simple"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_four_zero_order_one with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_four_zero_order_one"
  match env.find? ``Komorebi.PaperIV.exactLatticeEnumeration with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.exactLatticeEnumeration"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.reducedZero_surjective_of_orbitZero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.reducedZero_surjective_of_orbitZero"
  match env.find? ``Komorebi.PaperIV.SignedZeroEnumeration.exceptions_zero_of_surjective with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.SignedZeroEnumeration.exceptions_zero_of_surjective"
  match env.find? ``Komorebi.PaperIV.zero_zeta_exact_of_lattice with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.zero_zeta_exact_of_lattice"
  match env.find? ``Komorebi.PaperIV.signedZeroCenter_four with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedZeroCenter_four"
  match env.find? ``Komorebi.PaperIV.orderTwo_full_lattice with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.orderTwo_full_lattice"
  match env.find? ``Komorebi.PaperIV.orderFour_full_lattice with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.orderFour_full_lattice"
  match env.find? ``Komorebi.PaperIV.orderTwo_exact_zero_zeta_models with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.orderTwo_exact_zero_zeta_models"
  match env.find? ``Komorebi.PaperIV.orderFour_exact_zero_zeta_models with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.orderFour_exact_zero_zeta_models"
  match env.find? ``Komorebi.PaperIV.entire_zero_of_halfplane with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entire_zero_of_halfplane"
  match env.find? ``Komorebi.PaperIV.zero_zeta_corrections_of_lattice with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.zero_zeta_corrections_of_lattice"
  match env.find? ``Komorebi.PaperIV.orderTwo_zeta_corrections_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.orderTwo_zeta_corrections_zero"
  match env.find? ``Komorebi.PaperIV.orderFour_zeta_corrections_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.orderFour_zeta_corrections_zero"
  match env.find? ``Komorebi.PaperIV.ZeroMultiplicityIndex with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.ZeroMultiplicityIndex"
  match env.find? ``Komorebi.PaperIV.indexedZero with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.indexedZero"
  match env.find? ``Komorebi.PaperIV.fullCanonicalProduct with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.fullCanonicalProduct"
  match env.find? ``Komorebi.PaperIV.zeroMultiplicity_reciprocal_summable with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.zeroMultiplicity_reciprocal_summable"
  match env.find? ``Komorebi.PaperIV.fullCanonicalProduct_factors_summable with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.fullCanonicalProduct_factors_summable"
  match env.find? ``Komorebi.PaperIV.fullCanonicalProduct_multipliable with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.fullCanonicalProduct_multipliable"
  match env.find? ``Komorebi.PaperIV.fullCanonicalProduct_uniform_on_compact with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.fullCanonicalProduct_uniform_on_compact"
  match env.find? ``Komorebi.PaperIV.fullCanonicalProduct_locally_uniform with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.fullCanonicalProduct_locally_uniform"
  match env.find? ``Komorebi.PaperIV.fullCanonicalProduct_entire with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.fullCanonicalProduct_entire"
  match env.find? ``Komorebi.PaperIV.fullCanonicalProduct_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.fullCanonicalProduct_zero"
  match env.find? ``Komorebi.PaperIV.fullCanonicalProduct_ne_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.fullCanonicalProduct_ne_zero"
  match env.find? ``Komorebi.PaperIV.fullCanonicalProduct_zero_iff_index with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.fullCanonicalProduct_zero_iff_index"
  match env.find? ``Komorebi.PaperIV.indexedZero_ne_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.indexedZero_ne_zero"
  match env.find? ``Komorebi.PaperIV.entire_zero_multiplicity_pos with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entire_zero_multiplicity_pos"
  match env.find? ``Komorebi.PaperIV.fullCanonicalProduct_zero_iff with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.fullCanonicalProduct_zero_iff"
  match env.find? ``Komorebi.PaperIV.zeroMultiplicityIndex_countable with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.zeroMultiplicityIndex_countable"
  logInfo "PAPER_IV_KIND_BATCH_PASS 720 48"
run_cmd do
  let env ← getEnv
  match env.find? ``Komorebi.PaperIV.entireReducedDenominator_full_product_properties with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireReducedDenominator_full_product_properties"
  match env.find? ``Komorebi.PaperIV.reciprocalProduct with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reciprocalProduct"
  match env.find? ``Komorebi.PaperIV.reciprocalProduct_locally_uniform with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reciprocalProduct_locally_uniform"
  match env.find? ``Komorebi.PaperIV.reciprocalProduct_entire with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reciprocalProduct_entire"
  match env.find? ``Komorebi.PaperIV.reciprocalProduct_ne_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reciprocalProduct_ne_zero"
  match env.find? ``Komorebi.PaperIV.zeroIndexFiberEquiv with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.zeroIndexFiberEquiv"
  match env.find? ``Komorebi.PaperIV.otherZeroProduct with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.otherZeroProduct"
  match env.find? ``Komorebi.PaperIV.otherZeroProduct_entire with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.otherZeroProduct_entire"
  match env.find? ``Komorebi.PaperIV.otherZeroProduct_ne_zero_at_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.otherZeroProduct_ne_zero_at_zero"
  match env.find? ``Komorebi.PaperIV.fullCanonicalProduct_factor_at_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.fullCanonicalProduct_factor_at_zero"
  match env.find? ``Komorebi.PaperIV.linear_zero_factor_order with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.linear_zero_factor_order"
  match env.find? ``Komorebi.PaperIV.fullCanonicalProduct_order_at_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.fullCanonicalProduct_order_at_zero"
  match env.find? ``Komorebi.PaperIV.fullCanonicalProduct_same_orders with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.fullCanonicalProduct_same_orders"
  match env.find? ``Komorebi.PaperIV.entireReducedDenominator_full_product_same_orders with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireReducedDenominator_full_product_same_orders"
  match env.find? ``Komorebi.PaperIV.canonicalProductQuotient with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalProductQuotient"
  match env.find? ``Komorebi.PaperIV.rawCanonicalProductQuotient_meromorphic with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.rawCanonicalProductQuotient_meromorphic"
  match env.find? ``Komorebi.PaperIV.rawCanonicalProductQuotient_order_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.rawCanonicalProductQuotient_order_zero"
  match env.find? ``Komorebi.PaperIV.canonicalProductQuotient_entire with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalProductQuotient_entire"
  match env.find? ``Komorebi.PaperIV.canonicalProductQuotient_ne_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalProductQuotient_ne_zero"
  match env.find? ``Komorebi.PaperIV.canonicalProductQuotient_eq_div with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalProductQuotient_eq_div"
  match env.find? ``Komorebi.PaperIV.fullCanonicalProduct_times_quotient with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.fullCanonicalProduct_times_quotient"
  match env.find? ``Komorebi.PaperIV.canonicalProductQuotient_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalProductQuotient_zero"
  match env.find? ``Komorebi.PaperIV.entireReducedDenominator_product_quotient with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireReducedDenominator_product_quotient"
  match env.find? ``Komorebi.PaperIV.entire_normalized_exists_log with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entire_normalized_exists_log"
  match env.find? ``Komorebi.PaperIV.entire_realPart_sublinear_constant with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entire_realPart_sublinear_constant"
  match env.find? ``Komorebi.PaperIV.entire_zeroFree_sublinear_logNorm_eq_one with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entire_zeroFree_sublinear_logNorm_eq_one"
  match env.find? ``Komorebi.PaperIV.entireReducedDenominator_product_quotient_has_log with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireReducedDenominator_product_quotient_has_log"
  match env.find? ``Komorebi.PaperIV.entire_logCounting_poles_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entire_logCounting_poles_zero"
  match env.find? ``Komorebi.PaperIV.entire_normalized_proximity_inv_le with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entire_normalized_proximity_inv_le"
  match env.find? ``Komorebi.PaperIV.entire_eventually_codiscrete_ne_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entire_eventually_codiscrete_ne_zero"
  match env.find? ``Komorebi.PaperIV.entire_quotient_proximity_le with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entire_quotient_proximity_le"
  match env.find? ``Komorebi.PaperIV.entire_re_le_three_proximity_exp with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entire_re_le_three_proximity_exp"
  match env.find? ``Komorebi.PaperIV.entire_proximity_le_of_growth with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entire_proximity_le_of_growth"
  match env.find? ``Komorebi.PaperIV.entire_sublinear_factor_rigidity with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entire_sublinear_factor_rigidity"
  match env.find? ``Komorebi.PaperIV.log_one_add_le_rpow_div with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.log_one_add_le_rpow_div"
  match env.find? ``Komorebi.PaperIV.zeroMultiplicity_reciprocal_rpow_summable with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.zeroMultiplicity_reciprocal_rpow_summable"
  match env.find? ``Komorebi.PaperIV.reciprocalPowerMass with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reciprocalPowerMass"
  match env.find? ``Komorebi.PaperIV.reciprocalPowerMass_nonneg with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reciprocalPowerMass_nonneg"
  match env.find? ``Komorebi.PaperIV.fullCanonicalProduct_growth with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.fullCanonicalProduct_growth"
  match env.find? ``Komorebi.PaperIV.entireReducedDenominator_norm_le with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireReducedDenominator_norm_le"
  match env.find? ``Komorebi.PaperIV.entireReducedDenominator_and_product_growth with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireReducedDenominator_and_product_growth"
  match env.find? ``Komorebi.PaperIV.entireReducedDenominator_quotient_eq_one with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireReducedDenominator_quotient_eq_one"
  match env.find? ``Komorebi.PaperIV.entireReducedDenominator_eq_fullCanonicalProduct with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireReducedDenominator_eq_fullCanonicalProduct"
  match env.find? ``Komorebi.PaperIV.entireReducedDenominator_hadamard_uniform with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireReducedDenominator_hadamard_uniform"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_hadamard with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_hadamard"
  match env.find? ``Komorebi.PaperIV.zeroPartialFraction with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.zeroPartialFraction"
  match env.find? ``Komorebi.PaperIV.zeroPartialFraction_uniform_majorant with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.zeroPartialFraction_uniform_majorant"
  match env.find? ``Komorebi.PaperIV.zeroPartialFraction_norm_summable with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.zeroPartialFraction_norm_summable"
  logInfo "PAPER_IV_KIND_BATCH_PASS 768 48"
run_cmd do
  let env ← getEnv
  match env.find? ``Komorebi.PaperIV.zeroPartialFraction_uniform_on_compact with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.zeroPartialFraction_uniform_on_compact"
  match env.find? ``Komorebi.PaperIV.logDeriv_linear_factor with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.logDeriv_linear_factor"
  match env.find? ``Komorebi.PaperIV.fullCanonicalProduct_logDeriv with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.fullCanonicalProduct_logDeriv"
  match env.find? ``Komorebi.PaperIV.entireReducedDenominator_partialFractions with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireReducedDenominator_partialFractions"
  match env.find? ``Komorebi.PaperIV.zeroPartialFraction_locally_uniform with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.zeroPartialFraction_locally_uniform"
  match env.find? ``Komorebi.PaperIV.analyticTransferTangent with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticTransferTangent"
  match env.find? ``Komorebi.PaperIV.analyticTransferTangent_eq_reduced_logDeriv with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticTransferTangent_eq_reduced_logDeriv"
  match env.find? ``Komorebi.PaperIV.analyticTransferTangent_mittagLeffler with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticTransferTangent_mittagLeffler"
  match env.find? ``Komorebi.PaperIV.analyticTransferTangent_mittagLeffler_absolute with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticTransferTangent_mittagLeffler_absolute"
  match env.find? ``Komorebi.PaperIV.analyticTransferTangent_mittagLeffler_locally_uniform with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticTransferTangent_mittagLeffler_locally_uniform"
  match env.find? ``Komorebi.PaperIV.locally_uniform_sum_deriv with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.locally_uniform_sum_deriv"
  match env.find? ``Komorebi.PaperIV.zeroResolventJet with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.zeroResolventJet"
  match env.find? ``Komorebi.PaperIV.zeroResolventJet_hasDerivAt with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.zeroResolventJet_hasDerivAt"
  match env.find? ``Komorebi.PaperIV.zeroResolventJet_locally_uniform with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.zeroResolventJet_locally_uniform"
  match env.find? ``Komorebi.PaperIV.zeroPowerSum with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.zeroPowerSum"
  match env.find? ``Komorebi.PaperIV.zeroPowerSum_hasSum_from_resolvent with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.zeroPowerSum_hasSum_from_resolvent"
  match env.find? ``Komorebi.PaperIV.zeroPowerSum_resolvent_derivative with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.zeroPowerSum_resolvent_derivative"
  match env.find? ``Komorebi.PaperIV.entireReducedDenominator_iteratedDeriv_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireReducedDenominator_iteratedDeriv_zero"
  match env.find? ``Komorebi.PaperIV.zeroResolvent_analyticAt_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.zeroResolvent_analyticAt_zero"
  match env.find? ``Komorebi.PaperIV.reducedZeroPowerSum_convolution with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedZeroPowerSum_convolution"
  match env.find? ``Komorebi.PaperIV.zeroMomentSeries with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.zeroMomentSeries"
  match env.find? ``Komorebi.PaperIV.reducedDenominator_mul_zeroMomentSeries with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedDenominator_mul_zeroMomentSeries"
  match env.find? ``Komorebi.PaperIV.kappaCoeff_eq_zeroPowerSum with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.kappaCoeff_eq_zeroPowerSum"
  match env.find? ``Komorebi.PaperIV.reducedZeroPowerSum_newton with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedZeroPowerSum_newton"
  match env.find? ``Komorebi.PaperIV.transferTangentCoeff_zero_sum with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.transferTangentCoeff_zero_sum"
  match env.find? ``Komorebi.PaperIV.analyticTransferTangent_coefficient_hasSum with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticTransferTangent_coefficient_hasSum"
  match env.find? ``Komorebi.PaperIV.bellInput_zero_sums with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.bellInput_zero_sums"
  match env.find? ``Komorebi.PaperIV.reciprocalCoeff_zero_sum_bell with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reciprocalCoeff_zero_sum_bell"
  match env.find? ``Komorebi.PaperIV.powerSeries_linear_ode_unique with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.powerSeries_linear_ode_unique"
  match env.find? ``Komorebi.PaperIV.thetaZeroBellInput with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.thetaZeroBellInput"
  match env.find? ``Komorebi.PaperIV.thetaZeroBellInput_derivative with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.thetaZeroBellInput_derivative"
  match env.find? ``Komorebi.PaperIV.thetaSeries_eq_zero_bell_exp with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.thetaSeries_eq_zero_bell_exp"
  match env.find? ``Komorebi.PaperIV.thetaCoeff_zero_sum_bell with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.thetaCoeff_zero_sum_bell"
  match env.find? ``Komorebi.PaperIV.differentiableOn_ball_taylor_hasSum with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.differentiableOn_ball_taylor_hasSum"
  match env.find? ``Komorebi.PaperIV.reducedZeroPowerSum_logarithm with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedZeroPowerSum_logarithm"
  match env.find? ``Komorebi.PaperIV.reducedZeroPowerSum_resolvent_hasSum with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedZeroPowerSum_resolvent_hasSum"
  match env.find? ``Komorebi.PaperIV.finite_positive_gap with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.finite_positive_gap"
  match env.find? ``Komorebi.PaperIV.finite_exponential_dominant_bound with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.finite_exponential_dominant_bound"
  match env.find? ``Komorebi.PaperIV.finite_exponential_dominant_tendsto with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.finite_exponential_dominant_tendsto"
  match env.find? ``Komorebi.PaperIV.unit_complex_re_lt_one with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.unit_complex_re_lt_one"
  match env.find? ``Komorebi.PaperIV.canonicalSignedVertex_injective with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedVertex_injective"
  match env.find? ``Komorebi.PaperIV.canonicalSignedVertex_mul_star_self with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedVertex_mul_star_self"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_dominant_ray with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_dominant_ray"
  match env.find? ``Komorebi.PaperIV.diskMaximumModulus with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.diskMaximumModulus"
  match env.find? ``Komorebi.PaperIV.entireGrowthOrder with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireGrowthOrder"
  match env.find? ``Komorebi.PaperIV.entireExponentialType with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireExponentialType"
  match env.find? ``Komorebi.PaperIV.norm_le_diskMaximumModulus with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.norm_le_diskMaximumModulus"
  match env.find? ``Komorebi.PaperIV.diskMaximumModulus_le with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.diskMaximumModulus_le"
  logInfo "PAPER_IV_KIND_BATCH_PASS 816 48"
run_cmd do
  let env ← getEnv
  match env.find? ``Komorebi.PaperIV.log_growth_ratio_of_exp_bounds with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.log_growth_ratio_of_exp_bounds"
  match env.find? ``Komorebi.PaperIV.order_ratio_of_log_growth with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.order_ratio_of_log_growth"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_ray_lower with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_ray_lower"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_maximum_bounds with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_maximum_bounds"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_type_limit with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_type_limit"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_order_limit with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_order_limit"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_order_one with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_order_one"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_type_one with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_type_one"
  match env.find? ``Komorebi.PaperIV.entireReducedDenominator_maximum_bounds with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireReducedDenominator_maximum_bounds"
  match env.find? ``Komorebi.PaperIV.entireReducedDenominator_growth_limit with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireReducedDenominator_growth_limit"
  match env.find? ``Komorebi.PaperIV.entireReducedDenominator_order_limit with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireReducedDenominator_order_limit"
  match env.find? ``Komorebi.PaperIV.entireReducedDenominator_order_exact with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireReducedDenominator_order_exact"
  match env.find? ``Komorebi.PaperIV.rayDirection with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.rayDirection"
  match env.find? ``Komorebi.PaperIV.norm_rayDirection with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.norm_rayDirection"
  match env.find? ``Komorebi.PaperIV.signedProjection with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedProjection"
  match env.find? ``Komorebi.PaperIV.signedIndicator with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedIndicator"
  match env.find? ``Komorebi.PaperIV.signedProjection_cos with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedProjection_cos"
  match env.find? ``Komorebi.PaperIV.signedIndicator_cos with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedIndicator_cos"
  match env.find? ``Komorebi.PaperIV.continuous_signedProjection with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.continuous_signedProjection"
  match env.find? ``Komorebi.PaperIV.continuous_signedIndicator with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.continuous_signedIndicator"
  match env.find? ``Komorebi.PaperIV.signedProjection_le_indicator with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedProjection_le_indicator"
  match env.find? ``Komorebi.PaperIV.canonicalSignedVertex_sum_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedVertex_sum_zero"
  match env.find? ``Komorebi.PaperIV.signedIndicator_nonneg with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedIndicator_nonneg"
  match env.find? ``Komorebi.PaperIV.canonicalSignedVertex_pow with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedVertex_pow"
  match env.find? ``Komorebi.PaperIV.signed_root_in_vertices with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signed_root_in_vertices"
  match env.find? ``Komorebi.PaperIV.unit_complex_same_real with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.unit_complex_same_real"
  match env.find? ``Komorebi.PaperIV.signed_maximizer_strict_of_not_tie with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signed_maximizer_strict_of_not_tie"
  match env.find? ``Komorebi.PaperIV.signedTieDirection with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedTieDirection"
  match env.find? ``Komorebi.PaperIV.signedTieDirection_iff with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedTieDirection_iff"
  match env.find? ``Komorebi.PaperIV.range_erase_nonempty with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.range_erase_nonempty"
  match env.find? ``Komorebi.PaperIV.vertexProjectionGap with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.vertexProjectionGap"
  match env.find? ``Komorebi.PaperIV.directionSeparation with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.directionSeparation"
  match env.find? ``Komorebi.PaperIV.continuous_vertexProjectionGap with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.continuous_vertexProjectionGap"
  match env.find? ``Komorebi.PaperIV.continuous_directionSeparation with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.continuous_directionSeparation"
  match env.find? ``Komorebi.PaperIV.directionSeparation_pos with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.directionSeparation_pos"
  match env.find? ``Komorebi.PaperIV.compact_directions_uniform_gap with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.compact_directions_uniform_gap"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_dominant_error with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_dominant_error"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_compact_dominant_sectors with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_compact_dominant_sectors"
  match env.find? ``Komorebi.PaperIV.alignedRadii with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.alignedRadii"
  match env.find? ``Komorebi.PaperIV.alignedRadii_tendsto with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.alignedRadii_tendsto"
  match env.find? ``Komorebi.PaperIV.alignedRadii_phase with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.alignedRadii_phase"
  match env.find? ``Komorebi.PaperIV.alignedRadii_equal_projection with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.alignedRadii_equal_projection"
  match env.find? ``Komorebi.PaperIV.alignedRadii_lower_projection with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.alignedRadii_lower_projection"
  match env.find? ``Komorebi.PaperIV.finite_unit_exponential_aligned_limit with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.finite_unit_exponential_aligned_limit"
  match env.find? ``Komorebi.PaperIV.log_norm_slope_of_normalized_limit with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.log_norm_slope_of_normalized_limit"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_indicator_upper with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_indicator_upper"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_log_indicator_upper with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_log_indicator_upper"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_real_normalization with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_real_normalization"
  logInfo "PAPER_IV_KIND_BATCH_PASS 864 48"
run_cmd do
  let env ← getEnv
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_indicator_sequence with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_indicator_sequence"
  match env.find? ``Komorebi.PaperIV.limsup_eq_of_upper_and_sequence with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.limsup_eq_of_upper_and_sequence"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_indicator with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_indicator"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_indicator_nonzero_radii with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_indicator_nonzero_radii"
  match env.find? ``Komorebi.PaperIV.IsHilbertTraceClass with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.IsHilbertTraceClass"
  match env.find? ``Komorebi.PaperIV.diagonalHilbertBasis with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.diagonalHilbertBasis"
  match env.find? ``Komorebi.PaperIV.diagonalHilbertBasis_inner with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.diagonalHilbertBasis_inner"
  match env.find? ``Komorebi.PaperIV.diagonalHilbertBasis_norm with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.diagonalHilbertBasis_norm"
  match env.find? ``Komorebi.PaperIV.diagonalHilbertBasis_apply with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.diagonalHilbertBasis_apply"
  match env.find? ``Komorebi.PaperIV.diagonalRankOne with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.diagonalRankOne"
  match env.find? ``Komorebi.PaperIV.diagonalRankOne_norm with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.diagonalRankOne_norm"
  match env.find? ``Komorebi.PaperIV.diagonalRankOne_summable with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.diagonalRankOne_summable"
  match env.find? ``Komorebi.PaperIV.diagonalOperator with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.diagonalOperator"
  match env.find? ``Komorebi.PaperIV.diagonalOperator_traceClass with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.diagonalOperator_traceClass"
  match env.find? ``Komorebi.PaperIV.diagonalOperator_apply with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.diagonalOperator_apply"
  match env.find? ``Komorebi.PaperIV.diagonalOperator_apply_basis with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.diagonalOperator_apply_basis"
  match env.find? ``Komorebi.PaperIV.diagonalOperator_pow_apply with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.diagonalOperator_pow_apply"
  match env.find? ``Komorebi.PaperIV.hilbertBasis_hasSum_squared_coordinates with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.hilbertBasis_hasSum_squared_coordinates"
  match env.find? ``Komorebi.PaperIV.diagonal_trace_double_summable with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.diagonal_trace_double_summable"
  match env.find? ``Komorebi.PaperIV.hilbertBasisTrace with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.hilbertBasisTrace"
  match env.find? ``Komorebi.PaperIV.diagonalOperator_trace_in_any_basis with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.diagonalOperator_trace_in_any_basis"
  match env.find? ``Komorebi.PaperIV.diagonalOperator_trace_eq with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.diagonalOperator_trace_eq"
  match env.find? ``Komorebi.PaperIV.diagonalOperator_pow_eq with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.diagonalOperator_pow_eq"
  match env.find? ``Komorebi.PaperIV.diagonalOperator_pow_trace with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.diagonalOperator_pow_trace"
  match env.find? ``Komorebi.PaperIV.diagonalCompression with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.diagonalCompression"
  match env.find? ``Komorebi.PaperIV.diagonalCompression_eq_diagonal with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.diagonalCompression_eq_diagonal"
  match env.find? ``Komorebi.PaperIV.diagonalCompression_determinant with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.diagonalCompression_determinant"
  match env.find? ``Komorebi.PaperIV.diagonalFredholmDeterminant with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.diagonalFredholmDeterminant"
  match env.find? ``Komorebi.PaperIV.diagonalFredholmDeterminant_compression_limit with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.diagonalFredholmDeterminant_compression_limit"
  match env.find? ``Komorebi.PaperIV.reducedZeroEigenvalue with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedZeroEigenvalue"
  match env.find? ``Komorebi.PaperIV.reducedZeroEigenvalue_norm_summable with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedZeroEigenvalue_norm_summable"
  match env.find? ``Komorebi.PaperIV.reducedZeroOperator with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedZeroOperator"
  match env.find? ``Komorebi.PaperIV.reducedZeroOperator_traceClass with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedZeroOperator_traceClass"
  match env.find? ``Komorebi.PaperIV.reducedZeroOperator_basis with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedZeroOperator_basis"
  match env.find? ``Komorebi.PaperIV.reducedZeroOperator_fredholm with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedZeroOperator_fredholm"
  match env.find? ``Komorebi.PaperIV.reducedZeroOperator_trace_power with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedZeroOperator_trace_power"
  match env.find? ``Komorebi.PaperIV.reducedZeroOperator_finite_determinants_uniform with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reducedZeroOperator_finite_determinants_uniform"
  match env.find? ``Komorebi.PaperIV.powerSumLog with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.powerSumLog"
  match env.find? ``Komorebi.PaperIV.powerSumLog_constantCoeff with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.powerSumLog_constantCoeff"
  match env.find? ``Komorebi.PaperIV.powerSumLog_derivative_coeff with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.powerSumLog_derivative_coeff"
  match env.find? ``Komorebi.PaperIV.homogeneousSeries with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.homogeneousSeries"
  match env.find? ``Komorebi.PaperIV.homogeneousCoeff with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.homogeneousCoeff"
  match env.find? ``Komorebi.PaperIV.homogeneousSeries_constantCoeff with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.homogeneousSeries_constantCoeff"
  match env.find? ``Komorebi.PaperIV.homogeneousSeries_derivative with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.homogeneousSeries_derivative"
  match env.find? ``Komorebi.PaperIV.homogeneousCoeff_recurrence with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.homogeneousCoeff_recurrence"
  match env.find? ``Komorebi.PaperIV.homogeneousGeometric with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.homogeneousGeometric"
  match env.find? ``Komorebi.PaperIV.homogeneousGeometric_coeff with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.homogeneousGeometric_coeff"
  match env.find? ``Komorebi.PaperIV.homogeneousGeometric_constantCoeff with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.homogeneousGeometric_constantCoeff"
  logInfo "PAPER_IV_KIND_BATCH_PASS 912 48"
run_cmd do
  let env ← getEnv
  match env.find? ``Komorebi.PaperIV.homogeneousGeometric_inverse with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.homogeneousGeometric_inverse"
  match env.find? ``Komorebi.PaperIV.homogeneousGeometric_derivative with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.homogeneousGeometric_derivative"
  match env.find? ``Komorebi.PaperIV.finiteHomogeneousSeries with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.finiteHomogeneousSeries"
  match env.find? ``Komorebi.PaperIV.finiteHomogeneousSeries_constantCoeff with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.finiteHomogeneousSeries_constantCoeff"
  match env.find? ``Komorebi.PaperIV.finiteHomogeneousSeries_derivative with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.finiteHomogeneousSeries_derivative"
  match env.find? ``Komorebi.PaperIV.finiteHomogeneousSeries_eq_homogeneous with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.finiteHomogeneousSeries_eq_homogeneous"
  match env.find? ``Komorebi.PaperIV.finiteHomogeneousSeries_monomials with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.finiteHomogeneousSeries_monomials"
  match env.find? ``Komorebi.PaperIV.summable_norm_positive_powers with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.summable_norm_positive_powers"
  match env.find? ``Komorebi.PaperIV.homogeneousCoeff_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.homogeneousCoeff_zero"
  match env.find? ``Komorebi.PaperIV.homogeneousCoeff_succ with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.homogeneousCoeff_succ"
  match env.find? ``Komorebi.PaperIV.homogeneousCoeff_continuous with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.homogeneousCoeff_continuous"
  match env.find? ``Komorebi.PaperIV.homogeneousSeries_congr_positive with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.homogeneousSeries_congr_positive"
  match env.find? ``Komorebi.PaperIV.completeHomogeneous with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.completeHomogeneous"
  match env.find? ``Komorebi.PaperIV.finiteHomogeneousSeries_coefficient_limit with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.finiteHomogeneousSeries_coefficient_limit"
  match env.find? ``Komorebi.PaperIV.completeHomogeneous_monomial_limit with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.completeHomogeneous_monomial_limit"
  match env.find? ``Komorebi.PaperIV.repeatedEigenvalue with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.repeatedEigenvalue"
  match env.find? ``Komorebi.PaperIV.repeatedEigenvalue_norm_summable with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.repeatedEigenvalue_norm_summable"
  match env.find? ``Komorebi.PaperIV.repeatedEigenvalue_powerSum with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.repeatedEigenvalue_powerSum"
  match env.find? ``Komorebi.PaperIV.reciprocalSeries_eq_homogeneous_zero_sums with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reciprocalSeries_eq_homogeneous_zero_sums"
  match env.find? ``Komorebi.PaperIV.reciprocalCoeff_completeHomogeneous with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reciprocalCoeff_completeHomogeneous"
  match env.find? ``Komorebi.PaperIV.reciprocalCoeff_symmetric_polynomial_continuation with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reciprocalCoeff_symmetric_polynomial_continuation"
  match env.find? ``Komorebi.PaperIV.entireNormalizedSection with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireNormalizedSection"
  match env.find? ``Komorebi.PaperIV.normalizedSection_coeff_norm with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.normalizedSection_coeff_norm"
  match env.find? ``Komorebi.PaperIV.normalizedSection_entire_radius with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.normalizedSection_entire_radius"
  match env.find? ``Komorebi.PaperIV.analyticAt_entireNormalizedSection with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticAt_entireNormalizedSection"
  match env.find? ``Komorebi.PaperIV.hasSum_entireNormalizedSection with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.hasSum_entireNormalizedSection"
  match env.find? ``Komorebi.PaperIV.entireNormalizedSection_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireNormalizedSection_zero"
  match env.find? ``Komorebi.PaperIV.entireNormalizedSection_iteratedDeriv_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireNormalizedSection_iteratedDeriv_zero"
  match env.find? ``Komorebi.PaperIV.entireNormalizedSection_transfer with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireNormalizedSection_transfer"
  match env.find? ``Komorebi.PaperIV.entireTransfer_unit_norm_le with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireTransfer_unit_norm_le"
  match env.find? ``Komorebi.PaperIV.finite_sum_le_finsum_nonneg with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.finite_sum_le_finsum_nonneg"
  match env.find? ``Komorebi.PaperIV.entire_divisor_eq_orderNat with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entire_divisor_eq_orderNat"
  match env.find? ``Komorebi.PaperIV.entire_zero_finite_weight_growth with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entire_zero_finite_weight_growth"
  match env.find? ``Komorebi.PaperIV.entire_zero_subtype_weight_growth with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entire_zero_subtype_weight_growth"
  match env.find? ``Komorebi.PaperIV.entire_zero_bounded_finite with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entire_zero_bounded_finite"
  match env.find? ``Komorebi.PaperIV.weighted_growth_summable_large with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.weighted_growth_summable_large"
  match env.find? ``Komorebi.PaperIV.weighted_growth_summable with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.weighted_growth_summable"
  match env.find? ``Komorebi.PaperIV.entire_growth_zeroPowerSummable with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entire_growth_zeroPowerSummable"
  match env.find? ``Komorebi.PaperIV.entire_sublinear_growth_hadamard with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entire_sublinear_growth_hadamard"
  match env.find? ``Komorebi.PaperIV.entireNormalizedSection_norm_le with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireNormalizedSection_norm_le"
  match env.find? ``Komorebi.PaperIV.normalizedSectionGrowthConstant with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.normalizedSectionGrowthConstant"
  match env.find? ``Komorebi.PaperIV.normalizedSectionGrowthConstant_pos with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.normalizedSectionGrowthConstant_pos"
  match env.find? ``Komorebi.PaperIV.entireNormalizedSection_disk_growth with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireNormalizedSection_disk_growth"
  match env.find? ``Komorebi.PaperIV.entireNormalizedSection_zeroPowerSummable with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireNormalizedSection_zeroPowerSummable"
  match env.find? ``Komorebi.PaperIV.entireTransfer_positive_ray with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireTransfer_positive_ray"
  match env.find? ``Komorebi.PaperIV.log_growth_ratio_of_polynomial_exp_bounds with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.log_growth_ratio_of_polynomial_exp_bounds"
  match env.find? ``Komorebi.PaperIV.entireTransfer_positive_ray_lower with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireTransfer_positive_ray_lower"
  match env.find? ``Komorebi.PaperIV.entireNormalizedSection_maximum_bounds with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireNormalizedSection_maximum_bounds"
  logInfo "PAPER_IV_KIND_BATCH_PASS 960 48"
run_cmd do
  let env ← getEnv
  match env.find? ``Komorebi.PaperIV.entireNormalizedSection_growth_limit with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireNormalizedSection_growth_limit"
  match env.find? ``Komorebi.PaperIV.entireNormalizedSection_order_exact with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireNormalizedSection_order_exact"
  match env.find? ``Komorebi.PaperIV.entireNormalizedSection_hadamard with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireNormalizedSection_hadamard"
  match env.find? ``Komorebi.PaperIV.entireNormalizedSection_hadamard_uniform with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireNormalizedSection_hadamard_uniform"
  match env.find? ``Komorebi.PaperIV.analyticTaylorSeries_entireNormalizedSection with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticTaylorSeries_entireNormalizedSection"
  match env.find? ``Komorebi.PaperIV.normalized_zeroMomentSeries with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.normalized_zeroMomentSeries"
  match env.find? ``Komorebi.PaperIV.normalized_zeroPowerSum with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.normalized_zeroPowerSum"
  match env.find? ``Komorebi.PaperIV.bellInput_normalized_zeros with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.bellInput_normalized_zeros"
  match env.find? ``Komorebi.PaperIV.residuePowerCoeff_zero_sum_bell with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.residuePowerCoeff_zero_sum_bell"
  match env.find? ``Komorebi.PaperIV.powerSeries_eq_of_derivative_constant with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.powerSeries_eq_of_derivative_constant"
  match env.find? ``Komorebi.PaperIV.analyticTaylorSeries_log with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticTaylorSeries_log"
  match env.find? ``Komorebi.PaperIV.analyticTaylorSeries_exp with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticTaylorSeries_exp"
  match env.find? ``Komorebi.PaperIV.normalizedAnalyticPower with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.normalizedAnalyticPower"
  match env.find? ``Komorebi.PaperIV.normalizedAnalyticPower_taylor with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.normalizedAnalyticPower_taylor"
  match env.find? ``Komorebi.PaperIV.normalizedAnalyticPower_zero_sum_bell with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.normalizedAnalyticPower_zero_sum_bell"
  match env.find? ``Komorebi.PaperIV.analyticTaylorSeries with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticTaylorSeries"
  match env.find? ``Komorebi.PaperIV.analyticTaylorSeries_coeff with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticTaylorSeries_coeff"
  match env.find? ``Komorebi.PaperIV.analyticTaylorSeries_constantCoeff with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticTaylorSeries_constantCoeff"
  match env.find? ``Komorebi.PaperIV.analyticTaylorSeries_congr with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticTaylorSeries_congr"
  match env.find? ``Komorebi.PaperIV.analyticTaylorSeries_mul with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticTaylorSeries_mul"
  match env.find? ``Komorebi.PaperIV.analyticTaylorSeries_add with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticTaylorSeries_add"
  match env.find? ``Komorebi.PaperIV.analyticTaylorSeries_const with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticTaylorSeries_const"
  match env.find? ``Komorebi.PaperIV.analyticTaylorSeries_pow with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticTaylorSeries_pow"
  match env.find? ``Komorebi.PaperIV.analyticTaylorSeries_inverse_product with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticTaylorSeries_inverse_product"
  match env.find? ``Komorebi.PaperIV.analyticTaylorSeries_neg with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticTaylorSeries_neg"
  match env.find? ``Komorebi.PaperIV.analyticTaylorSeries_deriv with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticTaylorSeries_deriv"
  match env.find? ``Komorebi.PaperIV.analyticTaylorSeries_zeroResolvent with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticTaylorSeries_zeroResolvent"
  match env.find? ``Komorebi.PaperIV.hadamard_taylor_zeroMoment_identity with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.hadamard_taylor_zeroMoment_identity"
  match env.find? ``Komorebi.PaperIV.analyticTaylorCoefficient with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticTaylorCoefficient"
  match env.find? ``Komorebi.PaperIV.analyticTaylorCoefficient_norm_le with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticTaylorCoefficient_norm_le"
  match env.find? ``Komorebi.PaperIV.analyticTaylorCoefficient_isBigO with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticTaylorCoefficient_isBigO"
  match env.find? ``Komorebi.PaperIV.analyticTaylorCoefficient_block_error with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticTaylorCoefficient_block_error"
  match env.find? ``Komorebi.PaperIV.principalPartSeries with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.principalPartSeries"
  match env.find? ``Komorebi.PaperIV.principalPartSeries_coefficient with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.principalPartSeries_coefficient"
  match env.find? ``Komorebi.PaperIV.principalPartSeries_inverse with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.principalPartSeries_inverse"
  match env.find? ``Komorebi.PaperIV.lower_principal_part_choose_bound with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.lower_principal_part_choose_bound"
  match env.find? ``Komorebi.PaperIV.poleTerm with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.poleTerm"
  match env.find? ``Komorebi.PaperIV.polePrincipalPart with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.polePrincipalPart"
  match env.find? ``Komorebi.PaperIV.rawPoleRemainder with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.rawPoleRemainder"
  match env.find? ``Komorebi.PaperIV.poleTerm_analyticAt with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.poleTerm_analyticAt"
  match env.find? ``Komorebi.PaperIV.poleTerm_meromorphicAt with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.poleTerm_meromorphicAt"
  match env.find? ``Komorebi.PaperIV.polePrincipalPart_analyticAt with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.polePrincipalPart_analyticAt"
  match env.find? ``Komorebi.PaperIV.rawPoleRemainder_meromorphic with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.rawPoleRemainder_meromorphic"
  match env.find? ``Komorebi.PaperIV.rawPoleRemainder_analyticAt with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.rawPoleRemainder_analyticAt"
  match env.find? ``Komorebi.PaperIV.meromorphicOrderAt_nonneg_of_bounded with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.meromorphicOrderAt_nonneg_of_bounded"
  match env.find? ``Komorebi.PaperIV.rawPoleRemainder_bounded_at_pole with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.rawPoleRemainder_bounded_at_pole"
  match env.find? ``Komorebi.PaperIV.removedPoleRemainder with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.removedPoleRemainder"
  match env.find? ``Komorebi.PaperIV.removedPoleRemainder_analyticOnNhd with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.removedPoleRemainder_analyticOnNhd"
  logInfo "PAPER_IV_KIND_BATCH_PASS 1008 48"
run_cmd do
  let env ← getEnv
  match env.find? ``Komorebi.PaperIV.removedPoleRemainder_eq_raw with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.removedPoleRemainder_eq_raw"
  match env.find? ``Komorebi.PaperIV.analyticTaylorSeries_sub with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticTaylorSeries_sub"
  match env.find? ``Komorebi.PaperIV.analyticTaylorSeries_finsetSum with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticTaylorSeries_finsetSum"
  match env.find? ``Komorebi.PaperIV.analyticTaylorSeries_id with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticTaylorSeries_id"
  match env.find? ``Komorebi.PaperIV.analyticTaylorSeries_poleTerm with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticTaylorSeries_poleTerm"
  match env.find? ``Komorebi.PaperIV.analyticTaylorCoefficient_principalPart with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticTaylorCoefficient_principalPart"
  match env.find? ``Komorebi.PaperIV.analyticTaylorSeries_canonicalSignedDenominator with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticTaylorSeries_canonicalSignedDenominator"
  match env.find? ``Komorebi.PaperIV.reciprocalSeries_nat with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reciprocalSeries_nat"
  match env.find? ``Komorebi.PaperIV.analyticTaylorSeries_reciprocal_signed with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticTaylorSeries_reciprocal_signed"
  match env.find? ``Komorebi.PaperIV.reciprocalCoeff_analyticTaylor with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reciprocalCoeff_analyticTaylor"
  match env.find? ``Komorebi.PaperIV.poleNumerator with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.poleNumerator"
  match env.find? ``Komorebi.PaperIV.canonicalPoleCoefficient with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalPoleCoefficient"
  match env.find? ``Komorebi.PaperIV.poleNumerator_analyticAt with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.poleNumerator_analyticAt"
  match env.find? ``Komorebi.PaperIV.canonicalPoleCoefficient_leading with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalPoleCoefficient_leading"
  match env.find? ``Komorebi.PaperIV.poleNumerator_identity with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.poleNumerator_identity"
  match env.find? ``Komorebi.PaperIV.polePrincipalPart_scaled with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.polePrincipalPart_scaled"
  match env.find? ``Komorebi.PaperIV.canonicalPoleCoefficient_local_bound with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalPoleCoefficient_local_bound"
  match env.find? ``Komorebi.PaperIV.polePrincipalPart_scaled_general with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.polePrincipalPart_scaled_general"
  match env.find? ``Komorebi.PaperIV.polePrincipalPart_scaled_limit with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.polePrincipalPart_scaled_limit"
  match env.find? ``Komorebi.PaperIV.principalPart_leading_coefficient with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.principalPart_leading_coefficient"
  match env.find? ``Komorebi.PaperIV.removedPoleRemainder_taylor with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.removedPoleRemainder_taylor"
  match env.find? ``Komorebi.PaperIV.nearest_pole_taylor_bound with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.nearest_pole_taylor_bound"
  match env.find? ``Komorebi.PaperIV.reciprocalCoeff_nearest_pole_bound with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reciprocalCoeff_nearest_pole_bound"
  match env.find? ``Komorebi.PaperIV.principalCoefficientSum with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.principalCoefficientSum"
  match env.find? ``Komorebi.PaperIV.leadingPoleCoefficient with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.leadingPoleCoefficient"
  match env.find? ``Komorebi.PaperIV.lowerPrincipalConstant with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.lowerPrincipalConstant"
  match env.find? ``Komorebi.PaperIV.lowerPrincipalConstant_nonneg with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.lowerPrincipalConstant_nonneg"
  match env.find? ``Komorebi.PaperIV.lowerPrincipalConstant_one with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.lowerPrincipalConstant_one"
  match env.find? ``Komorebi.PaperIV.principalCoefficientSum_split with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.principalCoefficientSum_split"
  match env.find? ``Komorebi.PaperIV.principalCoefficientSum_leading_error with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.principalCoefficientSum_leading_error"
  match env.find? ``Komorebi.PaperIV.principalCoefficientSum_one with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.principalCoefficientSum_one"
  match env.find? ``Komorebi.PaperIV.reciprocalCoeff_leading_bound with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reciprocalCoeff_leading_bound"
  match env.find? ``Komorebi.PaperIV.leadingZeroWeight with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.leadingZeroWeight"
  match env.find? ``Komorebi.PaperIV.leadingZeroWeight_rotation with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.leadingZeroWeight_rotation"
  match env.find? ``Komorebi.PaperIV.leadingPoleCoefficient_eq_zero_weights with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.leadingPoleCoefficient_eq_zero_weights"
  match env.find? ``Komorebi.PaperIV.leading_zero_sum_orbit_reduction with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.leading_zero_sum_orbit_reduction"
  match env.find? ``Komorebi.PaperIV.reciprocalCoeff_orbit_leading_bound with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reciprocalCoeff_orbit_leading_bound"
  match env.find? ``Komorebi.PaperIV.cosineNearestZeros with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.cosineNearestZeros"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_two_cos with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_two_cos"
  match env.find? ``Komorebi.PaperIV.cosineNearestZeros_norm with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.cosineNearestZeros_norm"
  match env.find? ``Komorebi.PaperIV.cosineNearestZeros_root with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.cosineNearestZeros_root"
  match env.find? ``Komorebi.PaperIV.cosineNearestZeros_simple with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.cosineNearestZeros_simple"
  match env.find? ``Komorebi.PaperIV.cosine_nearest_zero_exhaustion with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.cosine_nearest_zero_exhaustion"
  match env.find? ``Komorebi.PaperIV.secant_leading_coefficient with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.secant_leading_coefficient"
  match env.find? ``Komorebi.PaperIV.secant_coefficient_error with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.secant_coefficient_error"
  match env.find? ``Komorebi.PaperIV.secantMainTerm with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.secantMainTerm"
  match env.find? ``Komorebi.PaperIV.secantMainTerm_norm with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.secantMainTerm_norm"
  match env.find? ``Komorebi.PaperIV.secantMainTerm_ne_zero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.secantMainTerm_ne_zero"
  logInfo "PAPER_IV_KIND_BATCH_PASS 1056 48"
run_cmd do
  let env ← getEnv
  match env.find? ``Komorebi.PaperIV.secant_relative_error with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.secant_relative_error"
  match env.find? ``Komorebi.PaperIV.secant_coefficient_ratio_limit with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.secant_coefficient_ratio_limit"
  match env.find? ``Komorebi.PaperIV.secant_coefficient_asymptotic with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.secant_coefficient_asymptotic"
  match env.find? ``Komorebi.PaperIV.pointwiseRootAverage with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.pointwiseRootAverage"
  match env.find? ``Komorebi.PaperIV.root_weight_sum with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.root_weight_sum"
  match env.find? ``Komorebi.PaperIV.mapsTo_root_pow with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.mapsTo_root_pow"
  match env.find? ``Komorebi.PaperIV.pointwiseRootAverage_covariant with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.pointwiseRootAverage_covariant"
  match env.find? ``Komorebi.PaperIV.pointwiseRootAverage_of_covariant with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.pointwiseRootAverage_of_covariant"
  match env.find? ``Komorebi.PaperIV.pointwiseRootAverage_projector with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.pointwiseRootAverage_projector"
  match env.find? ``Komorebi.PaperIV.pointwiseRootAverage_resolution with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.pointwiseRootAverage_resolution"
  match env.find? ``Komorebi.PaperIV.differentiableOn_pointwiseRootAverage with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.differentiableOn_pointwiseRootAverage"
  match env.find? ``Komorebi.PaperIV.pointwiseRootAverage_range_iff with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.pointwiseRootAverage_range_iff"
  match env.find? ``Komorebi.PaperIV.pointwiseRootAverage_sum with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.pointwiseRootAverage_sum"
  match env.find? ``Komorebi.PaperIV.pointwiseRootAverage_product with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.pointwiseRootAverage_product"
  match env.find? ``Komorebi.PaperIV.pointwiseRootAverage_hasSum with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.pointwiseRootAverage_hasSum"
  match env.find? ``Komorebi.PaperIV.pointwiseRootAverage_scaled_exp with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.pointwiseRootAverage_scaled_exp"
  match env.find? ``Komorebi.PaperIV.entireTransfer_addition with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireTransfer_addition"
  match env.find? ``Komorebi.PaperIV.signed_addition_weight with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signed_addition_weight"
  match env.find? ``Komorebi.PaperIV.entireSigned_addition with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireSigned_addition"
  match env.find? ``Komorebi.PaperIV.IsLogarithmOn with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.IsLogarithmOn"
  match env.find? ``Komorebi.PaperIV.logarithmPower with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.logarithmPower"
  match env.find? ``Komorebi.PaperIV.logarithmPower_add with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.logarithmPower_add"
  match env.find? ``Komorebi.PaperIV.IsLogarithmOn.nonzero with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.IsLogarithmOn.nonzero"
  match env.find? ``Komorebi.PaperIV.IsLogarithmOn.deriv with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.IsLogarithmOn.deriv"
  match env.find? ``Komorebi.PaperIV.hasDerivAt_logarithmPower with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.hasDerivAt_logarithmPower"
  match env.find? ``Komorebi.PaperIV.reciprocal_fixed_log_derivative with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reciprocal_fixed_log_derivative"
  match env.find? ``Komorebi.PaperIV.analyticDifferentialBell with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticDifferentialBell"
  match env.find? ``Komorebi.PaperIV.analyticOnNhd_differentialBell with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticOnNhd_differentialBell"
  match env.find? ``Komorebi.PaperIV.iteratedDeriv_eq_analyticDifferentialBell with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.iteratedDeriv_eq_analyticDifferentialBell"
  match env.find? ``Komorebi.PaperIV.analytic_higher_riccati with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analytic_higher_riccati"
  match env.find? ``Komorebi.PaperIV.truncatedDifferentialOperator_apply with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.truncatedDifferentialOperator_apply"
  match env.find? ``Komorebi.PaperIV.truncatedDifferentialOperator_egfAction with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.truncatedDifferentialOperator_egfAction"
  match env.find? ``Komorebi.PaperIV.residueAppell_operator_forward with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.residueAppell_operator_forward"
  match env.find? ``Komorebi.PaperIV.residueAppell_operator_inverse with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.residueAppell_operator_inverse"
  match env.find? ``Komorebi.PaperIV.canonicalSignedDenominator_one with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.canonicalSignedDenominator_one"
  match env.find? ``Komorebi.PaperIV.analyticTransferTangent_one with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticTransferTangent_one"
  match env.find? ``Komorebi.PaperIV.transferTangentCoeff_one_order with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.transferTangentCoeff_one_order"
  match env.find? ``Komorebi.PaperIV.analyticTransferTangent_one_hasSum with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticTransferTangent_one_hasSum"
  match env.find? ``Komorebi.PaperIV.analyticTransferTangent_hasSum_all_orders with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.analyticTransferTangent_hasSum_all_orders"
  match env.find? ``Komorebi.PaperIV.reciprocalCoeff_two_compact with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reciprocalCoeff_two_compact"
  match env.find? ``Komorebi.PaperIV.reciprocalCoeff_three_compact with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reciprocalCoeff_three_compact"
  match env.find? ``Komorebi.PaperIV.newtonHessenberg with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.newtonHessenberg"
  match env.find? ``Komorebi.PaperIV.newtonHessenberg_det with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.newtonHessenberg_det"
  match env.find? ``Komorebi.PaperIV.reciprocalOrdCoeff_newton_determinant with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.reciprocalOrdCoeff_newton_determinant"
  match env.find? ``Komorebi.PaperIV.residueHypergeometricParameters with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.residueHypergeometricParameters"
  match env.find? ``Komorebi.PaperIV.residueHypergeometricParameters_card with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.residueHypergeometricParameters_card"
  match env.find? ``Komorebi.PaperIV.residueHypergeometricParameters_re_pos with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.residueHypergeometricParameters_re_pos"
  match env.find? ``Komorebi.PaperIV.regularized_zeroF_normalization with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.regularized_zeroF_normalization"
  logInfo "PAPER_IV_KIND_BATCH_PASS 1104 48"
run_cmd do
  let env ← getEnv
  match env.find? ``Komorebi.PaperIV.residueHypergeometric with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.residueHypergeometric"
  match env.find? ``Komorebi.PaperIV.residueHypergeometric_hasSum with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.residueHypergeometric_hasSum"
  match env.find? ``Komorebi.PaperIV.entireTransfer_hypergeometric with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.entireTransfer_hypergeometric"
  match env.find? ``Komorebi.PaperIV.finiteAlgebraExponential with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.finiteAlgebraExponential"
  match env.find? ``Komorebi.PaperIV.hasSum_cyclicAlgebra_exponential with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.hasSum_cyclicAlgebra_exponential"
  match env.find? ``Komorebi.PaperIV.hasSum_signedAlgebra_exponential with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.hasSum_signedAlgebra_exponential"
  match env.find? ``Komorebi.PaperIV.cyclicAlgebraNormedAddCommGroup with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.cyclicAlgebraNormedAddCommGroup"
  match env.find? ``Komorebi.PaperIV.cyclicAlgebraNormedSpace with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.cyclicAlgebraNormedSpace"
  match env.find? ``Komorebi.PaperIV.signedAlgebraNormedAddCommGroup with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedAlgebraNormedAddCommGroup"
  match env.find? ``Komorebi.PaperIV.signedAlgebraNormedSpace with
  | some (.defnInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedAlgebraNormedSpace"
  match env.find? ``Komorebi.PaperIV.cyclicAlgebra_pointwise_exponential with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.cyclicAlgebra_pointwise_exponential"
  match env.find? ``Komorebi.PaperIV.signedAlgebra_pointwise_exponential with
  | some (.thmInfo _) => pure ()
  | _ => throwError "PAPER_IV_KIND_MISMATCH: Komorebi.PaperIV.signedAlgebra_pointwise_exponential"
  logInfo "PAPER_IV_KIND_BATCH_PASS 1152 12"
run_cmd do
  logInfo "PAPER_IV_KIND_PASS 1164"
