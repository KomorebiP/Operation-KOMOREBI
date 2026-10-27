import KomorebiLSM.RegressionConfidence

/-! The literal scalar ridge-one, unit-prior-bound specialization of P81. -/
set_option autoImplicit false
namespace Komorebi.LSM.RegressionConfidence
open MeasureTheory ProbabilityTheory Matrix
open scoped BigOperators

noncomputable def scalarV (x : ℕ → ℝ) (n : ℕ) : ℝ := 1+∑ i∈Finset.range n,(x i)^2
noncomputable def scalarEstimate (x y : ℕ → ℝ) (n : ℕ) : ℝ :=
  (∑ i∈Finset.range n,x i*y i)/scalarV x n
noncomputable def scalarRadius (σ δ : ℝ) (x : ℕ → ℝ) (n : ℕ) : ℝ :=
  σ*Real.sqrt ((Real.log (scalarV x n)+2*Real.log (1/δ))/scalarV x n)+
    Real.sqrt (1/scalarV x n)

theorem scalarV_ge_one (x : ℕ → ℝ) (n : ℕ) : 1≤scalarV x n := by
  exact le_add_of_nonneg_right (Finset.sum_nonneg (fun i _ => sq_nonneg (x i)))

theorem scalarV_pos (x : ℕ → ℝ) (n : ℕ) : 0<scalarV x n :=
  lt_of_lt_of_le zero_lt_one (scalarV_ge_one x n)

theorem ridgeMatrix_scalar_entry (x : ℕ → ℝ) (n : ℕ) :
    ridgeMatrix (I := Fin 1) 1 (fun i _ => x i) n 0 0=scalarV x n := by
  simp [ridgeMatrix,designGram,scalarV,Matrix.sum_apply,Matrix.vecMulVec_apply,pow_two]

theorem ridgeEstimate_scalar (x y : ℕ → ℝ) (n : ℕ) :
    ridgeEstimate (I := Fin 1) 1 (fun i _ => x i) y n 0=scalarEstimate x y n := by
  unfold ridgeEstimate
  rw [Matrix.inv_subsingleton]
  simp [Matrix.mulVec,dotProduct,Ring.inverse_eq_inv,responseVector,
    Finset.sum_apply,ridgeMatrix_scalar_entry,scalarEstimate,div_eq_mul_inv,mul_comm]

theorem weightedNorm_scalar (V : Matrix (Fin 1) (Fin 1) ℝ) (z : Fin 1 → ℝ)
    (hV : 0≤V 0 0) : weightedNorm V z=Real.sqrt (V 0 0)*|z 0| := by
  have hq : z ⬝ᵥ (V *ᵥ z)=V 0 0*(z 0)^2 := by
    simp [dotProduct,Matrix.mulVec,pow_two]
    ring
  unfold weightedNorm
  rw [hq,Real.sqrt_mul hV,Real.sqrt_sq_eq_abs]

theorem euclideanNorm_scalar (θ : ℝ) : euclideanNorm (fun _ : Fin 1 => θ)=|θ| := by
  simp [euclideanNorm_eq,dotProduct,← pow_two,Real.sqrt_sq_eq_abs]

variable {Ω : Type*}
/-- The same actual generic Gaussian-mixture good event, specialized to Fin1. -/
noncomputable def scalarGood (σ δ : ℝ) (x y : ℕ → Ω → ℝ) (θ : ℝ) : Set Ω :=
  regressionGood 1 σ δ (fun i ω (_ : Fin 1) => x i ω) y (fun _ => θ)

