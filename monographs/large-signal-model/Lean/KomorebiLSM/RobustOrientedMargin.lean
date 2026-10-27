import KomorebiLSM.LorentzCylinder
import KomorebiLSM.PolynomialGram
import KomorebiLSM.ContinuousRecords

/-! P71: an actual minimum margin on the normalized Lorentz base controls
orientation and spatial uncertainty before normalization. -/
set_option autoImplicit false
namespace Komorebi.LSM.RobustOrientedMargin
open LorentzCylinder MeasureTheory
open scoped BigOperators
variable {V : Type*} [NormedAddCommGroup V] [NormedSpace ℝ V]

/-- Oriented, unnormalized distance from the Lorentz boundary. -/
def slack (z : State V) : ℝ := z.1-‖z.2‖

omit [NormedSpace ℝ V] in
theorem slack_add_lower (w d : State V) :
    slack w-|d.1|-‖d.2‖≤slack (w+d) := by
  change w.1-‖w.2‖-|d.1|-‖d.2‖≤w.1+d.1-‖w.2+d.2‖
  linarith [norm_add_le w.2 d.2,neg_abs_le d.1]

variable [FiniteDimensional ℝ V]

/-- The minimum is attained on the actual entire normalized spatial ball. -/
theorem exists_minimum (F : State V →L[ℝ] State V) :
    ∃ v : V,‖v‖≤1 ∧ ∀ w : V,‖w‖≤1 → slack (F (1,v))≤slack (F (1,w)) := by
  have hc : IsCompact {v : V | ‖v‖≤1} := by
    simpa only [Metric.closedBall,dist_zero_right] using isCompact_closedBall (0 : V) 1
  have hn : ({v : V | ‖v‖≤1}).Nonempty := ⟨0,by simp⟩
  have hf : Continuous (fun v : V => slack (F (1,v))) := by
    exact ((F.continuous.comp (continuous_const.prodMk continuous_id)).fst).sub
      ((F.continuous.comp (continuous_const.prodMk continuous_id)).snd.norm)
  obtain ⟨v,hv,hmin⟩ := hc.exists_isMinOn hn hf.continuousOn
  exact ⟨v,hv,hmin⟩

noncomputable def worstInput (F : State V →L[ℝ] State V) : V := (exists_minimum F).choose
noncomputable def sigma (F : State V →L[ℝ] State V) : ℝ := slack (F (1,worstInput F))

theorem worstInput_mem (F : State V →L[ℝ] State V) : ‖worstInput F‖≤1 :=
  (exists_minimum F).choose_spec.1

theorem sigma_le (F : State V →L[ℝ] State V) (v : V) (hv : ‖v‖≤1) :
    sigma F≤slack (F (1,v)) := (exists_minimum F).choose_spec.2 v hv

/-- Thus a sigma bound is exactly a bound on every normalized input, not a grid. -/
theorem le_sigma_iff (F : State V →L[ℝ] State V) (kappa : ℝ) :
    kappa≤sigma F ↔ ∀ v : V,‖v‖≤1 → kappa≤slack (F (1,v)) := by
  constructor
  · intro h v hv
    exact h.trans (sigma_le F v hv)
  · intro h
    exact h (worstInput F) (worstInput_mem F)

/-- The residual slack is derived from the actual minimum and literal output errors. -/
theorem normalized_residual (F Delta : State V →L[ℝ] State V) (kappa e0 e1 : ℝ)
    (hmargin : kappa≤sigma F)
    (h0 : ∀ v : V,‖v‖≤1 → |(Delta (1,v)).1|≤e0)
    (h1 : ∀ v : V,‖v‖≤1 → ‖(Delta (1,v)).2‖≤e1)
    (v : V) (hv : ‖v‖≤1) : kappa-e0-e1≤slack ((F+Delta) (1,v)) := by
  have hm := hmargin.trans (sigma_le F v hv)
  have he0 := h0 v hv
  have he1 := h1 v hv
  have ha := slack_add_lower (F (1,v)) (Delta (1,v))
  change kappa-e0-e1≤slack (F (1,v)+Delta (1,v))
  linarith

