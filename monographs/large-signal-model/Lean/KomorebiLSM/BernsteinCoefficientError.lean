import KomorebiLSM.PositivePolynomialApproximation
import KomorebiLSM.ContinuousRecords

/-! P65: positive fitted Bernstein coefficients, genuine base-norm coefficient
error, approximation bias, and a separate correction budget. -/
set_option autoImplicit false
namespace Komorebi.LSM.BernsteinCoefficientError
open MeasureTheory ContinuousInstrument
open scoped BigOperators
noncomputable section

variable {E A : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
  [FiniteDimensional ℝ E]
variable (C : BaseNorm.ProbabilityCone E)

/-- The fitted density is the literal Bernstein combination of the fitted operators. -/
def combination (n : ℕ) (T : Fin (n+1) → E →L[ℝ] E) (x : ℝ) : E →L[ℝ] E :=
  ∑ k : Fin (n+1),BernsteinKernel.basis n k x • T k

omit [FiniteDimensional ℝ E] in
/-- Constant fitted coefficients give exactly the same constant density operator. -/
theorem combination_constant (n : ℕ) (T : E →L[ℝ] E) (x : ℝ) :
    combination n (fun _ => T) x=T := by
  unfold combination
  rw [← Finset.sum_smul,BernsteinKernel.sum_basis,one_smul]

omit [FiniteDimensional ℝ E] in
theorem combination_continuous (n : ℕ) (T : Fin (n+1) → E →L[ℝ] E) :
    Continuous (combination n T) := by
  exact continuous_finsetSum _ (fun k _ => (BernsteinKernel.basis_continuous n k).smul continuous_const)

omit [FiniteDimensional ℝ E] in
theorem combination_integrable (n : ℕ) (T : Fin (n+1) → E →L[ℝ] E) :
    Integrable (combination n T) BernsteinKernel.measure :=
  BernsteinKernel.continuous_integrable (combination_continuous n T)

/-- The coefficient average is the actual Bochner integral of the fitted density. -/
theorem combination_integral (n : ℕ) (T : Fin (n+1) → E →L[ℝ] E) :
    (∫ x,combination n T x∂BernsteinKernel.measure)=
      (1/((n : ℝ)+1)) • ∑ k,T k := by
  change (∫ x,∑ k : Fin (n+1),BernsteinKernel.basis n k x • T k∂BernsteinKernel.measure)=_
  rw [integral_finsetSum]
  · simp_rw [integral_smul_const,BernsteinKernel.basis_integral]
    rw [Finset.smul_sum]
  · intro k _
    exact BernsteinKernel.continuous_integrable
      ((BernsteinKernel.basis_continuous n k).smul continuous_const)

omit [FiniteDimensional ℝ E] in
/-- Nonnegative Bernstein weights preserve the same actual cone pointwise. -/
theorem combination_positive (n : ℕ) (T : Fin (n+1) → E →L[ℝ] E)
    (hT : ∀ k z,z∈C.carrier → T k z∈C.carrier)
    (x : ℝ) (hx : x∈Set.Icc (0 : ℝ) 1) (z : E) (hz : z∈C.carrier) :
    combination n T x z∈C.carrier := by
  simp only [combination,sum_apply,smul_apply]
  change (∑ k : Fin (n+1),BernsteinKernel.basis n k x • T k z)∈C.carrier
  apply Finset.sum_induction
  · intro a b ha hb
    exact C.add_mem ha hb
  · exact C.zero_mem
  · intro k _
    exact C.smul_mem (BernsteinKernel.basis_nonneg n k hx) (hT k z hz)

variable [MeasurableSpace E] [BorelSpace E]

/-- Positivity and exact average mass construct a true density instrument. -/
def fittedInstrument (n : ℕ) (T : A → Fin (n+1) → E →L[ℝ] E)
    (hT : ∀ a k z,z∈C.carrier → T a k z∈C.carrier)
    (hm : ∀ a z,C.mass (((1/((n : ℝ)+1)) • ∑ k,T a k) z)=C.mass z) :
    DensityInstrument (A := A) C BernsteinKernel.measure where
  op a := combination n (T a)
  measurable_op a := (combination_continuous n (T a)).measurable
  integrable_op a := combination_integrable n (T a)
  positive a := BernsteinKernel.support_ae.mono (fun x hx z hz => combination_positive C n (T a) (hT a) x hx z hz)
  mass_preserving a z := by rw [combination_integral]; exact hm a z

omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E] in
/-- The finite coefficient premise bounds the actual positive-decomposition infimum. -/
theorem coefficient_error_point (n : ℕ) (T U : Fin (n+1) → E →L[ℝ] E)
    (eta : Fin (n+1) → ℝ) (z : E)
    (herror : ∀ k,C.value (T k z-U k z)≤eta k)
    (x : ℝ) (hx : x∈Set.Icc (0 : ℝ) 1) :
    C.value (combination n T x z-combination n U x z)≤
      ∑ k : Fin (n+1),BernsteinKernel.basis n k x*eta k := by
  have he : combination n T x z-combination n U x z=
      ∑ k : Fin (n+1),BernsteinKernel.basis n k x • (T k z-U k z) := by
    simp only [combination,sum_apply,smul_apply,
      smul_sub,Finset.sum_sub_distrib]
  rw [he]
  calc
    _≤∑ k : Fin (n+1),C.value (BernsteinKernel.basis n k x • (T k z-U k z)) := C.value_sum_le _ _
    _=∑ k : Fin (n+1),BernsteinKernel.basis n k x*C.value (T k z-U k z) := by
      apply Finset.sum_congr rfl
      intro k _
      exact C.value_smul_of_nonneg (BernsteinKernel.basis_nonneg n k hx) _
    _≤_ := Finset.sum_le_sum (fun k _ => mul_le_mul_of_nonneg_left (herror k)
      (BernsteinKernel.basis_nonneg n k hx))