theorem scalarGood_error_bound (σ δ : ℝ) (hσ : 0<σ) (hδ : 0<δ) (hδ1 : δ≤1)
    (x y : ℕ → Ω → ℝ) (θ : ℝ) (hθ : |θ|≤1) (ω : Ω)
    (hg : ω∈scalarGood σ δ x y θ) (n : ℕ) :
    |scalarEstimate (fun i => x i ω) (fun i => y i ω) n-θ|≤
      scalarRadius σ δ (fun i => x i ω) n := by
  have hprior : euclideanNorm (fun _ : Fin 1 => θ)≤1 := by simpa only [euclideanNorm_scalar] using hθ
  have h := regressionGood_error_bound 1 σ δ 1 (by norm_num) hσ hδ
    (fun i ω (_ : Fin 1) => x i ω) y (fun _ => θ) hprior ω hg n
  rw [weightedNorm_scalar _ _ (by rw [ridgeMatrix_scalar_entry]; exact (scalarV_pos _ _).le),
    ridgeMatrix_scalar_entry] at h
  simp only [Pi.sub_apply,ridgeEstimate_scalar,noiseRadius,Matrix.det_fin_one,
    ridgeMatrix_scalar_entry,one_smul,Matrix.one_apply_eq,div_one,Real.sqrt_one,mul_one] at h
  have hbound : |scalarEstimate (fun i => x i ω) (fun i => y i ω) n-θ|≤
      (σ*Real.sqrt (Real.log (scalarV (fun i => x i ω) n)+2*Real.log (1/δ))+1)/
        Real.sqrt (scalarV (fun i => x i ω) n) := by
    apply (le_div_iff₀ (Real.sqrt_pos.2 (scalarV_pos _ _))).2
    simpa only [mul_comm] using h
  apply hbound.trans_eq
  unfold scalarRadius
  have hlog : 0≤Real.log (1/δ) :=
    Real.log_nonneg ((le_div_iff₀ hδ).2 (by simpa using hδ1))
  have ha : 0≤Real.log (scalarV (fun i => x i ω) n)+2*Real.log (1/δ) :=
    add_nonneg (Real.log_nonneg (scalarV_ge_one _ _)) (mul_nonneg (by norm_num) hlog)
  rw [Real.sqrt_div ha,Real.sqrt_div (show (0:ℝ)≤1 by norm_num),Real.sqrt_one]
  ring

variable [mΩ : MeasurableSpace Ω] {μ : Measure Ω} [IsProbabilityMeasure μ]
/-- The literal scalar estimator and source radius inherit the actual generic
P81 probability event, without an independent scalar concentration assumption. -/
theorem scalar_regression_confidence_certificate (ℱ : Filtration ℕ mΩ)
    (σ δ : ℝ) (hσ : 0<σ) (hδ : 0<δ) (hδ1 : δ≤1)
    (x y : ℕ → Ω → ℝ) (θ : ℝ)
    (hx : ∀ n,Measurable[ℱ n] (x n)) (hy : ∀ n,Measurable[ℱ (n+1)] (y n)) (hθ : |θ|≤1)
    (H : ∀ n,ConditionalSubgaussian (ℱ.le n) (fun ω => y n ω-θ*x n ω) σ μ) :
    MeasurableSet (scalarGood σ δ x y θ) ∧ 1-δ≤μ.real (scalarGood σ δ x y θ) ∧
    ∀ ω∈scalarGood σ δ x y θ,∀ n,
      |scalarEstimate (fun i => x i ω) (fun i => y i ω) n-θ|≤
        scalarRadius σ δ (fun i => x i ω) n := by
  have hprior : euclideanNorm (fun _ : Fin 1 => θ)≤1 := by simpa only [euclideanNorm_scalar] using hθ
  have H' : ∀ n,ConditionalSubgaussian (ℱ.le n)
      (regressionNoise (fun _ : Fin 1 => θ) (fun i ω _ => x i ω) y n) σ μ := by
    intro n
    unfold regressionNoise
    simpa [dotProduct] using H n
  have hc := regression_confidence_certificate ℱ 1 σ δ 1 (by norm_num) hσ hδ
    (fun i ω (_ : Fin 1) => x i ω) y (fun _ => θ) (fun n _ => hx n) hy hprior H'
  exact ⟨hc.1,hc.2.1,fun ω hω n => scalarGood_error_bound σ δ hσ hδ hδ1 x y θ hθ ω hω n⟩

end Komorebi.LSM.RegressionConfidence
