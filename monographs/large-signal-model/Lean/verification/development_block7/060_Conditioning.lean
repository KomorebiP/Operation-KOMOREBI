import KomorebiLSM.FiniteTV

/-! P44: conditioning costs an inverse event-probability factor.
The proof accounts for the discarded complementary event. -/
set_option autoImplicit false
namespace Komorebi.LSM.FiniteTV
open scoped BigOperators
open FiniteBayes FiniteInstruments
variable {I : Type*} [Fintype I]

/-- Normalization comparison for actual nonnegative subprobability vectors. -/
theorem normalized_l1_bound (u v : I → ℝ) (hv : ∀ i, 0 ≤ v i)
    (ha : 0<mass u) (hb : 0<mass v) :
    l1 (normalize mass u-normalize mass v) ≤
      (l1 (u-v)+|mass u-mass v|)/mass u := by
  rw [normalized_difference mass u v (ne_of_gt ha) (ne_of_gt hb),l1_smul]
  rw [abs_inv,abs_of_pos ha]
  have h := l1_sub_le (u-v) (mass (u-v) • normalize mass v)
  rw [l1_smul,l1_prior _ (normalized_prior v hv hb),mul_one,map_sub] at h
  have he := mul_le_mul_of_nonneg_left h (inv_nonneg.mpr ha.le)
  simpa only [oblique_apply,div_eq_mul_inv,mul_comm] using he

section Events
variable [DecidableEq I]

/-- Adequate true event mass forces positive comparison mass. -/
theorem comparison_event_positive (p q : I → ℝ) (hp : IsPrior p) (hq : IsPrior q)
    (H : Finset I) (δ : ℝ) (hδ : distance p q ≤ δ) (hH : δ<eventMass p H) :
    0<eventMass q H := by
  have he := (event_difference_le_distance p q hp hq H).trans hδ
  have hb := (abs_le.mp he).2
  linarith

/-- P44: conditional laws on the same event, with both evidences positive. -/
theorem conditioning_tv_bound (p q : I → ℝ) (hp : IsPrior p) (hq : IsPrior q)
    (H : Finset I) (δ : ℝ) (hδ : distance p q ≤ δ)
    (hP : 0<eventMass p H) (hQ : 0<eventMass q H) :
    distance (conditional p H) (conditional q H) ≤ min 1 (δ/eventMass p H) := by
  apply le_min
  · exact distance_le_one _ _ (conditional_prior p hp H hP) (conditional_prior q hq H hQ)
  · have hn := normalized_l1_bound (restrict p H) (restrict q H)
      (restrict_nonneg q hq.1 H) (by rwa [restrict_mass]) (by rwa [restrict_mass])
    rw [restrict_mass,restrict_mass] at hn
    change l1 (conditional p H-conditional q H) ≤
      (l1 (restrict p H-restrict q H)+|eventMass p H-eventMass q H|)/eventMass p H at hn
    have hb := restriction_budget p q hp hq H
    have hm := (le_div_iff₀ hP).mp hn
    unfold distance at hδ ⊢
    apply (le_div_iff₀ hP).mpr
    nlinarith

/-- The explicit positivity premise for the comparison event can be discharged by a margin. -/
theorem conditioning_tv_bound_of_margin (p q : I → ℝ) (hp : IsPrior p) (hq : IsPrior q)
    (H : Finset I) (δ : ℝ) (hδ : distance p q ≤ δ) (hP : δ<eventMass p H) :
    0<eventMass q H ∧
    distance (conditional p H) (conditional q H) ≤ min 1 (δ/eventMass p H) := by
  have hQ := comparison_event_positive p q hp hq H δ hδ hP
  have hd : 0 ≤ δ := (distance_nonneg p q).trans hδ
  exact ⟨hQ,conditioning_tv_bound p q hp hq H δ hδ (lt_of_le_of_lt hd hP) hQ⟩

/-- A deterministic continuation readout cannot increase the conditional bound. -/
theorem conditional_readout_bound {J : Type*} [Fintype J] [DecidableEq J]
    (c : I → J) (p q : I → ℝ) (hp : IsPrior p) (hq : IsPrior q)
    (H : Finset I) (δ : ℝ) (hδ : distance p q ≤ δ)
    (hP : 0<eventMass p H) (hQ : 0<eventMass q H) :
    distance (aggregate c (conditional p H)) (aggregate c (conditional q H)) ≤
      min 1 (δ/eventMass p H) :=
  (distance_aggregate_le c _ _).trans (conditioning_tv_bound p q hp hq H δ hδ hP hQ)

end Events
end Komorebi.LSM.FiniteTV
