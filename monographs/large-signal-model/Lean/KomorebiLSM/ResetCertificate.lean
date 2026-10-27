import Mathlib.Probability.Moments.SubGaussian
import Mathlib.Analysis.CStarAlgebra.Matrix

/-! The reset experiment concentration certificate. Trials for each experiment
are independent; experiments themselves may be arbitrarily dependent. -/
set_option autoImplicit false
namespace Komorebi.LSM.ResetCertificate
open MeasureTheory ProbabilityTheory Real
open scoped BigOperators

variable {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω} [IsProbabilityMeasure μ]

/-- Empirical probability of an experiment from its reset trials. -/
noncomputable def sampleMean {N : ℕ} (X : Fin N → Ω → ℝ) (ω : Ω) : ℝ :=
  (∑ i, X i ω) / N

/-- Hoeffding's lemma applies to every bounded reset indicator. -/
theorem centered_trial_subgaussian {X : Ω → ℝ} {p : ℝ}
    (hm : AEMeasurable X μ) (hb : ∀ᵐ ω ∂μ, X ω ∈ Set.Icc (0:ℝ) 1)
    (hp : ∫ ω, X ω ∂μ = p) :
    HasSubgaussianMGF (fun ω ↦ X ω - p) (1/4 : NNReal) μ := by
  have h := hasSubgaussianMGF_of_mem_Icc hm hb
  rw [hp] at h
  convert h using 1
  norm_num

/-- The centered sum of N independent reset trials has variance proxy N/4. -/
theorem centered_sum_subgaussian {N : ℕ} (X : Fin N → Ω → ℝ) (p : ℝ)
    (hind : iIndepFun X μ) (hm : ∀ i, AEMeasurable (X i) μ)
    (hb : ∀ i, ∀ᵐ ω ∂μ, X i ω ∈ Set.Icc (0:ℝ) 1)
    (hp : ∀ i, ∫ ω, X i ω ∂μ = p) :
    HasSubgaussianMGF (fun ω ↦ ∑ i, (X i ω-p)) ((N:NNReal)/4) μ := by
  have hi : iIndepFun (fun i ω ↦ X i ω-p) μ :=
    hind.comp (fun _ x ↦ x-p) (fun _ ↦ by fun_prop)
  have hs := HasSubgaussianMGF.sum_of_iIndepFun hi
    (s := Finset.univ) (c := fun _ ↦ (1/4:NNReal))
    (fun i _ ↦ centered_trial_subgaussian (hm i) (hb i) (hp i))
  simpa [div_eq_mul_inv] using hs

omit [MeasurableSpace Ω] in
/-- The sample-mean error is the centered reset sum divided by N. -/
theorem centered_sum_eq {N : ℕ} (hN : 0<N) (X : Fin N → Ω → ℝ) (p : ℝ) (ω : Ω) :
    (∑ i, (X i ω-p)) = (N:ℝ)*(sampleMean X ω-p) := by
  have hn : (N:ℝ) ≠ 0 := by exact_mod_cast Nat.ne_of_gt hN
  simp only [Finset.sum_sub_distrib, Finset.sum_const, Finset.card_univ,
    Fintype.card_fin, nsmul_eq_mul, sampleMean]
  field_simp

/-- Two-sided Hoeffding bound for one reset experiment, with no assumption
beyond the declared independence, bounded indicators and common expectation. -/
theorem reset_error_bound {N : ℕ} (hN : 0<N) (X : Fin N → Ω → ℝ) (p ε : ℝ)
    (hind : iIndepFun X μ) (hm : ∀ i, AEMeasurable (X i) μ)
    (hb : ∀ i, ∀ᵐ ω ∂μ, X i ω ∈ Set.Icc (0:ℝ) 1)
    (hp : ∀ i, ∫ ω, X i ω ∂μ = p) (hε : 0≤ε) :
    μ.real {ω | ε ≤ |sampleMean X ω-p|} ≤ 2*exp (-2*N*ε^2) := by
  have hn : (0:ℝ)<N := by exact_mod_cast hN
  have hs := centered_sum_subgaussian X p hind hm hb hp
  have hu := hs.measure_ge_le (mul_nonneg hn.le hε)
  have hl := hs.neg.measure_ge_le (mul_nonneg hn.le hε)
  have hexp : exp (-((N:ℝ)*ε)^2 / (2*((N:NNReal)/4:NNReal))) =
      exp (-2*N*ε^2) := by
    congr 1
    push_cast
    field_simp
    ring
  rw [hexp] at hu hl
  have hevent : {ω | ε ≤ |sampleMean X ω-p|} ⊆
      {ω | (N:ℝ)*ε ≤ ∑ i, (X i ω-p)} ∪
      {ω | (N:ℝ)*ε ≤ -(∑ i, (X i ω-p))} := by
    intro ω h
    change ε ≤ |sampleMean X ω-p| at h
    rw [le_abs] at h
    rcases h with h|h
    · exact Or.inl (by
        change (N:ℝ)*ε ≤ ∑ i, (X i ω-p)
        rw [centered_sum_eq hN]
        nlinarith)
    · exact Or.inr (by
        change (N:ℝ)*ε ≤ -(∑ i, (X i ω-p))
        rw [centered_sum_eq hN]
        nlinarith)
  calc
    _ ≤ μ.real ({ω | (N:ℝ)*ε ≤ ∑ i, (X i ω-p)} ∪
        {ω | (N:ℝ)*ε ≤ -(∑ i, (X i ω-p))}) := measureReal_mono hevent
    _ ≤ _ := measureReal_union_le _ _
    _ ≤ _ := by simpa only [Pi.neg_apply, two_mul] using add_le_add hu hl