omit [MeasurableSpace E] [BorelSpace E] in
/-- Integration yields exactly the arithmetic mean of the coefficient error budgets. -/
theorem coefficient_integrated_error (n : ℕ) (T U : Fin (n+1) → E →L[ℝ] E)
    (eta : Fin (n+1) → ℝ) (z : E) (herror : ∀ k,C.value (T k z-U k z)≤eta k) :
    (∫ x,C.value (combination n T x z-combination n U x z)∂BernsteinKernel.measure)≤
      (1/((n : ℝ)+1))*∑ k,eta k := by
  have hi := C.integrable_value
    (((ContinuousLinearMap.apply ℝ E z).integrable_comp (combination_integrable n T)).sub
      ((ContinuousLinearMap.apply ℝ E z).integrable_comp (combination_integrable n U)))
  have hj : Integrable (fun x => ∑ k : Fin (n+1),BernsteinKernel.basis n k x*eta k)
      BernsteinKernel.measure :=
    BernsteinKernel.continuous_integrable (continuous_finsetSum _
      (fun k _ => (BernsteinKernel.basis_continuous n k).mul continuous_const))
  calc
    _≤∫ x,∑ k : Fin (n+1),BernsteinKernel.basis n k x*eta k∂BernsteinKernel.measure := by
      apply integral_mono_ae hi hj
      exact BernsteinKernel.support_ae.mono (fun x hx => coefficient_error_point C n T U eta z herror x hx)
    _=∑ k : Fin (n+1),(1/((n : ℝ)+1))*eta k := by
      rw [integral_finsetSum]
      · simp_rw [integral_mul_const,BernsteinKernel.basis_integral]
      · intro k _
        exact BernsteinKernel.continuous_integrable ((BernsteinKernel.basis_continuous n k).mul continuous_const)
    _=_ := (Finset.mul_sum _ _ _).symm

