import KomorebiPaperIV.DiagonalFredholm
import KomorebiPaperIV.NormalizedZeroBell
import KomorebiPaperIV.NormalizedExactOrder
import KomorebiPaperIV.SecantAsymptotic
import KomorebiPaperIV.SharpGrowth
import KomorebiPaperIV.IndicatorLimit
import KomorebiPaperIV.CubicZeroCorrection
import KomorebiPaperIV.DerivativeWeightedZeta
import KomorebiPaperIV.ZeroZetaConvergence
import KomorebiPaperIV.LargeZeroCompletion
import KomorebiPaperIV.ZeroSequenceCounting
import KomorebiPaperIV.ReducedCanonicalProduct
import KomorebiPaperIV.ExactZetaModels
import KomorebiPaperIV.CanonicalProductQuotient
import KomorebiPaperIV.Wronskians
import KomorebiPaperIV.BellCompletion
import KomorebiPaperIV.CompanionBridge
import KomorebiPaperIV.ExponentialBounds
import KomorebiPaperIV.CompanionSpectrum
import KomorebiPaperIV.ZeroGeometry
import KomorebiPaperIV.ZeroMomentLogarithm
import KomorebiPaperIV.ThetaZeroBell

import KomorebiPaperIV.SignedZeroCorrection
import KomorebiPaperIV.SignedDerivativeAsymptotics
import KomorebiPaperIV.SignedDominance

/-! Independent closed specializations of the new public API. -/

namespace Komorebi.PaperIVChecks
open Komorebi.PaperIV

/-- The entire signed denominator at order two is actually cosine. -/
theorem signed_two_cos (z : ℂ) :
    entireSigned 2 0 (-1) Complex.I z = Complex.cos z := by
  rw [entireSigned_zero_eq_average]
  simp [Finset.sum_range_succ, Complex.cos, mul_comm]
  ring

/-- Nonvacuity of the signed Wronskian hypotheses. -/
theorem signed_two_wronskian (z : ℂ) :
    analyticWronskian (fun j : Fin 2 => entireSigned 2 j.val (-1) Complex.I) z = 1 := by
  apply signedWronskian_eq_one (by decide)
  · exact IsPrimitiveRoot.neg_one 0 (by decide)
  · exact Complex.I_sq

/-- The transfer Wronskian has the required dependence on the scale. -/
theorem transfer_two_wronskian (lambda z : ℂ) :
    analyticWronskian (fun j : Fin 2 => entireTransfer 2 j.val (-1) lambda) z = lambda := by
  simpa using transferWronskian_eq (by decide : 1 < 2)
    (IsPrimitiveRoot.neg_one 0 (by decide) : IsPrimitiveRoot (-1 : ℂ) 2) lambda z

/-- A positive-degree reciprocal polynomial vanishes at parameter zero. -/
theorem reciprocal_positive_zero (N : ℕ) {n : ℕ} (hn : 0 < n) :
    (reciprocalCoeffPolynomialOver (K := ℂ) N n).eval 0 = 0 := by
  rw [eval_reciprocalCoeffPolynomialOver, reciprocalCoeff_zero_parameter_of_pos N hn]

/-- A concrete degree-two leading coefficient checks the factorial normalization. -/
theorem reciprocal_two_leading :
    (reciprocalCoeffPolynomialOver (K := ℂ) 2 2).coeff 2 = 3 := by
  rw [coeff_reciprocalCoeffPolynomialOver_parameterDegree]
  norm_num

/-- Determinant one holds at an odd order, without root-certificate arguments. -/
theorem companion_three_det (z : ℂ) : (signedFundamentalMatrix 3 z).det = 1 :=
  signedFundamentalMatrix_det_one (by decide) z

/-- The real root -1 appears in the odd-order spectrum. -/
theorem companion_three_negative_eigenvalue :
    (-1 : ℂ) ∈ spectrum ℂ (signedShiftMatrix (R := ℂ) 3) := by
  rw [signedShiftMatrix_mem_spectrum_iff (by decide)]
  norm_num