/-- The actual minimum margin of the uncertain branch retains the residual slack. -/
theorem residual_margin (F Delta : State V →L[ℝ] State V) (kappa e0 e1 : ℝ)
    (hmargin : kappa≤sigma F)
    (h0 : ∀ v : V,‖v‖≤1 → |(Delta (1,v)).1|≤e0)
    (h1 : ∀ v : V,‖v‖≤1 → ‖(Delta (1,v)).2‖≤e1) :
    kappa-e0-e1≤sigma (F+Delta) :=
  (le_sigma_iff (F+Delta) _).mpr (fun v hv => normalized_residual F Delta kappa e0 e1 hmargin h0 h1 v hv)

omit [FiniteDimensional ℝ V] in
/-- Homogeneity extends normalized preservation to the entire cone, including zero mass. -/
theorem preserves_of_normalized (G : State V →L[ℝ] State V)
    (hG : ∀ v : V,‖v‖≤1 → G (1,v)∈cone) {z : State V} (hz : z∈cone) : G z∈cone := by
  have hm : 0≤z.1 := (norm_nonneg _).trans hz
  by_cases hm0 : z.1=0
  · have hz0 : z=0 := (probabilityCone.mass_zero_iff hz).mp hm0
    rw [hz0,map_zero]
    exact probabilityCone.zero_mem
  · have hmp : 0<z.1 := lt_of_le_of_ne hm (Ne.symm hm0)
    have hv : ‖z.1⁻¹ • z.2‖≤1 := by
      rw [norm_smul,Real.norm_eq_abs,abs_of_pos (inv_pos.mpr hmp)]
      exact (inv_mul_le_iff₀ hmp).mpr (by simpa using hz)
    have he : z=z.1 • (1,z.1⁻¹ • z.2) := by
      apply Prod.ext
      · simp
      · change z.2=z.1 • (z.1⁻¹ • z.2)
        rw [smul_smul,mul_inv_cancel₀ hm0,one_smul]
    rw [he,map_smul]
    exact probabilityCone.smul_mem hm (hG _ hv)

/-- P71 cone preservation follows from the oriented margin and the two error bounds. -/
theorem robust_preserves (F Delta : State V →L[ℝ] State V) (kappa e0 e1 : ℝ)
    (hmargin : kappa≤sigma F)
    (h0 : ∀ v : V,‖v‖≤1 → |(Delta (1,v)).1|≤e0)
    (h1 : ∀ v : V,‖v‖≤1 → ‖(Delta (1,v)).2‖≤e1)
    (hcover : e0+e1≤kappa) {z : State V} (hz : z∈cone) : (F+Delta) z∈cone := by
  apply preserves_of_normalized (F+Delta) _ hz
  intro v hv
  have hr := normalized_residual F Delta kappa e0 e1 hmargin h0 h1 v hv
  change ‖((F+Delta) (1,v)).2‖≤((F+Delta) (1,v)).1
  unfold slack at hr
  linarith

theorem strict_residual (F Delta : State V →L[ℝ] State V) (kappa e0 e1 : ℝ)
    (hmargin : kappa≤sigma F)
    (h0 : ∀ v : V,‖v‖≤1 → |(Delta (1,v)).1|≤e0)
    (h1 : ∀ v : V,‖v‖≤1 → ‖(Delta (1,v)).2‖≤e1)
    (hstrict : e0+e1<kappa) (v : V) (hv : ‖v‖≤1) :
    0<kappa-e0-e1 ∧ kappa-e0-e1≤slack ((F+Delta) (1,v)) :=
  ⟨by linarith,normalized_residual F Delta kappa e0 e1 hmargin h0 h1 v hv⟩

omit [FiniteDimensional ℝ V] in
/-- Positive-density branches have a normalized cone state; the premise is not floored. -/
theorem positive_posterior {G : State V →L[ℝ] State V}
    (hG : ∀ z∈cone,G z∈cone) {z : State V} (hz : z∈cone) (hp : 0<(G z).1) :
    ((G z).1⁻¹ • G z)∈probabilityCone.base := by
  refine ⟨probabilityCone.smul_mem (inv_nonneg.mpr hp.le) (hG z hz),?_⟩
  change (G z).1⁻¹*(G z).1=1
  exact inv_mul_cancel₀ hp.ne'

section Polynomial
variable {A : Type*} {n : ℕ}