omit [MeasurableSpace E] [BorelSpace E] in
/-- Triangle inequality for literal integrated base-norm discrepancies. -/
theorem integrated_triangle (F G H : ℝ → E →L[ℝ] E)
    (hF : Integrable F BernsteinKernel.measure) (hG : Integrable G BernsteinKernel.measure)
    (hH : Integrable H BernsteinKernel.measure) (z : E) :
    (∫ x,C.value (F x z-H x z)∂BernsteinKernel.measure)≤
      (∫ x,C.value (F x z-G x z)∂BernsteinKernel.measure)+
        ∫ x,C.value (G x z-H x z)∂BernsteinKernel.measure := by
  have hFV := (ContinuousLinearMap.apply ℝ E z).integrable_comp hF
  have hGV := (ContinuousLinearMap.apply ℝ E z).integrable_comp hG
  have hHV := (ContinuousLinearMap.apply ℝ E z).integrable_comp hH
  have hFG : Integrable (fun x => C.value (F x z-G x z)) BernsteinKernel.measure :=
    C.integrable_value (hFV.sub hGV)
  have hGH : Integrable (fun x => C.value (G x z-H x z)) BernsteinKernel.measure :=
    C.integrable_value (hGV.sub hHV)
  calc
    _≤∫ x,C.value (F x z-G x z)+C.value (G x z-H x z)∂BernsteinKernel.measure := by
      apply integral_mono (C.integrable_value (hFV.sub hHV)) (hFG.add hGH)
      intro x
      change C.value (F x z-H x z)≤C.value (F x z-G x z)+C.value (G x z-H x z)
      have he : F x z-H x z=(F x z-G x z)+(G x z-H x z) := by abel
      rw [he]
      exact C.value_add_le _ _
    _=_ := integral_add hFG hGH

/-- The finite action maximum is taken over the actual coefficient mean budgets. -/
def maximumCoefficientError [Fintype A] (n : ℕ) (eta : A → Fin (n+1) → ℝ) : ℝ :=
  sSup (Set.range (fun a => (1/((n : ℝ)+1))*∑ k,eta a k))

theorem coefficient_error_le_maximum [Fintype A] (n : ℕ) (eta : A → Fin (n+1) → ℝ) (a : A) :
    (1/((n : ℝ)+1))*∑ k,eta a k≤maximumCoefficientError n eta :=
  le_csSup (Set.finite_range _).bddAbove (Set.mem_range_self a)

omit [MeasurableSpace E] [BorelSpace E] in
/-- Genuine approximation bias and coefficient error remain separate addends. -/
theorem bias_plus_coefficient_error (n : ℕ)
    (D : DensityInstrument (A := A) C BernsteinKernel.measure)
    (T : A → Fin (n+1) → E →L[ℝ] E) (eta : A → Fin (n+1) → ℝ)
    (L : ℝ) (hL : 0≤L)
    (hLip : ∀ a x,x∈Set.Icc (0 : ℝ) 1 → ∀ v∈Set.Icc (0 : ℝ) 1,
      PositiveCellApproximation.inducedNorm (C := C) (D.op a v-D.op a x)≤L*|v-x|)
    (herror : ∀ a k z,z∈C.base →
      C.value (PositivePolynomialApproximation.coefficient n (D.op a) k z-T a k z)≤eta a k)
    (a : A) (z : E) (hz : z∈C.base) :
    (∫ x,C.value (D.op a x z-combination n (T a) x z)∂BernsteinKernel.measure)≤
      L/Real.sqrt (3*((n : ℝ)+2))+(1/((n : ℝ)+1))*∑ k,eta a k := by
  have htriangle := integrated_triangle C (D.op a)
    (PositivePolynomialApproximation.approximation n (D.op a)) (combination n (T a))
    (D.integrable_op a) (PositivePolynomialApproximation.approximation_integrable n (D.op a))
    (combination_integrable n (T a)) z
  have hbias := PositivePolynomialApproximation.approximating_instrument_discrepancy
    n D L hL hLip a z hz
  have hcoef := coefficient_integrated_error C n
    (PositivePolynomialApproximation.coefficient n (D.op a)) (T a) (eta a) z
    (fun k => herror a k z hz)
  exact htriangle.trans (add_le_add hbias hcoef)

