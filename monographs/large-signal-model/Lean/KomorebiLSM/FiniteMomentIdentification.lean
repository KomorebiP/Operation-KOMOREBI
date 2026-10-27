import KomorebiLSM.UniformIntervalMoments
import KomorebiLSM.ResetCertificate

/-! P54: conditional reconstruction from actual uniform moments, a full square
population core, and bounded signed reset experiments. -/
set_option autoImplicit false
open MeasureTheory Matrix
open scoped BigOperators

namespace Komorebi.LSM.FiniteMomentIdentification

section Mixing
variable {n : ℕ} {E : Type*} [AddCommGroup E] [Module ℝ E]

/-- A scalar matrix acts on a finite family in any real vector space. -/
def mix (W : Matrix (Fin n) (Fin n) ℝ) (X : Fin n → E) (k : Fin n) : E :=
  ∑ j, W k j • X j

@[simp] theorem mix_one (X : Fin n → E) : mix (1 : Matrix (Fin n) (Fin n) ℝ) X = X := by
  classical
  funext k
  simp [mix, Matrix.one_apply]

theorem mix_mul (W V : Matrix (Fin n) (Fin n) ℝ) (X : Fin n → E) :
    mix W (mix V X) = mix (W * V) X := by
  funext k
  simp only [mix, Finset.smul_sum, smul_smul, Matrix.mul_apply]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro l _
  rw [Finset.sum_smul]

theorem gram_inverse_reconstruction (D : ℕ) (X : Fin (D + 1) → E) :
    mix (UniformIntervalMoments.gram D)⁻¹ (mix (UniformIntervalMoments.gram D) X) = X := by
  rw [mix_mul, UniformIntervalMoments.gram_inv_mul, mix_one]
end Mixing

section Population
variable {r D : ℕ}
abbrev State (r : ℕ) := Fin r → ℝ
abbrev Operator (r : ℕ) := Matrix (Fin r) (Fin r) ℝ

/-- The declared degree bound is encoded by the supplied coefficient family. -/
def density (C : Fin (D + 1) → Operator r) (u : ℝ) : Operator r :=
  ∑ k : Fin (D + 1), u ^ (k : ℕ) • C k

/-- Actual population moment operators, evaluated entry by entry. -/
noncomputable def momentOperator (C : Fin (D + 1) → Operator r)
    (j : Fin (D + 1)) : Operator r :=
  fun i l => ∫ u, u ^ (j : ℕ) * density C u i l ∂UniformIntervalMoments.measure

/-- Integrating the finite polynomial expansion derives the moment equation. -/
theorem momentOperator_eq (C : Fin (D + 1) → Operator r) :
    momentOperator C = mix (UniformIntervalMoments.gram D) C := by
  funext j
  ext i l
  simp only [momentOperator, density, Matrix.sum_apply, Matrix.smul_apply, smul_eq_mul,
    Finset.mul_sum, mix, UniformIntervalMoments.gram]
  rw [integral_finsetSum (f := fun (k : Fin (D + 1)) u => u ^ (j : ℕ) * (u ^ (k : ℕ) * C k i l)) _
    (fun k _ => UniformIntervalMoments.continuous_integrable (by fun_prop))]
  apply Finset.sum_congr rfl
  intro k _
  rw [show (fun u : ℝ => u ^ (j : ℕ) * (u ^ (k : ℕ) * C k i l)) =
    (fun u => u ^ ((j : ℕ) + k) * C k i l) by funext u; rw [pow_add]; ring]
  exact integral_mul_const _ _

/-- Both factors are invertible because the population core is square in the
supplied true predictive dimension. -/
theorem core_factors_isUnit (T S : Operator r) (hH : IsUnit (T * S)) :
    IsUnit T ∧ IsUnit S :=
  ⟨isUnit_of_mul_isUnit_left hH, isUnit_of_mul_isUnit_right hH⟩

noncomputable def populationCore (T S : Operator r) : Operator r := T * S