/-- The first positive cosine zero has analytic multiplicity exactly one. -/
theorem signed_two_first_zero_simple :
    analyticOrderAt (entireSigned 2 0 (-1) Complex.I) ((Real.pi : ℂ) / 2) = 1 := by
  apply entireSigned_two_zero_order_one (IsPrimitiveRoot.neg_one 0 (by decide)) Complex.I_sq
  rw [entireSigned_two_zero_iff (IsPrimitiveRoot.neg_one 0 (by decide)) Complex.I_sq]
  exact ⟨0, by norm_num⟩

/-- Exact cancellation is included in the quantitative uniqueness theorem. -/
theorem exact_cancellation_unique :
    ∃! k : ℤ, ‖(Real.pi : ℂ) * Complex.I - oddExponentialCenter k‖ ≤ 0 := by
  have h := near_cancellation_unique (w := (Real.pi : ℂ) * Complex.I)
    (by simp [Complex.exp_pi_mul_I])
  simpa [Complex.exp_pi_mul_I] using h

end Komorebi.PaperIVChecks

namespace Komorebi.PaperIVChecks
open Komorebi.PaperIV

/-- A concrete quarter-turn preserves the actual order-four denominator. -/
theorem quartic_quarter_turn (z : ℂ) :
    canonicalSignedDenominator 4 (Complex.I * z) = canonicalSignedDenominator 4 z := by
  apply canonicalSignedDenominator_rotation (by decide)
  norm_num [show Complex.I ^ 4 = (Complex.I ^ 2) ^ 2 by ring, Complex.I_sq]

/-- The same quarter-turn has the inverse derivative weight. -/
theorem quartic_derivative_quarter_turn (z : ℂ) :
    deriv (canonicalSignedDenominator 4) (Complex.I * z) * Complex.I =
      deriv (canonicalSignedDenominator 4) z := by
  apply canonicalSignedDenominator_derivative_rotation (by decide)
  norm_num [show Complex.I ^ 4 = (Complex.I ^ 2) ^ 2 by ring, Complex.I_sq]

/-- The derived cubic strip width is log(2)/sqrt(3). -/
theorem cubic_sector_width : signedSectorWidth 3 = Real.log 2 / Real.sqrt 3 := by
  unfold signedSectorWidth
  norm_num [Real.sin_pi_div_three]
  ring

#print axioms quartic_quarter_turn
#print axioms quartic_derivative_quarter_turn
#print axioms cubic_sector_width
end Komorebi.PaperIVChecks

#print axioms Komorebi.PaperIVChecks.signed_two_cos
#print axioms Komorebi.PaperIVChecks.signed_two_wronskian
#print axioms Komorebi.PaperIVChecks.transfer_two_wronskian
#print axioms Komorebi.PaperIVChecks.reciprocal_positive_zero
#print axioms Komorebi.PaperIVChecks.reciprocal_two_leading
#print axioms Komorebi.PaperIVChecks.companion_three_det
#print axioms Komorebi.PaperIVChecks.companion_three_negative_eigenvalue
#print axioms Komorebi.PaperIVChecks.signed_two_first_zero_simple
#print axioms Komorebi.PaperIVChecks.exact_cancellation_unique

namespace Komorebi.PaperIVChecks
open Komorebi.PaperIV

