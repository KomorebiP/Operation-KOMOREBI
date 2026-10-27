import KomorebiLSM.BernsteinKernel
import KomorebiLSM.BaseNormIntegration
import KomorebiLSM.ContinuousInstrument
import KomorebiLSM.PositiveCellApproximation
import KomorebiLSM.ContinuousTV

/-! Positive polynomial approximation from actual integral coefficients. No
polynomial degree hypothesis is imposed on the original operator density. -/
set_option autoImplicit false
open MeasureTheory
open scoped BigOperators

namespace Komorebi.LSM.PositivePolynomialApproximation
noncomputable section

section Averaging
variable {F : Type*} [NormedAddCommGroup F] [NormedSpace ℝ F] [CompleteSpace F]

/-- The exact positive integral coefficients, with the classical normalization. -/
def coefficient (n : ℕ) (B : ℝ → F) (k : Fin (n+1)) : F :=
  ((n : ℝ)+1) • ∫ v, BernsteinKernel.basis n k v • B v ∂BernsteinKernel.measure

/-- The approximating polynomial is given by its finite Bernstein expansion. -/
def approximation (n : ℕ) (B : ℝ → F) (x : ℝ) : F :=
  ∑ k : Fin (n+1), BernsteinKernel.basis n k x • coefficient n B k

omit [CompleteSpace F] in
theorem basis_weighted_integrable (n : ℕ) (B : ℝ → F) (hB : Integrable B BernsteinKernel.measure)
    (k : Fin (n+1)) : Integrable (fun v => BernsteinKernel.basis n k v • B v) BernsteinKernel.measure := by
  apply hB.bdd_smul 1 (BernsteinKernel.basis_continuous n k).aestronglyMeasurable
  filter_upwards [BernsteinKernel.support_ae] with v hv
  rw [Real.norm_eq_abs, abs_of_nonneg (BernsteinKernel.basis_nonneg n k hv)]
  exact BernsteinKernel.basis_le_one n k hv

omit [CompleteSpace F] in
theorem approximation_continuous (n : ℕ) (B : ℝ → F) : Continuous (approximation n B) := by
  unfold approximation
  exact continuous_finsetSum _ fun k _ => (BernsteinKernel.basis_continuous n k).smul continuous_const

omit [CompleteSpace F] in
theorem approximation_integrable (n : ℕ) (B : ℝ → F) :
    Integrable (approximation n B) BernsteinKernel.measure :=
  BernsteinKernel.continuous_integrable (approximation_continuous n B)

omit [CompleteSpace F] in
/-- Kernel multiplication preserves integrability by its finite basis expansion. -/
theorem kernel_weighted_integrable (n : ℕ) (B : ℝ → F) (hB : Integrable B BernsteinKernel.measure) (x : ℝ) :
    Integrable (fun v => BernsteinKernel.kernel n x v • B v) BernsteinKernel.measure := by
  have heq : (fun v => BernsteinKernel.kernel n x v • B v) =
      (fun v => ((n : ℝ)+1) • ∑ k : Fin (n+1),
        BernsteinKernel.basis n k x • (BernsteinKernel.basis n k v • B v)) := by
    funext v
    simp only [BernsteinKernel.kernel, mul_smul, Finset.sum_smul]
  rw [heq]
  exact Integrable.smul _ (integrable_finsetSum _ fun k _ =>
    Integrable.smul _ (basis_weighted_integrable n B hB k))