/-- Simultaneous reset estimates need no independence across experiments. -/
theorem simultaneous_error_bound {W : Type*} [Fintype W] {N : ℕ}
    (hN : 0<N) (X : W → Fin N → Ω → ℝ) (p : W → ℝ) (ε : ℝ)
    (hind : ∀ w, iIndepFun (X w) μ)
    (hm : ∀ w i, AEMeasurable (X w i) μ)
    (hb : ∀ w i, ∀ᵐ ω ∂μ, X w i ω ∈ Set.Icc (0:ℝ) 1)
    (hp : ∀ w i, ∫ ω, X w i ω ∂μ = p w) (hε : 0≤ε) :
    μ.real {ω | ∃ w, ε < |sampleMean (X w) ω-p w|} ≤
      2*Fintype.card W*exp (-2*N*ε^2) := by
  classical
  have hset : {ω | ∃ w, ε < |sampleMean (X w) ω-p w|} ⊆
      ⋃ w, {ω | ε ≤ |sampleMean (X w) ω-p w|} := by
    rintro ω ⟨w, hw⟩
    exact Set.mem_iUnion.mpr ⟨w, hw.le⟩
  calc
    _ ≤ μ.real (⋃ w, {ω | ε ≤ |sampleMean (X w) ω-p w|}) := measureReal_mono hset
    _ ≤ ∑ w, μ.real {ω | ε ≤ |sampleMean (X w) ω-p w|} :=
      measureReal_iUnion_fintype_le _
    _ ≤ ∑ _w : W, 2*exp (-2*N*ε^2) := Finset.sum_le_sum (fun w _ ↦
      reset_error_bound hN (X w) (p w) ε (hind w) (hm w) (hb w) (hp w) hε)
    _ = _ := by simp; ring

/-- The declared simultaneous confidence radius for M experiments and N trials. -/
noncomputable def radius (M N : ℕ) (δ : ℝ) : ℝ :=
  sqrt (log (2*M/δ)/(2*N))

omit [MeasurableSpace Ω] in
/-- The radius converts the finite union bound into the chosen confidence budget. -/
theorem radius_budget {M N : ℕ} (hM : 0<M) (hN : 0<N) {δ : ℝ}
    (hδ : 0<δ) (hδ1 : δ<1) :
    2*(M:ℝ)*exp (-2*N*(radius M N δ)^2)=δ := by
  have hm : (1:ℝ) ≤ M := by exact_mod_cast hM
  have hn : (0:ℝ) < N := by exact_mod_cast hN
  have hratio : 0 < 2*(M:ℝ)/δ := by positivity
  have hrat1 : 1 ≤ 2*(M:ℝ)/δ := (le_div_iff₀ hδ).mpr (by nlinarith)
  have hlog : 0 ≤ log (2*(M:ℝ)/δ) := log_nonneg hrat1
  rw [radius, sq_sqrt (div_nonneg hlog (by positivity))]
  have he : -2*(N:ℝ)*(log (2*M/δ)/(2*N)) = -log (2*M/δ) := by
    field_simp
  rw [he, exp_neg, exp_log hratio]
  field_simp