noncomputable def populationTable (T S : Operator r)
    (C : Fin (D + 1) → Operator r) (j : Fin (D + 1)) : Operator r :=
  T * momentOperator C j * S

/-- A population-table entry is the signed integral of the corresponding
history-to-future entry of the actual polynomial density. -/
theorem populationTable_entry_integral (T S : Operator r)
    (C : Fin (D + 1) → Operator r) (j : Fin (D + 1)) (i l : Fin r) :
    populationTable T S C j i l =
      ∫ u, u ^ (j : ℕ) * (T * density C u * S) i l ∂UniformIntervalMoments.measure := by
  simp only [populationTable, Matrix.mul_apply, momentOperator,
    Finset.sum_mul, Finset.mul_sum]
  rw [integral_finsetSum (f := fun b u =>
    ∑ a, u ^ (j : ℕ) * (T i a * density C u a b * S b l)) _
    (fun b _ => UniformIntervalMoments.continuous_integrable (by
      unfold density
      fun_prop))]
  apply Finset.sum_congr rfl
  intro b _
  rw [integral_finsetSum (f := fun a u =>
    u ^ (j : ℕ) * (T i a * density C u a b * S b l)) _
    (fun a _ => UniformIntervalMoments.continuous_integrable (by
      unfold density
      fun_prop))]
  apply Finset.sum_congr rfl
  intro a _
  rw [show (fun u : ℝ => u ^ (j : ℕ) * (T i a * density C u a b * S b l)) =
      (fun u => T i a * (u ^ (j : ℕ) * density C u a b) * S b l) by
    funext u
    ring]
  rw [integral_mul_const, integral_const_mul]

noncomputable def reconstructedMoment (H : Operator r)
    (G : Fin (D + 1) → Operator r) (j : Fin (D + 1)) : Operator r := G j * H⁻¹

noncomputable def reconstructedCoefficient (H : Operator r)
    (G : Fin (D + 1) → Operator r) (k : Fin (D + 1)) : Operator r :=
  mix (UniformIntervalMoments.gram D)⁻¹ (reconstructedMoment H G) k

/-- Exact population tables recover the moment operators in test coordinates. -/
theorem reconstructedMoment_eq (T S : Operator r) (hH : IsUnit (populationCore T S))
    (C : Fin (D + 1) → Operator r) (j : Fin (D + 1)) :
    reconstructedMoment (populationCore T S) (populationTable T S C) j =
      T * momentOperator C j * T⁻¹ := by
  have hS := (core_factors_isUnit T S hH).2
  simp only [reconstructedMoment, populationTable, populationCore, Matrix.mul_inv_rev]
  calc
    T * momentOperator C j * S * (S⁻¹ * T⁻¹) =
      T * momentOperator C j * (S * S⁻¹) * T⁻¹ := by simp only [Matrix.mul_assoc]
    _ = _ := by rw [Matrix.mul_nonsing_inv S ((Matrix.isUnit_iff_isUnit_det S).mp hS)]; simp

/-- Scalar inversion commutes with the single fixed change of predictive coordinates. -/
theorem mix_conjugate (W : Matrix (Fin (D + 1)) (Fin (D + 1)) ℝ)
    (T : Operator r) (X : Fin (D + 1) → Operator r) (k : Fin (D + 1)) :
    mix W (fun j => T * X j * T⁻¹) k = T * mix W X k * T⁻¹ := by
  simp only [mix, Matrix.mul_sum, Matrix.sum_mul, Matrix.mul_smul, Matrix.smul_mul]

/-- The inverse coefficient formula is derived from exact integration and the
proved Gram inverse; it is not an assumed moment relation. -/
theorem reconstructedCoefficient_eq (T S : Operator r)
    (hH : IsUnit (populationCore T S)) (C : Fin (D + 1) → Operator r)
    (k : Fin (D + 1)) :
    reconstructedCoefficient (populationCore T S) (populationTable T S C) k =
      T * C k * T⁻¹ := by
  have hm : reconstructedMoment (populationCore T S) (populationTable T S C) =
      (fun j => T * momentOperator C j * T⁻¹) := by
    funext j
    exact reconstructedMoment_eq T S hH C j
  rw [reconstructedCoefficient, hm, mix_conjugate, momentOperator_eq]
  rw [gram_inverse_reconstruction]