omit [FiniteDimensional ℝ V] in
theorem polynomial_add (F Delta : Fin n → State V →L[ℝ] State V) (u : ℝ) :
    PolynomialGram.operatorPolynomial (fun k => F k+Delta k) u=
      PolynomialGram.operatorPolynomial F u+PolynomialGram.operatorPolynomial Delta u := by
  simp only [PolynomialGram.operatorPolynomial,smul_add,Finset.sum_add_distrib]

/-- Complete interval margin data, with no desired cone-invariance conclusion supplied. -/
structure MarginCertificate (F Delta : A → Fin n → State V →L[ℝ] State V)
    (kappa e0 e1 : A → ℝ → ℝ) where
  margin : ∀ a u,u∈Set.Icc (-1 : ℝ) 1 → kappa a u≤sigma (PolynomialGram.operatorPolynomial (F a) u)
  mass_error : ∀ a u,u∈Set.Icc (-1 : ℝ) 1 → ∀ v : V,‖v‖≤1 →
    |(PolynomialGram.operatorPolynomial (Delta a) u (1,v)).1|≤e0 a u
  spatial_error : ∀ a u,u∈Set.Icc (-1 : ℝ) 1 → ∀ v : V,‖v‖≤1 →
    ‖(PolynomialGram.operatorPolynomial (Delta a) u (1,v)).2‖≤e1 a u
  cover : ∀ a u,u∈Set.Icc (-1 : ℝ) 1 → e0 a u+e1 a u≤kappa a u

/-- Every certified interval value preserves the cone pointwise, including endpoints. -/
theorem MarginCertificate.preserves {F Delta : A → Fin n → State V →L[ℝ] State V}
    {kappa e0 e1 : A → ℝ → ℝ} (cert : MarginCertificate F Delta kappa e0 e1)
    (a : A) (u : ℝ) (hu : u∈Set.Icc (-1 : ℝ) 1) {z : State V} (hz : z∈cone) :
    PolynomialGram.operatorPolynomial (fun k => F a k+Delta a k) u z∈cone := by
  rw [polynomial_add]
  exact robust_preserves _ _ _ _ _ (cert.margin a u hu) (cert.mass_error a u hu)
    (cert.spatial_error a u hu) (cert.cover a u hu) hz

variable [MeasurableSpace V] [BorelSpace V]

/-- The uncertain polynomial itself is the literal valid observation density. -/
noncomputable def uncertainInstrument (F Delta : A → Fin n → State V →L[ℝ] State V)
    (kappa e0 e1 : A → ℝ → ℝ) (cert : MarginCertificate F Delta kappa e0 e1)
    (hm : ∀ a z,probabilityCone.mass ((∑ k : Fin n,UniformIntervalMoments.moment k • (F a k+Delta a k)) z)=
      probabilityCone.mass z) :
    ContinuousInstrument.DensityInstrument (A := A) (probabilityCone (V := V)) UniformIntervalMoments.measure where
  op a := PolynomialGram.operatorPolynomial (fun k => F a k+Delta a k)
  measurable_op a := (PolynomialGram.operatorPolynomial_continuous _).measurable
  integrable_op a := PolynomialGram.operatorPolynomial_integrable _
  positive a := by
    filter_upwards [PolynomialGram.uniform_ae_interval] with u hu
    intro z hz
    rw [polynomial_add]
    exact robust_preserves _ _ _ _ _ (cert.margin a u hu) (cert.mass_error a u hu)
      (cert.spatial_error a u hu) (cert.cover a u hu) hz
  mass_preserving a z := by
    rw [PolynomialGram.operatorPolynomial_integral]
    exact hm a z

theorem uncertain_record_probability [Fintype A] [MeasurableSpace A] [MeasurableSingletonClass A]
    (F Delta : A → Fin n → State V →L[ℝ] State V) (kappa e0 e1 : A → ℝ → ℝ)
    (cert : MarginCertificate F Delta kappa e0 e1)
    (hm : ∀ a z,probabilityCone.mass ((∑ k : Fin n,UniformIntervalMoments.moment k • (F a k+Delta a k)) z)=
      probabilityCone.mass z)
    (policy : ContinuousRecords.Policy (A := A) (Y := ℝ)) (z : State V)
    (hz : z∈probabilityCone.base) (horizon : ℕ) :
    IsProbabilityMeasure (ContinuousRecords.recordLaw (uncertainInstrument F Delta kappa e0 e1 cert hm)
      policy z horizon) :=
  ContinuousRecords.recordLaw_probability (uncertainInstrument F Delta kappa e0 e1 cert hm)
    policy ⟨z,hz⟩ horizon