omit [CompleteSpace F] in
/-- Kernel averaging and the finite Bernstein coefficient formula coincide. -/
theorem approximation_eq_kernel (n : ℕ) (B : ℝ → F) (hB : Integrable B BernsteinKernel.measure) (x : ℝ) :
    approximation n B x = ∫ v, BernsteinKernel.kernel n x v • B v ∂BernsteinKernel.measure := by
  have heq : (fun v => BernsteinKernel.kernel n x v • B v) =
      (fun v => ((n : ℝ)+1) • ∑ k : Fin (n+1),
        BernsteinKernel.basis n k x • (BernsteinKernel.basis n k v • B v)) := by
    funext v
    simp only [BernsteinKernel.kernel, mul_smul, Finset.sum_smul]
  calc
    approximation n B x = ((n : ℝ)+1) • ∑ k : Fin (n+1),
        BernsteinKernel.basis n k x • (∫ v, BernsteinKernel.basis n k v • B v ∂BernsteinKernel.measure) := by
      simp only [approximation, coefficient, Finset.smul_sum, smul_smul]
      apply Finset.sum_congr rfl
      intro k _
      rw [mul_comm]
    _ = _ := by
      rw [heq, integral_smul, integral_finsetSum
        (f := fun (k : Fin (n+1)) v => BernsteinKernel.basis n k x • (BernsteinKernel.basis n k v • B v)) _
        (fun k _ => Integrable.smul _ (basis_weighted_integrable n B hB k))]
      congr 1
      apply Finset.sum_congr rfl
      intro k _
      exact (integral_smul _ _).symm

/-- Double stochasticity preserves the original integrated operator exactly. -/
theorem approximation_integral (n : ℕ) (B : ℝ → F) (hB : Integrable B BernsteinKernel.measure) :
    (∫ x, approximation n B x ∂BernsteinKernel.measure) = ∫ v, B v ∂BernsteinKernel.measure := by
  simp only [approximation]
  rw [integral_finsetSum
    (f := fun (k : Fin (n+1)) x => BernsteinKernel.basis n k x • coefficient n B k) _
    (fun k _ => (BernsteinKernel.continuous_integrable (BernsteinKernel.basis_continuous n k)).smul_const _)]
  have hi (k : Fin (n+1)) :
      (∫ x, BernsteinKernel.basis n k x • coefficient n B k ∂BernsteinKernel.measure) =
        ∫ v, BernsteinKernel.basis n k v • B v ∂BernsteinKernel.measure := by
    rw [integral_smul_const, BernsteinKernel.basis_integral n k, coefficient, smul_smul]
    have hm : (1 / ((n : ℝ)+1)) * ((n : ℝ)+1) = 1 := by field_simp
    rw [hm, one_smul]
  simp_rw [hi]
  rw [← integral_finsetSum (f := fun (k : Fin (n+1)) v => BernsteinKernel.basis n k v • B v) _
    (fun k _ => basis_weighted_integrable n B hB k)]
  apply integral_congr_ae
  filter_upwards [] with v
  rw [← Finset.sum_smul, BernsteinKernel.sum_basis, one_smul]
/-- Constant operator densities retain their exact coefficient normalization. -/
theorem coefficient_constant (n : ℕ) (c : F) (k : Fin (n+1)) :
    coefficient n (fun _ => c) k = c := by
  rw [coefficient, integral_smul_const, BernsteinKernel.basis_integral n k, smul_smul]
  have hn : ((n : ℝ)+1) * (1 / ((n : ℝ)+1)) = 1 := by field_simp
  rw [hn, one_smul]

theorem approximation_constant (n : ℕ) (c : F) (x : ℝ) :
    approximation n (fun _ => c) x = c := by
  simp only [approximation, coefficient_constant]
  rw [← Finset.sum_smul, BernsteinKernel.sum_basis, one_smul]
end Averaging