/-- Reconstruction determines the entire declared polynomial density at every
observation value, rather than just its sampled moments. -/
theorem reconstructed_density_eq (T S : Operator r)
    (hH : IsUnit (populationCore T S)) (C : Fin (D + 1) → Operator r) (u : ℝ) :
    density (reconstructedCoefficient (populationCore T S) (populationTable T S C)) u =
      T * density C u * T⁻¹ := by
  simp only [density, reconstructedCoefficient_eq T S hH C,
    Matrix.mul_sum, Matrix.sum_mul, Matrix.mul_smul, Matrix.smul_mul]

/-- The supplied initial test vector is exactly the transformed initial state. -/
theorem initial_test_coordinates (T S : Operator r)
    (hH : IsUnit (populationCore T S)) (z : State r) :
    T⁻¹ *ᵥ (T *ᵥ z) = z := by
  have hT := (core_factors_isUnit T S hH).1
  rw [Matrix.mulVec_mulVec,
    Matrix.nonsing_inv_mul T ((Matrix.isUnit_iff_isUnit_det T).mp hT), Matrix.one_mulVec]

/-- Sequential polynomial operators on an unnormalized predictive state. -/
def wordState {A : Type*} (B : A → ℝ → Operator r) : List (A × ℝ) → State r → State r
  | [], z => z
  | (a, u) :: w, z => wordState B w (B a u *ᵥ z)

/-- The recovered family and supplied initial test vector reproduce every
finite operator word in the same test coordinates. -/
theorem reconstructed_word_coordinates {A : Type*} (T S : Operator r)
    (hH : IsUnit (populationCore T S)) (C : A → Fin (D + 1) → Operator r)
    (w : List (A × ℝ)) (z : State r) :
    wordState (fun a => density (reconstructedCoefficient (populationCore T S)
      (populationTable T S (C a)))) w (T *ᵥ z) =
      T *ᵥ wordState (fun a => density (C a)) w z := by
  induction w generalizing z with
  | nil => rfl
  | cons s w ih =>
    rcases s with ⟨a, u⟩
    simp only [wordState, reconstructed_density_eq T S hH]
    have hstep : (T * density (C a) u * T⁻¹) *ᵥ (T *ᵥ z) =
        T *ᵥ (density (C a) u *ᵥ z) := by
      rw [← Matrix.mulVec_mulVec, initial_test_coordinates T S hH,
        ← Matrix.mulVec_mulVec]
    rw [hstep, ih]
end Population

section Error
variable {n : ℕ} {E : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]

/-- The inverse-row estimate holds for one fixed norm on the moment and
coefficient space; in particular it holds for any fixed induced operator norm. -/
theorem fixed_norm_reconstruction_error (W : Matrix (Fin n) (Fin n) ℝ)
    (X Y : Fin n → E) (η : ℝ) (_hη : 0 ≤ η) (herror : ∀ j, ‖Y j - X j‖ ≤ η)
    (k : Fin n) :
    ‖mix W Y k - mix W X k‖ ≤ η * ∑ j, |W k j| := by
  have heq : mix W Y k - mix W X k = ∑ j, W k j • (Y j - X j) := by
    simp only [mix, smul_sub, Finset.sum_sub_distrib]
  rw [heq]
  calc
    _ ≤ ∑ j, ‖W k j • (Y j - X j)‖ := norm_sum_le _ _
    _ ≤ ∑ j, |W k j| * η := Finset.sum_le_sum (fun j _ => by
      rw [norm_smul, Real.norm_eq_abs]
      exact mul_le_mul_of_nonneg_left (herror j) (abs_nonneg _))
    _ = _ := by rw [← Finset.sum_mul]; ring

