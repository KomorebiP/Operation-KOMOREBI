import Komorebi.SufficientResolution.GlobalizationRefinement

/-!
# Finite and closed-range globalization contracts

Finite-dimensional local-data spaces automatically provide the projection and
coercivity hypotheses. In Hilbert spaces the realized range must be closed;
closure is not substituted for actual realizability.
-/

set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.FiniteGlobalization

open OrthogonalResolution HilbertGlobalization HilbertConditioning

variable {G V W : Type*}
variable [AddCommGroup G] [Module ℝ G]
variable [NormedAddCommGroup V] [InnerProductSpace ℝ V]
variable [NormedAddCommGroup W] [NormedSpace ℝ W]
variable (A : G →ₗ[ℝ] V) (delta : V →L[ℝ] W)

/-- In finite local dimension, a residual-only bound exists exactly when the chain is exact. -/
 theorem finite_residual_bound_iff_exact [FiniteDimensional ℝ V]
    (h : delta.toLinearMap.comp A = 0) :
    (∃ c : ℝ, 0 < c ∧ ∀ v : V,
      Metric.infDist v (LinearMap.range A : Set V) ≤ c * ‖delta v‖) ↔
      LinearMap.range A = delta.ker := by
  constructor
  · rintro ⟨c, _, hc⟩
    exact exact_of_residual_distance_bound delta (LinearMap.range A) (range_le_kernel A delta h) c hc
  · intro he
    obtain ⟨s, hs, hc⟩ := exists_coercivity_finite delta
    refine ⟨s⁻¹, inv_pos.mpr hs, fun v => ?_⟩
    have hb := distance_le_residual_of_exact delta (LinearMap.range A) he s hs hc v
    simpa only [div_eq_mul_inv, mul_comm] using hb

/-- Positive conditioning and actual global preimages are both obtained, not assumed. -/
 theorem finite_conditioned_globalization [FiniteDimensional ℝ V]
    (h : delta.toLinearMap.comp A = 0) :
    ∃ sigma : ℝ, 0 < sigma ∧ CoerciveOffKernel delta sigma ∧ ∀ v : V,
      ∃ g : G, A g = realized (LinearMap.range A) v ∧
        ‖v - A g‖ ^ 2 =
          ‖obstruction (LinearMap.range A) delta.ker v‖ ^ 2 +
          ‖inconsistency delta.ker v‖ ^ 2 ∧
        ‖v - A g‖ ^ 2 ≤
          ‖obstruction (LinearMap.range A) delta.ker v‖ ^ 2 + (‖delta v‖ / sigma) ^ 2 := by
  obtain ⟨s, hs, hc⟩ := exists_coercivity_finite delta
  refine ⟨s, hs, hc, fun v => ?_⟩
  obtain ⟨g, hg⟩ := exists_best_global_image A v
  refine ⟨g, hg, ?_, ?_⟩
  · rw [hg]
    exact error_norm_sq _ _ (range_le_kernel A delta h) v
  · rw [hg, ← infDist_eq_error]
    exact conditioned_distance_sq delta _ (range_le_kernel A delta h) s hs hc v

/-- Every finite-dimensional compatible class has exactly one harmonic representative. -/
 theorem finite_unique_harmonic_representative [FiniteDimensional ℝ V]
    (h : delta.toLinearMap.comp A = 0)
    (c : Globalization.ObstructionSpace A delta.toLinearMap) :
    ∃! v : harmonic (LinearMap.range A) delta.ker, harmonicToQuotient A delta v = c := by
  let e := obstructionEquivHarmonic A delta h
  refine ⟨e c, e.symm_apply_apply c, ?_⟩
  intro v hv
  have he := congrArg e hv
  change e (e.symm v) = e c at he
  simpa only [e.apply_symm_apply] using he

/-- Closedness is explicit when leaving finite-dimensional local spaces. -/
 theorem closed_range_best_global [CompleteSpace V]
    (hclosed : IsClosed (LinearMap.range A : Set V)) (v : V) :
    ∃ g : G, ‖v - A g‖ = Metric.infDist v (LinearMap.range A : Set V) := by
  let : CompleteSpace (LinearMap.range A) := hclosed.completeSpace_coe
  obtain ⟨g, hg⟩ := exists_best_global_image A v
  exact ⟨g, by rw [hg, infDist_eq_error]⟩

 theorem closed_range_zero_distance_iff_realizable [CompleteSpace V]
    (hclosed : IsClosed (LinearMap.range A : Set V)) (v : V) :
    Metric.infDist v (LinearMap.range A : Set V) = 0 ↔ ∃ g : G, A g = v := by
  constructor
  · intro hz
    obtain ⟨g, hg⟩ := closed_range_best_global A hclosed v
    rw [hz] at hg
    exact ⟨g, (sub_eq_zero.mp (norm_eq_zero.mp hg)).symm⟩
  · rintro ⟨g, rfl⟩
    exact Metric.infDist_zero_of_mem (LinearMap.mem_range_self A g)

/-- Injectivity is a separate assumption for uniqueness in the global source. -/
 theorem finite_unique_best_preimage [FiniteDimensional ℝ V]
    (hA : Function.Injective A) (v : V) :
    ∃! g : G, ‖v - A g‖ = Metric.infDist v (LinearMap.range A : Set V) := by
  obtain ⟨g, hg⟩ := exists_best_global_image A v
  refine ⟨g, (best_global_image_unique A v g).mpr hg, ?_⟩
  intro g' hg'
  exact hA (((best_global_image_unique A v g').mp hg').trans hg.symm)

end Komorebi.SufficientResolution.FiniteGlobalization