/-- Every Bernstein basis polynomial has the declared degree bound. -/
theorem basis_degree_le (n : ℕ) (k : Fin (n+1)) :
    (bernsteinPolynomial ℝ n k).natDegree ≤ n := by
  have hlin : (1 - Polynomial.X : Polynomial ℝ).natDegree ≤ 1 := by
    simpa using Polynomial.natDegree_sub_le (1 : Polynomial ℝ) Polynomial.X
  unfold bernsteinPolynomial
  calc
    _ ≤ (n.choose k : Polynomial ℝ).natDegree + (Polynomial.X^(k : ℕ) : Polynomial ℝ).natDegree +
        ((1 - Polynomial.X)^(n-(k : ℕ)) : Polynomial ℝ).natDegree :=
      Polynomial.natDegree_mul_le.trans (Nat.add_le_add_right Polynomial.natDegree_mul_le _)
    _ ≤ 0 + (k : ℕ) + (n-(k : ℕ)) := by
      apply Nat.add_le_add
      · simp
      · exact (Polynomial.natDegree_pow_le_of_le _ hlin).trans_eq (Nat.mul_one _)
    _ = n := by omega

theorem basis_power_expansion (n : ℕ) (k : Fin (n+1)) (x : ℝ) :
    BernsteinKernel.basis n k x = ∑ m : Fin (n+1),
      (bernsteinPolynomial ℝ n k).coeff m * x^(m : ℕ) := by
  have h := congrArg (Polynomial.eval x)
    (Polynomial.as_sum_range_C_mul_X_pow' (bernsteinPolynomial ℝ n k)
      (Nat.lt_succ_of_le (basis_degree_le n k)))
  simpa [BernsteinKernel.basis, Polynomial.eval_finsetSum, Finset.sum_range] using h

section Degree
variable {F : Type*} [NormedAddCommGroup F] [NormedSpace ℝ F] [CompleteSpace F]

def powerCoefficient (n : ℕ) (B : ℝ → F) (m : Fin (n+1)) : F :=
  ∑ k : Fin (n+1), (bernsteinPolynomial ℝ n k).coeff m • coefficient n B k

omit [CompleteSpace F] in
/-- An explicit power expansion certifies degree at most n in the vector space. -/
theorem approximation_power_expansion (n : ℕ) (B : ℝ → F) (x : ℝ) :
    approximation n B x = ∑ m : Fin (n+1), x^(m : ℕ) • powerCoefficient n B m := by
  simp only [approximation, powerCoefficient, basis_power_expansion, Finset.sum_smul,
    Finset.smul_sum, smul_smul]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro m _
  apply Finset.sum_congr rfl
  intro k _
  rw [mul_comm]
end Degree

section Operators
variable {E A : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E] [CompleteSpace E]
variable [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E]
variable (C : BaseNorm.ProbabilityCone E)

omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E] in
/-- Every integral coefficient is a positive operator on the original cone. -/
theorem coefficient_positive (n : ℕ) (B : ℝ → E →L[ℝ] E)
    (hB : Integrable B BernsteinKernel.measure)
    (hpos : ∀ᵐ v ∂BernsteinKernel.measure, ∀ z ∈ C.carrier, B v z ∈ C.carrier)
    (k : Fin (n+1)) (z : E) (hz : z ∈ C.carrier) : coefficient n B k z ∈ C.carrier := by
  have hi := basis_weighted_integrable n B hB k
  simp only [coefficient, smul_apply, ContinuousLinearMap.integral_apply hi]
  apply C.smul_mem (by positivity)
  apply C.convex_carrier.integral_mem C.closed _ ((ContinuousLinearMap.apply ℝ E z).integrable_comp hi)
  filter_upwards [BernsteinKernel.support_ae, hpos] with v hv hBv
  exact C.smul_mem (BernsteinKernel.basis_nonneg n k hv) (hBv z hz)

omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E] in
/-- The entire approximating polynomial is cone positive at every unit input. -/
theorem approximation_positive (n : ℕ) (B : ℝ → E →L[ℝ] E)
    (hB : Integrable B BernsteinKernel.measure)
    (hpos : ∀ᵐ v ∂BernsteinKernel.measure, ∀ z ∈ C.carrier, B v z ∈ C.carrier)
    {x : ℝ} (hx : x ∈ Set.Icc (0 : ℝ) 1) (z : E) (hz : z ∈ C.carrier) :
    approximation n B x z ∈ C.carrier := by
  simp only [approximation, sum_apply, smul_apply]
  apply Finset.sum_induction
  · exact fun _ _ => C.add_mem
  · exact C.zero_mem
  · intro k _
    exact C.smul_mem (BernsteinKernel.basis_nonneg n k hx) (coefficient_positive C n B hB hpos k z hz)

omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E] in
/-- The error subtracts the original operator inside the normalized kernel. -/
theorem approximation_error_identity (n : ℕ) (B : ℝ → E →L[ℝ] E)
    (hB : Integrable B BernsteinKernel.measure) (x : ℝ) (z : E) :
    approximation n B x z - B x z =
      ∫ v, BernsteinKernel.kernel n x v • (B v z - B x z) ∂BernsteinKernel.measure := by
  have hi := kernel_weighted_integrable n B hB x
  have ha : Integrable (fun v => BernsteinKernel.kernel n x v • B v z) BernsteinKernel.measure :=
    (ContinuousLinearMap.apply ℝ E z).integrable_comp hi
  have hc : Integrable (fun v => BernsteinKernel.kernel n x v • B x z) BernsteinKernel.measure :=
    BernsteinKernel.continuous_integrable
      (((BernsteinKernel.kernel_continuous n).comp (continuous_const.prodMk continuous_id)).smul continuous_const)
  simp_rw [smul_sub]
  rw [integral_sub ha hc, integral_smul_const, BernsteinKernel.kernel_integral_right, one_smul,
    approximation_eq_kernel n B hB, ContinuousLinearMap.integral_apply hi z]
  simp only [smul_apply]

omit [MeasurableSpace E] [BorelSpace E] in
/-- A fixed normalized input obeys the kernel displacement bound pointwise. -/
theorem approximation_error_point (n : ℕ) (B : ℝ → E →L[ℝ] E)
    (hB : Integrable B BernsteinKernel.measure) (L : ℝ) (_hL : 0 ≤ L)
    {x : ℝ} (hx : x ∈ Set.Icc (0 : ℝ) 1) (z : E)
    (hLip : ∀ v ∈ Set.Icc (0 : ℝ) 1, C.value (B v z-B x z) ≤ L*|v-x|) :
    C.value (approximation n B x z-B x z) ≤
      L * ∫ v, BernsteinKernel.kernel n x v * |v-x| ∂BernsteinKernel.measure := by
  have hf : Integrable (fun v => B v z-B x z) BernsteinKernel.measure :=
    ((ContinuousLinearMap.apply ℝ E z).integrable_comp hB).sub (integrable_const _)
  have hi := kernel_weighted_integrable n (fun v => B v z-B x z) hf x
  rw [approximation_error_identity n B hB x z]
  calc
    _ ≤ ∫ v, C.value (BernsteinKernel.kernel n x v • (B v z-B x z)) ∂BernsteinKernel.measure :=
      C.value_integral_le_integral_value hi
    _ ≤ ∫ v, L * (BernsteinKernel.kernel n x v * |v-x|) ∂BernsteinKernel.measure := by
      apply integral_mono_ae (C.integrable_value hi)
        (BernsteinKernel.continuous_integrable (by
          have hc : Continuous (fun v : ℝ => BernsteinKernel.kernel n x v) :=
            (BernsteinKernel.kernel_continuous n).comp (continuous_const.prodMk continuous_id)
          exact continuous_const.mul (hc.mul (continuous_id.sub continuous_const).abs)))
      filter_upwards [BernsteinKernel.support_ae] with v hv
      rw [C.value_smul, abs_of_nonneg (BernsteinKernel.kernel_nonneg n hx hv)]
      have h := mul_le_mul_of_nonneg_left (hLip v hv) (BernsteinKernel.kernel_nonneg n hx hv)
      nlinarith [h]
    _ = _ := integral_const_mul _ _