/-- P35's confidence statement, for measurable bounded reset indicators. -/
theorem reset_probability_certificate {W : Type*} [Fintype W] [Nonempty W] {N : ℕ}
    (hN : 0<N) (X : W → Fin N → Ω → ℝ) (p : W → ℝ) {δ : ℝ}
    (hδ : 0<δ) (hδ1 : δ<1)
    (hind : ∀ w, iIndepFun (X w) μ)
    (hm : ∀ w i, Measurable (X w i))
    (hb : ∀ w i, ∀ᵐ ω ∂μ, X w i ω ∈ Set.Icc (0:ℝ) 1)
    (hp : ∀ w i, ∫ ω, X w i ω ∂μ = p w) :
    1-δ ≤ μ.real {ω | ∀ w, |sampleMean (X w) ω-p w| ≤ radius (Fintype.card W) N δ} := by
  have hbad := simultaneous_error_bound hN X p (radius (Fintype.card W) N δ)
    hind (fun w i ↦ (hm w i).aemeasurable) hb hp (sqrt_nonneg _)
  rw [radius_budget Fintype.card_pos hN hδ hδ1] at hbad
  have hmeas : MeasurableSet {ω | ∃ w, radius (Fintype.card W) N δ <
      |sampleMean (X w) ω-p w|} := by
    simp only [Set.ofPred_exists]
    apply MeasurableSet.iUnion
    intro w
    apply measurableSet_lt measurable_const
    unfold sampleMean
    fun_prop
  have hcomp : {ω | ∀ w, |sampleMean (X w) ω-p w| ≤ radius (Fintype.card W) N δ} =
      {ω | ∃ w, radius (Fintype.card W) N δ < |sampleMean (X w) ω-p w|}ᶜ := by
    ext ω
    simp
  rw [hcomp, measureReal_compl hmeas]
  simpa using sub_le_sub_left hbad 1

/-- Entrywise probability error bounds the Euclidean initial-coordinate error. -/
theorem vector_norm_le {r : ℕ} (x : EuclideanSpace ℝ (Fin r)) (ε : ℝ)
    (hε : 0≤ε) (hx : ∀ i, |x i|≤ε) : ‖x‖ ≤ sqrt r*ε := by
  have hsum : ∑ i, ‖x i‖^2 ≤ (r:ℝ)*ε^2 := by
    calc
      _ ≤ ∑ _i : Fin r, ε^2 := Finset.sum_le_sum (fun i _ ↦
        by simpa only [Real.norm_eq_abs] using pow_le_pow_left₀ (abs_nonneg _) (hx i) 2)
      _ = _ := by simp
  rw [← EuclideanSpace.norm_sq_eq] at hsum
  have hs : (sqrt (r:ℝ))^2=(r:ℝ) := sq_sqrt (Nat.cast_nonneg r)
  nlinarith [norm_nonneg x, sqrt_nonneg (r:ℝ), mul_nonneg (sqrt_nonneg (r:ℝ)) hε]

set_option maxHeartbeats 800000 in
/-- Entrywise probability error bounds the actual spectral operator norm. -/
theorem matrix_opNorm_le {r : ℕ} (A : Matrix (Fin r) (Fin r) ℝ) (ε : ℝ)
    (hε : 0≤ε) (hA : ∀ i j, |A i j|≤ε) :
    ‖((A.toEuclideanLin.toContinuousLinearMap) : EuclideanSpace ℝ (Fin r) →L[ℝ] EuclideanSpace ℝ (Fin r))‖ ≤ (r:ℝ)*ε := by
  apply ContinuousLinearMap.opNorm_le_bound _ (by positivity)
  intro x
  have hx : ∑ j : Fin r, (x j)^2 = ‖x‖^2 := by
    simpa only [Real.norm_eq_abs, sq_abs] using (EuclideanSpace.norm_sq_eq x).symm
  have hrow : ∀ i, ∑ j, (A i j)^2 ≤ (r:ℝ)*ε^2 := by
    intro i
    calc
      _ ≤ ∑ _j : Fin r, ε^2 := Finset.sum_le_sum (fun j _ ↦
        by simpa only [sq_abs] using pow_le_pow_left₀ (abs_nonneg _) (hA i j) 2)
      _ = _ := by simp
  have hi : ∀ i, ((((A.toEuclideanLin.toContinuousLinearMap) : EuclideanSpace ℝ (Fin r) →L[ℝ] EuclideanSpace ℝ (Fin r))) x i)^2 ≤ (r:ℝ)*ε^2*‖x‖^2 := by
    intro i
    calc
      _ = (∑ j, A i j*x j)^2 := rfl
      _ ≤ (∑ j, (A i j)^2)*(∑ j, (x j)^2) := by
        simpa using Finset.sum_mul_sq_le_sq_mul_sq Finset.univ (fun j ↦ A i j) (fun j ↦ x j)
      _ ≤ _ := by rw [hx]; exact mul_le_mul_of_nonneg_right (hrow i) (sq_nonneg _)
  have hout : ‖(((A.toEuclideanLin.toContinuousLinearMap) : EuclideanSpace ℝ (Fin r) →L[ℝ] EuclideanSpace ℝ (Fin r))) x‖^2 ≤ ((r:ℝ)*ε*‖x‖)^2 := by
    rw [EuclideanSpace.norm_sq_eq]
    simp only [Real.norm_eq_abs, sq_abs]
    calc
      _ ≤ ∑ _i : Fin r, (r:ℝ)*ε^2*‖x‖^2 := Finset.sum_le_sum (fun i _ ↦ hi i)
      _ = _ := by simp; ring
  nlinarith [norm_nonneg ((((A.toEuclideanLin.toContinuousLinearMap) : EuclideanSpace ℝ (Fin r) →L[ℝ] EuclideanSpace ℝ (Fin r))) x),
    mul_nonneg (mul_nonneg (Nat.cast_nonneg r) hε) (norm_nonneg x)]