omit [MeasurableSpace E] [BorelSpace E] in
/-- The stated action-uniform budget uses the actual finite maximum. -/
theorem uniform_bias_plus_coefficient_error [Fintype A] (n : ℕ)
    (D : DensityInstrument (A := A) C BernsteinKernel.measure)
    (T : A → Fin (n+1) → E →L[ℝ] E) (eta : A → Fin (n+1) → ℝ)
    (L : ℝ) (hL : 0≤L)
    (hLip : ∀ a x,x∈Set.Icc (0 : ℝ) 1 → ∀ v∈Set.Icc (0 : ℝ) 1,
      PositiveCellApproximation.inducedNorm (C := C) (D.op a v-D.op a x)≤L*|v-x|)
    (herror : ∀ a k z,z∈C.base →
      C.value (PositivePolynomialApproximation.coefficient n (D.op a) k z-T a k z)≤eta a k)
    (a : A) (z : E) (hz : z∈C.base) :
    (∫ x,C.value (D.op a x z-combination n (T a) x z)∂BernsteinKernel.measure)≤
      L/Real.sqrt (3*((n : ℝ)+2))+maximumCoefficientError n eta :=
  (bias_plus_coefficient_error C n D T eta L hL hLip herror a z hz).trans
    (add_le_add le_rfl (coefficient_error_le_maximum n eta a))

omit [MeasurableSpace E] [BorelSpace E] in
/-- A separately known model-correction discrepancy adds by another actual triangle inequality. -/
theorem separate_correction_budget [Fintype A] (n : ℕ)
    (D G : DensityInstrument (A := A) C BernsteinKernel.measure)
    (T : A → Fin (n+1) → E →L[ℝ] E) (eta : A → Fin (n+1) → ℝ)
    (L correction : ℝ) (hL : 0≤L)
    (hLip : ∀ a x,x∈Set.Icc (0 : ℝ) 1 → ∀ v∈Set.Icc (0 : ℝ) 1,
      PositiveCellApproximation.inducedNorm (C := C) (D.op a v-D.op a x)≤L*|v-x|)
    (herror : ∀ a k z,z∈C.base →
      C.value (PositivePolynomialApproximation.coefficient n (D.op a) k z-T a k z)≤eta a k)
    (hcorrection : ∀ a z,z∈C.base →
      (∫ x,C.value (combination n (T a) x z-G.op a x z)∂BernsteinKernel.measure)≤correction)
    (a : A) (z : E) (hz : z∈C.base) :
    (∫ x,C.value (D.op a x z-G.op a x z)∂BernsteinKernel.measure)≤
      L/Real.sqrt (3*((n : ℝ)+2))+maximumCoefficientError n eta+correction :=
  (integrated_triangle C (D.op a) (combination n (T a)) (G.op a)
    (D.integrable_op a) (combination_integrable n (T a)) (G.integrable_op a) z).trans
      (add_le_add (uniform_bias_plus_coefficient_error C n D T eta L hL hLip herror a z hz)
        (hcorrection a z hz))

/-- Every finite joint record law of the fitted valid model is normalized. -/
theorem fitted_record_probability [Fintype A] [MeasurableSpace A] [MeasurableSingletonClass A]
    (n : ℕ) (T : A → Fin (n+1) → E →L[ℝ] E)
    (hT : ∀ a k z,z∈C.carrier → T a k z∈C.carrier)
    (hm : ∀ a z,C.mass (((1/((n : ℝ)+1)) • ∑ k,T a k) z)=C.mass z)
    (policy : ContinuousRecords.Policy (A := A) (Y := ℝ))
    (z : E) (hz : z∈C.base) (horizon : ℕ) :
    IsProbabilityMeasure (ContinuousRecords.recordLaw (fittedInstrument C n T hT hm) policy z horizon) :=
  ContinuousRecords.recordLaw_probability (fittedInstrument C n T hT hm) policy ⟨z,hz⟩ horizon

end
end Komorebi.LSM.BernsteinCoefficientError