omit [MeasurableSpace E] [BorelSpace E] in
/-- The integrated error has the universal Bernstein–Durrmeyer rate. -/
theorem approximation_integrated_error (n : ℕ) (B : ℝ → E →L[ℝ] E)
    (hB : Integrable B BernsteinKernel.measure) (L : ℝ) (hL : 0 ≤ L) (z : E)
    (hLip : ∀ x ∈ Set.Icc (0 : ℝ) 1, ∀ v ∈ Set.Icc (0 : ℝ) 1,
      C.value (B v z-B x z) ≤ L*|v-x|) :
    (∫ x, C.value (approximation n B x z-B x z) ∂BernsteinKernel.measure) ≤
      L / Real.sqrt (3*((n : ℝ)+2)) := by
  have hleft := C.integrable_value
    (((ContinuousLinearMap.apply ℝ E z).integrable_comp (approximation_integrable n B)).sub
      ((ContinuousLinearMap.apply ℝ E z).integrable_comp hB))
  have hj : Integrable (fun p : ℝ × ℝ => BernsteinKernel.kernel n p.1 p.2 * |p.2-p.1|)
      (BernsteinKernel.measure.prod BernsteinKernel.measure) :=
    BernsteinKernel.continuous_joint_integrable
      ((BernsteinKernel.kernel_continuous n).mul (continuous_snd.sub continuous_fst).abs)
  have hright : Integrable (fun x => ∫ v, BernsteinKernel.kernel n x v * |v-x| ∂BernsteinKernel.measure)
      BernsteinKernel.measure := hj.integral_prod_left
  calc
    _ ≤ ∫ x, L * (∫ v, BernsteinKernel.kernel n x v * |v-x| ∂BernsteinKernel.measure)
        ∂BernsteinKernel.measure := by
      apply integral_mono_ae hleft (hright.const_mul L)
      filter_upwards [BernsteinKernel.support_ae] with x hx
      exact approximation_error_point C n B hB L hL hx z (hLip x hx)
    _ = L * (∫ x, ∫ v, BernsteinKernel.kernel n x v * |v-x|
        ∂BernsteinKernel.measure ∂BernsteinKernel.measure) := integral_const_mul _ _
    _ ≤ L * (1 / Real.sqrt (3*((n : ℝ)+2))) :=
      mul_le_mul_of_nonneg_left (BernsteinKernel.kernel_distance_bound n) hL
    _ = _ := by ring

variable {C}

/-- A genuine probability instrument, with exact mass rather than a correction. -/
def approximatingInstrument (n : ℕ)
    (D : ContinuousInstrument.DensityInstrument (A := A) C BernsteinKernel.measure) :
    ContinuousInstrument.DensityInstrument (A := A) C BernsteinKernel.measure where
  op a := approximation n (D.op a)
  measurable_op a := (approximation_continuous n (D.op a)).measurable
  integrable_op a := approximation_integrable n (D.op a)
  positive a := BernsteinKernel.support_ae.mono fun _ hx z hz =>
    approximation_positive C n (D.op a) (D.integrable_op a) (D.positive a) hx z hz
  mass_preserving a z := by
    rw [approximation_integral n (D.op a) (D.integrable_op a)]
    exact D.mass_preserving a z

omit [MeasurableSpace E] [BorelSpace E] in
/-- The source's Lipschitz premise uses the actual induced base norm. -/
theorem induced_lipschitz_approximation_error (n : ℕ) (B : ℝ → E →L[ℝ] E)
    (hB : Integrable B BernsteinKernel.measure) (L : ℝ) (hL : 0 ≤ L)
    (hLip : ∀ x ∈ Set.Icc (0 : ℝ) 1, ∀ v ∈ Set.Icc (0 : ℝ) 1,
      PositiveCellApproximation.inducedNorm (C := C) (B v-B x) ≤ L*|v-x|)
    (z : E) (hz : z ∈ C.base) :
    (∫ x, C.value (approximation n B x z-B x z) ∂BernsteinKernel.measure) ≤
      L / Real.sqrt (3*((n : ℝ)+2)) := by
  apply approximation_integrated_error C n B hB L hL z
  intro x hx v hv
  have h := PositiveCellApproximation.value_apply_le_inducedNorm (C := C) (B v-B x) z
  change C.value (B v z-B x z) ≤ _ at h
  rw [C.value_on_cone hz.1, hz.2, mul_one] at h
  exact h.trans (hLip x hx v hv)