/-- P54's coefficient error bound for the same fixed induced norm throughout. -/
theorem induced_norm_coefficient_error {F : Type*} [NormedAddCommGroup F]
    [NormedSpace ℝ F] (D : ℕ)
    (X Y : Fin (D + 1) → (F →L[ℝ] F)) (η : ℝ) (hη : 0 ≤ η)
    (herror : ∀ j, ‖Y j - X j‖ ≤ η) (k : Fin (D + 1)) :
    ‖mix (UniformIntervalMoments.gram D)⁻¹ Y k - mix (UniformIntervalMoments.gram D)⁻¹ X k‖ ≤
      η * ∑ j, |(UniformIntervalMoments.gram D)⁻¹ k j| :=
  fixed_norm_reconstruction_error _ X Y η hη herror k
end Error

section SignedReset
open ProbabilityTheory Real
variable {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω} [IsProbabilityMeasure μ]

/-- A reset event-word trial weighted by the designated observation power.
Odd powers are signed; no branch-probability normalization is applied. -/
noncomputable def signedResetValue (event : Set Ω) (observation : Ω → ℝ) (j : ℕ) : Ω → ℝ :=
  event.indicator (fun ω => observation ω ^ j)

omit [MeasurableSpace Ω] in
theorem signedResetValue_bounded (event : Set Ω) (observation : Ω → ℝ) (j : ℕ)
    (hobs : ∀ ω, observation ω ∈ Set.Icc (-1 : ℝ) 1) (ω : Ω) :
    signedResetValue event observation j ω ∈ Set.Icc (-1 : ℝ) 1 := by
  classical
  by_cases h : ω ∈ event
  · rw [signedResetValue, Set.indicator_of_mem h]
    apply abs_le.mp
    rw [abs_pow]
    exact pow_le_one₀ (abs_nonneg _) (abs_le.mpr (hobs ω))
  · simp [signedResetValue, h]

omit [IsProbabilityMeasure μ] in
/-- The population expectation is the event-restricted signed moment. -/
theorem signedResetValue_expectation (event : Set Ω) (hevent : MeasurableSet event)
    (observation : Ω → ℝ) (j : ℕ) :
    (∫ ω, signedResetValue event observation j ω ∂μ) =
      ∫ ω in event, observation ω ^ j ∂μ := integral_indicator hevent

theorem signed_centered_trial_subgaussian {X : Ω → ℝ} {p : ℝ}
    (hm : AEMeasurable X μ) (hb : ∀ᵐ ω ∂μ, X ω ∈ Set.Icc (-1 : ℝ) 1)
    (hp : ∫ ω, X ω ∂μ = p) :
    HasSubgaussianMGF (fun ω => X ω - p) 1 μ := by
  have h := hasSubgaussianMGF_of_mem_Icc hm hb
  rw [hp] at h
  convert h using 1
  norm_num

theorem signed_centered_sum_subgaussian {N : ℕ} (X : Fin N → Ω → ℝ) (p : ℝ)
    (hind : iIndepFun X μ) (hm : ∀ i, AEMeasurable (X i) μ)
    (hb : ∀ i, ∀ᵐ ω ∂μ, X i ω ∈ Set.Icc (-1 : ℝ) 1)
    (hp : ∀ i, ∫ ω, X i ω ∂μ = p) :
    HasSubgaussianMGF (fun ω => ∑ i, (X i ω - p)) (N : NNReal) μ := by
  have hi : iIndepFun (fun i ω => X i ω - p) μ :=
    hind.comp (fun _ x => x - p) (fun _ => by fun_prop)
  simpa using HasSubgaussianMGF.sum_of_iIndepFun hi
    (s := Finset.univ) (c := fun _ => (1 : NNReal))
    (fun i _ => signed_centered_trial_subgaussian (hm i) (hb i) (hp i))

