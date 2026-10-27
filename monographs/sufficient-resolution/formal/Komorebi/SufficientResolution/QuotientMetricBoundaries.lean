import Komorebi.SufficientResolution.MetricObstruction

/-!
# Boundaries of quotient-norm obstruction detection

The standard quotient seminorm sees the closure of a subspace. For a nonclosed
subspace it can vanish on a nonzero algebraic class. No closed-range assumption
is dropped from the positive reconstruction results.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.QuotientMetricBoundaries

variable {V : Type*} [NormedAddCommGroup V] [NormedSpace ℝ V]
variable (R : Submodule ℝ V)

/-- This is Mathlib's standard quotient seminorm, not a norm defined in this project. -/
theorem quotient_norm_eq_distance (v : V) :
    ‖(Submodule.Quotient.mk v : V ⧸ R)‖ = Metric.infDist v (R : Set V) :=
  QuotientAddGroup.norm_mk (S := R.toAddSubgroup) v

theorem zero_norm_iff_closure (v : V) :
    ‖(Submodule.Quotient.mk v : V ⧸ R)‖ = 0 ↔ v ∈ closure (R : Set V) :=
  QuotientAddGroup.norm_mk_eq_zero_iff_mem_closure (S := R.toAddSubgroup)

/-- Algebraic zero still means actual membership, not membership in the closure. -/
theorem class_zero_iff_membership (v : V) :
    (Submodule.Quotient.mk v : V ⧸ R) = 0 ↔ v ∈ R :=
  Submodule.Quotient.mk_eq_zero R

/-- Nonclosedness produces an actual nonzero quotient vector of seminorm zero. -/
theorem nonclosed_nonzero_zero_norm (hR : ¬ IsClosed (R : Set V)) :
    ∃ z : V ⧸ R, z ≠ 0 ∧ ‖z‖ = 0 := by
  have hx : ∃ v : V, v ∈ closure (R : Set V) ∧ v ∉ R := by
    by_contra hn
    push Not at hn
    exact hR (isClosed_of_closure_subset hn)
  obtain ⟨v, hv, hn⟩ := hx
  exact ⟨Submodule.Quotient.mk v,
    fun hz => hn ((class_zero_iff_membership R v).mp hz),
    (zero_norm_iff_closure R v).mpr hv⟩

/-- Definiteness of the standard quotient seminorm is equivalent to closedness. -/
theorem norm_detects_zero_iff_closed :
    (∀ z : V ⧸ R, ‖z‖ = 0 → z = 0) ↔ IsClosed (R : Set V) := by
  constructor
  · intro hz
    by_contra hR
    obtain ⟨z, hn, he⟩ := nonclosed_nonzero_zero_norm R hR
    exact hn (hz z he)
  · intro hR z
    refine Submodule.Quotient.induction_on R z ?_
    intro v hv
    apply (class_zero_iff_membership R v).mpr
    have hc := (zero_norm_iff_closure R v).mp hv
    rwa [hR.closure_eq] at hc

/-- Hence no bijective isometric identification with a genuine normed space exists. -/
theorem nonclosed_no_normed_isometry (hR : ¬ IsClosed (R : Set V))
    (H : Type*) [NormedAddCommGroup H] [NormedSpace ℝ H] :
    ¬ Nonempty ((V ⧸ R) ≃ₗᵢ[ℝ] H) := by
  rintro ⟨e⟩
  obtain ⟨z, hn, hz⟩ := nonclosed_nonzero_zero_norm R hR
  have he : e z = 0 := norm_eq_zero.mp ((e.norm_map z).trans hz)
  apply hn
  apply e.injective
  simpa using he

/-- The standard scalar quotient by zero retains the ordinary absolute-value norm. -/
theorem scalar_zero_range_norm (x : ℝ) :
    ‖(Submodule.Quotient.mk x : ℝ ⧸ (⊥ : Submodule ℝ ℝ))‖ = |x| := by
  rw [quotient_norm_eq_distance]
  simp

theorem scalar_unit_class_nonzero :
    (Submodule.Quotient.mk (1 : ℝ) : ℝ ⧸ (⊥ : Submodule ℝ ℝ)) ≠ 0 := by
  intro hz
  have hm : (1 : ℝ) ∈ (⊥ : Submodule ℝ ℝ) :=
    (Submodule.Quotient.mk_eq_zero (⊥ : Submodule ℝ ℝ)).mp hz
  simp only [Submodule.mem_bot, one_ne_zero] at hm

/-- A change of scale changes the quotient norm unless the metric is transported too. -/
theorem scalar_rescaling_norm (c x : ℝ) :
    ‖(Submodule.Quotient.mk (c*x) : ℝ ⧸ (⊥ : Submodule ℝ ℝ))‖ =
      |c| * ‖(Submodule.Quotient.mk x : ℝ ⧸ (⊥ : Submodule ℝ ℝ))‖ := by
  rw [scalar_zero_range_norm, scalar_zero_range_norm, abs_mul]

end Komorebi.SufficientResolution.QuotientMetricBoundaries