omit [MeasurableSpace E] [BorelSpace E] in
/-- Uniform integrated discrepancy of the actual valid instruments, in the
orientation used by the common-policy law comparison. -/
theorem approximating_instrument_discrepancy (n : ℕ)
    (D : ContinuousInstrument.DensityInstrument (A := A) C BernsteinKernel.measure)
    (L : ℝ) (hL : 0 ≤ L)
    (hLip : ∀ a x, x ∈ Set.Icc (0 : ℝ) 1 → ∀ v ∈ Set.Icc (0 : ℝ) 1,
      PositiveCellApproximation.inducedNorm (C := C) (D.op a v-D.op a x) ≤ L*|v-x|)
    (a : A) (z : E) (hz : z ∈ C.base) :
    (∫ x, C.value (D.op a x z-(approximatingInstrument n D).op a x z) ∂BernsteinKernel.measure) ≤
      L / Real.sqrt (3*((n : ℝ)+2)) := by
  have heq : (fun x => C.value (D.op a x z-(approximatingInstrument n D).op a x z)) =
      (fun x => C.value (approximation n (D.op a) x z-D.op a x z)) := by
    funext x
    change C.value (D.op a x z-approximation n (D.op a) x z) = _
    rw [← C.value_neg (D.op a x z-approximation n (D.op a) x z), neg_sub]
  rw [heq]
  exact induced_lipschitz_approximation_error n (D.op a) (D.integrable_op a) L hL (hLip a) z hz
/-- P64's length-T bound compares the actual laws under the same reported-history
policy and identical initial states. It invokes the full P59 comparison theorem. -/
theorem common_policy_law_error [MeasurableSpace A] [Fintype A] [MeasurableSingletonClass A]
    (n : ℕ) (D : ContinuousInstrument.DensityInstrument (A := A) C BernsteinKernel.measure)
    (L : ℝ) (hL : 0 ≤ L)
    (hLip : ∀ a x, x ∈ Set.Icc (0 : ℝ) 1 → ∀ v ∈ Set.Icc (0 : ℝ) 1,
      PositiveCellApproximation.inducedNorm (C := C) (D.op a v-D.op a x) ≤ L*|v-x|)
    (π : ContinuousRecords.Policy (A := A) (Y := ℝ))
    (z : ContinuousInstrument.DensityInstrument.State C) (T : ℕ) :
    SequentialLowerCertificate.lawTV
      (TimeRecords.recordLaw (fun _ => D) π z.1 T)
      (TimeRecords.recordLaw (fun _ => approximatingInstrument n D) π z.1 T) ≤
        min 1 ((T : ℝ)*L/(2*Real.sqrt (3*((n : ℝ)+2)))) := by
  have h := ContinuousTV.record_lawTV_le (fun _ => D) (fun _ => approximatingInstrument n D)
    π z z (fun _ => L / Real.sqrt (3*((n : ℝ)+2)))
    (fun _ => div_nonneg hL (Real.sqrt_nonneg _))
    (fun _ a u hu => approximating_instrument_discrepancy n D L hL hLip a u hu)
    0 (by simp) T
  convert h using 1
  congr 1
  simp only [Finset.sum_const, Finset.card_range, nsmul_eq_mul, zero_add]
  ring
end Operators

end
end Komorebi.LSM.PositivePolynomialApproximation