/-- The two-sided signed-trial bound has range two and exponent `-N ε²/2`. -/
theorem signed_reset_error_bound {N : ℕ} (hN : 0 < N) (X : Fin N → Ω → ℝ) (p ε : ℝ)
    (hind : iIndepFun X μ) (hm : ∀ i, AEMeasurable (X i) μ)
    (hb : ∀ i, ∀ᵐ ω ∂μ, X i ω ∈ Set.Icc (-1 : ℝ) 1)
    (hp : ∀ i, ∫ ω, X i ω ∂μ = p) (hε : 0 ≤ ε) :
    μ.real {ω | ε ≤ |ResetCertificate.sampleMean X ω - p|} ≤ 2 * exp (-(N : ℝ) * ε^2 / 2) := by
  have hn : (0 : ℝ) < N := by exact_mod_cast hN
  have hs := signed_centered_sum_subgaussian X p hind hm hb hp
  have hu := hs.measure_ge_le (mul_nonneg hn.le hε)
  have hl := hs.neg.measure_ge_le (mul_nonneg hn.le hε)
  have hexp : exp (-((N : ℝ) * ε)^2 / (2 * (N : NNReal))) =
      exp (-(N : ℝ) * ε^2 / 2) := by
    congr 1
    push_cast
    field_simp
  rw [hexp] at hu hl
  have hevent : {ω | ε ≤ |ResetCertificate.sampleMean X ω - p|} ⊆
      {ω | (N : ℝ) * ε ≤ ∑ i, (X i ω - p)} ∪
      {ω | (N : ℝ) * ε ≤ -(∑ i, (X i ω - p))} := by
    intro ω h
    change ε ≤ |ResetCertificate.sampleMean X ω - p| at h
    rw [le_abs] at h
    rcases h with h | h
    · exact Or.inl (by
        change (N : ℝ) * ε ≤ ∑ i, (X i ω - p)
        rw [ResetCertificate.centered_sum_eq hN]
        nlinarith)
    · exact Or.inr (by
        change (N : ℝ) * ε ≤ -(∑ i, (X i ω - p))
        rw [ResetCertificate.centered_sum_eq hN]
        nlinarith)
  calc
    _ ≤ μ.real ({ω | (N : ℝ) * ε ≤ ∑ i, (X i ω - p)} ∪
        {ω | (N : ℝ) * ε ≤ -(∑ i, (X i ω - p))}) := measureReal_mono hevent
    _ ≤ _ := measureReal_union_le _ _
    _ ≤ _ := by simpa only [Pi.neg_apply, two_mul] using add_le_add hu hl

/-- Entries are predeclared; independence is required within each entry's reset
trials, with no independence assumption between different entries. -/
theorem simultaneous_signed_error_bound {W : Type*} [Fintype W] {N : ℕ}
    (hN : 0 < N) (X : W → Fin N → Ω → ℝ) (p : W → ℝ) (ε : ℝ)
    (hind : ∀ w, iIndepFun (X w) μ) (hm : ∀ w i, AEMeasurable (X w i) μ)
    (hb : ∀ w i, ∀ᵐ ω ∂μ, X w i ω ∈ Set.Icc (-1 : ℝ) 1)
    (hp : ∀ w i, ∫ ω, X w i ω ∂μ = p w) (hε : 0 ≤ ε) :
    μ.real {ω | ∃ w, ε < |ResetCertificate.sampleMean (X w) ω - p w|} ≤
      2 * Fintype.card W * exp (-(N : ℝ) * ε^2 / 2) := by
  classical
  have hset : {ω | ∃ w, ε < |ResetCertificate.sampleMean (X w) ω - p w|} ⊆
      ⋃ w, {ω | ε ≤ |ResetCertificate.sampleMean (X w) ω - p w|} := by
    rintro ω ⟨w, hw⟩
    exact Set.mem_iUnion.mpr ⟨w, hw.le⟩
  calc
    _ ≤ μ.real (⋃ w, {ω | ε ≤ |ResetCertificate.sampleMean (X w) ω - p w|}) :=
      measureReal_mono hset
    _ ≤ ∑ w, μ.real {ω | ε ≤ |ResetCertificate.sampleMean (X w) ω - p w|} :=
      measureReal_iUnion_fintype_le _
    _ ≤ ∑ _w : W, 2 * exp (-(N : ℝ) * ε^2 / 2) := Finset.sum_le_sum (fun w _ =>
      signed_reset_error_bound hN (X w) (p w) ε (hind w) (hm w) (hb w) (hp w) hε)
    _ = _ := by simp; ring