/-- Error in a probability table whose entries are covered by selected experiments. -/
noncomputable def tableError {W : Type*} {N r : ℕ}
    (X : W → Fin N → Ω → ℝ) (p : W → ℝ)
    (entry : Fin r → Fin r → W) (ω : Ω) : Matrix (Fin r) (Fin r) ℝ :=
  fun i j ↦ sampleMean (X (entry i j)) ω-p (entry i j)

/-- Error in initial coordinates covered by selected experiments. -/
noncomputable def initialError {W : Type*} {N r : ℕ}
    (X : W → Fin N → Ω → ℝ) (p : W → ℝ)
    (entry : Fin r → W) (ω : Ω) : EuclideanSpace ℝ (Fin r) :=
  WithLp.toLp 2 (fun i ↦ sampleMean (X (entry i)) ω-p (entry i))

/-- Full P35 endpoint: the same reset event controls H, every G_s and b₀,
using actual matrix spectral norms and the Euclidean initial-coordinate norm.
The coverage maps may repeat selected words; cross-word independence is absent. -/
theorem reset_table_probability_certificate {W S : Type*}
    [Fintype W] [Nonempty W] [Fintype S] {N r : ℕ}
    (hN : 0<N) (X : W → Fin N → Ω → ℝ) (p : W → ℝ) {δ : ℝ}
    (hδ : 0<δ) (hδ1 : δ<1)
    (hind : ∀ w, iIndepFun (X w) μ)
    (hm : ∀ w i, Measurable (X w i))
    (hb : ∀ w i, ∀ᵐ ω ∂μ, X w i ω ∈ Set.Icc (0:ℝ) 1)
    (hp : ∀ w i, ∫ ω, X w i ω ∂μ = p w)
    (Hentry : Fin r → Fin r → W) (Gentry : S → Fin r → Fin r → W)
    (bentry : Fin r → W) :
    1-δ ≤ μ.real {ω |
      ‖((tableError X p Hentry ω).toEuclideanLin.toContinuousLinearMap :
        EuclideanSpace ℝ (Fin r) →L[ℝ] EuclideanSpace ℝ (Fin r))‖ ≤
        (r:ℝ)*radius (Fintype.card W) N δ ∧
      (∀ s, ‖((tableError X p (Gentry s) ω).toEuclideanLin.toContinuousLinearMap :
        EuclideanSpace ℝ (Fin r) →L[ℝ] EuclideanSpace ℝ (Fin r))‖ ≤
        (r:ℝ)*radius (Fintype.card W) N δ) ∧
      ‖initialError X p bentry ω‖ ≤ sqrt r*radius (Fintype.card W) N δ} := by
  have hprob := reset_probability_certificate hN X p hδ hδ1 hind hm hb hp
  apply hprob.trans (measureReal_mono ?_)
  intro ω hω
  change ∀ w, |sampleMean (X w) ω-p w| ≤ radius (Fintype.card W) N δ at hω
  refine ⟨matrix_opNorm_le _ _ (sqrt_nonneg _) (fun i j ↦ hω (Hentry i j)), ?_, ?_⟩
  · intro s
    exact matrix_opNorm_le _ _ (sqrt_nonneg _) (fun i j ↦ hω (Gentry s i j))
  · exact vector_norm_le _ _ (sqrt_nonneg _) (fun i ↦ hω (bentry i))

end Komorebi.LSM.ResetCertificate