/-- A nonzero positive constant remainder exercises the local existence theorem. -/
theorem nonzero_remainder_unique_zero :
    ∃! z : ℂ, z ∈ Metric.closedBall ((Real.pi : ℂ) * Complex.I) 1 ∧
      1 + Complex.exp z + (1 / 4 : ℂ) = 0 := by
  have h := perturbed_exponential_unique_zero (a := 1)
    (t := (Real.pi : ℂ) * Complex.I) (R := fun _ => (1 / 4 : ℂ))
    (R' := fun _ => (0 : ℂ)) (by norm_num)
    (by simp)
    (by intro z hz; norm_num)
    (by intro z hz; exact hasDerivAt_const z (1 / 4 : ℂ))
    (by intro z hz; norm_num)
  simpa using h

/-- The cubic polygon has the exact spectral gap 3/2. -/
theorem cubic_polygon_gap : signedPolygonGap 3 = 3 / 2 := by
  unfold signedPolygonGap
  norm_num only [Nat.cast_ofNat, Real.cos_pi_div_three,
    show 3 * (Real.pi / 3) = Real.pi by ring, Real.cos_pi]

#print axioms nonzero_remainder_unique_zero
#print axioms cubic_polygon_gap
end Komorebi.PaperIVChecks

namespace Komorebi.PaperIVChecks
open Komorebi.PaperIV

theorem reduced_two_first_zero :
    entireReducedDenominator 2 (((Real.pi : ℂ) / 2) ^ 2) = 0 := by
  apply entireReducedDenominator_two_zero_iff.mpr
  exact ⟨0, by norm_num; ring⟩

theorem reduced_two_negative_nonzero : entireReducedDenominator 2 (-1) ≠ 0 := by
  intro h
  obtain ⟨m, hm⟩ := entireReducedDenominator_two_zero_iff.mp h
  have he := congrArg Complex.re hm
  have hp : 0 ≤ (((m : ℝ) + 1 / 2) * Real.pi) ^ 2 := sq_nonneg _
  have hr : (((m : ℂ) + 1 / 2) * Real.pi) = ((((m : ℝ) + 1 / 2) * Real.pi : ℝ) : ℂ) := by push_cast; rfl
  rw [hr, ← Complex.ofReal_pow] at he
  change (-1 : ℝ) = (((m : ℝ) + 1 / 2) * Real.pi) ^ 2 at he
  linarith

theorem cubic_reduced_reciprocals_summable :
    Summable (fun m => 1 / reducedPositiveZero 3 m) :=
  reducedPositiveZero_reciprocal_summable (by norm_num)

theorem cubic_critical_exponent_diverges :
    ¬ Summable (fun m => 1 / reducedPositiveZero 3 m ^ (1 / 3 : ℝ)) := by
  rw [reducedPositiveZero_reciprocal_rpow_summable_iff (by norm_num)]
  norm_num

#print axioms reduced_two_first_zero
#print axioms reduced_two_negative_nonzero
#print axioms cubic_reduced_reciprocals_summable
#print axioms cubic_critical_exponent_diverges
end Komorebi.PaperIVChecks

namespace Komorebi.PaperIVChecks
open Komorebi.PaperIV

/-- An exceptional zero of order three must contribute three, not one. -/
theorem triple_zero_weight : analyticZeroCount (fun z : ℂ => z ^ 3) 1 = 3 := by
  have hz : zeroDisk (fun z : ℂ => z ^ 3) 1 = {0} := by
    ext z
    simp only [zeroDisk, Set.mem_ofPred_eq, pow_eq_zero_iff (by norm_num : (3 : ℕ) ≠ 0), Set.mem_singleton_iff]
    constructor
    · exact fun h => h.2
    · intro h; subst z; norm_num
  rw [analyticZeroCount, hz, finiteWeight_of_finite _ (Set.finite_singleton 0)]
  rw [Set.Finite.toFinset_singleton, Finset.sum_singleton]
  change analyticOrderNatAt ((id : ℂ → ℂ) ^ 3) 0 = 3
  rw [analyticOrderNatAt_pow (show AnalyticAt ℂ (id : ℂ → ℂ) 0 from analyticAt_id)]
  norm_num [analyticOrderNatAt, show (fun z : ℂ => z) = id from rfl]

/-- The cosine disk count has the classical density 2/pi. -/
theorem cosine_full_count_density :
    ∃ K : ℝ, 0 < K ∧ ∀ R : ℝ, 0 ≤ R →
      |(analyticZeroCount (canonicalSignedDenominator 2) R : ℝ) - (2 / Real.pi) * R| ≤ K := by
  simpa only [Nat.cast_ofNat, Real.sin_pi_div_two, mul_one] using
    canonicalSignedDenominator_zero_counting (by norm_num : 2 ≤ 2)

/-- The full cosine zero multiset diverges at its critical exponent. -/
theorem cosine_full_critical_exponent_diverges :
    ¬ ZeroPowerSummable (canonicalSignedDenominator 2) 1 := by
  rw [canonicalSignedDenominator_zero_power_summable_iff (by norm_num)]
  norm_num

/-- Every reduced cosine zero, including the finite prefix, is included. -/
theorem reduced_cosine_full_reciprocals_summable :
    ZeroPowerSummable (entireReducedDenominator 2) 1 :=
  entireReducedDenominator_reciprocal_zeros_summable (by norm_num)

/-- A nonreal point on the boundary still fails absolute convergence. -/
theorem cubic_zeta_nonreal_boundary_diverges :
    ¬ Summable (fun z => ‖absoluteZeroZetaTerm (entireReducedDenominator 3) z
      (1 / 3 + 7 * Complex.I)‖) := by
  rw [entireReducedDenominator_zeta_absolute_convergence (by norm_num)]
  norm_num

/-- The reduced cubic zeta is holomorphic at a genuinely complex interior point. -/
theorem cubic_zeta_interior_holomorphic :
    DifferentiableAt ℂ (absoluteZeroZeta (entireReducedDenominator 3)) (1 + 7 * Complex.I) := by
  apply (entireReducedDenominator_zeta_holomorphic (by norm_num : 2 ≤ 3)).differentiableAt
  apply (isOpen_lt continuous_const Complex.continuous_re).mem_nhds
  norm_num

#print axioms triple_zero_weight
#print axioms cosine_full_count_density
#print axioms cosine_full_critical_exponent_diverges
#print axioms reduced_cosine_full_reciprocals_summable
#print axioms cubic_zeta_nonreal_boundary_diverges
#print axioms cubic_zeta_interior_holomorphic
end Komorebi.PaperIVChecks

namespace Komorebi.PaperIVChecks
open Komorebi.PaperIV

/-- The explicit correction alternates: its first two values have opposite signs. -/
theorem cubic_correction_even_positive : 0 < (signedLeadingCorrection 3 0).re := by
  rw [signedLeadingCorrection_three]
  norm_num only [pow_zero, Complex.ofReal_re]
  positivity

theorem cubic_correction_odd_negative : (signedLeadingCorrection 3 1).re < 0 := by
  rw [signedLeadingCorrection_three]
  norm_num only [pow_one, Complex.ofReal_re]
  have hs : 0 < Real.sqrt 3 := Real.sqrt_pos.mpr (by norm_num)
  have he := Real.exp_pos (-3 * signedZeroCenter 3 1 / 2)
  exact mul_neg_of_neg_of_pos (div_neg_of_neg_of_pos (by norm_num) hs) he

/-- Principal logarithms give a concrete entire derivative-weighted cubic zeta;
the branch hypotheses are satisfied, not merely assumed by this check. -/
theorem cubic_principal_derivative_zeta_entire :
    Differentiable ℂ (derivativeWeightedZeroZeta 3 1 (fun z => Complex.log z.val)) := by
  apply (derivativeWeightedZeroZeta_entire (by norm_num : 3 ≤ 3) (by norm_num : 0 < 1)
    (fun z => Complex.log z.val) ?_ Real.pi_pos.le ?_).2
  · intro z
    apply Complex.exp_log
    exact norm_pos_iff.mp (zero_norm_pos_of_value_at_zero
      (by rw [canonicalSignedDenominator_zero (by norm_num : 0 < 3)]; exact one_ne_zero) z.toZero)
  · intro z
    simpa only [Complex.log_im] using Complex.abs_arg_le_pi z.val

/-- The derivative weight retains its complex sign. It is -1 at the first
cosine zero, so replacing the denominator by its norm would fail this test. -/
theorem cosine_first_derivative_weight_signed
    (z : SimpleZeros (canonicalSignedDenominator 2)) (hz : z.val = (Real.pi : ℂ) / 2) :
    derivativeZeroWeight 2 1 z = -1 := by
  have he : canonicalSignedDenominator 2 = Complex.cos := funext
    (entireSigned_two_eq_cos (canonicalPrimitiveRoot_isPrimitive (by norm_num : 0 < 2))
      (canonicalSignedRoot_pow (by norm_num : 0 < 2)))
  simp only [derivativeZeroWeight, he, Complex.deriv_cos, hz, Complex.sin_pi_div_two,
    pow_one, inv_neg, inv_one]

#print axioms cubic_correction_even_positive
#print axioms cubic_correction_odd_negative
#print axioms cubic_principal_derivative_zeta_entire
#print axioms cosine_first_derivative_weight_signed
end Komorebi.PaperIVChecks

namespace Komorebi.PaperIVChecks
open Komorebi.PaperIV

/-- Original and reduced zeta really have different pole locations in order two. -/
theorem orderTwo_distinct_pole_locations :
    meromorphicOrderAt (reducedZetaContinuation (by norm_num : 2 ≤ 2)) (1 / 2 : ℂ) = (-1 : ℤ) ∧
    DifferentiableAt ℂ (absoluteZetaContinuation (by norm_num : 2 ≤ 2)) (1 / 2 : ℂ) := by
  constructor
  · exact reducedZetaContinuation_simple_pole (by norm_num)
  · exact absoluteZetaContinuation_holomorphic_off_pole (by norm_num) (by norm_num)

/-- The explicit quartic zero calculation agrees with the global comparison. -/
theorem orderFour_correction_vanishes :
    absoluteZetaCorrection (by norm_num : 2 ≤ 4) = 0 ∧
    reducedZetaCorrection (by norm_num : 2 ≤ 4) = 0 := orderFour_zeta_corrections_zero

/-- The complete product retains the actual multiplicity of the first reduced cosine zero. -/
theorem first_cosine_reduced_product_order :
    analyticOrderAt (fullCanonicalProduct (entireReducedDenominator 2))
      (((Real.pi : ℂ) / 2) ^ 2) = 1 := by
  rw [entireReducedDenominator_full_product_same_orders (by norm_num)]
  apply entireReducedDenominator_two_zero_order_one
  rw [← canonicalSignedDenominator_eq_reduced_power (by norm_num)]
  exact (entireSigned_two_zero_iff_nat (canonicalPrimitiveRoot_isPrimitive (by norm_num))
    (canonicalSignedRoot_pow (by norm_num))).mpr ⟨0, Or.inl (by norm_num; ring)⟩

end Komorebi.PaperIVChecks

#print axioms Komorebi.PaperIVChecks.orderTwo_distinct_pole_locations
#print axioms Komorebi.PaperIVChecks.orderFour_correction_vanishes
#print axioms Komorebi.PaperIVChecks.first_cosine_reduced_product_order

namespace Komorebi.PaperIVChecks
open Komorebi.PaperIV

/-- The new full product includes the smallest allowed order, where the
original entire denominator is cosine. -/
theorem cosine_complete_product (z : ℂ) :
    Complex.cos z = ∏' i : ZeroMultiplicityIndex (entireReducedDenominator 2),
      (1 - z ^ 2 / indexedZero i) := by
  rw [← canonicalSignedDenominator_hadamard (by decide : 2 ≤ 2)]
  exact (entireSigned_two_eq_cos (canonicalPrimitiveRoot_isPrimitive (by decide : 0 < 2)) (canonicalSignedRoot_pow (by decide : 0 < 2)) z).symm

/-- Newton's first step tests the sign and factorial against a known value. -/
theorem cosine_first_zero_moment :
    zeroPowerSum (entireReducedDenominator 2) 1 = (1 / 2 : ℂ) := by
  have h := reducedZeroPowerSum_newton (by decide : 2 ≤ 2) 0
  norm_num [coeff_reducedDenominator] at h
  exact h

/-- The second moment tests the nontrivial convolution term in Newton's rule. -/
theorem cosine_second_zero_moment :
    zeroPowerSum (entireReducedDenominator 2) 2 = (1 / 6 : ℂ) := by
  have h := reducedZeroPowerSum_newton (by decide : 2 ≤ 2) 1
  norm_num [Finset.sum_range_succ, coeff_reducedDenominator, cosine_first_zero_moment] at h
  exact h

/-- The zero-data Bell formula retains the empty Bell polynomial at n=0. -/
theorem reciprocal_zero_data_constant (r : ℂ) : reciprocalCoeff 3 0 r = 1 := by
  rw [reciprocalCoeff_zero_sum_bell (by decide : 2 ≤ 3)]
  simp

#print axioms cosine_complete_product
#print axioms cosine_first_zero_moment
#print axioms cosine_second_zero_moment
#print axioms reciprocal_zero_data_constant
end Komorebi.PaperIVChecks


namespace Komorebi.PaperIVChecks
open Komorebi.PaperIV Filter
open scoped Topology

/-- Cosine on the real axis exercises a tie direction with infinitely many zeros. -/
theorem cosine_real_axis_indicator :
    limsup (fun r : ℝ => Real.log ‖canonicalSignedDenominator 2 (r : ℂ)‖ / r) atTop = 0 := by
  have h := canonicalSignedDenominator_indicator (by decide : 2 ≤ 2) 0
  have hp (k : ℕ) (hk : k < 2) : signedProjection 2 0 k = 0 := by
    interval_cases k
    · norm_num [signedProjection_cos]
    · rw [signedProjection_cos]
      norm_num only [Nat.cast_one, Nat.cast_ofNat]
      rw [show (0 : ℝ) + 3 * (Real.pi / 2) = Real.pi / 2 + Real.pi by ring,
        Real.cos_add_pi, Real.cos_pi_div_two, neg_zero]
  have hi : signedIndicator 2 (by decide) 0 = 0 := by
    apply le_antisymm
    · exact (Finset.sup'_le_iff _ _).mpr (fun k hk => (hp k (Finset.mem_range.mp hk)).le)
    · exact signedIndicator_nonneg (by decide) 0
  simpa only [hi, rayDirection, Complex.ofReal_zero, zero_mul, Complex.exp_zero, mul_one] using h

/-- The reduced quartic has growth order 1/4, rather than the original order one. -/
theorem reduced_quartic_sharp_order : entireGrowthOrder (entireReducedDenominator 4) = (1 / 4 : ℝ) := by
  simpa using entireReducedDenominator_order_exact (by decide : 0 < 4)

/-- The signed cubic has exact type one despite its smaller growth on the real axis. -/
theorem cubic_sharp_type : entireExponentialType (canonicalSignedDenominator 3) = 1 :=
  canonicalSignedDenominator_type_one (by decide)

/-- Negative imaginary phases use positive radii and still align exactly. -/
theorem negative_phase_aligned_radius : alignedRadii (-1) 2 = 4 * Real.pi := by
  norm_num [alignedRadii]
  ring

#print axioms cosine_real_axis_indicator
#print axioms reduced_quartic_sharp_order
#print axioms cubic_sharp_type
#print axioms negative_phase_aligned_radius
end Komorebi.PaperIVChecks

namespace Komorebi.PaperIVChecks
open Komorebi.PaperIV
noncomputable section
-- The order-one boundary is retained even though the zero-product theorem requires N>=2.
theorem normalized_order_one : entireGrowthOrder (entireNormalizedSection 1 0) = 1 := by
  simpa using entireNormalizedSection_order_exact (by norm_num : 0 < 1) (by norm_num : 0 < 1)

-- Actual normalized-section zeros have a negative first reciprocal moment: the sign is essential.
theorem normalized_first_zero_moment : zeroPowerSum (entireNormalizedSection 2 1) 1 = -(1/6 : ℂ) := by
  have h := normalized_zeroPowerSum (by norm_num : 2 ≤ 2) 1 0
  norm_num [coeff_one_normalizedResidueNegativeLog] at h
  exact h

-- The actual Hilbert-space diagonal operator has the denominator's first logarithmic moment.
theorem diagonal_trace_cosine : hilbertBasisTrace (diagonalHilbertBasis (ZeroMultiplicityIndex (entireReducedDenominator 2)))
    (reducedZeroOperator 2) = (1/2 : ℂ) := by
  have h := reducedZeroOperator_trace_power (by norm_num : 2 ≤ 2) (by norm_num : 0 < 1)
    (diagonalHilbertBasis (ZeroMultiplicityIndex (entireReducedDenominator 2)))
  norm_num [kappaCoeff, coeff_one_negativeLogDenominator] at h
  exact h

-- Integer order zero repeats no variables and kills every positive-degree reciprocal coefficient.
theorem symmetric_zero_order : completeHomogeneous (repeatedEigenvalue
    (fun i : ZeroMultiplicityIndex (entireReducedDenominator 2) => (indexedZero i)⁻¹) 0) 1 = 0 := by
  have h := reciprocalCoeff_completeHomogeneous (by norm_num : 2 ≤ 2) 1 0
  simpa [reciprocalCoeff, blockCoeff, reciprocalSeries_zero] using h.symm
end
end Komorebi.PaperIVChecks

#print axioms Komorebi.PaperIVChecks.normalized_order_one
#print axioms Komorebi.PaperIVChecks.normalized_first_zero_moment
#print axioms Komorebi.PaperIVChecks.diagonal_trace_cosine
#print axioms Komorebi.PaperIVChecks.symmetric_zero_order