noncomputable def signedRadius (M N : ℕ) (δ : ℝ) : ℝ :=
  sqrt (2 * log (2 * M / δ) / N)

omit [MeasurableSpace Ω] in
theorem signedRadius_budget {M N : ℕ} (hM : 0 < M) (hN : 0 < N) {δ : ℝ}
    (hδ : 0 < δ) (hδ1 : δ < 1) :
    2 * (M : ℝ) * exp (-(N : ℝ) * (signedRadius M N δ)^2 / 2) = δ := by
  have hm : (1 : ℝ) ≤ M := by exact_mod_cast hM
  have hn : (0 : ℝ) < N := by exact_mod_cast hN
  have hratio : 0 < 2 * (M : ℝ) / δ := by positivity
  have hrat1 : 1 ≤ 2 * (M : ℝ) / δ := (le_div_iff₀ hδ).mpr (by nlinarith)
  have hlog : 0 ≤ log (2 * (M : ℝ) / δ) := log_nonneg hrat1
  rw [signedRadius, sq_sqrt (div_nonneg (mul_nonneg (by norm_num) hlog) hn.le)]
  have he : -(N : ℝ) * (2 * log (2 * M / δ) / N) / 2 = -log (2 * M / δ) := by
    field_simp
  rw [he, exp_neg, exp_log hratio]
  field_simp

/-- P54's simultaneous range-two confidence radius for actual bounded reset
random variables with the declared exact population expectations. -/
theorem signed_reset_probability_certificate {W : Type*} [Fintype W] [Nonempty W] {N : ℕ}
    (hN : 0 < N) (X : W → Fin N → Ω → ℝ) (p : W → ℝ) {δ : ℝ}
    (hδ : 0 < δ) (hδ1 : δ < 1)
    (hind : ∀ w, iIndepFun (X w) μ) (hm : ∀ w i, Measurable (X w i))
    (hb : ∀ w i, ∀ᵐ ω ∂μ, X w i ω ∈ Set.Icc (-1 : ℝ) 1)
    (hp : ∀ w i, ∫ ω, X w i ω ∂μ = p w) :
    1 - δ ≤ μ.real {ω | ∀ w, |ResetCertificate.sampleMean (X w) ω - p w| ≤
      signedRadius (Fintype.card W) N δ} := by
  have hbad := simultaneous_signed_error_bound hN X p
    (signedRadius (Fintype.card W) N δ) hind
    (fun w i => (hm w i).aemeasurable) hb hp (sqrt_nonneg _)
  rw [signedRadius_budget Fintype.card_pos hN hδ hδ1] at hbad
  have hmeas : MeasurableSet {ω | ∃ w, signedRadius (Fintype.card W) N δ <
      |ResetCertificate.sampleMean (X w) ω - p w|} := by
    simp only [Set.ofPred_exists]
    apply MeasurableSet.iUnion
    intro w
    apply measurableSet_lt measurable_const
    unfold ResetCertificate.sampleMean
    fun_prop
  have hcomp : {ω | ∀ w, |ResetCertificate.sampleMean (X w) ω - p w| ≤
      signedRadius (Fintype.card W) N δ} =
      {ω | ∃ w, signedRadius (Fintype.card W) N δ <
        |ResetCertificate.sampleMean (X w) ω - p w|}ᶜ := by
    ext ω
    simp
  rw [hcomp, measureReal_compl hmeas]
  simpa using (by linarith : 1 - δ ≤ 1 - μ.real {ω | ∃ w,
    signedRadius (Fintype.card W) N δ < |ResetCertificate.sampleMean (X w) ω - p w|})
end SignedReset

end Komorebi.LSM.FiniteMomentIdentification