end Polynomial

section Atlas
variable {E A : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
  [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E]
  [MeasurableSpace V] [BorelSpace V] {n : ℕ}

/-- Inverse conjugation uses the actual atlas, with its actual inverse. -/
noncomputable def pullbackOperator (T : E ≃ₗ[ℝ] State V) (G : State V →L[ℝ] State V) : E →L[ℝ] E :=
  (T.symm.toLinearMap.comp (G.toLinearMap.comp T.toLinearMap)).toContinuousLinearMap

omit [FiniteDimensional ℝ V] [MeasurableSpace E] [BorelSpace E] [MeasurableSpace V] [BorelSpace V] in
@[simp] theorem pullbackOperator_action (T : E ≃ₗ[ℝ] State V)
    (G : State V →L[ℝ] State V) (z : E) : T (pullbackOperator T G z)=G (T z) := by
  change T (T.symm (G (T z)))=_
  exact T.apply_symm_apply _

omit [FiniteDimensional ℝ V] [MeasurableSpace E] [BorelSpace E] [MeasurableSpace V] [BorelSpace V] in
theorem pullback_weighted_action (T : E ≃ₗ[ℝ] State V)
    (G : Fin n → State V →L[ℝ] State V) (weights : Fin n → ℝ) (z : E) :
    T ((∑ k : Fin n,weights k • pullbackOperator T (G k)) z)=
      (∑ k : Fin n,weights k • G k) (T z) := by
  simp only [sum_apply,smul_apply,map_sum,map_smul,pullbackOperator_action]

omit [FiniteDimensional ℝ V] [MeasurableSpace E] [BorelSpace E] [MeasurableSpace V] [BorelSpace V] in
/-- Original and transported polynomial densities are the same linear family in different coordinates. -/
theorem pullback_polynomial_action (T : E ≃ₗ[ℝ] State V)
    (G : Fin n → State V →L[ℝ] State V) (u : ℝ) (z : E) :
    T (PolynomialGram.operatorPolynomial (fun k => pullbackOperator T (G k)) u z)=
      PolynomialGram.operatorPolynomial G u (T z) :=
  pullback_weighted_action T G (fun k => u^(k:ℕ)) z

omit [FiniteDimensional ℝ V] [MeasurableSpace E] [BorelSpace E] [MeasurableSpace V] [BorelSpace V] in
/-- The explicit mass-preservation premise identifies the original declared mass row. -/
theorem atlas_mass_agrees (T : E ≃ₗ[ℝ] State V) (l : E →ₗ[ℝ] ℝ)
    (hT : ∀ z,l z=(T z).1) : (atlasCone T).mass=l := by
  apply LinearMap.ext
  intro z
  exact (hT z).symm

omit [FiniteDimensional ℝ V] [MeasurableSpace E] [BorelSpace E] [MeasurableSpace V] [BorelSpace V] in
/-- This is exactly the normalized domain K_T from the source. -/
theorem atlas_base_iff (T : E ≃ₗ[ℝ] State V) (z : E) :
    z∈(atlasCone T).base ↔ ∃ v : V,‖v‖≤1 ∧ z=T.symm (1,v) := by
  constructor
  · rintro ⟨hz,hm⟩
    change ‖(T z).2‖≤(T z).1 at hz
    change (T z).1=1 at hm
    refine ⟨(T z).2,hz.trans_eq hm,?_⟩
    apply T.injective
    rw [T.apply_symm_apply]
    exact Prod.ext hm rfl
  · rintro ⟨v,hv,rfl⟩
    change (T (T.symm (1,v))∈cone ∧ (T (T.symm (1,v))).1=1)
    rw [T.apply_symm_apply]
    exact ⟨hv,rfl⟩

omit [FiniteDimensional ℝ V] [MeasurableSpace E] [BorelSpace E] [MeasurableSpace V] [BorelSpace V] in
/-- Exact integrated mass can equivalently be checked in the original coordinates. -/
theorem atlas_moment_mass_iff (T : E ≃ₗ[ℝ] State V)
    (G : Fin n → State V →L[ℝ] State V) :
    (∀ z,(atlasCone T).mass ((∑ k : Fin n,UniformIntervalMoments.moment k • pullbackOperator T (G k)) z)=
      (atlasCone T).mass z) ↔
    (∀ y,probabilityCone.mass ((∑ k : Fin n,UniformIntervalMoments.moment k • G k) y)=probabilityCone.mass y) := by
  constructor
  · intro h y
    have hz := h (T.symm y)
    change probabilityCone.mass (T ((∑ k : Fin n,UniformIntervalMoments.moment k • pullbackOperator T (G k))
      (T.symm y)))=probabilityCone.mass (T (T.symm y)) at hz
    rwa [pullback_weighted_action,T.apply_symm_apply] at hz
  · intro h z
    change probabilityCone.mass (T ((∑ k : Fin n,UniformIntervalMoments.moment k • pullbackOperator T (G k)) z))=
      probabilityCone.mass (T z)
    rw [pullback_weighted_action]
    exact h (T z)

/-- The literal inverse-conjugated uncertain family is a valid density instrument on K_T. -/
noncomputable def atlasUncertainInstrument (T : E ≃ₗ[ℝ] State V)
    (F Delta : A → Fin n → State V →L[ℝ] State V) (kappa e0 e1 : A → ℝ → ℝ)
    (cert : MarginCertificate F Delta kappa e0 e1)
    (hm : ∀ a y,probabilityCone.mass ((∑ k : Fin n,UniformIntervalMoments.moment k • (F a k+Delta a k)) y)=
      probabilityCone.mass y) :
    ContinuousInstrument.DensityInstrument (A := A) (atlasCone T) UniformIntervalMoments.measure where
  op a := PolynomialGram.operatorPolynomial (fun k => pullbackOperator T (F a k+Delta a k))
  measurable_op a := (PolynomialGram.operatorPolynomial_continuous _).measurable
  integrable_op a := PolynomialGram.operatorPolynomial_integrable _
  positive a := by
    filter_upwards [PolynomialGram.uniform_ae_interval] with u hu
    intro z hz
    change T (PolynomialGram.operatorPolynomial (fun k => pullbackOperator T (F a k+Delta a k)) u z)∈cone
    rw [pullback_polynomial_action,polynomial_add]
    exact robust_preserves _ _ _ _ _ (cert.margin a u hu) (cert.mass_error a u hu)
      (cert.spatial_error a u hu) (cert.cover a u hu) hz
  mass_preserving a z := by
    rw [PolynomialGram.operatorPolynomial_integral]
    exact (atlas_moment_mass_iff T (fun k => F a k+Delta a k)).mpr (hm a) z

omit [MeasurableSpace V] [BorelSpace V] in
/-- A supplied initial state in K_T gives genuine finite laws in the original atlas. -/
theorem atlas_record_probability [Fintype A] [MeasurableSpace A] [MeasurableSingletonClass A]
    (T : E ≃ₗ[ℝ] State V) (F Delta : A → Fin n → State V →L[ℝ] State V)
    (kappa e0 e1 : A → ℝ → ℝ) (cert : MarginCertificate F Delta kappa e0 e1)
    (hm : ∀ a y,probabilityCone.mass ((∑ k : Fin n,UniformIntervalMoments.moment k • (F a k+Delta a k)) y)=
      probabilityCone.mass y)
    (policy : ContinuousRecords.Policy (A := A) (Y := ℝ)) (z : E)
    (hz : ∃ v : V,‖v‖≤1 ∧ z=T.symm (1,v)) (horizon : ℕ) :
    IsProbabilityMeasure (ContinuousRecords.recordLaw (atlasUncertainInstrument T F Delta kappa e0 e1 cert hm)
      policy z horizon) :=
  ContinuousRecords.recordLaw_probability (atlasUncertainInstrument T F Delta kappa e0 e1 cert hm)
    policy ⟨z,(atlas_base_iff T z).mpr hz⟩ horizon
end Atlas

end Komorebi.LSM.RobustOrientedMargin
